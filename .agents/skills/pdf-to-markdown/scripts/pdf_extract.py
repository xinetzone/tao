"""PDF 全文提取与结构分析脚本（参数化通用版本）.

针对中文学术/古籍类 PDF，完成：
1. 使用 pdfplumber 逐页提取文本，区分扫描页/文本页；
2. 用 pypdfium2 渲染封面为 PNG；
3. 基于章节标记（中文数字编号、篇章/章节/附录）分析文档结构；
4. 输出原始文本、结构分析报告、JSON 元数据（含 schema 验证）。

CLI 用法::

    python pdf_extract.py <pdf_path> [--output-dir <dir>] [--page-range 1-100]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import warnings
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

import pdfplumber

# 抑制 pdfplumber/pdfminer 的 FontBBox 等无害警告
warnings.filterwarnings("ignore")

PAGE_SEP = "===== PAGE {page} ====="

# 章节识别用正则
# 1. 篇章标题：独立成行的「德经注读 / 道经注读」
RE_PIAN = re.compile(r"^\s*(德经注读|道经注读)\s*$")
# 2. 章节标题：形如「一、道、德是这样沦丧的（今38章）」
RE_CHAPTER = re.compile(
    r"^\s*(?P<cn_num>[一二三四五六七八九十百零〇○]{1,5})、\s*(?P<title>.+?)\s*（今\s*(?P<modern_num>\d{1,3}|[一二三四五六七八九十百零〇○]{1,5})\s*章）\s*$"
)
# 3. 附录标题
RE_APPENDIX = re.compile(r"^\s*附录(?:\s+(.+))?\s*$")
# 4. 前置内容（独立行）
FRONT_MATTER_TITLES = {
    "版权信息": "版权信息",
    "目录": "目录",
    "作者简介": "作者简介",
    "序": "序",
    "注读说明": "注读说明",
}


@dataclass
class PageInfo:
    page: int
    char_count: int
    is_scan: bool
    text: str = ""
    extract_error: str | None = None


@dataclass
class Heading:
    page: int
    line_index: int
    raw: str
    level: str  # "pian" | "chapter" | "appendix" | "front"
    title: str
    chapter_index: int | None = None  # 在书内的章节序（1..81）
    modern_chapter: int | None = None  # 对应通行本章号
    end_page: int | None = None


# ---------- CLI 解析 ----------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="PDF 全文提取与结构分析")
    parser.add_argument("pdf_path", help="PDF 文件路径")
    parser.add_argument(
        "--output-dir", "-o", default=None, help="输出目录（默认与 PDF 同目录）"
    )
    parser.add_argument("--page-range", help="页码范围，如 1-100")
    return parser.parse_args()


def _parse_page_range(spec: str | None, total: int) -> tuple[int, int]:
    """解析 --page-range 参数为 (start, end) 闭区间，1-based。"""
    if not spec:
        return 1, total
    m = re.match(r"^\s*(\d+)\s*-\s*(\d+)\s*$", spec)
    if not m:
        raise ValueError(f"invalid --page-range: {spec!r}, expected like '1-100'")
    start, end = int(m.group(1)), int(m.group(2))
    if start < 1 or end < start:
        raise ValueError(f"invalid --page-range range: {start}-{end}")
    return start, min(end, total)


# ---------- 提取阶段 ----------


def extract_pages(
    pdf_path: Path, page_range: tuple[int, int] | None = None
) -> list[PageInfo]:
    pages: list[PageInfo] = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        total = len(pdf.pages)
        if page_range is None:
            start, end = 1, total
        else:
            start, end = page_range
        print(
            f"[INFO] 打开 PDF：{pdf_path.name}，共 {total} 页；"
            f"提取范围 P{start}-P{end}"
        )
        for idx, page in enumerate(pdf.pages, start=1):
            if idx < start or idx > end:
                continue
            try:
                text = page.extract_text() or ""
            except Exception as exc:  # noqa: BLE001
                pages.append(
                    PageInfo(page=idx, char_count=0, is_scan=False, text="", extract_error=str(exc))
                )
                print(f"[WARN] 第 {idx} 页提取失败：{exc}")
                continue
            char_count = len(text.strip())
            is_scan = char_count == 0
            pages.append(PageInfo(page=idx, char_count=char_count, is_scan=is_scan, text=text))
            if idx % 30 == 0 or idx == end:
                print(f"[INFO] 已处理 {idx}/{end} 页")
    return pages


def write_raw_text(pages: Iterable[PageInfo], target: Path) -> None:
    lines: list[str] = []
    for p in pages:
        lines.append(PAGE_SEP.format(page=p.page))
        if p.extract_error:
            lines.append(f"[EXTRACT_ERROR] {p.extract_error}")
        elif p.is_scan:
            lines.append("[SCAN_PAGE_NO_TEXT]")
        else:
            lines.append(p.text.rstrip())
        lines.append("")
    target.write_text("\n".join(lines), encoding="utf-8")
    print(f"[OK] 全文已写入 {target}")


# ---------- 封面渲染 ----------


def render_cover(pdf_path: Path, out_png: Path) -> bool:
    """使用 pypdfium2 渲染首页为 PNG，poppler 缺失也能工作."""
    try:
        import pypdfium2 as pdfium

        pdf = pdfium.PdfDocument(str(pdf_path))
        page = pdf[0]
        pil_image = page.render(scale=2.0).to_pil()
        pil_image.save(out_png, format="PNG")
        page.close()
        pdf.close()
        print(f"[OK] 封面已渲染至 {out_png}")
        return True
    except Exception as exc:  # noqa: BLE001
        print(f"[WARN] pypdfium2 渲染封面失败：{exc}")
        try:
            from pdf2image import convert_from_path

            images = convert_from_path(str(pdf_path), first_page=1, last_page=1, dpi=200)
            if images:
                images[0].save(out_png, "PNG")
                print(f"[OK] pdf2image 渲染封面 -> {out_png}")
                return True
        except Exception as exc2:  # noqa: BLE001
            print(f"[WARN] pdf2image 渲染失败：{exc2}")
    return False


# ---------- 结构分析 ----------

CN_NUM_MAP = {
    "零": 0, "〇": 0, "○": 0,
    "一": 1, "二": 2, "三": 3, "四": 4, "五": 5,
    "六": 6, "七": 7, "八": 8, "九": 9,
}


def cn_to_int(text: str) -> int | None:
    """将中文数字（≤百位）转换为整数；失败返回 None."""
    text = text.strip()
    if not text:
        return None
    if text.isdigit():
        return int(text)
    if text == "十":
        return 10
    if text.startswith("十") and len(text) == 2:
        return 10 + CN_NUM_MAP.get(text[1], 0)
    if "百" in text:
        try:
            hundred_idx = text.index("百")
            h = CN_NUM_MAP.get(text[hundred_idx - 1], 1) if hundred_idx > 0 else 1
            rest = text[hundred_idx + 1 :]
            tail = 0
            if not rest:
                tail = 0
            elif rest in CN_NUM_MAP:
                tail = CN_NUM_MAP[rest]
            elif rest.startswith("零"):
                tail = CN_NUM_MAP.get(rest[1:], 0) if len(rest) > 1 else 0
            elif "十" in rest:
                ten_idx = rest.index("十")
                t = CN_NUM_MAP.get(rest[ten_idx - 1], 1) if ten_idx > 0 else 1
                ones = rest[ten_idx + 1 :]
                tail = t * 10 + (CN_NUM_MAP.get(ones, 0) if ones else 0)
            return h * 100 + tail
        except Exception:  # noqa: BLE001
            return None
    if "十" in text:
        ten_idx = text.index("十")
        t = CN_NUM_MAP.get(text[ten_idx - 1], 1) if ten_idx > 0 else 1
        ones = text[ten_idx + 1 :]
        return t * 10 + (CN_NUM_MAP.get(ones, 0) if ones else 0)
    if text in CN_NUM_MAP:
        return CN_NUM_MAP[text]
    return None


RE_CHAPTER_PREFIX = re.compile(
    r"^\s*[一二三四五六七八九十百零〇○]{1,5}、"
)


def _merge_wrapped_lines(text: str) -> list[str]:
    """合并被排版换行打散的章节标题。

    一行如果以「中文数字、」开头但未以「章）」结尾，则向后看最多 2 行
    尝试拼接直到遇到「章）」。
    """
    raw_lines = text.splitlines()
    merged: list[str] = []
    skip_count = 0
    for i, line in enumerate(raw_lines):
        if skip_count:
            skip_count -= 1
            continue
        stripped = line.strip()
        if (
            RE_CHAPTER_PREFIX.match(stripped)
            and "章）" not in stripped
        ):
            combined = stripped
            consumed = 0
            for j in (1, 2):
                if i + j >= len(raw_lines):
                    break
                nxt = raw_lines[i + j].strip()
                if not nxt:
                    break
                combined += nxt
                consumed += 1
                if "章）" in combined:
                    break
            if "章）" in combined:
                merged.append(combined)
                skip_count = consumed
                continue
        merged.append(line)
    return merged


def _merge_intra_page_titles(pages: list[PageInfo]) -> None:
    """页内标题合并：将同一页内被排版换行打散的章节标题拼接为单行。"""
    for page in pages:
        if not page.text:
            continue
        merged = _merge_wrapped_lines(page.text)
        page.text = "\n".join(merged)


def _merge_cross_page_titles(pages: list[PageInfo]) -> None:
    """跨页标题合并：当前页末尾有未闭合的章节标题时，从下一页首行吸收碎片。"""
    for i in range(len(pages) - 1):
        cur = pages[i]
        nxt = pages[i + 1]
        if not cur.text or not nxt.text:
            continue
        cur_lines = cur.text.rstrip().splitlines()
        if not cur_lines:
            continue
        for tail_offset in (1, 2):
            if len(cur_lines) < tail_offset:
                break
            tail_line = cur_lines[-tail_offset].strip()
            if RE_CHAPTER_PREFIX.match(tail_line) and "章）" not in tail_line:
                nxt_lines = nxt.text.lstrip().splitlines()
                fragment_lines = []
                for j in range(min(2, len(nxt_lines))):
                    candidate = nxt_lines[j].strip()
                    if not candidate:
                        break
                    fragment_lines.append(candidate)
                    if "章）" in candidate:
                        break
                combined = tail_line + "".join(fragment_lines)
                if "章）" in combined:
                    cur_lines[-tail_offset] = combined
                    cur.text = "\n".join(cur_lines)
                    nxt_remaining = nxt_lines[len(fragment_lines):]
                    nxt.text = "\n".join(nxt_remaining)
                    break


def detect_headings(pages: list[PageInfo]) -> list[Heading]:
    """识别篇章/章节/附录标题。

    过滤策略：
    1. 一页中匹配章节模板的行 ≥5 视为目录页，跳过；
    2. 篇章标题（德经注读/道经注读）仅在非目录页识别；
    3. 章节标题处理跨行换行。
    """
    _merge_intra_page_titles(pages)
    _merge_cross_page_titles(pages)
    page_lines: dict[int, list[str]] = {}
    is_toc_page: dict[int, bool] = {}
    for p in pages:
        if not p.text:
            page_lines[p.page] = []
            is_toc_page[p.page] = False
            continue
        lines = _merge_wrapped_lines(p.text)
        page_lines[p.page] = lines
        cnt = sum(1 for ln in lines if RE_CHAPTER.match(ln.strip()))
        is_toc_page[p.page] = cnt >= 5

    headings: list[Heading] = []
    chapter_seq = 0
    for p in pages:
        lines = page_lines.get(p.page, [])
        if not lines:
            continue
        is_toc = is_toc_page[p.page]
        for line_idx, raw_line in enumerate(lines):
            line = raw_line.strip()
            if not line:
                continue
            # 1) 篇章标题（仅非目录页）
            if RE_PIAN.match(line) and not is_toc:
                headings.append(
                    Heading(
                        page=p.page,
                        line_index=line_idx,
                        raw=line,
                        level="pian",
                        title=line.replace("注读", ""),
                    )
                )
                continue
            # 2) 章节：仅在非目录页识别
            if is_toc:
                continue
            mc = RE_CHAPTER.match(line)
            if mc:
                cn_num = cn_to_int(mc.group("cn_num"))
                modern_num_raw = mc.group("modern_num")
                modern_num = (
                    int(modern_num_raw)
                    if modern_num_raw.isdigit()
                    else cn_to_int(modern_num_raw)
                )
                title = mc.group("title").strip()
                chapter_seq += 1
                headings.append(
                    Heading(
                        page=p.page,
                        line_index=line_idx,
                        raw=line,
                        level="chapter",
                        title=f"{cn_num}、{title}（今{modern_num}章）",
                        chapter_index=chapter_seq,
                        modern_chapter=modern_num,
                    )
                )
                continue
            # 3) 附录
            ma = RE_APPENDIX.match(line)
            if ma and len(line) <= 30:
                title = line if ma.group(1) is None else line
                if not any(h.level == "appendix" for h in headings):
                    headings.append(
                        Heading(
                            page=p.page,
                            line_index=line_idx,
                            raw=line,
                            level="appendix",
                            title=title,
                        )
                    )
                continue

    # 计算结束页
    for i, h in enumerate(headings):
        if i + 1 < len(headings):
            nxt = headings[i + 1]
            if nxt.page > h.page:
                h.end_page = nxt.page - 1
            else:
                h.end_page = h.page
        else:
            h.end_page = pages[-1].page
    return headings


def detect_front_matter(pages: list[PageInfo], first_pian_page: int | None) -> list[dict]:
    """识别前置内容：版权、目录、作者简介、序、注读说明等。"""
    found: list[dict] = []
    upto = first_pian_page - 1 if first_pian_page else 20
    for p in pages:
        if p.page > upto:
            break
        if not p.text:
            continue
        for raw_line in p.text.splitlines()[:3]:
            line = raw_line.strip()
            if line in FRONT_MATTER_TITLES and not any(
                f["page"] == p.page for f in found
            ):
                found.append({"page": p.page, "title": line, "keyword": line})
                break
    return found


# ---------- 报告输出 ----------


def write_structure_report(
    pages: list[PageInfo],
    headings: list[Heading],
    front_matter: list[dict],
    cover_ok: bool,
    target: Path,
    pdf_name: str,
) -> None:
    total = len(pages)
    scan_pages = [p.page for p in pages if p.is_scan]
    text_pages = [p.page for p in pages if not p.is_scan and not p.extract_error]
    err_pages = [(p.page, p.extract_error) for p in pages if p.extract_error]

    pian_headings = [h for h in headings if h.level == "pian"]
    chapter_headings = [h for h in headings if h.level == "chapter"]
    appendix_headings = [h for h in headings if h.level == "appendix"]

    lines: list[str] = []
    lines.append(f"# {pdf_name} · PDF 结构分析报告")
    lines.append("")
    lines.append(f"> 由 `pdf_extract.py` 自动生成，输入 `{pdf_name}`。")
    lines.append("")
    lines.append("## 1. 文档基本信息")
    lines.append("")
    lines.append(f"- 总页数：**{total}**")
    lines.append(f"- 文本页数：**{len(text_pages)}**")
    lines.append(f"- 扫描页（无可提取文本）数：**{len(scan_pages)}**")
    lines.append(f"- 提取失败页数：**{len(err_pages)}**")
    lines.append(f"- 封面渲染：{'成功' if cover_ok else '失败'}")
    lines.append("")
    lines.append("## 2. 扫描页清单")
    lines.append("")
    if scan_pages:
        lines.append(", ".join(f"P{p}" for p in scan_pages))
    else:
        lines.append("无")
    lines.append("")
    if err_pages:
        lines.append("## 2.1 提取失败页")
        lines.append("")
        for p, err in err_pages:
            lines.append(f"- P{p}: {err}")
        lines.append("")

    lines.append("## 3. 前置内容（front matter）")
    lines.append("")
    if front_matter:
        lines.append("| 页码 | 标题 | 关键字 |")
        lines.append("| --- | --- | --- |")
        for fm in front_matter:
            lines.append(f"| P{fm['page']} | {fm['title']} | {fm['keyword']} |")
    else:
        lines.append("未检测到典型的「序/前言/凡例/目录」标记，前置内容可能融入正文或扫描化。")
    lines.append("")

    lines.append("## 4. 篇章")
    lines.append("")
    if pian_headings:
        lines.append("| 序号 | 篇名 | 起始页 |")
        lines.append("| --- | --- | --- |")
        for i, h in enumerate(pian_headings, 1):
            lines.append(f"| {i} | {h.title} | P{h.page} |")
    else:
        lines.append("未检测到独立成行的篇章标记。")
    lines.append("")

    lines.append("## 5. 章节列表")
    lines.append("")
    lines.append(f"共检测到 **{len(chapter_headings)}** 处章节标题。")
    lines.append("")
    if chapter_headings:
        pian_by_page: list[tuple[int, str]] = [(h.page, h.title) for h in pian_headings]

        def belong(page: int) -> str:
            current = ""
            for pp, title in pian_by_page:
                if pp <= page:
                    current = title
            return current or "-"

        lines.append("| # | 篇 | 书内序 | 通行本章号 | 章节标题 | 起始页 | 结束页 |")
        lines.append("| --- | --- | --- | --- | --- | --- | --- |")
        for i, h in enumerate(chapter_headings, 1):
            lines.append(
                f"| {i} | {belong(h.page)} | {h.chapter_index} | 今{h.modern_chapter}章 | {h.title} | P{h.page} | P{h.end_page} |"
            )
    lines.append("")

    lines.append("## 5.1 附录")
    lines.append("")
    if appendix_headings:
        for h in appendix_headings:
            lines.append(f"- **{h.title}** —— 起始 P{h.page}，结束 P{h.end_page}")
    else:
        lines.append("未识别到独立成行的「附录」标题。")
    lines.append("")

    lines.append("## 6. 层级关系")
    lines.append("")
    lines.append("```mermaid")
    lines.append("flowchart TD")
    lines.append(f'    Root["{pdf_name}"]')
    if front_matter:
        lines.append('    Front["前置内容"]')
        lines.append("    Root --> Front")
        for fm in front_matter:
            node_id = f"FM{fm['page']}"
            lines.append(f'    {node_id}["{fm["title"]} (P{fm["page"]})"]')
            lines.append(f"    Front --> {node_id}")
    chapter_count_by_pian: dict[str, int] = {}
    for ch in chapter_headings:
        cur_pian = ""
        for ph in pian_headings:
            if ph.page <= ch.page:
                cur_pian = ph.title
        chapter_count_by_pian[cur_pian] = chapter_count_by_pian.get(cur_pian, 0) + 1
    for i, h in enumerate(pian_headings, 1):
        node = f"Pian{i}"
        cnt = chapter_count_by_pian.get(h.title, 0)
        lines.append(f'    {node}["{h.title} (P{h.page}, {cnt}章)"]')
        lines.append(f"    Root --> {node}")
    if appendix_headings:
        ap = appendix_headings[0]
        lines.append(f'    Appendix["{ap.title} (P{ap.page}-P{ap.end_page})"]')
        lines.append("    Root --> Appendix")
    lines.append("```")
    lines.append("")

    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[OK] 结构分析报告 -> {target}")


def write_page_meta(pages: list[PageInfo], headings: list[Heading], target: Path) -> dict:
    payload = {
        "total_pages": len(pages),
        "scan_pages": [p.page for p in pages if p.is_scan],
        "text_pages": [p.page for p in pages if not p.is_scan and not p.extract_error],
        "errors": [{"page": p.page, "error": p.extract_error} for p in pages if p.extract_error],
        "headings": [
            {
                "page": h.page,
                "end_page": h.end_page,
                "level": h.level,
                "title": h.title,
                "raw": h.raw,
                "chapter_index": h.chapter_index,
                "modern_chapter": h.modern_chapter,
            }
            for h in headings
        ],
    }
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] 页面元数据 -> {target}")
    return payload


# ---------- Schema 验证 ----------


def _validate_meta(meta: dict, schema: dict) -> None:
    """验证 meta 数据是否符合 schema。优先使用 jsonschema 库，否则退回基本断言。"""
    try:
        import jsonschema  # type: ignore[import-not-found]

        jsonschema.validate(meta, schema)
    except ImportError:
        # 轻量级验证
        assert isinstance(meta.get("total_pages"), int) and meta["total_pages"] >= 1
        assert isinstance(meta.get("scan_pages"), list)
        assert isinstance(meta.get("text_pages"), list)
        assert isinstance(meta.get("headings"), list)
        for h in meta["headings"]:
            assert h.get("level") in ("pian", "chapter", "appendix", "front")
            assert isinstance(h.get("page"), int)
            assert isinstance(h.get("end_page"), int)
        print("[INFO] jsonschema 不可用，使用基本断言验证")


# ---------- 主流程 ----------


def main() -> int:
    args = parse_args()
    pdf_path = Path(args.pdf_path).resolve()
    if not pdf_path.exists():
        print(f"[ERR] PDF 不存在：{pdf_path}", file=sys.stderr)
        return 1

    output_dir = Path(args.output_dir).resolve() if args.output_dir else pdf_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    raw_txt_path = output_dir / "pdf_raw_text.txt"
    struct_md_path = output_dir / "pdf_structure_analysis.md"
    cover_png_path = output_dir / f"{pdf_path.stem}-cover.png"
    page_meta_json = output_dir / "pdf_page_meta.json"

    # 解析页码范围
    try:
        with pdfplumber.open(str(pdf_path)) as _pdf:
            total = len(_pdf.pages)
        page_range = _parse_page_range(args.page_range, total)
    except ValueError as exc:
        print(f"[ERR] {exc}", file=sys.stderr)
        return 1

    pages = extract_pages(pdf_path, page_range=page_range)

    cover_ok = render_cover(pdf_path, cover_png_path)
    headings = detect_headings(pages)
    # 注意：write_raw_text 必须在 detect_headings 之后执行
    # 因为 detect_headings 内部会调用 _merge_cross_page_titles 修改 pages 中的文本
    write_raw_text(pages, raw_txt_path)
    first_pian_page = next((h.page for h in headings if h.level == "pian"), None)
    front_matter = detect_front_matter(pages, first_pian_page)

    write_structure_report(
        pages, headings, front_matter, cover_ok, struct_md_path, pdf_path.name
    )
    meta = write_page_meta(pages, headings, page_meta_json)

    # Schema 验证（可选，schema 文件存在时执行）
    schema_path = Path(__file__).resolve().parent.parent / "schemas" / "page-meta.schema.json"
    if schema_path.exists():
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        try:
            _validate_meta(meta, schema)
            print("[OK] JSON Schema 验证通过")
        except AssertionError as exc:
            print(f"[ERR] Schema 轻量验证失败：{exc}", file=sys.stderr)
            return 2
        except Exception as exc:  # noqa: BLE001
            print(f"[ERR] Schema 验证失败：{exc}", file=sys.stderr)
            return 2

    print("[DONE] PDF 提取与结构分析完成")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
