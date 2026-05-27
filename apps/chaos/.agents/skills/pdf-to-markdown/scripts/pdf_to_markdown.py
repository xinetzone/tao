"""PDF -> Markdown 拆分脚本（参数化通用版本）.

读取 `pdf_extract.py` 产物（`pdf_raw_text.txt` + `pdf_page_meta.json`），
按帛书本《老子》体例（德经在前、道经在后）拆分为格式规范的 Markdown 文件。

输出结构::

    <output_dir>/
    ├── index.md
    ├── images/cover.png（如提供 --cover）
    ├── front-matter/
    │   ├── copyright.md
    │   ├── author.md
    │   ├── preface.md
    │   └── introduction.md
    ├── de-jing/
    │   ├── index.md
    │   └── chapter-01..44.md
    ├── dao-jing/
    │   ├── index.md
    │   └── chapter-01..37.md
    └── appendix/
        └── phonetic.md

CLI 用法::

    python pdf_to_markdown.py <meta_json> <raw_txt> --output-dir <dir> [--cover <png>]
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

# 章节内部小节标记
SECTION_MARKERS = ("帛书版", "传世版", "版本差异", "直译", "解读")
# 应作为引用块（经文）的小节
QUOTE_SECTIONS = {"帛书版", "传世版"}


# ---------- CLI 解析 ----------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="PDF 结构元数据 -> Markdown 文件集")
    parser.add_argument("meta_json", help="pdf_page_meta.json 路径")
    parser.add_argument("raw_txt", help="pdf_raw_text.txt 路径")
    parser.add_argument("--output-dir", "-o", required=True, help="Markdown 输出目录")
    parser.add_argument("--cover", help="封面图片路径（可选）")
    return parser.parse_args()


# ---------- 数据加载 ----------


@dataclass
class Heading:
    page: int
    end_page: int
    level: str
    title: str
    raw: str
    chapter_index: int | None
    modern_chapter: int | None


def load_pages(raw_path: Path) -> OrderedDict[int, list[str]]:
    """按页码加载原始文本。"""
    text = raw_path.read_text(encoding="utf-8")
    pages: OrderedDict[int, list[str]] = OrderedDict()
    current: int | None = None
    buffer: list[str] = []
    page_re = re.compile(r"^=====\s*PAGE\s*(\d+)\s*=====\s*$")
    for line in text.splitlines():
        m = page_re.match(line)
        if m:
            if current is not None:
                pages[current] = buffer
            current = int(m.group(1))
            buffer = []
        else:
            buffer.append(line)
    if current is not None:
        pages[current] = buffer
    return pages


def load_headings(meta_path: Path) -> list[Heading]:
    data = json.loads(meta_path.read_text(encoding="utf-8"))
    return [
        Heading(
            page=h["page"],
            end_page=h["end_page"],
            level=h["level"],
            title=h["title"],
            raw=h["raw"],
            chapter_index=h.get("chapter_index"),
            modern_chapter=h.get("modern_chapter"),
        )
        for h in data["headings"]
    ]


# ---------- 文本工具 ----------


def collect_lines(
    pages: OrderedDict[int, list[str]], start: int, end: int
) -> list[str]:
    """汇集 [start, end] 闭区间内的所有行。"""
    out: list[str] = []
    for p in range(start, end + 1):
        if p in pages:
            out.extend(pages[p])
    return out


def strip_chapter_title(lines: list[str], title_raw: str) -> list[str]:
    """剥除正文起始处出现的章节标题行。"""
    out = list(lines)
    target = title_raw.strip()
    for i, line in enumerate(out):
        s = line.strip()
        if not s:
            continue
        if s == target:
            return out[i + 1 :]
        # 第一处非空行未必精确匹配，若包含核心标题文本亦剥除
        if i < 5 and target and target[:6] in s:
            return out[i + 1 :]
        break
    return out


def is_section_marker(line: str) -> str | None:
    """判断是否为章节内部小节标记，返回小节名或 None。"""
    s = line.strip()
    for marker in SECTION_MARKERS:
        if s == f"{marker}：" or s == f"{marker}:":
            return marker
    return None


def split_into_sections(lines: list[str]) -> list[tuple[str | None, list[str]]]:
    """按内部小节标记拆分章节正文。"""
    sections: list[tuple[str | None, list[str]]] = []
    current_name: str | None = None
    current_lines: list[str] = []
    for line in lines:
        marker = is_section_marker(line)
        if marker:
            if current_name is not None or current_lines:
                sections.append((current_name, current_lines))
            current_name = marker
            current_lines = []
        else:
            current_lines.append(line)
    if current_name is not None or current_lines:
        sections.append((current_name, current_lines))
    return sections


def merge_paragraph(lines: list[str]) -> str:
    """将多行中文文本合并为单段（去除断行排版导致的硬换行）。"""
    joined = "".join(line.strip() for line in lines if line.strip())
    return joined


def split_paragraphs(lines: list[str]) -> list[str]:
    """把一组行切分为段落。

    规则：空行作为段落分隔；否则全部合并为一段，去除排版换行。
    """
    paragraphs: list[str] = []
    buf: list[str] = []
    for line in lines:
        if line.strip():
            buf.append(line)
        else:
            if buf:
                paragraphs.append(merge_paragraph(buf))
                buf = []
    if buf:
        paragraphs.append(merge_paragraph(buf))
    return [p for p in paragraphs if p]


def render_section(name: str | None, lines: list[str]) -> list[str]:
    """渲染一个小节为 Markdown 行片段。"""
    out: list[str] = []
    paragraphs = split_paragraphs(lines)
    if name is not None:
        out.append(f"### {name}")
        out.append("")
    if not paragraphs:
        return out
    if name in QUOTE_SECTIONS:
        for i, para in enumerate(paragraphs):
            if i > 0:
                out.append(">")
            out.append(f"> {para}")
        out.append("")
    else:
        for para in paragraphs:
            out.append(para)
            out.append("")
    return out


# ---------- 文件渲染 ----------


@dataclass
class ChapterFile:
    relpath: str  # 相对 OUT_DIR 的路径，无 .md 后缀
    title: str
    chapter_index: int
    modern_chapter: int


def write_chapter(
    heading: Heading,
    pages: OrderedDict[int, list[str]],
    target: Path,
) -> int:
    """写入单个章节 Markdown 文件，返回字符数。"""
    body_lines = collect_lines(pages, heading.page, heading.end_page)
    body_lines = strip_chapter_title(body_lines, heading.raw)
    sections = split_into_sections(body_lines)

    md: list[str] = []
    md.append(f"# {heading.raw}")
    md.append("")
    if not sections:
        for para in split_paragraphs(body_lines):
            md.append(para)
            md.append("")
    else:
        for name, lines in sections:
            if name is None and not [ln for ln in lines if ln.strip()]:
                continue
            md.extend(render_section(name, lines))

    text = "\n".join(md).rstrip() + "\n"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8", newline="\n")
    return len(text)


def write_simple_page(
    title: str,
    pages: OrderedDict[int, list[str]],
    page_range: tuple[int, int],
    target: Path,
    *,
    strip_first_title: str | None = None,
) -> int:
    """写入一个简单的前置内容页面（版权 / 序 / 注读说明 / 作者简介）。"""
    start, end = page_range
    lines = collect_lines(pages, start, end)
    if strip_first_title:
        lines = strip_chapter_title(lines, strip_first_title)
    paragraphs = split_paragraphs(lines)

    md = [f"# {title}", ""]
    for para in paragraphs:
        md.append(para)
        md.append("")
    text = "\n".join(md).rstrip() + "\n"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8", newline="\n")
    return len(text)


def write_appendix(
    pages: OrderedDict[int, list[str]],
    page_range: tuple[int, int],
    target: Path,
) -> int:
    """附录（帛书《老子》注音版）：保留原始拼音/汉字交错排版，使用代码块呈现。"""
    start, end = page_range
    raw_lines: list[str] = []
    for p in range(start, end + 1):
        if p in pages:
            raw_lines.extend(pages[p])
    while raw_lines and not raw_lines[0].strip():
        raw_lines.pop(0)
    while raw_lines and not raw_lines[-1].strip():
        raw_lines.pop()

    md: list[str] = []
    md.append("# 附录·帛书《老子》注音版")
    md.append("")
    md.append(
        "> 本附录按帛书篇次（德经在前、道经在后）逐章注音，保留原书拼音与汉字交错的排版。"
    )
    md.append("")
    md.append("```text")
    md.extend(raw_lines)
    md.append("```")
    text = "\n".join(md).rstrip() + "\n"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8", newline="\n")
    return len(text)


# ---------- 索引 ----------


def write_pian_index(
    pian_name: str,
    chapters: list[ChapterFile],
    target: Path,
) -> int:
    md: list[str] = []
    md.append(f"# {pian_name}")
    md.append("")
    md.append("| 帛书章序 | 通行本章号 | 章节标题 |")
    md.append("| --- | --- | --- |")
    for ch in chapters:
        fname = Path(ch.relpath).name
        md.append(
            f"| {ch.chapter_index} | 今{ch.modern_chapter}章 | "
            f"[{ch.title}]({fname}.md) |"
        )
    md.append("")
    md.append("```{toctree}")
    md.append(":maxdepth: 1")
    md.append(":hidden:")
    md.append("")
    for ch in chapters:
        md.append(Path(ch.relpath).name)
    md.append("```")
    text = "\n".join(md).rstrip() + "\n"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8", newline="\n")
    return len(text)


def write_root_index(
    de_chapters: list[ChapterFile],
    dao_chapters: list[ChapterFile],
    target: Path,
    has_cover: bool,
) -> int:
    md: list[str] = []
    md.append("# 帛书老子注读")
    md.append("")
    if has_cover:
        md.append("![封面](images/cover.png)")
        md.append("")
    md.append(
        "本目录收录《帛书老子注读》（秦波 著）全本电子版的 Markdown 转录，"
        "依帛书本《老子》体例呈现：**德经在前、道经在后**，共 81 章，"
        "并附帛书《老子》注音版。"
    )
    md.append("")
    md.append("- 底本：长沙马王堆帛书整理小组校勘的帛书《老子》合订本")
    md.append("- 参校：中华书局《帛书老子校注》（高明）、王弼通行本、河上公注本")
    md.append(
        "- 章节次序遵循帛书本，部分位置错乱章（如今 24、22、23、80、81、67-79）"
        "已按帛书经文次序回正"
    )
    md.append("")
    md.append("## 篇章统计")
    md.append("")
    md.append(f"- 德经：**{len(de_chapters)} 章**（对应通行本第 38-79 章，含次序变化）")
    md.append(f"- 道经：**{len(dao_chapters)} 章**（对应通行本第 1-37 章，含次序变化）")
    md.append("- 附录：帛书《老子》注音版")
    md.append("")
    md.append("```{toctree}")
    md.append(":maxdepth: 2")
    md.append(":caption: 目录")
    md.append("")
    md.append("front-matter/preface")
    md.append("front-matter/introduction")
    md.append("front-matter/author")
    md.append("front-matter/copyright")
    md.append("de-jing/index")
    md.append("dao-jing/index")
    md.append("appendix/phonetic")
    md.append("```")
    text = "\n".join(md).rstrip() + "\n"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8", newline="\n")
    return len(text)


def _process_chapter_group(
    chapter_headings: list[Heading],
    sub_dir: Path,
    relpath_root: str,
    offset: int,
    pages: OrderedDict[int, list[str]],
) -> tuple[list[ChapterFile], int, int]:
    """处理一组章节（德经或道经），返回 (chapter_files, file_count, char_count)。"""
    chapters: list[ChapterFile] = []
    total_chars = 0
    count = 0
    for h in chapter_headings:
        seq = h.chapter_index - offset
        fname = f"chapter-{seq:02d}.md"
        target = sub_dir / fname
        chars = write_chapter(h, pages, target)
        total_chars += chars
        count += 1
        chapters.append(
            ChapterFile(
                relpath=f"{relpath_root}/chapter-{seq:02d}",
                title=h.raw,
                chapter_index=seq,
                modern_chapter=h.modern_chapter or 0,
            )
        )
    return chapters, count, total_chars


# ---------- 主流程 ----------


def main() -> int:
    args = parse_args()
    meta_path = Path(args.meta_json).resolve()
    raw_path = Path(args.raw_txt).resolve()
    out_dir = Path(args.output_dir).resolve()
    cover_path = Path(args.cover).resolve() if args.cover else None

    if not raw_path.exists() or not meta_path.exists():
        print(
            f"[ERR] 缺少前置产物: {raw_path} / {meta_path}",
            file=sys.stderr,
        )
        return 1

    img_dir = out_dir / "images"
    fm_dir = out_dir / "front-matter"
    de_dir = out_dir / "de-jing"
    dao_dir = out_dir / "dao-jing"
    appendix_dir = out_dir / "appendix"

    pages = load_pages(raw_path)
    headings = load_headings(meta_path)

    # 清空输出目录的章节内容，避免残留
    for sub in (de_dir, dao_dir, appendix_dir, fm_dir, img_dir):
        if sub.exists():
            shutil.rmtree(sub)

    out_dir.mkdir(parents=True, exist_ok=True)

    stats = {
        "files": 0,
        "chars": 0,
        "de_chapters": 0,
        "dao_chapters": 0,
        "front_matter": 0,
        "appendix": 0,
    }

    # 1. 复制封面
    has_cover = False
    if cover_path and cover_path.exists():
        img_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(cover_path, img_dir / "cover.png")
        has_cover = True
        print(f"[OK] 封面已复制 -> {img_dir / 'cover.png'}")
    elif cover_path:
        print(f"[WARN] 封面图片缺失：{cover_path}")

    # 2. 前置内容页
    fm_pages = [
        ("preface", "序", (7, 9), "序"),
        ("introduction", "注读说明", (10, 11), "注读说明"),
        ("author", "作者简介", (6, 6), "作者简介"),
        ("copyright", "版权信息", (2, 2), "版权信息"),
    ]
    for slug, title, rng, strip_title in fm_pages:
        target = fm_dir / f"{slug}.md"
        chars = write_simple_page(
            title, pages, rng, target, strip_first_title=strip_title
        )
        stats["files"] += 1
        stats["chars"] += chars
        stats["front_matter"] += 1
        print(f"[OK] front-matter/{slug}.md ({chars} chars)")

    # 3. 章节文件
    chapter_headings = [h for h in headings if h.level == "chapter"]
    pian_headings = [h for h in headings if h.level == "pian"]
    de_pian = next((h for h in pian_headings if h.title == "德经"), None)
    dao_pian = next((h for h in pian_headings if h.title == "道经"), None)
    if de_pian is None or dao_pian is None:
        print("[ERR] 缺失德经/道经篇章标题", file=sys.stderr)
        return 2

    # 按篇分组
    de_headings = [h for h in chapter_headings if h.page < dao_pian.page]
    dao_headings = [h for h in chapter_headings if h.page >= dao_pian.page]

    de_dir.mkdir(parents=True, exist_ok=True)
    dao_dir.mkdir(parents=True, exist_ok=True)

    # 并行处理德经和道经
    with ThreadPoolExecutor(max_workers=2) as executor:
        fut_de = executor.submit(
            _process_chapter_group, de_headings, de_dir, "de-jing", 0, pages
        )
        fut_dao = executor.submit(
            _process_chapter_group, dao_headings, dao_dir, "dao-jing", 44, pages
        )
        de_chapters, de_count, de_chars = fut_de.result()
        dao_chapters, dao_count, dao_chars = fut_dao.result()

    stats["de_chapters"] = de_count
    stats["dao_chapters"] = dao_count
    stats["files"] += de_count + dao_count
    stats["chars"] += de_chars + dao_chars
    print(f"[OK] 德经 {de_count} 章 + 道经 {dao_count} 章 并行写入完成")

    # 4. 篇章索引
    chars = write_pian_index("德经", de_chapters, de_dir / "index.md")
    stats["files"] += 1
    stats["chars"] += chars
    print(f"[OK] de-jing/index.md ({chars} chars)")

    chars = write_pian_index("道经", dao_chapters, dao_dir / "index.md")
    stats["files"] += 1
    stats["chars"] += chars
    print(f"[OK] dao-jing/index.md ({chars} chars)")

    # 5. 附录
    appendix_h = next((h for h in headings if h.level == "appendix"), None)
    if appendix_h is None:
        print("[WARN] 未找到附录标题，跳过附录生成")
    else:
        chars = write_appendix(
            pages, (appendix_h.page, appendix_h.end_page), appendix_dir / "phonetic.md"
        )
        stats["files"] += 1
        stats["chars"] += chars
        stats["appendix"] = 1
        print(f"[OK] appendix/phonetic.md ({chars} chars)")

    # 6. 主索引
    chars = write_root_index(de_chapters, dao_chapters, out_dir / "index.md", has_cover)
    stats["files"] += 1
    stats["chars"] += chars
    print(f"[OK] index.md ({chars} chars)")

    # 7. 统计
    print()
    print("=" * 60)
    print("[DONE] Markdown 转换完成")
    print(f"  总文件数：{stats['files']}")
    print(f"  总字符数：{stats['chars']:,}")
    print(f"  德经章节：{stats['de_chapters']} 章")
    print(f"  道经章节：{stats['dao_chapters']} 章")
    print(f"  前置内容：{stats['front_matter']} 篇")
    print(f"  附录：{stats['appendix']} 篇")
    print(f"  输出目录：{out_dir}")
    print("=" * 60)

    expected = 81
    actual = stats["de_chapters"] + stats["dao_chapters"]
    if actual != expected:
        print(f"[WARN] 章节数 {actual} ≠ 预期 {expected}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
