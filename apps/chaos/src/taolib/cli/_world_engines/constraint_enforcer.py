"""Constraint enforcer: constraints.toml 的运行时执行引擎。

本模块实现对 ``.agents/constraints.toml`` 约束声明的运行时执行。
它与 :mod:`~taolib.cli._world_engines.role_resolver` 中的 :class:`RoleContext`
配合使用，在多智能体协作中强制执行操作合法性校验。

仅依赖标准库（``tomllib`` / ``dataclasses`` / ``pathlib``）。
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from taolib.cli._world_engines.role_resolver import RoleContext

__all__ = [
    "ParallelConstraints",
    "ConstraintsConfig",
    "EnforcementResult",
    "ConstraintError",
    "ConstraintConfigError",
    "load_constraints",
    "enforce_constraints",
    "check_parallel_isolation",
]


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class ConstraintError(Exception):
    """约束系统基础异常。"""


class ConstraintConfigError(ConstraintError):
    """约束配置解析失败。"""


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ParallelConstraints:
    """并行执行约束配置。"""

    file_isolation: bool = False
    module_boundary: bool = False
    integration_serial: bool = False
    conflict_strategy: str = "merge"  # "merge" | "reboundary" | "serialize"


@dataclass(frozen=True)
class ConstraintsConfig:
    """解析后的 constraints.toml 配置。"""

    strong: dict[str, bool] = field(default_factory=dict)
    weak: dict[str, str] = field(default_factory=dict)
    parallel: ParallelConstraints = field(default_factory=ParallelConstraints)


@dataclass(frozen=True)
class EnforcementResult:
    """约束执行结果。"""

    passed: bool
    violated_constraints: list[str] = field(default_factory=list)
    details: dict[str, str] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _parse_parallel(raw: dict) -> ParallelConstraints:
    """从 TOML dict 解析 ParallelConstraints。"""
    return ParallelConstraints(
        file_isolation=bool(raw.get("file_isolation", False)),
        module_boundary=bool(raw.get("module_boundary", False)),
        integration_serial=bool(raw.get("integration_serial", False)),
        conflict_strategy=str(raw.get("conflict_strategy", "merge")),
    )


def _parse_strong(raw: dict) -> dict[str, bool]:
    """将 [constraints.strong] 区块解析为 {name: bool} 映射。"""
    return {str(k): bool(v) for k, v in raw.items()}


def _parse_weak(raw: dict) -> dict[str, str]:
    """将 [constraints.weak] 区块解析为 {name: decision_owner} 映射。"""
    return {str(k): str(v) for k, v in raw.items()}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def load_constraints(constraints_path: Path) -> ConstraintsConfig:
    """解析 constraints.toml 文件并返回结构化配置。

    Args:
        constraints_path: constraints.toml 文件的完整路径。

    Returns:
        解析后的 :class:`ConstraintsConfig` 实例。

    Raises:
        FileNotFoundError: 文件不存在。
        ConstraintConfigError: TOML 解析失败。
    """
    if not constraints_path.exists():
        raise FileNotFoundError(f"Constraints file not found: {constraints_path}")

    try:
        text = constraints_path.read_bytes()
        data = tomllib.loads(text.decode("utf-8"))
    except tomllib.TOMLDecodeError as exc:
        raise ConstraintConfigError(
            f"Failed to parse constraints file '{constraints_path}': {exc}"
        ) from exc
    except OSError as exc:
        raise ConstraintConfigError(
            f"Cannot read constraints file '{constraints_path}': {exc}"
        ) from exc

    # 缺少 [constraints] 区块时返回全空默认值
    constraints_section = data.get("constraints")
    if constraints_section is None:
        return ConstraintsConfig()

    strong_raw = constraints_section.get("strong", {})
    weak_raw = constraints_section.get("weak", {})
    parallel_raw = constraints_section.get("parallel", {})

    return ConstraintsConfig(
        strong=_parse_strong(strong_raw),
        weak=_parse_weak(weak_raw),
        parallel=_parse_parallel(parallel_raw),
    )


def enforce_constraints(
    constraints_path: Path,
    role_ctx: RoleContext | None,
    action: str,
    context: dict,
) -> EnforcementResult:
    """执行约束检查。

    根据 action 类型应用对应的约束规则，返回执行结果。

    Args:
        constraints_path: constraints.toml 文件路径。
        role_ctx: 当前角色上下文，可为 None（表示无角色）。
        action: 操作类型。支持：
            - ``"enter_session"``: 检查 agent_requires_role
            - ``"modify_file"``: 检查 permission_scoped_to_role_or_agent
            - ``"switch_role"``: 检查 handoff_explicit
            - ``"parallel_assign"``: 检查 file_isolation
        context: 操作上下文字典，不同 action 需要不同的键值。

    Returns:
        :class:`EnforcementResult` 实例。

    Raises:
        FileNotFoundError: constraints.toml 不存在。
        ConstraintConfigError: 配置解析失败。
    """
    config = load_constraints(constraints_path)

    violated: list[str] = []
    details: dict[str, str] = {}

    if action == "enter_session":
        _check_enter_session(config, role_ctx, violated, details)
    elif action == "modify_file":
        _check_modify_file(config, role_ctx, context, violated, details)
    elif action == "switch_role":
        _check_switch_role(config, context, violated, details)
    elif action == "parallel_assign":
        _check_parallel_assign(config, context, violated, details)

    return EnforcementResult(
        passed=len(violated) == 0,
        violated_constraints=violated,
        details=details,
    )


def check_parallel_isolation(
    config: ConstraintsConfig,
    file_sets: list[set[str]],
) -> list[tuple[int, int, set[str]]]:
    """专用并行隔离检查。

    接受多个 Agent 的文件集合列表，检测各集合之间是否存在文件交集。

    Args:
        config: 约束配置实例。
        file_sets: 每个 Agent 操作的文件路径集合列表。

    Returns:
        冲突对列表，每个元素为 ``(agent_index_a, agent_index_b, overlapping_files)``。
        无冲突时返回空列表。
    """
    if not config.parallel.file_isolation:
        return []

    conflicts: list[tuple[int, int, set[str]]] = []
    count = len(file_sets)

    for i in range(count):
        for j in range(i + 1, count):
            overlap = file_sets[i] & file_sets[j]
            if overlap:
                conflicts.append((i, j, overlap))

    return conflicts


# ---------------------------------------------------------------------------
# Action-specific enforcement checks
# ---------------------------------------------------------------------------


def _check_enter_session(
    config: ConstraintsConfig,
    role_ctx: RoleContext | None,
    violated: list[str],
    details: dict[str, str],
) -> None:
    """检查 enter_session 动作：agent_requires_role 约束。"""
    if config.strong.get("agent_requires_role", False) and role_ctx is None:
        constraint_name = "agent_requires_role"
        violated.append(constraint_name)
        details[constraint_name] = (
            "Agent must have an active role to enter a session, "
            "but no role context was provided."
        )


def _check_modify_file(
    config: ConstraintsConfig,
    role_ctx: RoleContext | None,
    context: dict,
    violated: list[str],
    details: dict[str, str],
) -> None:
    """检查 modify_file 动作：permission_scoped_to_role_or_agent 约束。"""
    if not config.strong.get("permission_scoped_to_role_or_agent", False):
        return

    # 约束启用时，必须有 role 才能修改文件
    if role_ctx is None:
        constraint_name = "permission_scoped_to_role_or_agent"
        violated.append(constraint_name)
        details[constraint_name] = (
            "File modification requires an active role or agent identity, "
            "but no role context was provided."
        )
        return

    # 检查 context 中是否提供了 file_path
    file_path = context.get("file_path")
    if not file_path:
        constraint_name = "permission_scoped_to_role_or_agent"
        violated.append(constraint_name)
        details[constraint_name] = (
            "File modification requires 'file_path' in context "
            "when permission_scoped_to_role_or_agent is enabled."
        )


def _check_switch_role(
    config: ConstraintsConfig,
    context: dict,
    violated: list[str],
    details: dict[str, str],
) -> None:
    """检查 switch_role 动作：handoff_explicit 约束。"""
    if not config.strong.get("handoff_explicit", False):
        return

    handoff_reason = context.get("handoff_reason")
    if not handoff_reason or not str(handoff_reason).strip():
        constraint_name = "handoff_explicit"
        violated.append(constraint_name)
        details[constraint_name] = (
            "Role switch requires an explicit handoff reason "
            "(non-empty 'handoff_reason' in context) "
            "when handoff_explicit constraint is enabled."
        )


def _check_parallel_assign(
    config: ConstraintsConfig,
    context: dict,
    violated: list[str],
    details: dict[str, str],
) -> None:
    """检查 parallel_assign 动作：file_isolation 约束。"""
    if not config.parallel.file_isolation:
        return

    file_sets = context.get("file_sets")
    if not file_sets or not isinstance(file_sets, list):
        constraint_name = "file_isolation"
        violated.append(constraint_name)
        details[constraint_name] = (
            "Parallel assignment requires 'file_sets' (list[set[str]]) "
            "in context when file_isolation is enabled."
        )
        return

    conflicts = check_parallel_isolation(config, file_sets)
    if conflicts:
        constraint_name = "file_isolation"
        violated.append(constraint_name)
        conflict_descriptions = []
        for idx_a, idx_b, overlap in conflicts:
            conflict_descriptions.append(
                f"Agent {idx_a} and Agent {idx_b} share files: {sorted(overlap)}"
            )
        details[constraint_name] = "File isolation violated — " + "; ".join(
            conflict_descriptions
        )
