"""校验 docs/ 目录结构遵循 tech/general 双轨分类规范。

规则:
    R1. docs/ 顶层除 ``index.md`` 外不应直接存在 ``.md`` 业务文档
        （所有项目技术文档应位于 ``docs/tech/``，通用知识应位于 ``docs/general/``）。
    R2. ``docs/tech/index.md`` 与 ``docs/general/index.md`` 必须存在
        （作为双轨子入口，不得带 ``orphan: true``）。
    R3. ``docs/tech/`` 与 ``docs/general/`` 子目录内允许任意结构，但
        ``docs/tech/`` 不得放置 ``philosophy/``、``math/`` 等通用知识专属命名子目录；
        ``docs/general/`` 不得放置 ``api/``、``changelogs/`` 等技术专属命名子目录。

退出码:
    0 - 结构合规
    1 - 至少一项违规
    2 - 输入参数或运行时错误
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

# docs/ 顶层允许保留的非 .md 文件（Sphinx 配置、参考文献、invoke 任务等）
_ROOT_ALLOWED_FILES: frozenset[str] = frozenset(
    {"index.md", "conf.py", "_config.toml", "refs.bib", "tasks.py"}
)

# docs/ 顶层允许保留的目录（业务子树 + Sphinx 构建/资源目录）
_ROOT_ALLOWED_DIRS: frozenset[str] = frozenset(
    {"tech", "general", "_build", "_static", "_templates", "__pycache__"}
)

# 双轨子入口必须存在的路径（相对 docs/）
_REQUIRED_ENTRIES: tuple[str, ...] = ("tech/index.md", "general/index.md")

# 严禁出现在 docs/tech/ 顶层的通用知识专属命名子目录
_TECH_FORBIDDEN_SUBDIRS: frozenset[str] = frozenset(
    {"philosophy", "math", "linguistics", "history", "science"}
)

# 严禁出现在 docs/general/ 顶层的技术专属命名子目录
_GENERAL_FORBIDDEN_SUBDIRS: frozenset[str] = frozenset({"api", "changelogs"})


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


def _check_root_layer(docs_dir: Path) -> list[Violation]:
    """R1: docs/ 顶层除 index.md 外不应有 .md 业务文档。"""

    violations: list[Violation] = []
    for child in docs_dir.iterdir():
        if child.is_file() and child.suffix == ".md":
            if child.name not in _ROOT_ALLOWED_FILES:
                violations.append(
                    Violation(
                        rule_id="R1",
                        path=child,
                        reason=(
                            f"docs/ 顶层不应直接存在业务文档 {child.name!r}，"
                            "应按双轨分类迁移至 docs/tech/ 或 docs/general/"
                        ),
                    )
                )
    return violations


def _check_required_entries(docs_dir: Path) -> list[Violation]:
    """R2: 双轨子入口 docs/{tech,general}/index.md 必须存在。"""

    violations: list[Violation] = []
    for rel in _REQUIRED_ENTRIES:
        target = docs_dir / rel
        if not target.is_file():
            violations.append(
                Violation(
                    rule_id="R2",
                    path=target,
                    reason=f"必需的子入口 {rel!r} 不存在；双轨结构要求两个子入口同时存在",
                )
            )
    return violations


def _check_subdir_isolation(docs_dir: Path) -> list[Violation]:
    """R3: 双轨子目录命名隔离（防止技术与通用知识相互渗入）。"""

    violations: list[Violation] = []

    tech_dir = docs_dir / "tech"
    if tech_dir.is_dir():
        for child in tech_dir.iterdir():
            if child.is_dir() and child.name in _TECH_FORBIDDEN_SUBDIRS:
                violations.append(
                    Violation(
                        rule_id="R3",
                        path=child,
                        reason=(
                            f"docs/tech/ 不应包含通用知识命名子目录 {child.name!r}，"
                            "请迁移至 docs/general/"
                        ),
                    )
                )

    general_dir = docs_dir / "general"
    if general_dir.is_dir():
        for child in general_dir.iterdir():
            if child.is_dir() and child.name in _GENERAL_FORBIDDEN_SUBDIRS:
                violations.append(
                    Violation(
                        rule_id="R3",
                        path=child,
                        reason=(
                            f"docs/general/ 不应包含技术专属命名子目录 {child.name!r}，"
                            "请迁移至 docs/tech/"
                        ),
                    )
                )

    return violations


def check(docs_dir: Path) -> list[Violation]:
    """对 docs_dir 执行全部双轨结构规则校验。"""

    if not docs_dir.is_dir():
        raise FileNotFoundError(f"docs 目录不存在: {docs_dir}")

    violations: list[Violation] = []
    violations.extend(_check_root_layer(docs_dir))
    violations.extend(_check_required_entries(docs_dir))
    violations.extend(_check_subdir_isolation(docs_dir))
    return violations


def _format_report(violations: list[Violation], docs_dir: Path) -> str:
    """生成人类可读的违规清单。"""

    if not violations:
        return f"✅ docs/ 结构合规 (扫描根目录: {docs_dir})"

    lines = [
        f"❌ docs/ 结构校验发现 {len(violations)} 项违规 (扫描根目录: {docs_dir})",
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
        description="校验 docs/ 目录结构遵循 tech/general 双轨分类规范"
    )
    parser.add_argument(
        "--docs-dir",
        type=Path,
        default=Path("docs"),
        help="待校验的 docs 目录路径（默认: 当前目录下的 docs/）",
    )
    args = parser.parse_args(argv)

    try:
        violations = check(args.docs_dir.resolve())
    except FileNotFoundError as exc:
        print(f"[error] {exc}", file=sys.stderr)
        return 2

    print(_format_report(violations, args.docs_dir))
    return 0 if not violations else 1


if __name__ == "__main__":
    sys.exit(main())
