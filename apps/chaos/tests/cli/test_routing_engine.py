"""``world route`` 路由引擎单元测试。

覆盖 :mod:`taolib.cli._world_engines.routing_engine` 的核心 API
（``parse_routing_config`` / ``resolve_routes`` / ``collect_targets`` /
``resolve_role_bindings``），以及 ``world route`` CLI 子命令的端到端集成。

所有测试基于项目实际的 ``apps/chaos/.agents/world.toml`` 与
``apps/chaos/.agents/roles/`` 资产，避免重复构造 fixture 数据。
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from taolib.cli._world_engines import routing_engine
from taolib.cli._world_engines.routing_engine import (
    RoutingConfig,
    collect_targets,
    parse_routing_config,
    resolve_role_bindings,
    resolve_routes,
)
from taolib.cli.world import main

# ---------------------------------------------------------------------------
# Fixtures：定位项目实际的 world.toml 与 roles/ 目录
# ---------------------------------------------------------------------------

# tests/cli/test_routing_engine.py → tests/cli → tests → <chaos root>
_CHAOS_ROOT = Path(__file__).resolve().parents[2]
_AGENTS_DIR = _CHAOS_ROOT / ".agents"


@pytest.fixture(scope="module")
def world_toml_path() -> Path:
    """返回 ``apps/chaos/.agents/world.toml`` 的绝对路径。"""
    path = _AGENTS_DIR / "world.toml"
    assert path.is_file(), f"测试前置：world.toml 必须存在于 {path}"
    return path


@pytest.fixture(scope="module")
def routing_config(world_toml_path: Path) -> RoutingConfig:
    """解析项目实际 world.toml 得到的 RoutingConfig。"""
    return parse_routing_config(world_toml_path)


@pytest.fixture(scope="module")
def roles_dir() -> Path:
    """返回 ``apps/chaos/.agents/roles/`` 的绝对路径。"""
    path = _AGENTS_DIR / "roles"
    assert path.is_dir(), f"测试前置：roles 目录必须存在于 {path}"
    return path


# ---------------------------------------------------------------------------
# 1. parse_routing_config
# ---------------------------------------------------------------------------


def test_parse_routing_config_top_level(routing_config: RoutingConfig) -> None:
    """version / conflict_resolution / supported_phases / 规则总数。"""
    assert routing_config.version == "0.1.0"
    assert routing_config.conflict_resolution == "merge"
    assert routing_config.supported_phases == [
        "planning",
        "coding",
        "testing",
        "review",
        "deploying",
    ]
    assert len(routing_config.rules) == 11


def test_parse_routing_config_python_dev_rule(routing_config: RoutingConfig) -> None:
    """验证具体 ``python-dev`` 规则的所有字段值与 world.toml 一致。"""
    rule = next(r for r in routing_config.rules if r.id == "python-dev")
    assert rule.targets == ["rules/python.md", "rules/data-flow-ordering.md"]
    assert rule.priority == 5
    assert rule.roles == ["python-dev", "full-stack"]
    assert rule.triggers.intents == [
        "python",
        "uv",
        "dependency",
        "import",
        "venv",
    ]
    assert rule.triggers.file_patterns == [
        "**/*.py",
        "pyproject.toml",
        "uv.lock",
    ]
    assert rule.triggers.phases == ["coding", "testing"]


def test_parse_routing_config_missing_file(tmp_path: Path) -> None:
    """world.toml 不存在时抛 FileNotFoundError。"""
    with pytest.raises(FileNotFoundError):
        parse_routing_config(tmp_path / "nonexistent.toml")


def test_parse_routing_config_missing_routing_section(tmp_path: Path) -> None:
    """world.toml 缺少 ``[routing]`` 区块时抛 KeyError。"""
    p = tmp_path / "world.toml"
    p.write_text('[world]\nname = "x"\n', encoding="utf-8")
    with pytest.raises(KeyError):
        parse_routing_config(p)


# ---------------------------------------------------------------------------
# 2. resolve_routes
# ---------------------------------------------------------------------------


def test_resolve_routes_intent_only(routing_config: RoutingConfig) -> None:
    """纯 intent 匹配 → 命中 python-dev 且 matched_by 仅含 intent。"""
    matches = resolve_routes(
        routing_config, intents=["python"], role="python-dev"
    )
    rule_ids = [m.rule_id for m in matches]
    assert "python-dev" in rule_ids
    target = next(m for m in matches if m.rule_id == "python-dev")
    assert target.matched_by == ["intent"]
    assert target.priority == 5


def test_resolve_routes_file_pattern_only(routing_config: RoutingConfig) -> None:
    """纯 file_pattern 匹配 → 命中 backend 规则。"""
    matches = resolve_routes(
        routing_config, files=["src/app/main.py"], role="backend-dev"
    )
    rule_ids = [m.rule_id for m in matches]
    assert "backend" in rule_ids
    target = next(m for m in matches if m.rule_id == "backend")
    assert target.matched_by == ["file_pattern"]


def test_resolve_routes_phase_only(routing_config: RoutingConfig) -> None:
    """纯 phase 匹配 → pr-review 因 ``roles=["reviewer","*"]`` 命中。"""
    matches = resolve_routes(routing_config, phase="review")
    rule_ids = [m.rule_id for m in matches]
    assert "pr-review" in rule_ids
    target = next(m for m in matches if m.rule_id == "pr-review")
    assert target.matched_by == ["phase"]


def test_resolve_routes_multi_dimension(routing_config: RoutingConfig) -> None:
    """同时提供 intent + file + phase，python-dev 三维度全命中。"""
    matches = resolve_routes(
        routing_config,
        intents=["python"],
        files=["src/main.py"],
        phase="coding",
        role="python-dev",
    )
    target = next(m for m in matches if m.rule_id == "python-dev")
    assert set(target.matched_by) == {"intent", "file_pattern", "phase"}


def test_resolve_routes_role_filter_excludes(routing_config: RoutingConfig) -> None:
    """frontend-dev 不在 python-dev.roles 中 → 不命中 python-dev。"""
    matches = resolve_routes(
        routing_config, intents=["python"], role="frontend-dev"
    )
    assert all(m.rule_id != "python-dev" for m in matches)


def test_resolve_routes_wildcard_role(routing_config: RoutingConfig) -> None:
    """``roles=["*"]`` 应匹配任意 role（含未在任何规则中声明的角色）。"""
    matches = resolve_routes(
        routing_config, intents=["context"], role="any-role"
    )
    rule_ids = [m.rule_id for m in matches]
    assert "context-economy" in rule_ids


def test_resolve_routes_no_match(routing_config: RoutingConfig) -> None:
    """不存在的 intent + 不存在的 role → 空匹配列表。"""
    matches = resolve_routes(
        routing_config,
        intents=["nonexistent-intent"],
        role="nonexistent-role",
    )
    assert matches == []


def test_resolve_routes_sorted_by_priority_desc(
    routing_config: RoutingConfig,
) -> None:
    """匹配结果按 priority 降序，priority 相等时 rule_id 字典序升序。"""
    matches = resolve_routes(
        routing_config,
        intents=["python"],
        files=["src/main.py"],
        phase="coding",
        role="python-dev",
    )
    assert len(matches) >= 2
    priorities = [m.priority for m in matches]
    assert priorities == sorted(priorities, reverse=True)
    # 同 priority 段内验证 rule_id 字典序
    for i in range(len(matches) - 1):
        if matches[i].priority == matches[i + 1].priority:
            assert matches[i].rule_id < matches[i + 1].rule_id


# ---------------------------------------------------------------------------
# 3. collect_targets
# ---------------------------------------------------------------------------


def test_collect_targets_merge_dedup(routing_config: RoutingConfig) -> None:
    """merge 策略：多匹配规则 targets 合并去重保序。"""
    matches = resolve_routes(
        routing_config,
        intents=["python"],
        files=["src/main.py"],
        phase="coding",
        role="python-dev",
    )
    targets = collect_targets(matches, "merge")
    # 去重：每个路径仅出现一次
    assert len(targets) == len(set(targets))
    # 期望含 python-dev 自身的 targets
    assert "rules/python.md" in targets
    assert "rules/data-flow-ordering.md" in targets


def test_collect_targets_priority_first(routing_config: RoutingConfig) -> None:
    """priority-first 策略：仅取最高优先级且 rule_id 字典序最小的规则。"""
    matches = resolve_routes(
        routing_config,
        intents=["python"],
        files=["src/main.py"],
        phase="coding",
        role="python-dev",
    )
    targets = collect_targets(matches, "priority-first")
    top_priority = max(m.priority for m in matches)
    top_rules = sorted(
        [m for m in matches if m.priority == top_priority],
        key=lambda m: m.rule_id,
    )
    assert targets == list(top_rules[0].targets)


def test_collect_targets_empty() -> None:
    """空匹配列表无论策略均返回空列表。"""
    assert collect_targets([], "merge") == []
    assert collect_targets([], "priority-first") == []


def test_collect_targets_invalid_strategy(routing_config: RoutingConfig) -> None:
    """非法策略名抛 ValueError。"""
    matches = resolve_routes(
        routing_config, intents=["python"], role="python-dev"
    )
    assert matches  # 前置：确保非空
    with pytest.raises(ValueError):
        collect_targets(matches, "ask")


# ---------------------------------------------------------------------------
# 4. resolve_role_bindings
# ---------------------------------------------------------------------------


def test_resolve_role_bindings_known_role(roles_dir: Path) -> None:
    """已知角色 python-dev 返回 frontmatter 中的 rules+references 合并。"""
    bindings = resolve_role_bindings(roles_dir, "python-dev")
    assert "rules/python.md" in bindings
    assert "rules/data-flow-ordering.md" in bindings
    assert "docs/version-tracking.md" in bindings
    # 去重保序：唯一性
    assert len(bindings) == len(set(bindings))


def test_resolve_role_bindings_unknown_role(roles_dir: Path) -> None:
    """未知角色返回空列表，不抛异常。"""
    assert resolve_role_bindings(roles_dir, "nonexistent-role-xyz") == []


# ---------------------------------------------------------------------------
# 5. CLI 集成测试（subprocess + 直接 main 调用）
# ---------------------------------------------------------------------------


def _run_world_cli(
    args: list[str], cwd: Path
) -> subprocess.CompletedProcess[str]:
    """以子进程方式调用 ``python -m taolib.cli.world ...``。

    将 ``apps/chaos/src`` 注入 PYTHONPATH，确保未安装时也能正确导入。
    """
    env = os.environ.copy()
    src_dir = str(_CHAOS_ROOT / "src")
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = (
        src_dir + os.pathsep + existing if existing else src_dir
    )
    return subprocess.run(
        [sys.executable, "-m", "taolib.cli.world", *args],
        cwd=str(cwd),
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )


def test_cli_route_json_output() -> None:
    """``world route --intent python --role python-dev`` 输出有效 JSON。"""
    result = _run_world_cli(
        ["route", "--intent", "python", "--role", "python-dev"],
        cwd=_CHAOS_ROOT,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["routing_version"] == "0.1.0"
    assert payload["query"]["intents"] == ["python"]
    assert payload["query"]["role"] == "python-dev"
    assert payload["strategy"] == "merge"
    assert isinstance(payload["matches"], list)
    assert any(m["rule_id"] == "python-dev" for m in payload["matches"])
    assert "rules/python.md" in payload["resolved_targets"]


def test_cli_route_targets_only(
    routing_config: RoutingConfig,
) -> None:
    """``--targets-only`` 模式输出每行一条路径，且与 collect_targets 一致。"""
    result = _run_world_cli(
        [
            "route",
            "--intent",
            "python",
            "--role",
            "python-dev",
            "--targets-only",
        ],
        cwd=_CHAOS_ROOT,
    )
    assert result.returncode == 0, result.stderr
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    expected = collect_targets(
        resolve_routes(routing_config, intents=["python"], role="python-dev"),
        "merge",
    )
    assert lines == expected


def test_cli_route_missing_world_toml(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
) -> None:
    """在不含 .agents/world.toml 的目录运行 ``world route`` → 退出码 1。"""
    monkeypatch.chdir(tmp_path)
    rc = main(["route", "--intent", "python"])
    assert rc == 1
    err = capsys.readouterr().err
    assert "world.toml" in err


def test_cli_route_strategy_override(monkeypatch: pytest.MonkeyPatch) -> None:
    """``--strategy priority-first`` 覆盖 world.toml 默认策略。"""
    monkeypatch.chdir(_CHAOS_ROOT)
    result = _run_world_cli(
        [
            "route",
            "--intent",
            "python",
            "--file",
            "src/main.py",
            "--phase",
            "coding",
            "--role",
            "python-dev",
            "--strategy",
            "priority-first",
        ],
        cwd=_CHAOS_ROOT,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["strategy"] == "priority-first"
