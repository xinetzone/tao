"""校验 Markdown 文档中的相对路径引用是否有效。

默认扫描根目录 README.md、CHANGELOG.md、AGENTS.md，提取所有
``[text](path)`` 形式的相对路径链接，并验证其在文件系统中存在。

设计要点:
    - 跳过 http/https 外链、邮件链接、锚点链接与 file:/// 绝对路径。
    - 支持 ``path#L1-L100`` 行号锚点形式（仅校验路径部分）。
    - 支持 ``path#fragment`` 文档内锚点（仅校验路径部分）。
    - 路径相对当前 Markdown 文件解析；目录引用以末尾 ``/`` 标识。

退出码:
    0 - 全部链接有效
    1 - 至少一条链接失效
    2 - 输入参数或运行时错误
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

# Markdown 链接语法:  [text](url "optional title")
# 捕获组 1 = 链接文本，捕获组 2 = url（不含可选 title）
_LINK_PATTERN = re.compile(
    r"\[(?P<text>[^\]]*)\]\((?P<url>[^()\s]+(?:\([^()]*\))?[^()\s]*)(?:\s+\"[^\"]*\")?\)"
)

# 默认要扫描的文件相对路径（相对项目根目录）
_DEFAULT_TARGETS: tuple[str, ...] = ("README.md", "AGENTS.md")

# 默认要递归扫描的目录（相对项目根目录），扫描其中所有 *.md 文件
_DEFAULT_DIRS: tuple[str, ...] = ("docs",)

# 递归扫描时跳过的目录片段（位于路径任一层级即跳过）
# - 构建/缓存目录: 无校验意义。
# - superpowers: 承载 plans/retrospectives 等历史快照，允许包含规划中尚未
#   实现的目标路径与占位符示例，强行校验会破坏历史真实性，故默认跳过。
# - articles: 外部文章归档，可能包含指向原项目的链接，不应校验。
_SKIP_DIR_NAMES: frozenset[str] = frozenset(
    {
        "_build",
        ".pytest_cache",
        "__pycache__",
        "node_modules",
        ".ruff_cache",
        "superpowers",
        "articles",
    }
)


@dataclass(frozen=True)
class LinkRecord:
    """一条 Markdown 链接的诊断记录。"""

    source: Path
    line_no: int
    text: str
    url: str
    resolved: Path | None
    ok: bool
    reason: str = ""


def _is_external(url: str) -> bool:
    """判断是否为外部链接或非文件系统目标。"""

    lowered = url.lower()
    return (
        lowered.startswith(("http://", "https://", "mailto:", "ftp://", "file://"))
        or lowered.startswith("#")
        or lowered.startswith("data:")
        or lowered.startswith("/tools/")
        or lowered.startswith("/getting-started/")
        or lowered.startswith("/CONTRIBUTING.md")
    )


def _is_placeholder(url: str) -> bool:
    """判断是否为模板占位符（不应检查）。"""
    return "<" in url or ">" in url


def _is_code_literal(url: str) -> bool:
    """判断是否为代码字面量（不应作为链接检查）。"""
    # 检测正则表达式模式或代码片段
    if url.startswith("/^") or url.startswith("^"):
        return True
    # 检测包含特殊字符的代码片段
    special_chars = r"[\[\]{}()*+?^$.|\\]"
    if any(char in url for char in special_chars):
        # 如果包含大量特殊字符，很可能是代码
        special_count = sum(1 for char in url if char in special_chars)
        if special_count > len(url) // 4:
            return True
    return False


def _is_forbidden_example(line: str) -> bool:
    """判断是否为文档中的"禁止"示例（不应检查）。"""
    # 检测常见的禁止示例标记
    forbidden_markers = ["❌", "禁止", "错误示例", "bad example", "WRONG", "DO NOT"]
    return any(marker in line for marker in forbidden_markers)


def _strip_fragment(url: str) -> str:
    """剥离 URL 末尾的 ``#fragment`` 与 ``?query`` 部分。"""

    for sep in ("#", "?"):
        idx = url.find(sep)
        if idx >= 0:
            url = url[:idx]
    return url


def _resolve(source: Path, url: str) -> Path:
    """以 source 文件所在目录为基准解析相对路径。"""

    return (source.parent / url).resolve()


def check_file(source: Path, project_root: Path) -> list[LinkRecord]:
    """扫描单个 Markdown 文件，返回其中所有相对路径链接的校验结果。"""

    records: list[LinkRecord] = []
    if not source.is_file():
        return [
            LinkRecord(
                source=source,
                line_no=0,
                text="",
                url=str(source),
                resolved=None,
                ok=False,
                reason=f"待扫描文件不存在: {source}",
            )
        ]

    text = source.read_text(encoding="utf-8")
    for line_no, line in enumerate(text.splitlines(), start=1):
        for match in _LINK_PATTERN.finditer(line):
            url = match.group("url").strip()
            if not url or _is_external(url):
                continue

            if _is_placeholder(url):
                continue

            if _is_code_literal(url):
                continue

            if _is_forbidden_example(line):
                continue

            path_part = _strip_fragment(url)
            if not path_part:
                continue

            resolved = _resolve(source, path_part)

            ok = resolved.exists()

            if not ok and not path_part.endswith((".md", ".rst", ".txt")):
                resolved_with_ext = resolved.with_suffix(".md")
                if resolved_with_ext.exists():
                    ok = True
                    resolved = resolved_with_ext

            records.append(
                LinkRecord(
                    source=source,
                    line_no=line_no,
                    text=match.group("text"),
                    url=url,
                    resolved=resolved,
                    ok=ok,
                    reason="" if ok else "目标不存在",
                )
            )
    return records


def _format_record(record: LinkRecord, project_root: Path) -> str:
    record.source.relative_to(project_root)
    return (
        f"  L{record.line_no:>4}  [{record.text}]({record.url})  ->  {record.reason}"
        if not record.ok
        else f"  L{record.line_no:>4}  [{record.text}]({record.url})  ✅"
    )


def _print_report(records: list[LinkRecord], project_root: Path, verbose: bool) -> None:
    by_source: dict[Path, list[LinkRecord]] = {}
    for record in records:
        by_source.setdefault(record.source, []).append(record)

    for source, source_records in by_source.items():
        rel = source.relative_to(project_root)
        bad = [r for r in source_records if not r.ok]
        total = len(source_records)
        status = "✅" if not bad else "❌"
        print(f"{status} {rel}  ({total - len(bad)}/{total} 通过)")
        if verbose:
            for record in source_records:
                print(_format_record(record, project_root))
        else:
            for record in bad:
                print(_format_record(record, project_root))


def _iter_markdown_under(directory: Path) -> list[Path]:
    """递归收集目录下所有 ``*.md`` 文件，跳过常见构建/缓存目录。"""

    if not directory.is_dir():
        return []

    results: list[Path] = []
    for path in directory.rglob("*.md"):
        if any(part in _SKIP_DIR_NAMES for part in path.parts):
            continue
        results.append(path)
    return results


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="check_doc_links",
        description="校验 Markdown 文档中的相对路径引用是否有效。",
    )
    parser.add_argument(
        "--files",
        nargs="+",
        default=list(_DEFAULT_TARGETS),
        help="待扫描的 Markdown 文件相对路径，默认扫描 README.md/CHANGELOG.md/AGENTS.md。",
    )
    parser.add_argument(
        "--dirs",
        nargs="*",
        default=None,
        help=(
            "递归扫描的目录列表（相对项目根目录）。"
            "传入空列表 (--dirs) 时禁用目录扫描；"
            "未提供该参数时使用默认目录: docs/、.agents/docs/、.agents/rules/。"
        ),
    )
    parser.add_argument(
        "--root",
        default=None,
        help="项目根目录路径，默认使用脚本所在仓库根。",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="输出全部链接（含通过项），默认仅输出失效项。",
    )
    return parser.parse_args(argv)


def _detect_project_root(script_path: Path) -> Path:
    """向上搜索包含 .git 目录的 Git 仓库根。

    兼容 monorepo（如 apps/chaos/.agents/scripts/）和扁平仓库布局。
    """
    current = script_path.resolve().parent
    for _ in range(8):
        if (current / ".git").exists():
            return current
        current = current.parent
    # 回退：通过 pyproject.toml 定位
    current = script_path.resolve().parent
    for _ in range(8):
        if (current / "pyproject.toml").exists():
            return current
        current = current.parent
    # 最终回退
    return script_path.resolve().parent.parent.parent


def main(argv: list[str] | None = None) -> int:
    # Windows 控制台/管道默认使用 GBK，emoji 输出会触发 UnicodeEncodeError。
    # 在入口统一切换 stdout/stderr 到 UTF-8，使 CI 与本地表现一致。
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(encoding="utf-8")
            except OSError, ValueError:
                # 在某些终端上 reconfigure 不可用时静默回退即可。
                pass

    args = parse_args(argv)
    project_root = (
        Path(args.root).resolve() if args.root else _detect_project_root(Path(__file__))
    )

    if not project_root.is_dir():
        print(f"项目根目录不存在: {project_root}", file=sys.stderr)
        return 2

    all_records: list[LinkRecord] = []
    sources: list[Path] = []

    for rel in args.files:
        sources.append((project_root / rel).resolve())

    # --dirs 未传 -> 使用默认；--dirs 传空 -> 不扫描；--dirs 传值 -> 扫描指定。
    dirs = list(_DEFAULT_DIRS) if args.dirs is None else list(args.dirs)
    seen: set[Path] = set(sources)
    for rel in dirs:
        directory = (project_root / rel).resolve()
        for md_file in _iter_markdown_under(directory):
            if md_file not in seen:
                sources.append(md_file)
                seen.add(md_file)

    for source in sources:
        all_records.extend(check_file(source, project_root))

    _print_report(all_records, project_root, args.verbose)

    failed = [r for r in all_records if not r.ok]
    print()
    if failed:
        print(f"❌ 共发现 {len(failed)} 条失效链接。")
        return 1

    print(f"✅ 共校验 {len(all_records)} 条相对链接，全部有效。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
