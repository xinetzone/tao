"""Registry 解析集成单元测试。

覆盖范围：

- :func:`taolib.cli._world_engines.source_parser.parse_source`
- :func:`taolib.cli._world_engines.registry_config.load_registry_config`
- :func:`taolib.cli._world_engines.registry_index.query_entry`
- :func:`taolib.cli._world_engines.registry_index.select_version`
- :func:`taolib.cli._world_engines.fetcher.fetch_git`
- ``world install name@version --dry-run`` 完整链路
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from taolib.cli._world_engines.fetcher import FetchError, FetchResult, fetch_git
from taolib.cli._world_engines.registry_config import load_registry_config
from taolib.cli._world_engines.registry_index import (
    IndexEntry,
    IndexVersion,
    query_entry,
    select_version,
)
from taolib.cli._world_engines.source_parser import SourceType, parse_source
from taolib.cli.world import main

# ---------------------------------------------------------------------------
# 1. parse_source() — source 字符串分类
# ---------------------------------------------------------------------------


def test_parse_source_relative_local_path() -> None:
    """``./path/to/fragment`` 形式应识别为 LOCAL。"""
    parsed = parse_source("./path/to/fragment")
    assert parsed.source_type is SourceType.LOCAL
    assert parsed.raw == "./path/to/fragment"


def test_parse_source_absolute_local_path() -> None:
    """``/absolute/path`` 形式应识别为 LOCAL。"""
    parsed = parse_source("/absolute/path")
    assert parsed.source_type is SourceType.LOCAL
    assert parsed.raw == "/absolute/path"


def test_parse_source_registry_with_exact_version() -> None:
    """``name@1.2.0`` 应识别为 REGISTRY 并解析 name 与精确版本。"""
    parsed = parse_source("python-engineering@1.2.0")
    assert parsed.source_type is SourceType.REGISTRY
    assert parsed.name == "python-engineering"
    assert parsed.constraint == "1.2.0"


def test_parse_source_registry_with_caret_constraint() -> None:
    """``name@^1.2`` 应保留 caret 约束原文。"""
    parsed = parse_source("python-engineering@^1.2")
    assert parsed.source_type is SourceType.REGISTRY
    assert parsed.name == "python-engineering"
    assert parsed.constraint == "^1.2"


def test_parse_source_registry_without_constraint() -> None:
    """仅 ``name`` 形式应识别为 REGISTRY 且 constraint=None（即 latest.stable）。"""
    parsed = parse_source("python-engineering")
    assert parsed.source_type is SourceType.REGISTRY
    assert parsed.name == "python-engineering"
    assert parsed.constraint is None


def test_parse_source_https_git_url() -> None:
    """``https://`` URL 应识别为 GIT_URL，url 字段保留完整字符串。"""
    parsed = parse_source("https://github.com/org/repo")
    assert parsed.source_type is SourceType.GIT_URL
    assert parsed.url == "https://github.com/org/repo"


def test_parse_source_ssh_git_url() -> None:
    """``git@host:org/repo`` 应识别为 GIT_URL，避免被误识别为 registry。"""
    parsed = parse_source("git@github.com:org/repo")
    assert parsed.source_type is SourceType.GIT_URL
    assert parsed.url == "git@github.com:org/repo"


def test_parse_source_registry_short_name_with_version() -> None:
    """``citations@1.0.0`` 含 ``@`` 但无 ``//``，应识别为 REGISTRY。"""
    parsed = parse_source("citations@1.0.0")
    assert parsed.source_type is SourceType.REGISTRY
    assert parsed.name == "citations"
    assert parsed.constraint == "1.0.0"


# ---------------------------------------------------------------------------
# 2. load_registry_config() — registry.toml 读取与排序
# ---------------------------------------------------------------------------


_REGISTRY_TOML_TWO_SOURCES = """\
[registries.default]
url = "https://example.com/registry-index"
type = "git"
priority = 2

[registries.local]
url = "./registry-index"
type = "git"
priority = 1
"""


def test_load_registry_config_sorted_by_priority(tmp_path: Path) -> None:
    """两个源应按 priority 升序返回（local 在前）。"""
    agents_dir = tmp_path / ".agents"
    agents_dir.mkdir()
    (agents_dir / "registry.toml").write_text(
        _REGISTRY_TOML_TWO_SOURCES, encoding="utf-8"
    )

    sources = load_registry_config(agents_dir)

    assert len(sources) == 2
    assert sources[0].name == "local"
    assert sources[0].priority == 1
    assert sources[0].url == "./registry-index"
    assert sources[1].name == "default"
    assert sources[1].priority == 2


def test_load_registry_config_missing_file(tmp_path: Path) -> None:
    """registry.toml 不存在时应返回空列表。"""
    agents_dir = tmp_path / ".agents"
    agents_dir.mkdir()
    # 故意不创建 registry.toml

    assert load_registry_config(agents_dir) == []


def test_load_registry_config_empty_file(tmp_path: Path) -> None:
    """空 registry.toml 应返回空列表。"""
    agents_dir = tmp_path / ".agents"
    agents_dir.mkdir()
    (agents_dir / "registry.toml").write_text("", encoding="utf-8")

    assert load_registry_config(agents_dir) == []


# ---------------------------------------------------------------------------
# 3. query_entry() — Registry Index 条目查询
# ---------------------------------------------------------------------------


_INDEX_ENTRY_TOML = """\
[metadata]
name = "citations"
description = "Citations fragment"
category = "ci"
type = "fragment"

[source]
repository = "https://example.com/citations"

[[versions]]
version = "1.0.0"
git_url = "https://example.com/citations"
git_ref = "v1.0.0"
manifest_path = "manifest.toml"
yanked = false

[latest]
stable = "1.0.0"
"""


def _make_index(tmp_path: Path) -> Path:
    """构造 ``tmp_path/registry-index/fragments/ci/citations.toml`` 索引。"""
    index_root = tmp_path / "registry-index"
    fragments_dir = index_root / "fragments" / "ci"
    fragments_dir.mkdir(parents=True)
    (fragments_dir / "citations.toml").write_text(_INDEX_ENTRY_TOML, encoding="utf-8")
    return index_root


def test_query_entry_hit(tmp_path: Path) -> None:
    """命中条目时返回完整 IndexEntry。"""
    index_root = _make_index(tmp_path)

    entry = query_entry(index_root, "citations")

    assert entry is not None
    assert entry.name == "citations"
    assert entry.entry_type == "fragment"
    assert entry.latest_stable == "1.0.0"
    assert len(entry.versions) == 1
    assert entry.versions[0].version == "1.0.0"
    assert entry.versions[0].git_ref == "v1.0.0"


def test_query_entry_not_found(tmp_path: Path) -> None:
    """名称未在 Index 中时返回 None。"""
    index_root = _make_index(tmp_path)

    assert query_entry(index_root, "nonexistent") is None


def test_query_entry_index_dir_missing(tmp_path: Path) -> None:
    """Index 目录不存在时返回 None。"""
    missing = tmp_path / "no-such-index"

    assert query_entry(missing, "citations") is None


# ---------------------------------------------------------------------------
# 4. select_version() — 版本选择策略
# ---------------------------------------------------------------------------


def _make_entry(versions: list[IndexVersion], latest_stable: str = "") -> IndexEntry:
    """构造测试用 IndexEntry（其余字段保留默认）。"""
    return IndexEntry(
        name="demo",
        description="",
        category="",
        entry_type="fragment",
        source_repository="",
        versions=versions,
        latest_stable=latest_stable,
    )


def _v(version: str, *, yanked: bool = False) -> IndexVersion:
    """生成一个最小可用的 IndexVersion。"""
    return IndexVersion(
        version=version,
        git_url="https://example.com/demo",
        git_ref=f"v{version}",
        manifest_path="manifest.toml",
        yanked=yanked,
    )


def test_select_version_none_returns_latest_stable() -> None:
    """constraint=None 时应返回 latest_stable 对应版本。"""
    entry = _make_entry(
        [_v("1.0.0"), _v("1.2.0"), _v("2.0.0")],
        latest_stable="1.2.0",
    )

    selected = select_version(entry, None)

    assert selected is not None
    assert selected.version == "1.2.0"


def test_select_version_exact_match() -> None:
    """精确版本约束（``==1.0.0``）应严格命中该版本。"""
    entry = _make_entry([_v("1.0.0"), _v("1.1.0")], latest_stable="1.1.0")

    selected = select_version(entry, "==1.0.0")

    assert selected is not None
    assert selected.version == "1.0.0"


def test_select_version_caret_picks_max_compatible() -> None:
    """``^1.0`` 约束应在 1.x 中挑选最大版本。"""
    entry = _make_entry(
        [_v("1.0.0"), _v("1.2.3"), _v("1.5.0"), _v("2.0.0")],
        latest_stable="1.5.0",
    )

    selected = select_version(entry, "^1.0")

    assert selected is not None
    assert selected.version == "1.5.0"


def test_select_version_skips_yanked() -> None:
    """``yanked=True`` 的版本应被跳过，即使匹配约束。"""
    entry = _make_entry(
        [_v("1.0.0"), _v("1.5.0", yanked=True), _v("1.2.0")],
        latest_stable="1.2.0",
    )

    selected = select_version(entry, "^1.0")

    assert selected is not None
    # 1.5.0 被 yank，应回退到 1.2.0
    assert selected.version == "1.2.0"


def test_select_version_no_match_returns_none() -> None:
    """约束不匹配任何版本时返回 None。"""
    entry = _make_entry([_v("1.0.0"), _v("1.2.0")], latest_stable="1.2.0")

    assert select_version(entry, "^3.0") is None


# ---------------------------------------------------------------------------
# 5. fetch_git() — 通过 mock subprocess 验证不做真实网络调用
# ---------------------------------------------------------------------------


_FETCH_MANIFEST = """\
[fragment]
name = "demo"
version = "1.0.0"
description = "demo"
"""


def test_fetch_git_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """成功 clone 时返回 FetchResult，且 manifest 路径存在。"""

    def fake_run(cmd, **kwargs):
        # 提取 git clone 的目标目录（命令最后一个参数）
        target = Path(cmd[-1])
        target.mkdir(parents=True, exist_ok=True)
        (target / "manifest.toml").write_text(_FETCH_MANIFEST, encoding="utf-8")
        return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

    with patch("subprocess.run", side_effect=fake_run):
        result = fetch_git("https://example.com/demo", "v1.0.0")

    try:
        assert isinstance(result, FetchResult)
        assert result.manifest_path.exists()
        assert result.manifest_path.name == "manifest.toml"
        assert result.local_path.is_dir()
    finally:
        result.cleanup()


def test_fetch_git_missing_git_command() -> None:
    """git 不可用时（FileNotFoundError）应抛 FetchError。"""
    with (
        patch("subprocess.run", side_effect=FileNotFoundError("git")),
        pytest.raises(FetchError, match="git"),
    ):
        fetch_git("https://example.com/demo", "v1.0.0")


def test_fetch_git_clone_failure() -> None:
    """returncode != 0 时应抛 FetchError 并清理临时目录。"""

    def fake_run(cmd, **kwargs):
        return subprocess.CompletedProcess(
            args=cmd, returncode=128, stdout="", stderr="fatal: not found"
        )

    with (
        patch("subprocess.run", side_effect=fake_run),
        pytest.raises(FetchError, match="git clone 失败"),
    ):
        fetch_git("https://example.com/demo", "v1.0.0")


# ---------------------------------------------------------------------------
# 6. 集成：world install name@version --dry-run 完整链路
# ---------------------------------------------------------------------------


_WORLD_TOML = """\
[world]
name = "test-world"
version = "2.0.0"
description = "Test world"
min-alpha = 0.1
"""

_REGISTRY_TOML_LOCAL_ONLY = """\
[registries.local]
url = "./registry-index"
type = "git"
priority = 1
"""

_CITATIONS_INDEX_TOML = """\
[metadata]
name = "citations"
description = "Citations fragment"
category = "ci"
type = "fragment"

[source]
repository = "https://example.com/citations"

[[versions]]
version = "1.0.0"
git_url = "https://example.com/citations"
git_ref = "v1.0.0"
manifest_path = "manifest.toml"
yanked = false

[latest]
stable = "1.0.0"
"""

_CITATIONS_FRAGMENT_MANIFEST = """\
[fragment]
name = "citations"
version = "1.0.0"
description = "Citations fragment"

[fragment.kernel-compat]
min-version = "1.0.0"
max-version = "5.0.0"

[fragment.dependencies]

[fragment.conflicts]

[fragment.contents]
rules = []
"""


def test_registry_install_dry_run(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """``world install citations@1.0.0 --dry-run`` 完整链路：

    parse_source → load_registry_config → query_entry → select_version
    → fetch_git（mock） → validate → 输出 PASS 报告，返回 0。
    """
    # 1) 构造 .agents/world.toml + .agents/registry.toml
    agents_dir = tmp_path / ".agents"
    agents_dir.mkdir()
    (agents_dir / "world.toml").write_text(_WORLD_TOML, encoding="utf-8")
    (agents_dir / "registry.toml").write_text(
        _REGISTRY_TOML_LOCAL_ONLY, encoding="utf-8"
    )

    # 2) 构造 mock registry-index：tmp_path/registry-index/fragments/ci/citations.toml
    index_dir = tmp_path / "registry-index" / "fragments" / "ci"
    index_dir.mkdir(parents=True)
    (index_dir / "citations.toml").write_text(_CITATIONS_INDEX_TOML, encoding="utf-8")

    # 3) 构造 fetch_git 返回的临时目录（含 manifest.toml）
    fetched_dir = tmp_path / "fetched-citations"
    fetched_dir.mkdir()
    fetched_manifest = fetched_dir / "manifest.toml"
    fetched_manifest.write_text(_CITATIONS_FRAGMENT_MANIFEST, encoding="utf-8")

    cleanup_called: list[bool] = []

    def fake_fetch_git(git_url, git_ref, manifest_path="manifest.toml"):
        return FetchResult(
            local_path=fetched_dir,
            manifest_path=fetched_manifest,
            cleanup=lambda: cleanup_called.append(True),
        )

    # 4) 在 install 模块中替换 fetch_git（避免真实网络调用）
    monkeypatch.setattr(
        "taolib.cli._world_commands.install.fetch_git",
        fake_fetch_git,
    )

    # 5) 切换工作目录以便 find_world_toml 与相对 url 解析生效
    monkeypatch.chdir(tmp_path)

    rc = main(["install", "citations@1.0.0", "--dry-run"])

    out = capsys.readouterr().out
    assert rc == 0, out
    assert "citations@1.0.0" in out
    assert "PASS" in out
    # 确保 cleanup 回调被触发（FetchResult.cleanup 应在 _install_with_cleanup 中调用）
    assert cleanup_called == [True]
