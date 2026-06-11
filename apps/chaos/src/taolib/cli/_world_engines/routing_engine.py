"""Routing engine: parse ``[routing]`` from ``world.toml`` and resolve matches.

本模块实现 ``routing-protocol.md`` Draft v0.1 描述的声明式上下文路由：
将 ``world.toml`` 的 ``[routing]`` 区块解析为结构化配置，并根据 intents /
file_patterns / phases / role 评估匹配的规则，最后按冲突解决策略汇总
``targets`` 资产路径。

仅依赖标准库（``tomllib`` / ``dataclasses`` / ``fnmatch`` / ``pathlib``）。
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from fnmatch import fnmatch
from pathlib import Path

from taolib.cli._world_engines.role_file_utils import extract_frontmatter, find_role_file

__all__ = [
    "RouteTriggers",
    "RouteRule",
    "RoutingConfig",
    "RouteMatch",
    "parse_routing_config",
    "resolve_routes",
    "collect_targets",
    "resolve_role_bindings",
]


@dataclass(frozen=True)
class RouteTriggers:
    """路由触发条件（三维度）。"""

    intents: list[str] = field(default_factory=list)
    file_patterns: list[str] = field(default_factory=list)
    phases: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class RouteRule:
    """单条路由规则。"""

    id: str
    targets: list[str]
    priority: int
    roles: list[str]
    triggers: RouteTriggers


@dataclass(frozen=True)
class RoutingConfig:
    """完整路由配置。"""

    version: str
    conflict_resolution: str  # "merge" | "priority-first" | "ask"
    supported_phases: list[str]
    rules: list[RouteRule]


@dataclass(frozen=True)
class RouteMatch:
    """单条规则的匹配结果。"""

    rule_id: str
    targets: list[str]
    priority: int
    matched_by: list[str]  # 命中维度: "intent" / "file_pattern" / "phase"


def parse_routing_config(world_toml_path: Path) -> RoutingConfig:
    """从 ``world.toml`` 解析 ``[routing]`` 区块为结构化配置。

    Args:
        world_toml_path: ``world.toml`` 文件路径。

    Returns:
        解析后的 :class:`RoutingConfig` 实例。

    Raises:
        FileNotFoundError: ``world.toml`` 不存在。
        KeyError: ``[routing]`` 区块缺失。
    """
    if not world_toml_path.exists():
        raise FileNotFoundError(f"world.toml not found: {world_toml_path}")

    with world_toml_path.open("rb") as f:
        data = tomllib.load(f)

    if "routing" not in data:
        raise KeyError(f"[routing] section missing in {world_toml_path}")

    routing = data["routing"]
    version = routing.get("version", "")
    conflict_resolution = routing.get("conflict_resolution", "merge")
    supported_phases = list(routing.get("phases", {}).get("supported", []))

    rules: list[RouteRule] = []
    for raw in routing.get("rules", []):
        triggers_data = raw.get("triggers", {})
        triggers = RouteTriggers(
            intents=list(triggers_data.get("intents", [])),
            file_patterns=list(triggers_data.get("file_patterns", [])),
            phases=list(triggers_data.get("phases", [])),
        )
        rules.append(
            RouteRule(
                id=raw.get("id", ""),
                targets=list(raw.get("targets", [])),
                priority=int(raw.get("priority", 0)),
                roles=list(raw.get("roles", [])),
                triggers=triggers,
            ),
        )

    return RoutingConfig(
        version=version,
        conflict_resolution=conflict_resolution,
        supported_phases=supported_phases,
        rules=rules,
    )


def _role_matches(rule_roles: list[str], role: str | None) -> bool:
    """检查 role 是否满足规则的 roles 过滤。

    - ``"*"`` 在 ``rule_roles`` 中视为通配，匹配任意角色（含 ``None``）
    - 否则要求 ``role`` 非空且出现在 ``rule_roles`` 中
    """
    if "*" in rule_roles:
        return True
    if role is None:
        return False
    return role in rule_roles


def resolve_routes(
    config: RoutingConfig,
    *,
    intents: list[str] | None = None,
    files: list[str] | None = None,
    phase: str | None = None,
    role: str | None = None,
) -> list[RouteMatch]:
    """评估所有路由规则，返回匹配的规则列表。

    匹配逻辑（按 ``routing-protocol.md`` §3）：

    - ``triggers`` 内部三维度之间 **OR** 关系
    - ``triggers`` 与 ``roles`` 之间 **AND** 关系
    - 同一维度内多值 **OR** 关系
    - ``"*"`` 在 ``roles`` 中匹配所有角色

    Args:
        config: 路由配置。
        intents: 任务意图关键词列表。
        files: 涉及的文件路径列表。
        phase: 当前 session 阶段。
        role: 当前 agent 角色 id。

    Returns:
        匹配的规则列表，按 ``priority`` 降序排列；并列时按 ``rule_id``
        字典序升序，便于确定性输出。
    """
    intents = intents or []
    files = files or []

    matches: list[RouteMatch] = []
    for rule in config.rules:
        if not _role_matches(rule.roles, role):
            continue

        matched_by: list[str] = []

        if intents and any(i in rule.triggers.intents for i in intents):
            matched_by.append("intent")

        if (
            files
            and rule.triggers.file_patterns
            and any(
                fnmatch(f, pat) for f in files for pat in rule.triggers.file_patterns
            )
        ):
            matched_by.append("file_pattern")

        if phase is not None and phase in rule.triggers.phases:
            matched_by.append("phase")

        if not matched_by:
            continue

        matches.append(
            RouteMatch(
                rule_id=rule.id,
                targets=list(rule.targets),
                priority=rule.priority,
                matched_by=matched_by,
            ),
        )

    matches.sort(key=lambda m: (-m.priority, m.rule_id))
    return matches


def collect_targets(
    matches: list[RouteMatch],
    strategy: str = "merge",
) -> list[str]:
    """根据冲突解决策略汇总最终 ``targets`` 列表。

    Args:
        matches: 匹配结果列表（应已按 ``priority`` 降序排列）。
        strategy: 冲突解决策略。

            - ``"merge"``：合并所有匹配规则的 ``targets``，去重保序。
            - ``"priority-first"``：仅取 ``priority`` 最高的规则的
              ``targets``，并列时取 ``rule_id`` 字典序最小者。

    Returns:
        去重后的 ``targets`` 路径列表。

    Raises:
        ValueError: 当 ``strategy`` 不在受支持枚举内时抛出。
    """
    if not matches:
        return []

    if strategy == "merge":
        seen: set[str] = set()
        result: list[str] = []
        for m in matches:
            for t in m.targets:
                if t not in seen:
                    seen.add(t)
                    result.append(t)
        return result

    if strategy == "priority-first":
        top_priority = max(m.priority for m in matches)
        top = [m for m in matches if m.priority == top_priority]
        top.sort(key=lambda m: m.rule_id)
        chosen = top[0]
        seen = set()
        result = []
        for t in chosen.targets:
            if t not in seen:
                seen.add(t)
                result.append(t)
        return result

    raise ValueError(f"Unsupported conflict resolution strategy: {strategy!r}")


def resolve_role_bindings(roles_dir: Path, role_id: str) -> list[str]:
    """从 Role 文件的 TOML frontmatter 提取 always-on bindings。

    解析 ``roles/<role_id>.md`` 的 ``+++`` TOML frontmatter，
    提取 ``bindings.rules`` 与 ``bindings.references`` 并按顺序合并。

    Args:
        roles_dir: ``roles/`` 目录路径。
        role_id: 角色 id。

    Returns:
        该角色默认绑定的资产路径列表。找不到角色文件或 frontmatter
        缺失时返回空列表。
    """
    role_path = find_role_file(roles_dir, role_id)
    if role_path is None:
        return []

    try:
        text = role_path.read_text(encoding="utf-8")
        frontmatter = extract_frontmatter(text)
        if frontmatter is None:
            return []
        data = tomllib.loads(frontmatter)
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError):
        return []

    bindings = data.get("bindings", {})
    rules = list(bindings.get("rules", []))
    references = list(bindings.get("references", []))

    seen: set[str] = set()
    result: list[str] = []
    for item in [*rules, *references]:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result
