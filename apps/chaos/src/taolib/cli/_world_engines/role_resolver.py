"""Role resolver: @role 提及功能的核心解析器。

本模块实现角色文件的定位、解析与激活逻辑，支持从 ``.agents/roles/``
目录结构中按 role_id 加载完整角色上下文（frontmatter 元数据 + Markdown body），
并组装为可注入 Agent 的 :class:`ContextBundle`。

仅依赖标准库（``tomllib`` / ``dataclasses`` / ``fnmatch`` / ``pathlib``）。
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from fnmatch import fnmatch
from pathlib import Path

from taolib.cli._world_engines.routing_engine import _extract_frontmatter, _find_role_file

__all__ = [
    "RoleBindings",
    "RolePermissions",
    "RoleContext",
    "PermissionResult",
    "ContextBundle",
    "RoleError",
    "RoleNotFoundError",
    "RoleParseError",
    "resolve_role",
    "activate_role",
    "check_permission",
]


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class RoleError(Exception):
    """角色系统基础异常。"""


class RoleNotFoundError(RoleError):
    """角色文件不存在。"""


class RoleParseError(RoleError):
    """角色文件解析失败。"""


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RoleBindings:
    """角色绑定资源声明。"""

    rules: list[str] = field(default_factory=list)
    references: list[str] = field(default_factory=list)
    skills: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class RolePermissions:
    """角色文件修改权限声明。"""

    can_modify: list[str] = field(default_factory=list)
    cannot_modify: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class RoleContext:
    """解析后的完整角色上下文。"""

    id: str
    domain: str
    layer: str  # "governance" | "engineering"
    bindings: RoleBindings
    permissions: RolePermissions
    non_goals: list[str]
    description: str
    responsibilities: list[str]


@dataclass(frozen=True)
class PermissionResult:
    """权限检查结果。"""

    allowed: bool
    reason: str
    matched_rule: str | None


@dataclass
class ContextBundle:
    """激活角色后的完整上下文包。"""

    role: RoleContext
    loaded_rules: dict[str, str] = field(default_factory=dict)
    loaded_references: dict[str, str] = field(default_factory=dict)
    active_skills: list[str] = field(default_factory=list)
    routing_overrides: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_LAYER_DIRS = ("governance", "engineering")


def _determine_layer(role_path: Path) -> str:
    """根据文件所在子目录确定 layer。

    若文件位于 ``governance/`` 或 ``engineering/`` 子目录则返回对应名称，
    否则默认为 ``"engineering"``。
    """
    parent_name = role_path.parent.name
    if parent_name in _LAYER_DIRS:
        return parent_name
    return "engineering"


def _parse_markdown_body(text: str) -> tuple[str, list[str], list[str]]:
    """解析 Markdown body 中的 Description / Responsibilities / Non-Goals。

    Args:
        text: 完整文件文本（含 frontmatter）。

    Returns:
        (description, responsibilities, non_goals) 三元组。
        缺失的节返回空字符串或空列表。
    """
    # 跳过 frontmatter
    lines = text.splitlines()
    body_start = 0
    if lines and lines[0].strip() == "+++":
        for idx in range(1, len(lines)):
            if lines[idx].strip() == "+++":
                body_start = idx + 1
                break

    body_lines = lines[body_start:]

    # 按 ## 标题切分 sections
    sections: dict[str, list[str]] = {}
    current_section: str | None = None

    for line in body_lines:
        stripped = line.strip()
        if stripped.startswith("## "):
            current_section = stripped[3:].strip().lower()
            sections[current_section] = []
        elif current_section is not None:
            sections[current_section].append(line)

    # 提取 description
    desc_lines = sections.get("description", [])
    description = "\n".join(desc_lines).strip()

    # 提取 responsibilities（列表项）
    responsibilities = _extract_list_items(sections.get("responsibilities", []))

    # 提取 non-goals（列表项）
    non_goals = _extract_list_items(sections.get("non-goals", []))

    return description, responsibilities, non_goals


def _extract_list_items(lines: list[str]) -> list[str]:
    """从行列表中提取以 ``- `` 开头的列表项内容。"""
    items: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("- "):
            items.append(stripped[2:].strip())
    return items


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def resolve_role(agents_dir: Path, role_id: str) -> RoleContext:
    """解析角色文件并返回结构化的 :class:`RoleContext`。

    Args:
        agents_dir: ``.agents/`` 目录路径。
        role_id: 角色标识符（不含 ``.md`` 后缀）。

    Returns:
        解析后的角色上下文。

    Raises:
        RoleNotFoundError: 角色文件不存在。
        RoleParseError: frontmatter 解析失败。
    """
    roles_dir = agents_dir / "roles"
    role_path = _find_role_file(roles_dir, role_id)

    if role_path is None:
        raise RoleNotFoundError(f"Role '{role_id}' not found in {roles_dir}")

    try:
        text = role_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise RoleNotFoundError(f"Cannot read role file '{role_path}': {exc}") from exc

    # 解析 TOML frontmatter
    frontmatter_text = _extract_frontmatter(text)
    if frontmatter_text is None:
        raise RoleParseError(
            f"Role '{role_id}' has no valid TOML frontmatter (+++...+++)"
        )

    try:
        data = tomllib.loads(frontmatter_text)
    except tomllib.TOMLDecodeError as exc:
        raise RoleParseError(
            f"Role '{role_id}' frontmatter TOML parse error: {exc}"
        ) from exc

    # 提取 frontmatter 字段
    role_id_from_file = data.get("id", role_id)
    domain = data.get("domain", "")

    bindings_data = data.get("bindings", {})
    bindings = RoleBindings(
        rules=list(bindings_data.get("rules", [])),
        references=list(bindings_data.get("references", [])),
        skills=list(bindings_data.get("skills", [])),
    )

    permissions_data = data.get("permissions", {})
    permissions = RolePermissions(
        can_modify=list(permissions_data.get("can_modify", [])),
        cannot_modify=list(permissions_data.get("cannot_modify", [])),
    )

    # 确定 layer
    layer = _determine_layer(role_path)

    # 解析 Markdown body
    description, responsibilities, non_goals = _parse_markdown_body(text)

    return RoleContext(
        id=role_id_from_file,
        domain=domain,
        layer=layer,
        bindings=bindings,
        permissions=permissions,
        non_goals=non_goals,
        description=description,
        responsibilities=responsibilities,
    )


def activate_role(agents_dir: Path, role_id: str) -> ContextBundle:
    """激活角色：解析角色文件并加载绑定的所有资源。

    Args:
        agents_dir: ``.agents/`` 目录路径。
        role_id: 角色标识符。

    Returns:
        包含角色上下文及所有已加载资源的 :class:`ContextBundle`。

    Raises:
        RoleNotFoundError: 角色文件不存在。
        RoleParseError: 角色文件解析失败。
    """
    role_ctx = resolve_role(agents_dir, role_id)

    # 加载 rules
    loaded_rules: dict[str, str] = {}
    for rule_path in role_ctx.bindings.rules:
        full_path = agents_dir / rule_path
        try:
            loaded_rules[rule_path] = full_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            loaded_rules[rule_path] = ""

    # 加载 references
    loaded_references: dict[str, str] = {}
    for ref_path in role_ctx.bindings.references:
        full_path = agents_dir / ref_path
        try:
            loaded_references[ref_path] = full_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            loaded_references[ref_path] = ""

    # 验证 skills
    active_skills: list[str] = []
    for skill_id in role_ctx.bindings.skills:
        skill_manifest = agents_dir / "skills" / skill_id / "SKILL.md"
        if skill_manifest.exists():
            active_skills.append(skill_id)

    return ContextBundle(
        role=role_ctx,
        loaded_rules=loaded_rules,
        loaded_references=loaded_references,
        active_skills=active_skills,
        routing_overrides={"role": role_id},
    )


def check_permission(
    role_ctx: RoleContext,
    file_path: str,
    action: str = "modify",
) -> PermissionResult:
    """检查角色对指定文件的操作权限（deny-first 逻辑）。

    规则评估顺序：
    1. 若 ``file_path`` 匹配 ``cannot_modify`` 中任一 glob → **DENY**
    2. 若 ``can_modify`` 非空且 ``file_path`` 不匹配任何 glob → **DENY**
    3. 否则 → **ALLOW**

    Args:
        role_ctx: 已解析的角色上下文。
        file_path: 待检查的文件路径。
        action: 操作类型（目前仅支持 ``"modify"``）。

    Returns:
        权限检查结果。
    """
    # Step 1: deny-list check
    for pattern in role_ctx.permissions.cannot_modify:
        if fnmatch(file_path, pattern):
            return PermissionResult(
                allowed=False,
                reason=f"Path matches cannot_modify pattern: {pattern!r}",
                matched_rule=pattern,
            )

    # Step 2: allow-list check (only if can_modify is non-empty)
    if role_ctx.permissions.can_modify:
        for pattern in role_ctx.permissions.can_modify:
            if fnmatch(file_path, pattern):
                return PermissionResult(
                    allowed=True,
                    reason=f"Path matches can_modify pattern: {pattern!r}",
                    matched_rule=pattern,
                )
        # No match in allow-list → deny
        return PermissionResult(
            allowed=False,
            reason="Path does not match any can_modify pattern",
            matched_rule=None,
        )

    # Step 3: no restrictions → allow
    return PermissionResult(
        allowed=True,
        reason="No permission restrictions defined for this role",
        matched_rule=None,
    )
