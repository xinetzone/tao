"""Registry 缓存机制单元测试。

覆盖范围：

- :func:`taolib.cli._world_engines.registry_cache.get_cache_config`
- :func:`taolib.cli._world_engines.registry_cache._is_cache_fresh`
- :func:`taolib.cli._world_engines.registry_cache.ensure_index_cache`
- :func:`taolib.cli._world_engines.registry_cache._clone_index`
- :func:`taolib.cli._world_engines.registry_cache._fetch_index`
- :func:`taolib.cli._world_engines.registry_index.resolve_index_path`
- :class:`taolib.cli._world_engines.registry_config.RegistrySource` ``cache_ttl`` 字段
"""

from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path
from unittest.mock import patch

import pytest

from taolib.cli._world_engines.registry_cache import (
    DEFAULT_TTL,
    CacheConfig,
    _clone_index,
    _fetch_index,
    _is_cache_fresh,
    ensure_index_cache,
    get_cache_config,
)
from taolib.cli._world_engines.registry_config import (
    RegistrySource,
    load_registry_config,
)
from taolib.cli._world_engines.registry_index import resolve_index_path


# ---------------------------------------------------------------------------
# 1. get_cache_config() — 环境变量读取
# ---------------------------------------------------------------------------


def test_get_cache_config_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    """未设置环境变量时返回默认 TTL，offline/force_update 均为 False。"""
    monkeypatch.delenv("WORLD_CACHE_DIR", raising=False)
    monkeypatch.delenv("WORLD_OFFLINE", raising=False)

    config = get_cache_config()

    assert config.ttl == DEFAULT_TTL
    assert config.offline is False
    assert config.force_update is False
    assert isinstance(config.cache_dir, Path)


def test_get_cache_config_world_cache_dir_override(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """``WORLD_CACHE_DIR`` 环境变量应覆盖默认缓存目录。"""
    custom_dir = tmp_path / "custom-cache"
    monkeypatch.setenv("WORLD_CACHE_DIR", str(custom_dir))
    monkeypatch.delenv("WORLD_OFFLINE", raising=False)

    config = get_cache_config()

    assert config.cache_dir == custom_dir


def test_get_cache_config_offline_true(monkeypatch: pytest.MonkeyPatch) -> None:
    """``WORLD_OFFLINE=true`` 应启用离线模式。"""
    monkeypatch.setenv("WORLD_OFFLINE", "true")
    monkeypatch.delenv("WORLD_CACHE_DIR", raising=False)

    config = get_cache_config()

    assert config.offline is True


def test_get_cache_config_offline_one(monkeypatch: pytest.MonkeyPatch) -> None:
    """``WORLD_OFFLINE=1`` 应启用离线模式。"""
    monkeypatch.setenv("WORLD_OFFLINE", "1")
    monkeypatch.delenv("WORLD_CACHE_DIR", raising=False)

    config = get_cache_config()

    assert config.offline is True


def test_get_cache_config_offline_false_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """未设置 ``WORLD_OFFLINE`` 时 offline=False。"""
    monkeypatch.delenv("WORLD_OFFLINE", raising=False)
    monkeypatch.delenv("WORLD_CACHE_DIR", raising=False)

    config = get_cache_config()

    assert config.offline is False


def test_get_cache_config_force_update(monkeypatch: pytest.MonkeyPatch) -> None:
    """``force_update=True`` 传入时正确设置。"""
    monkeypatch.delenv("WORLD_OFFLINE", raising=False)
    monkeypatch.delenv("WORLD_CACHE_DIR", raising=False)

    config = get_cache_config(force_update=True)

    assert config.force_update is True


def test_get_cache_config_custom_ttl(monkeypatch: pytest.MonkeyPatch) -> None:
    """传入的 ttl 参数应被原样保留。"""
    monkeypatch.delenv("WORLD_OFFLINE", raising=False)
    monkeypatch.delenv("WORLD_CACHE_DIR", raising=False)

    config = get_cache_config(ttl=7200)

    assert config.ttl == 7200


# ---------------------------------------------------------------------------
# 2. _is_cache_fresh() — TTL 判断
# ---------------------------------------------------------------------------


def _make_git_dir(cache_path: Path) -> Path:
    """创建 ``cache_path/.git`` 目录并返回其路径。"""
    git_dir = cache_path / ".git"
    git_dir.mkdir(parents=True, exist_ok=True)
    return git_dir


def test_is_cache_fresh_fetch_head_in_ttl(tmp_path: Path) -> None:
    """``FETCH_HEAD`` 存在且 mtime 在 TTL 内应返回 True。"""
    cache_path = tmp_path / "cache"
    git_dir = _make_git_dir(cache_path)
    fetch_head = git_dir / "FETCH_HEAD"
    fetch_head.write_text("", encoding="utf-8")
    # 设置 mtime 为当前时间（在任何 TTL 内）
    now = time.time()
    os.utime(fetch_head, (now, now))

    assert _is_cache_fresh(cache_path, ttl=3600) is True


def test_is_cache_fresh_fetch_head_expired(tmp_path: Path) -> None:
    """``FETCH_HEAD`` mtime 已过 TTL 应返回 False。"""
    cache_path = tmp_path / "cache"
    git_dir = _make_git_dir(cache_path)
    fetch_head = git_dir / "FETCH_HEAD"
    fetch_head.write_text("", encoding="utf-8")
    # 设置 mtime 为 7200 秒前（超过 3600 TTL）
    old = time.time() - 7200
    os.utime(fetch_head, (old, old))

    assert _is_cache_fresh(cache_path, ttl=3600) is False


def test_is_cache_fresh_falls_back_to_head(tmp_path: Path) -> None:
    """无 ``FETCH_HEAD`` 但有 ``HEAD`` 且在 TTL 内应返回 True。"""
    cache_path = tmp_path / "cache"
    git_dir = _make_git_dir(cache_path)
    head = git_dir / "HEAD"
    head.write_text("ref: refs/heads/main\n", encoding="utf-8")
    now = time.time()
    os.utime(head, (now, now))

    assert _is_cache_fresh(cache_path, ttl=3600) is True


def test_is_cache_fresh_head_expired(tmp_path: Path) -> None:
    """无 ``FETCH_HEAD`` 且 ``HEAD`` 已过期应返回 False。"""
    cache_path = tmp_path / "cache"
    git_dir = _make_git_dir(cache_path)
    head = git_dir / "HEAD"
    head.write_text("ref: refs/heads/main\n", encoding="utf-8")
    old = time.time() - 7200
    os.utime(head, (old, old))

    assert _is_cache_fresh(cache_path, ttl=3600) is False


def test_is_cache_fresh_no_git_metadata(tmp_path: Path) -> None:
    """无 ``.git/HEAD`` 和 ``.git/FETCH_HEAD`` 应返回 False。"""
    cache_path = tmp_path / "cache"
    _make_git_dir(cache_path)  # 仅创建 .git 目录，无元数据文件

    assert _is_cache_fresh(cache_path, ttl=3600) is False


# ---------------------------------------------------------------------------
# 3. ensure_index_cache() — 缓存决策矩阵
# ---------------------------------------------------------------------------


def test_ensure_index_cache_first_clone(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """缓存不存在 + 非离线 → 调用 _clone_index → 返回路径。"""
    cache_dir = tmp_path / "cache-root"
    config = CacheConfig(
        cache_dir=cache_dir,
        ttl=3600,
        offline=False,
        force_update=False,
    )

    clone_calls: list[tuple[str, Path]] = []
    fetch_calls: list[Path] = []

    def fake_clone(url: str, dest: Path) -> bool:
        clone_calls.append((url, dest))
        # 模拟 clone 成功：创建 .git 目录
        (dest / ".git").mkdir(parents=True, exist_ok=True)
        return True

    def fake_fetch(cache_path: Path) -> bool:
        fetch_calls.append(cache_path)
        return True

    monkeypatch.setattr(
        "taolib.cli._world_engines.registry_cache._clone_index", fake_clone
    )
    monkeypatch.setattr(
        "taolib.cli._world_engines.registry_cache._fetch_index", fake_fetch
    )

    result = ensure_index_cache("default", "https://example.com/index", config)

    assert result == cache_dir / "default"
    assert len(clone_calls) == 1
    assert clone_calls[0][0] == "https://example.com/index"
    assert fetch_calls == []


def test_ensure_index_cache_reuse_within_ttl(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """缓存存在 + 未过期 → 不调网络 → 直接返回路径。"""
    cache_dir = tmp_path / "cache-root"
    cache_path = cache_dir / "default"
    git_dir = cache_path / ".git"
    git_dir.mkdir(parents=True)
    fetch_head = git_dir / "FETCH_HEAD"
    fetch_head.write_text("", encoding="utf-8")
    # mtime 为当前时间 → 未过期
    now = time.time()
    os.utime(fetch_head, (now, now))

    config = CacheConfig(
        cache_dir=cache_dir,
        ttl=3600,
        offline=False,
        force_update=False,
    )

    clone_calls: list[tuple[str, Path]] = []
    fetch_calls: list[Path] = []

    monkeypatch.setattr(
        "taolib.cli._world_engines.registry_cache._clone_index",
        lambda url, dest: clone_calls.append((url, dest)) or True,
    )
    monkeypatch.setattr(
        "taolib.cli._world_engines.registry_cache._fetch_index",
        lambda p: fetch_calls.append(p) or True,
    )

    result = ensure_index_cache("default", "https://example.com/index", config)

    assert result == cache_path
    assert clone_calls == []
    assert fetch_calls == []


def test_ensure_index_cache_fetch_when_expired(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """缓存存在 + 已过期 → 调用 _fetch_index → 返回路径。"""
    cache_dir = tmp_path / "cache-root"
    cache_path = cache_dir / "default"
    git_dir = cache_path / ".git"
    git_dir.mkdir(parents=True)
    fetch_head = git_dir / "FETCH_HEAD"
    fetch_head.write_text("", encoding="utf-8")
    # mtime 为 7200 秒前 → 过期
    old = time.time() - 7200
    os.utime(fetch_head, (old, old))

    config = CacheConfig(
        cache_dir=cache_dir,
        ttl=3600,
        offline=False,
        force_update=False,
    )

    clone_calls: list[tuple[str, Path]] = []
    fetch_calls: list[Path] = []

    monkeypatch.setattr(
        "taolib.cli._world_engines.registry_cache._clone_index",
        lambda url, dest: clone_calls.append((url, dest)) or True,
    )
    monkeypatch.setattr(
        "taolib.cli._world_engines.registry_cache._fetch_index",
        lambda p: fetch_calls.append(p) or True,
    )

    result = ensure_index_cache("default", "https://example.com/index", config)

    assert result == cache_path
    assert clone_calls == []
    assert fetch_calls == [cache_path]


def test_ensure_index_cache_offline_with_cache(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """离线模式 + 缓存存在 → 直接返回（不调网络，不检查 TTL）。"""
    cache_dir = tmp_path / "cache-root"
    cache_path = cache_dir / "default"
    (cache_path / ".git").mkdir(parents=True)
    # 故意不创建 FETCH_HEAD/HEAD，验证 offline 路径不检查 TTL

    config = CacheConfig(
        cache_dir=cache_dir,
        ttl=3600,
        offline=True,
        force_update=False,
    )

    clone_calls: list[tuple[str, Path]] = []
    fetch_calls: list[Path] = []

    monkeypatch.setattr(
        "taolib.cli._world_engines.registry_cache._clone_index",
        lambda url, dest: clone_calls.append((url, dest)) or True,
    )
    monkeypatch.setattr(
        "taolib.cli._world_engines.registry_cache._fetch_index",
        lambda p: fetch_calls.append(p) or True,
    )

    result = ensure_index_cache("default", "https://example.com/index", config)

    assert result == cache_path
    assert clone_calls == []
    assert fetch_calls == []


def test_ensure_index_cache_offline_without_cache(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """离线模式 + 缓存不存在 → 返回 None。"""
    cache_dir = tmp_path / "cache-root"

    config = CacheConfig(
        cache_dir=cache_dir,
        ttl=3600,
        offline=True,
        force_update=False,
    )

    clone_calls: list[tuple[str, Path]] = []

    monkeypatch.setattr(
        "taolib.cli._world_engines.registry_cache._clone_index",
        lambda url, dest: clone_calls.append((url, dest)) or True,
    )

    result = ensure_index_cache("default", "https://example.com/index", config)

    assert result is None
    assert clone_calls == []


def test_ensure_index_cache_force_update(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """``force_update=True`` 强制调用 _fetch_index，即使未过期。"""
    cache_dir = tmp_path / "cache-root"
    cache_path = cache_dir / "default"
    git_dir = cache_path / ".git"
    git_dir.mkdir(parents=True)
    fetch_head = git_dir / "FETCH_HEAD"
    fetch_head.write_text("", encoding="utf-8")
    # mtime 为当前 → 未过期
    now = time.time()
    os.utime(fetch_head, (now, now))

    config = CacheConfig(
        cache_dir=cache_dir,
        ttl=3600,
        offline=False,
        force_update=True,
    )

    fetch_calls: list[Path] = []

    monkeypatch.setattr(
        "taolib.cli._world_engines.registry_cache._fetch_index",
        lambda p: fetch_calls.append(p) or True,
    )

    result = ensure_index_cache("default", "https://example.com/index", config)

    assert result == cache_path
    assert fetch_calls == [cache_path]


# ---------------------------------------------------------------------------
# 4. _clone_index() / _fetch_index() — subprocess mock
# ---------------------------------------------------------------------------


def test_clone_index_success(tmp_path: Path) -> None:
    """``git clone`` returncode=0 时返回 True。"""
    dest = tmp_path / "cache" / "default"

    def fake_run(cmd, **kwargs):  # noqa: ANN001, ANN003
        return subprocess.CompletedProcess(
            args=cmd, returncode=0, stdout="", stderr=""
        )

    with patch("subprocess.run", side_effect=fake_run):
        assert _clone_index("https://example.com/index", dest) is True


def test_clone_index_failure(tmp_path: Path) -> None:
    """``git clone`` returncode!=0 时返回 False。"""
    dest = tmp_path / "cache" / "default"

    def fake_run(cmd, **kwargs):  # noqa: ANN001, ANN003
        return subprocess.CompletedProcess(
            args=cmd, returncode=128, stdout="", stderr="fatal: not found"
        )

    with patch("subprocess.run", side_effect=fake_run):
        assert _clone_index("https://example.com/index", dest) is False


def test_clone_index_git_not_available(tmp_path: Path) -> None:
    """git 命令不可用（FileNotFoundError）时返回 False。"""
    dest = tmp_path / "cache" / "default"

    with patch("subprocess.run", side_effect=FileNotFoundError("git")):
        assert _clone_index("https://example.com/index", dest) is False


def test_fetch_index_success(tmp_path: Path) -> None:
    """fetch 与 reset 均 returncode=0 时返回 True。"""
    cache_path = tmp_path / "cache" / "default"
    cache_path.mkdir(parents=True)

    def fake_run(cmd, **kwargs):  # noqa: ANN001, ANN003
        return subprocess.CompletedProcess(
            args=cmd, returncode=0, stdout="", stderr=""
        )

    with patch("subprocess.run", side_effect=fake_run):
        assert _fetch_index(cache_path) is True


def test_fetch_index_fetch_failure(tmp_path: Path) -> None:
    """``git fetch`` returncode!=0 时返回 False。"""
    cache_path = tmp_path / "cache" / "default"
    cache_path.mkdir(parents=True)

    def fake_run(cmd, **kwargs):  # noqa: ANN001, ANN003
        return subprocess.CompletedProcess(
            args=cmd, returncode=1, stdout="", stderr="fatal"
        )

    with patch("subprocess.run", side_effect=fake_run):
        assert _fetch_index(cache_path) is False


def test_fetch_index_reset_failure(tmp_path: Path) -> None:
    """``git fetch`` 成功但 ``git reset`` 失败时返回 False。"""
    cache_path = tmp_path / "cache" / "default"
    cache_path.mkdir(parents=True)

    call_count = {"n": 0}

    def fake_run(cmd, **kwargs):  # noqa: ANN001, ANN003
        call_count["n"] += 1
        rc = 0 if call_count["n"] == 1 else 1
        return subprocess.CompletedProcess(
            args=cmd, returncode=rc, stdout="", stderr=""
        )

    with patch("subprocess.run", side_effect=fake_run):
        assert _fetch_index(cache_path) is False


def test_fetch_index_git_not_available(tmp_path: Path) -> None:
    """git 命令不可用（FileNotFoundError）时返回 False。"""
    cache_path = tmp_path / "cache" / "default"
    cache_path.mkdir(parents=True)

    with patch("subprocess.run", side_effect=FileNotFoundError("git")):
        assert _fetch_index(cache_path) is False


# ---------------------------------------------------------------------------
# 5. resolve_index_path() — 远程 URL 集成
# ---------------------------------------------------------------------------


def test_resolve_index_path_remote_url_hit(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """远程 URL + ensure_index_cache 返回路径 → 返回该路径。"""
    expected_path = tmp_path / "fake-cache" / "default"
    expected_path.mkdir(parents=True)

    monkeypatch.setattr(
        "taolib.cli._world_engines.registry_index.ensure_index_cache",
        lambda name, url, config: expected_path,
    )

    source = RegistrySource(
        name="default",
        url="https://example.com/index.git",
        type="git",
        priority=1,
        cache_ttl=3600,
    )

    result = resolve_index_path(source)

    assert result == expected_path


def test_resolve_index_path_remote_url_miss(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """远程 URL + ensure_index_cache 返回 None → 返回 None。"""
    monkeypatch.setattr(
        "taolib.cli._world_engines.registry_index.ensure_index_cache",
        lambda name, url, config: None,
    )

    source = RegistrySource(
        name="default",
        url="https://example.com/index.git",
        type="git",
        priority=1,
        cache_ttl=3600,
    )

    result = resolve_index_path(source)

    assert result is None


def test_resolve_index_path_local_path_bypasses_cache(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """本地路径不应调用 ensure_index_cache。"""
    local_index = tmp_path / "registry-index"
    local_index.mkdir()

    call_log: list[str] = []

    def spy(name, url, config):  # noqa: ANN001
        call_log.append(name)
        return None

    monkeypatch.setattr(
        "taolib.cli._world_engines.registry_index.ensure_index_cache", spy
    )

    source = RegistrySource(
        name="local",
        url=str(local_index),
        type="git",
        priority=1,
        cache_ttl=3600,
    )

    result = resolve_index_path(source)

    assert result == local_index.resolve()
    assert call_log == []


def test_resolve_index_path_empty_url() -> None:
    """空 URL 直接返回 None。"""
    source = RegistrySource(
        name="x",
        url="",
        type="git",
        priority=1,
        cache_ttl=3600,
    )

    assert resolve_index_path(source) is None


# ---------------------------------------------------------------------------
# 6. RegistrySource.cache_ttl 字段
# ---------------------------------------------------------------------------


_REGISTRY_TOML_WITH_CACHE_TTL = """\
[registries.default]
url = "https://example.com/registry-index"
type = "git"
priority = 1
cache-ttl = 7200
"""

_REGISTRY_TOML_WITHOUT_CACHE_TTL = """\
[registries.default]
url = "https://example.com/registry-index"
type = "git"
priority = 1
"""


def test_load_registry_config_with_cache_ttl(tmp_path: Path) -> None:
    """含 ``cache-ttl = 7200`` 时解析为 ``cache_ttl=7200``。"""
    agents_dir = tmp_path / ".agents"
    agents_dir.mkdir()
    (agents_dir / "registry.toml").write_text(
        _REGISTRY_TOML_WITH_CACHE_TTL, encoding="utf-8"
    )

    sources = load_registry_config(agents_dir)

    assert len(sources) == 1
    assert sources[0].cache_ttl == 7200


def test_load_registry_config_default_cache_ttl(tmp_path: Path) -> None:
    """缺省 ``cache-ttl`` 时默认值为 3600。"""
    agents_dir = tmp_path / ".agents"
    agents_dir.mkdir()
    (agents_dir / "registry.toml").write_text(
        _REGISTRY_TOML_WITHOUT_CACHE_TTL, encoding="utf-8"
    )

    sources = load_registry_config(agents_dir)

    assert len(sources) == 1
    assert sources[0].cache_ttl == 3600
