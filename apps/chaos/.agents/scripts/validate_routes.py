"""校验 .agents/world.toml 中 [routing] 区块的内部一致性。

校验项:
    1. ``targets`` 路径必须存在于 ``.agents/`` 目录下。
    2. ``roles`` 引用必须在 ``.agents/roles/`` 中存在对应文件；
       ``*`` 视为通配符跳过；角色 id 从 Role 文件的 TOML frontmatter 中提取。
    3. ``id`` 在所有 ``[[routing.rules]]`` 中必须唯一。
    4. ``priority`` 必须为 0-10 之间的整数。
    5. ``triggers.phases`` 中的值必须出现在 ``routing.phases.supported`` 枚举中。

输出格式:
    每个问题一行，前缀为 ``ERROR:`` 或 ``WARNING:``；
    无任何 ERROR/WARNING 时输出 ``All routing rules validated successfully.``。

退出码:
    0 - 无 ERROR（仅 WARNING 或完全通过）
    1 - 至少一项 ERROR
"""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path
from typing import Any


def _ensure_utf8_stdout() -> None:
    """在 Windows GBK 终端下强制 stdout/stderr 使用 utf-8。"""

    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(encoding="utf-8")
            except OSError, ValueError:
                pass


def _load_world(world_toml: Path) -> dict[str, Any]:
    """读取并解析 world.toml。"""

    with world_toml.open("rb") as fp:
        return tomllib.load(fp)


def _parse_frontmatter(filepath: Path) -> dict[str, Any] | None:
    """解析 +++ 分隔的 TOML frontmatter。返回解析后的 dict 或 None。"""

    try:
        text = filepath.read_text(encoding="utf-8")
    except OSError, UnicodeDecodeError:
        return None
    if not text.startswith("+++"):
        return None
    end = text.find("+++", 3)
    if end == -1:
        return None
    toml_text = text[3:end].strip()
    try:
        return tomllib.loads(toml_text)
    except Exception:
        return None


def _existing_role_ids(roles_dir: Path) -> frozenset[str]:
    """从 roles/ 下 Role 文件的 TOML frontmatter 中提取已定义的角色 id。"""

    if not roles_dir.is_dir():
        return frozenset()
    ids: set[str] = set()
    for p in roles_dir.glob("*.md"):
        if not p.is_file() or p.name == "README.md":
            continue
        frontmatter = _parse_frontmatter(p)
        if frontmatter and "id" in frontmatter:
            ids.add(frontmatter["id"])
        else:
            # fallback to filename stem if no frontmatter
            ids.add(p.stem)
    return frozenset(ids)


def _check_targets(
    rule_id: str,
    targets: list[Any],
    agents_root: Path,
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    for target in targets:
        if not isinstance(target, str):
            errors.append(f"ERROR: rule '{rule_id}' has non-string target: {target!r}")
            continue
        target_path = (agents_root / target).resolve()
        try:
            target_path.relative_to(agents_root.resolve())
        except ValueError:
            errors.append(
                f"ERROR: rule '{rule_id}' target '{target}' escapes .agents/ root"
            )
            continue
        if not target_path.exists():
            errors.append(f"ERROR: rule '{rule_id}' target path not found: {target}")
    return errors, warnings


def _check_roles(
    rule_id: str,
    roles: list[Any],
    existing_roles: frozenset[str],
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    for role in roles:
        if not isinstance(role, str):
            errors.append(f"ERROR: rule '{rule_id}' has non-string role: {role!r}")
            continue
        if role == "*":
            continue
        if role in existing_roles:
            continue
        errors.append(
            f"ERROR: rule '{rule_id}' references unknown role '{role}' "
            f"(no roles/*.md with id='{role}')"
        )
    return errors, warnings


def _check_priority(rule_id: str, priority: Any) -> list[str]:
    if not isinstance(priority, int) or isinstance(priority, bool):
        return [
            f"ERROR: rule '{rule_id}' priority must be an integer, got "
            f"{type(priority).__name__}: {priority!r}"
        ]
    if not 0 <= priority <= 10:
        return [f"ERROR: rule '{rule_id}' priority {priority} out of range [0, 10]"]
    return []


def _check_phases(
    rule_id: str,
    phases: list[Any],
    supported: frozenset[str],
) -> list[str]:
    errors: list[str] = []
    for phase in phases:
        if not isinstance(phase, str):
            errors.append(
                f"ERROR: rule '{rule_id}' triggers.phases contains non-string: "
                f"{phase!r}"
            )
            continue
        if phase not in supported:
            errors.append(
                f"ERROR: rule '{rule_id}' triggers.phases value '{phase}' is not "
                f"in routing.phases.supported {sorted(supported)}"
            )
    return errors


def validate(agents_root: Path) -> tuple[list[str], list[str]]:
    """执行全部校验，返回 (errors, warnings) 两个消息列表。"""

    world_toml = agents_root / "world.toml"
    if not world_toml.is_file():
        return ([f"ERROR: world.toml not found at {world_toml}"], [])

    data = _load_world(world_toml)

    routing = data.get("routing")
    if not isinstance(routing, dict):
        return (["ERROR: [routing] section is missing or invalid"], [])

    phases_block = routing.get("phases", {})
    supported_raw = (
        phases_block.get("supported", []) if isinstance(phases_block, dict) else []
    )
    supported_phases: frozenset[str] = frozenset(
        p for p in supported_raw if isinstance(p, str)
    )

    rules = routing.get("rules", [])
    if not isinstance(rules, list):
        return (["ERROR: routing.rules must be an array of tables"], [])

    existing_roles = _existing_role_ids(agents_root / "roles")

    errors: list[str] = []
    warnings: list[str] = []
    seen_ids: dict[str, int] = {}

    for index, rule in enumerate(rules):
        if not isinstance(rule, dict):
            errors.append(f"ERROR: routing.rules[{index}] is not a table: {rule!r}")
            continue

        rule_id = rule.get("id")
        if not isinstance(rule_id, str) or not rule_id:
            errors.append(f"ERROR: routing.rules[{index}] missing required string 'id'")
            rule_id = f"<index {index}>"
        else:
            if rule_id in seen_ids:
                errors.append(
                    f"ERROR: duplicate rule id '{rule_id}' "
                    f"(first seen at index {seen_ids[rule_id]}, again at {index})"
                )
            else:
                seen_ids[rule_id] = index

        targets = rule.get("targets", [])
        if isinstance(targets, list):
            t_err, t_warn = _check_targets(rule_id, targets, agents_root)
            errors.extend(t_err)
            warnings.extend(t_warn)
        else:
            errors.append(
                f"ERROR: rule '{rule_id}' targets must be a list, got "
                f"{type(targets).__name__}"
            )

        roles = rule.get("roles", [])
        if isinstance(roles, list):
            r_err, r_warn = _check_roles(rule_id, roles, existing_roles)
            errors.extend(r_err)
            warnings.extend(r_warn)
        else:
            errors.append(
                f"ERROR: rule '{rule_id}' roles must be a list, got "
                f"{type(roles).__name__}"
            )

        if "priority" in rule:
            errors.extend(_check_priority(rule_id, rule["priority"]))
        else:
            errors.append(f"ERROR: rule '{rule_id}' missing required 'priority'")

        triggers = rule.get("triggers", {})
        if isinstance(triggers, dict):
            phases = triggers.get("phases", [])
            if isinstance(phases, list):
                errors.extend(_check_phases(rule_id, phases, supported_phases))
            else:
                errors.append(
                    f"ERROR: rule '{rule_id}' triggers.phases must be a list, "
                    f"got {type(phases).__name__}"
                )
        elif "triggers" in rule:
            errors.append(
                f"ERROR: rule '{rule_id}' triggers must be a table, got "
                f"{type(triggers).__name__}"
            )

    return errors, warnings


def main(argv: list[str] | None = None) -> int:
    """命令行入口。返回退出码 0/1。"""

    _ensure_utf8_stdout()

    # 脚本位于 .agents/scripts/validate_routes.py，向上一级即 .agents/ 根。
    agents_root = Path(__file__).resolve().parent.parent

    errors, warnings = validate(agents_root)

    for msg in errors:
        print(msg)
    for msg in warnings:
        print(msg)

    if not errors and not warnings:
        print("All routing rules validated successfully.")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
