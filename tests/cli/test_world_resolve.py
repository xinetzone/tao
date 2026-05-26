"""``world resolve`` 子命令及 lock_generator / token 注入单元测试。"""

from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from taolib.cli._world_commands.resolve import handle_resolve, register_resolve_parser
from taolib.cli._world_engines.lock_generator import (
    LockFile,
    LockPackage,
    compute_world_toml_hash,
    generate_lock,
    parse_lock,
)
from taolib.cli._world_engines.registry_cache import inject_token

# ---------------------------------------------------------------------------
# 辅助工具
# ---------------------------------------------------------------------------

_WORLD_TOML_TEMPLATE = """\
[world]
name = "test-world"
version = "2.0.0"
description = "Test world"

[fragments.citations]
version = ">=1.0.0"

[fragments.python]
version = ">=1.0.0"
"""

_REGISTRY_TOML_TEMPLATE = """\
[registries.local]
url = "{index_path}"
type = "git"
priority = 0
"""

_INDEX_CITATIONS = """\
[metadata]
name = "citations"
description = "Citations fragment"
category = "ci"
type = "fragment"

[source]
repository = "https://github.com/org/repo"

[[versions]]
version = "1.2.0"
git_url = "https://github.com/org/repo"
git_ref = "v1.2.0"
manifest_path = "manifest.toml"
yanked = false

[latest]
stable = "1.2.0"
"""

_INDEX_PYTHON = """\
[metadata]
name = "python"
description = "Python fragment"
category = "py"
type = "fragment"

[source]
repository = "https://github.com/org/repo"

[[versions]]
version = "1.0.0"
git_url = "https://github.com/org/repo"
git_ref = "v1.0.0"
manifest_path = "manifest.toml"
yanked = false

[latest]
stable = "1.0.0"
"""


def _setup_world(tmp_path: Path) -> Path:
    """创建 .agents/world.toml 并返回 world.toml 路径。"""
    agents_dir = tmp_path / ".agents"
    agents_dir.mkdir(parents=True, exist_ok=True)
    world_toml = agents_dir / "world.toml"
    world_toml.write_text(_WORLD_TOML_TEMPLATE, encoding="utf-8")
    return world_toml


def _setup_registry_index(tmp_path: Path) -> Path:
    """创建 mock registry-index 目录结构，返回根目录。"""
    index_root = tmp_path / "mock-index"
    # citations → fragments/ci/citations.toml
    ci_dir = index_root / "fragments" / "ci"
    ci_dir.mkdir(parents=True, exist_ok=True)
    (ci_dir / "citations.toml").write_text(_INDEX_CITATIONS, encoding="utf-8")
    # python → fragments/py/python.toml
    py_dir = index_root / "fragments" / "py"
    py_dir.mkdir(parents=True, exist_ok=True)
    (py_dir / "python.toml").write_text(_INDEX_PYTHON, encoding="utf-8")
    return index_root


def _setup_registry_toml(agents_dir: Path, index_path: Path) -> None:
    """创建 .agents/registry.toml 指向本地 index 路径。"""
    content = _REGISTRY_TOML_TEMPLATE.format(
        index_path=str(index_path).replace("\\", "/")
    )
    (agents_dir / "registry.toml").write_text(content, encoding="utf-8")


# ---------------------------------------------------------------------------
# test_world_resolve: 正常解析生成 world.lock
# ---------------------------------------------------------------------------


def test_resolve_generates_lock(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """正常解析生成 world.lock，含 [lock] 段和 [[packages]] 段。"""
    world_toml = _setup_world(tmp_path)
    index_path = _setup_registry_index(tmp_path)
    agents_dir = world_toml.parent
    _setup_registry_toml(agents_dir, index_path)

    monkeypatch.chdir(tmp_path)

    # mock resolve_index_path 直接返回本地 index 路径
    monkeypatch.setattr(
        "taolib.cli._world_commands.resolve.resolve_index_path",
        lambda source, force_update=False: index_path,
    )

    args = argparse.Namespace(locked=False, update=False)
    rc = handle_resolve(args)

    assert rc == 0

    lock_path = agents_dir / "world.lock"
    assert lock_path.exists()

    # 验证 lock 文件结构
    lock_file = parse_lock(lock_path)
    assert lock_file is not None
    assert lock_file.world_toml_hash.startswith("sha256:")
    assert lock_file.resolver_version == "1"
    assert len(lock_file.packages) == 2

    names = {p.name for p in lock_file.packages}
    assert "citations" in names
    assert "python" in names


# ---------------------------------------------------------------------------
# test_world_resolve: --locked + hash 一致
# ---------------------------------------------------------------------------


def test_resolve_locked_hash_match(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """--locked 模式下 hash 一致时返回 0。"""
    world_toml = _setup_world(tmp_path)
    agents_dir = world_toml.parent
    monkeypatch.chdir(tmp_path)

    # 计算当前 hash 并预生成一致的 lock 文件
    current_hash = compute_world_toml_hash(world_toml)
    lock_file = LockFile(
        generated="2026-01-01T00:00:00Z",
        resolver_version="1",
        world_toml_hash=current_hash,
        packages=[],
    )
    generate_lock(lock_file, agents_dir / "world.lock")

    args = argparse.Namespace(locked=True, update=False)
    rc = handle_resolve(args)
    assert rc == 0


# ---------------------------------------------------------------------------
# test_world_resolve: --locked + hash 不一致
# ---------------------------------------------------------------------------


def test_resolve_locked_hash_mismatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """--locked 模式下 hash 不一致时返回 10。"""
    world_toml = _setup_world(tmp_path)
    agents_dir = world_toml.parent
    monkeypatch.chdir(tmp_path)

    # 预生成 lock 文件（使用错误的 hash）
    lock_file = LockFile(
        generated="2026-01-01T00:00:00Z",
        resolver_version="1",
        world_toml_hash="sha256:0000000000000000000000000000000000000000000000000000000000000000",
        packages=[],
    )
    generate_lock(lock_file, agents_dir / "world.lock")

    args = argparse.Namespace(locked=True, update=False)
    rc = handle_resolve(args)
    assert rc == 10


# ---------------------------------------------------------------------------
# test_world_resolve: Registry 中找不到组件
# ---------------------------------------------------------------------------


def test_resolve_fragment_not_found(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Registry 中找不到组件时返回 10。"""
    world_toml = _setup_world(tmp_path)
    agents_dir = world_toml.parent
    monkeypatch.chdir(tmp_path)

    # 创建空 registry-index（无条目）
    empty_index = tmp_path / "empty-index"
    (empty_index / "fragments").mkdir(parents=True, exist_ok=True)
    _setup_registry_toml(agents_dir, empty_index)

    monkeypatch.setattr(
        "taolib.cli._world_commands.resolve.resolve_index_path",
        lambda source, force_update=False: empty_index,
    )

    args = argparse.Namespace(locked=False, update=False)
    rc = handle_resolve(args)
    assert rc == 10


# ---------------------------------------------------------------------------
# lock_generator: roundtrip
# ---------------------------------------------------------------------------


def test_lock_generator_roundtrip(tmp_path: Path) -> None:
    """LockFile → generate_lock → parse_lock roundtrip 验证字段一致。"""
    lock_file = LockFile(
        generated="2026-05-26T12:00:00Z",
        resolver_version="1",
        world_toml_hash="sha256:abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
        packages=[
            LockPackage(
                name="citations",
                version="1.2.0",
                type="fragment",
                source="registry+local",
                git_url="https://github.com/org/repo",
                git_ref="v1.2.0",
                checksum="sha256:deadbeef",
                dependencies=["python@>=1.0.0"],
            ),
            LockPackage(
                name="python",
                version="1.0.0",
                type="fragment",
                source="registry+local",
                git_url="https://github.com/org/repo",
                git_ref="v1.0.0",
                checksum=None,
                dependencies=[],
            ),
        ],
    )

    lock_path = tmp_path / "world.lock"
    generate_lock(lock_file, lock_path)

    parsed = parse_lock(lock_path)
    assert parsed is not None
    assert parsed.generated == lock_file.generated
    assert parsed.resolver_version == lock_file.resolver_version
    assert parsed.world_toml_hash == lock_file.world_toml_hash
    assert len(parsed.packages) == 2

    pkg0 = parsed.packages[0]
    assert pkg0.name == "citations"
    assert pkg0.version == "1.2.0"
    assert pkg0.type == "fragment"
    assert pkg0.source == "registry+local"
    assert pkg0.git_url == "https://github.com/org/repo"
    assert pkg0.git_ref == "v1.2.0"
    assert pkg0.checksum == "sha256:deadbeef"
    assert pkg0.dependencies == ["python@>=1.0.0"]

    pkg1 = parsed.packages[1]
    assert pkg1.name == "python"
    assert pkg1.checksum is None
    assert pkg1.dependencies == []


# ---------------------------------------------------------------------------
# compute_world_toml_hash
# ---------------------------------------------------------------------------


def test_compute_world_toml_hash(tmp_path: Path) -> None:
    """验证 hash 前缀为 'sha256:' 且长度正确 (sha256: + 64 hex)。"""
    f = tmp_path / "world.toml"
    f.write_text("[world]\nname = \"test\"\n", encoding="utf-8")

    result = compute_world_toml_hash(f)
    assert result.startswith("sha256:")
    hex_part = result[len("sha256:"):]
    assert len(hex_part) == 64
    # 确保全是十六进制字符
    int(hex_part, 16)


# ---------------------------------------------------------------------------
# register_resolve_parser
# ---------------------------------------------------------------------------


def test_register_resolve_parser() -> None:
    """验证 parser 注册后包含 --locked 和 --update。"""
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    register_resolve_parser(subparsers)

    args = parser.parse_args(["resolve", "--locked", "--update"])
    assert args.locked is True
    assert args.update is True


# ---------------------------------------------------------------------------
# Token 注入测试 (inject_token)
# ---------------------------------------------------------------------------


def test_inject_token_https(monkeypatch: pytest.MonkeyPatch) -> None:
    """HTTPS URL 设置 WORLD_TOKEN 后正确注入。"""
    monkeypatch.setenv("WORLD_TOKEN", "mytoken")
    url = "https://github.com/org/repo"
    result = inject_token(url)
    assert result == "https://x-access-token:mytoken@github.com/org/repo"


def test_inject_token_non_https(monkeypatch: pytest.MonkeyPatch) -> None:
    """非 HTTPS URL 不注入。"""
    monkeypatch.setenv("WORLD_TOKEN", "mytoken")
    url = "git@github.com:org/repo"
    result = inject_token(url)
    assert result == url


def test_inject_token_not_set(monkeypatch: pytest.MonkeyPatch) -> None:
    """WORLD_TOKEN 未设置时 URL 不变。"""
    monkeypatch.delenv("WORLD_TOKEN", raising=False)
    url = "https://github.com/org/repo"
    result = inject_token(url)
    assert result == url
