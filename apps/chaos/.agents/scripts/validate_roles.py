"""校验 .agents/roles/*.md 的 TOML frontmatter 结构一致性。

校验项:
    1. ``id`` 必须存在，且与文件名（去 ``.md`` 后缀）一致。
    2. ``id`` 必须符合 kebab-case 正则 ``^[a-z][a-z0-9]*(-[a-z0-9]+)*$``。
    3. ``domain`` 必须存在且为非空字符串。
    4. ``bindings.rules``/``bindings.references`` 中每个路径在 ``.agents/`` 下
       必须存在。
    5. frontmatter 顶层字段仅允许 ``id``/``domain``/``bindings``/``permissions``，
       出现未知字段视为 ERROR。
    6. ``bindings`` 仅允许 ``rules``/``references``/``skills`` 子键；
       ``permissions`` 仅允许 ``can_modify``/``cannot_modify`` 子键。

输出格式:
    每个问题一行，前缀为 ``ERROR:`` 或 ``WARNING:``；
    最后输出已校验的 Role 清单，例如
    ``Validated 10 roles: backend-dev, devops, ...``；
    无任何 ERROR/WARNING 时输出
    ``All N role definitions validated successfully.``。

退出码:
    0 - 无 ERROR（仅 WARNING 或完全通过）
    1 - 至少一项 ERROR
"""

from __future__ import annotations

import json  # noqa: F401  # 预留：未来如需读取 schema 元数据。
import re
import sys
import tomllib
from pathlib import Path
from typing import Any

# 与 role.schema.json 中 ``id.pattern`` 保持一致。
_ID_PATTERN = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")

# 顶层允许的字段集合，对照 role.schema.json 的 properties。
_ALLOWED_TOP_LEVEL: frozenset[str] = frozenset(
    {"id", "domain", "bindings", "permissions"}
)

# bindings 子键白名单。
_ALLOWED_BINDINGS_KEYS: frozenset[str] = frozenset(
    {"rules", "references", "skills"}
)

# permissions 子键白名单。
_ALLOWED_PERMISSIONS_KEYS: frozenset[str] = frozenset(
    {"can_modify", "cannot_modify"}
)

# frontmatter 分隔符。
_FRONTMATTER_DELIM = "+++"


def _ensure_utf8_stdout() -> None:
    """在 Windows GBK 终端下强制 stdout/stderr 使用 utf-8。"""

    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(encoding="utf-8")
            except (OSError, ValueError):
                pass


def _extract_frontmatter(text: str) -> tuple[str | None, str | None]:
    """从 Markdown 文本中提取 ``+++`` 分隔的 TOML frontmatter。

    返回 ``(toml_text, error_msg)``：成功时 ``error_msg`` 为 None；
    失败时 ``toml_text`` 为 None 并附带错误描述。
    """

    lines = text.splitlines()
    # 跳过文件首部可能存在的 BOM 或空白行。
    idx = 0
    while idx < len(lines) and lines[idx].strip() == "":
        idx += 1

    if idx >= len(lines) or lines[idx].strip() != _FRONTMATTER_DELIM:
        return None, "missing opening '+++' delimiter"

    start = idx + 1
    end = None
    for i in range(start, len(lines)):
        if lines[i].strip() == _FRONTMATTER_DELIM:
            end = i
            break

    if end is None:
        return None, "missing closing '+++' delimiter"

    return "\n".join(lines[start:end]), None


def _check_path_list(
    role_id: str,
    field_name: str,
    values: list[Any],
    agents_root: Path,
) -> list[str]:
    """校验 ``bindings.rules`` / ``bindings.references`` 中的路径存在性。"""

    errors: list[str] = []
    agents_root_resolved = agents_root.resolve()
    for item in values:
        if not isinstance(item, str):
            errors.append(
                f"ERROR: role '{role_id}' {field_name} contains non-string: "
                f"{item!r}"
            )
            continue
        target_path = (agents_root / item).resolve()
        try:
            target_path.relative_to(agents_root_resolved)
        except ValueError:
            errors.append(
                f"ERROR: role '{role_id}' {field_name} path '{item}' escapes "
                ".agents/ root"
            )
            continue
        if not target_path.exists():
            errors.append(
                f"ERROR: role '{role_id}' {field_name} path not found: {item}"
            )
    return errors


def _validate_role_file(
    md_path: Path,
    agents_root: Path,
) -> tuple[str | None, list[str], list[str]]:
    """校验单个 Role 文件，返回 ``(role_id, errors, warnings)``。

    ``role_id`` 为 frontmatter 中解析出的 id（解析失败时回退为文件名 stem，
    便于在汇总清单中标识失败条目）。
    """

    file_stem = md_path.stem
    errors: list[str] = []
    warnings: list[str] = []

    try:
        text = md_path.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"ERROR: cannot read role file '{md_path.name}': {exc}")
        return file_stem, errors, warnings

    toml_text, fm_err = _extract_frontmatter(text)
    if toml_text is None:
        errors.append(
            f"ERROR: role file '{md_path.name}' frontmatter invalid: {fm_err}"
        )
        return file_stem, errors, warnings

    try:
        data = tomllib.loads(toml_text)
    except tomllib.TOMLDecodeError as exc:
        errors.append(
            f"ERROR: role file '{md_path.name}' TOML parse error: {exc}"
        )
        return file_stem, errors, warnings

    if not isinstance(data, dict):
        errors.append(
            f"ERROR: role file '{md_path.name}' frontmatter is not a table"
        )
        return file_stem, errors, warnings

    # 未知顶层字段。
    unknown = sorted(set(data.keys()) - _ALLOWED_TOP_LEVEL)
    if unknown:
        errors.append(
            f"ERROR: role file '{md_path.name}' has unknown top-level "
            f"field(s): {unknown}"
        )

    # id 校验。
    role_id_raw = data.get("id")
    role_id: str
    if not isinstance(role_id_raw, str) or not role_id_raw:
        errors.append(
            f"ERROR: role file '{md_path.name}' missing required string 'id'"
        )
        role_id = file_stem
    else:
        role_id = role_id_raw
        if not _ID_PATTERN.match(role_id):
            errors.append(
                f"ERROR: role '{role_id}' id does not match kebab-case "
                f"pattern '{_ID_PATTERN.pattern}'"
            )
        if role_id != file_stem:
            errors.append(
                f"ERROR: role file '{md_path.name}' id '{role_id}' does not "
                f"match filename stem '{file_stem}'"
            )

    # domain 校验。
    domain = data.get("domain")
    if not isinstance(domain, str) or not domain.strip():
        errors.append(
            f"ERROR: role '{role_id}' missing required non-empty string "
            "'domain'"
        )

    # bindings 校验。
    if "bindings" in data:
        bindings = data["bindings"]
        if not isinstance(bindings, dict):
            errors.append(
                f"ERROR: role '{role_id}' bindings must be a table, got "
                f"{type(bindings).__name__}"
            )
        else:
            unknown_b = sorted(set(bindings.keys()) - _ALLOWED_BINDINGS_KEYS)
            if unknown_b:
                errors.append(
                    f"ERROR: role '{role_id}' bindings has unknown key(s): "
                    f"{unknown_b}"
                )

            for field in ("rules", "references"):
                if field not in bindings:
                    continue
                value = bindings[field]
                if not isinstance(value, list):
                    errors.append(
                        f"ERROR: role '{role_id}' bindings.{field} must be a "
                        f"list, got {type(value).__name__}"
                    )
                    continue
                errors.extend(
                    _check_path_list(role_id, f"bindings.{field}", value, agents_root)
                )

            if "skills" in bindings and not isinstance(bindings["skills"], list):
                errors.append(
                    f"ERROR: role '{role_id}' bindings.skills must be a list, "
                    f"got {type(bindings['skills']).__name__}"
                )

    # permissions 校验（仅做结构层面的简版校验）。
    if "permissions" in data:
        permissions = data["permissions"]
        if not isinstance(permissions, dict):
            errors.append(
                f"ERROR: role '{role_id}' permissions must be a table, got "
                f"{type(permissions).__name__}"
            )
        else:
            unknown_p = sorted(
                set(permissions.keys()) - _ALLOWED_PERMISSIONS_KEYS
            )
            if unknown_p:
                errors.append(
                    f"ERROR: role '{role_id}' permissions has unknown key(s): "
                    f"{unknown_p}"
                )
            for field in ("can_modify", "cannot_modify"):
                if field in permissions and not isinstance(
                    permissions[field], list
                ):
                    errors.append(
                        f"ERROR: role '{role_id}' permissions.{field} must "
                        f"be a list, got {type(permissions[field]).__name__}"
                    )

    return role_id, errors, warnings


def validate(agents_root: Path) -> tuple[list[str], list[str], list[str]]:
    """执行全部校验，返回 ``(errors, warnings, validated_role_ids)``。"""

    roles_dir = agents_root / "roles"
    if not roles_dir.is_dir():
        return ([f"ERROR: roles directory not found at {roles_dir}"], [], [])

    md_files = sorted(
        p for p in roles_dir.glob("*.md")
        if p.is_file() and p.name != "README.md"
    )

    errors: list[str] = []
    warnings: list[str] = []
    role_ids: list[str] = []

    for md_path in md_files:
        role_id, f_errors, f_warnings = _validate_role_file(md_path, agents_root)
        errors.extend(f_errors)
        warnings.extend(f_warnings)
        role_ids.append(role_id)

    return errors, warnings, role_ids


def main(argv: list[str] | None = None) -> int:
    """命令行入口。返回退出码 0/1。"""

    _ensure_utf8_stdout()

    # 脚本位于 .agents/scripts/validate_roles.py，向上一级即 .agents/ 根。
    agents_root = Path(__file__).resolve().parent.parent

    errors, warnings, role_ids = validate(agents_root)

    for msg in errors:
        print(msg)
    for msg in warnings:
        print(msg)

    count = len(role_ids)
    if not errors and not warnings:
        print(f"All {count} role definitions validated successfully.")
    else:
        listed = ", ".join(role_ids) if role_ids else "(none)"
        print(f"Validated {count} roles: {listed}")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
