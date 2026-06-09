"""预编译检查所有 Python 文件的语法正确性，防止 Python 2 残留语法进入 CI。

与 ruff/pyright 互补：ruff 侧重风格与常见错误，py_compile 侧重语法正确性（如
``except X, Y:`` 这类 Python 2 语法在 ruff 当前规则下不会被捕获）。

退出码:
    0 - 所有 .py 文件语法正确
    1 - 至少一个文件存在语法错误
    2 - 运行时错误（如目录不存在）
"""

from __future__ import annotations

import argparse
import py_compile
import sys
from pathlib import Path

# 跳过的目录（虚拟环境、构建产物、缓存、临时文件）
_SKIP_DIRS: frozenset[str] = frozenset(
    {
        ".venv",
        "venv",
        ".tox",
        "__pycache__",
        ".temp",
        "node_modules",
        ".git",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        "_build",
        "htmlcov",
        "dist",
        "build",
        "*.egg-info",
    }
)

# 跳过的目录前缀（如 old/ 归档代码）
_SKIP_PREFIXES: tuple[str, ...] = ("old/",)


def collect_py_files(root: Path) -> list[Path]:
    """递归收集 root 下所有 .py 文件，跳过排除目录。"""
    py_files: list[Path] = []
    for entry in root.rglob("*.py"):
        # 检查路径中是否有应跳过的目录
        skip = False
        for part in entry.parts:
            if part in _SKIP_DIRS or part.endswith(".egg-info"):
                skip = True
                break
        if skip:
            continue

        # 检查是否匹配跳过前缀
        rel = entry.relative_to(root)
        for prefix in _SKIP_PREFIXES:
            if str(rel).startswith(prefix):
                skip = True
                break
        if skip:
            continue

        py_files.append(entry)
    return sorted(py_files)


def compile_file(filepath: Path) -> tuple[Path, str | None]:
    """编译单个文件，返回 (路径, 错误信息或 None)。"""
    try:
        py_compile.compile(str(filepath), doraise=True)
        return filepath, None
    except py_compile.PyCompileError as exc:
        return filepath, str(exc)


def check(project_root: Path) -> tuple[list[Path], list[tuple[Path, str]]]:
    """扫描并编译所有 .py 文件，返回 (通过列表, 失败列表)。"""
    if not project_root.is_dir():
        raise FileNotFoundError(f"项目根目录不存在: {project_root}")

    py_files = collect_py_files(project_root)
    passed: list[Path] = []
    failed: list[tuple[Path, str]] = []

    for filepath in py_files:
        _, error = compile_file(filepath)
        if error is None:
            passed.append(filepath)
        else:
            failed.append((filepath, error))

    return passed, failed


def format_report(passed: list[Path], failed: list[tuple[Path, str]]) -> str:
    """生成人类可读的检查报告。"""
    total = len(passed) + len(failed)
    lines = [
        f"Python 语法编译检查完成：{len(passed)}/{total} 通过",
    ]

    if failed:
        lines.append(f"\n❌ {len(failed)} 个文件存在语法错误：")
        for filepath, error in failed:
            lines.append(f"\n  📄 {filepath}")
            # 提取关键行（SyntaxError 行）
            for line in error.splitlines():
                stripped = line.strip()
                if stripped:
                    lines.append(f"     {stripped}")
    else:
        lines.append("✅ 所有 Python 文件语法正确。")

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    """命令行入口。"""
    parser = argparse.ArgumentParser(
        description="预编译检查所有 Python 文件的语法正确性"
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="项目根目录（默认: 脚本所在项目的根目录）",
    )
    parser.add_argument(
        "--files",
        type=str,
        default=None,
        help="仅检查指定文件/目录（逗号分隔路径，用于 CI 选择性检查）",
    )
    args = parser.parse_args(argv)

    if args.root is None:
        # 默认：脚本位于 apps/chaos/.agents/scripts/，项目根为 ../..
        args.root = Path(__file__).resolve().parents[2]

    try:
        passed, failed = check(args.root)
    except FileNotFoundError as exc:
        print(f"[error] {exc}", file=sys.stderr)
        return 2

    print(format_report(passed, failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
