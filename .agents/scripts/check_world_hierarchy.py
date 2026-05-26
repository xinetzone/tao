"""校验多世界层级结构遵循 world-hierarchy 规范。

规则:
    R1. 子世界 AGENTS.md 必须包含继承关系声明（引用父 AGENTS.md）
    R2. 子世界 AGENTS.md 必须包含「规则增量说明」或「覆盖说明」节
    R3. 子目录 .agents/ 中禁止存在独立的 world.toml
    R4. 从根目录到最深子世界的 AGENTS.md 嵌套层数 ≤ 3
    R5. 子世界 .agents/rules/ 中禁止存在与 world.toml immutable_rules 同名的文件

退出码:
    0 - 结构合规
    1 - 至少一项违规
    2 - 输入参数或运行时错误
"""

from __future__ import annotations

import argparse
import re
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

# 最大允许嵌套深度（根世界为第 1 层）
_MAX_DEPTH = 3

# 继承声明关键词（匹配子世界 AGENTS.md 中对父世界的引用）
_INHERIT_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"继承", re.IGNORECASE),
    re.compile(r"父.*AGENTS\.md", re.IGNORECASE),
    re.compile(r"\.\./AGENTS\.md", re.IGNORECASE),
)

# 规则增量/覆盖说明节标题模式（兼容编号，如 "## 2. 规则增量说明"）
_RULE_SECTION_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"^#+\s*\d*\.?\s*规则增量说明", re.MULTILINE),
    re.compile(r"^#+\s*\d*\.?\s*覆盖说明", re.MULTILINE),
)


@dataclass(frozen=True)
class Violation:
    """一条结构违规记录。"""

    rule_id: str
    path: Path
    reason: str


def _ensure_utf8_stdout() -> None:
    """在 Windows GBK 终端下强制 stdout 使用 utf-8，避免管道编码异常。"""

    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except (AttributeError, ValueError):
        pass


def _find_sub_agents_md(root_dir: Path) -> list[Path]:
    """从根目录递归发现所有非根 AGENTS.md（子世界）。"""

    root_agents = root_dir / "AGENTS.md"
    results: list[Path] = []

    for p in root_dir.rglob("AGENTS.md"):
        # 排除根目录自身、.venv、node_modules、.git 等无关目录
        if p == root_agents:
            continue
        parts = p.relative_to(root_dir).parts
        if any(part.startswith(".") and part not in (".agents",) for part in parts):
            continue
        if "node_modules" in parts or ".venv" in parts or "__pycache__" in parts:
            continue
        results.append(p)

    return sorted(results)


def _compute_depth(sub_agents: Path, root_dir: Path) -> int:
    """计算子世界 AGENTS.md 的嵌套深度（根 = 1，一级子目录 = 2，以此类推）。"""

    rel = sub_agents.relative_to(root_dir)
    # AGENTS.md 所在目录的层级数 + 1（根世界算第 1 层）
    return len(rel.parts)  # rel.parts 最后一项是 AGENTS.md，前面是目录层级


def _read_immutable_rules(world_toml_path: Path) -> list[str]:
    """从 world.toml 的 [kernel] 中读取 immutable_rules 列表。"""

    if not world_toml_path.is_file():
        return []

    try:
        with open(world_toml_path, "rb") as f:
            data = tomllib.load(f)
        kernel = data.get("kernel", {})
        rules = kernel.get("immutable_rules", [])
        return rules if isinstance(rules, list) else []
    except (tomllib.TOMLDecodeError, OSError):
        return []


def _check_inheritance_declaration(sub_agents: Path) -> list[Violation]:
    """R1: 子世界 AGENTS.md 必须包含继承关系声明。"""

    try:
        content = sub_agents.read_text(encoding="utf-8")
    except OSError:
        return [
            Violation(
                rule_id="R1",
                path=sub_agents,
                reason="无法读取 AGENTS.md 文件内容",
            )
        ]

    if not any(pat.search(content) for pat in _INHERIT_PATTERNS):
        return [
            Violation(
                rule_id="R1",
                path=sub_agents,
                reason=(
                    "子世界 AGENTS.md 缺少继承关系声明；"
                    "应包含对父 AGENTS.md 的引用（如「继承」关键词或 ../AGENTS.md 链接）"
                ),
            )
        ]

    return []


def _check_rule_section(sub_agents: Path) -> list[Violation]:
    """R2: 子世界 AGENTS.md 必须包含「规则增量说明」或「覆盖说明」节。"""

    try:
        content = sub_agents.read_text(encoding="utf-8")
    except OSError:
        return [
            Violation(
                rule_id="R2",
                path=sub_agents,
                reason="无法读取 AGENTS.md 文件内容",
            )
        ]

    if not any(pat.search(content) for pat in _RULE_SECTION_PATTERNS):
        return [
            Violation(
                rule_id="R2",
                path=sub_agents,
                reason=(
                    "子世界 AGENTS.md 缺少「规则增量说明」或「覆盖说明」节；"
                    "应显式声明增量/覆盖的规则"
                ),
            )
        ]

    return []


def _check_sub_world_toml(sub_agents: Path) -> list[Violation]:
    """R3: 子目录 .agents/ 中禁止存在独立的 world.toml。"""

    sub_dir = sub_agents.parent
    sub_world_toml = sub_dir / ".agents" / "world.toml"

    if sub_world_toml.is_file():
        return [
            Violation(
                rule_id="R3",
                path=sub_world_toml,
                reason=(
                    "子目录 .agents/ 中存在独立的 world.toml；"
                    "一个 monorepo 仅允许一份 world.toml（位于根 .agents/）"
                ),
            )
        ]

    return []


def _check_nesting_depth(sub_agents: Path, root_dir: Path) -> list[Violation]:
    """R4: 从根目录到最深子世界的 AGENTS.md 嵌套层数 ≤ 3。"""

    depth = _compute_depth(sub_agents, root_dir)

    if depth > _MAX_DEPTH:
        return [
            Violation(
                rule_id="R4",
                path=sub_agents,
                reason=(
                    f"子世界嵌套深度为 {depth}，超过最大允许深度 {_MAX_DEPTH}；"
                    "推荐世界层级 ≤ 3 层"
                ),
            )
        ]

    return []


def _check_kernel_override(
    sub_agents: Path, immutable_rules: list[str]
) -> list[Violation]:
    """R5: 子世界 .agents/rules/ 中禁止存在与 immutable_rules 同名的文件。"""

    if not immutable_rules:
        return []

    sub_dir = sub_agents.parent
    rules_dir = sub_dir / ".agents" / "rules"

    if not rules_dir.is_dir():
        return []

    violations: list[Violation] = []
    for rule_file in rules_dir.iterdir():
        if not rule_file.is_file():
            continue
        stem = rule_file.stem
        if stem in immutable_rules:
            violations.append(
                Violation(
                    rule_id="R5",
                    path=rule_file,
                    reason=(
                        f"子世界规则文件 {rule_file.name!r} 与 Kernel 不可覆盖规则 "
                        f"{stem!r} 同名；子世界禁止覆盖 Kernel 法则，只允许 Fragment 扩展"
                    ),
                )
            )

    return violations


def check(root_dir: Path) -> list[Violation]:
    """对 root_dir 执行全部世界层级结构规则校验。"""

    if not root_dir.is_dir():
        raise FileNotFoundError(f"项目根目录不存在: {root_dir}")

    root_agents = root_dir / "AGENTS.md"
    if not root_agents.is_file():
        raise FileNotFoundError(f"根 AGENTS.md 不存在: {root_agents}")

    # 解析 immutable_rules
    root_world_toml = root_dir / ".agents" / "world.toml"
    immutable_rules = _read_immutable_rules(root_world_toml)

    # 发现所有子世界
    sub_worlds = _find_sub_agents_md(root_dir)

    violations: list[Violation] = []

    for sub_agents in sub_worlds:
        violations.extend(_check_inheritance_declaration(sub_agents))
        violations.extend(_check_rule_section(sub_agents))
        violations.extend(_check_sub_world_toml(sub_agents))
        violations.extend(_check_nesting_depth(sub_agents, root_dir))
        violations.extend(_check_kernel_override(sub_agents, immutable_rules))

    return violations


def _format_report(violations: list[Violation], root_dir: Path) -> str:
    """生成人类可读的违规清单。"""

    if not violations:
        return f"✅ World hierarchy check passed (扫描根目录: {root_dir})"

    lines = [
        f"❌ World hierarchy check 发现 {len(violations)} 项违规 (扫描根目录: {root_dir})",
        "",
    ]
    for v in violations:
        lines.append(f"  [{v.rule_id}] {v.path}")
        lines.append(f"        {v.reason}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    """命令行入口。返回退出码 0/1/2。"""

    _ensure_utf8_stdout()

    parser = argparse.ArgumentParser(
        description="校验多世界层级结构遵循 world-hierarchy 规范"
    )
    parser.add_argument(
        "--root-dir",
        type=Path,
        default=Path("."),
        help="项目根目录路径（默认: 当前目录）",
    )
    args = parser.parse_args(argv)

    try:
        violations = check(args.root_dir.resolve())
    except FileNotFoundError as exc:
        print(f"[error] {exc}", file=sys.stderr)
        return 2

    print(_format_report(violations, args.root_dir))
    return 0 if not violations else 1


if __name__ == "__main__":
    sys.exit(main())
