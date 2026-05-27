"""English academic PDF -> Markdown splitting script.

Reads the output of `pdf_extract.py` (`pdf_raw_text.txt` + `pdf_page_meta.json`),
identifies English academic paper structure and splits into a Markdown file set.

Output structure::

    <output_dir>/
    ├── index.md              # Paper metadata + toctree
    ├── abstract.md           # Abstract
    ├── sections/
    │   ├── 01-introduction.md
    │   ├── 02-methods.md
    │   └── ...
    ├── references.md         # References
    └── appendix/             # Appendix (if present)
        └── appendix.md

CLI usage::

    python pdf_to_markdown_en.py <meta_json> <raw_txt> --output-dir <dir> [--cover <png>]
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from collections import OrderedDict
from dataclasses import dataclass, field
from pathlib import Path

# ---------- Constants ----------

# Numbered section pattern: "1.", "1.1", "2.3.1" etc. (line-start, uppercase first letter)
NUMBERED_SECTION_RE = re.compile(
    r"^(\d+(?:\.\d+)*)\s+([A-Z][^\n]{2,})$", re.MULTILINE
)

# Standard un-numbered sections (case-insensitive matching)
STANDARD_SECTIONS = [
    "Abstract",
    "Introduction",
    "Background",
    "Related Work",
    "Methods",
    "Methodology",
    "Materials and Methods",
    "Results",
    "Discussion",
    "Conclusion",
    "Conclusions",
    "References",
    "Bibliography",
    "Acknowledgments",
    "Appendix",
]

_STANDARD_SECTIONS_LOWER = {s.lower() for s in STANDARD_SECTIONS}

# Page delimiter pattern used in pdf_raw_text.txt
_PAGE_RE = re.compile(r"^=====\s*PAGE\s*(\d+)\s*=====\s*$")


# ---------- CLI ----------


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="English academic PDF metadata -> Markdown file set"
    )
    parser.add_argument("meta_json", help="Path to pdf_page_meta.json")
    parser.add_argument("raw_txt", help="Path to pdf_raw_text.txt")
    parser.add_argument(
        "--output-dir", "-o", required=True, help="Markdown output directory"
    )
    parser.add_argument("--cover", help="Cover image path (optional)")
    return parser.parse_args()


# ---------- Data structures ----------


@dataclass
class Section:
    """Represents a detected section in the paper."""

    number: str  # e.g. "1", "2.1", "" for un-numbered
    title: str  # e.g. "Introduction", "Abstract"
    level: int  # heading depth: 1 = top-level, 2 = sub-section, etc.
    start_line: int  # index into flat_lines
    end_line: int = 0  # exclusive
    content: str = ""
    slug: str = ""  # filename slug


@dataclass
class PaperMeta:
    """Paper-level metadata extracted from the first page."""

    title: str = ""
    authors: str = ""
    first_page_lines: list[str] = field(default_factory=list)


# ---------- Text loading ----------


def load_pages(raw_path: Path) -> OrderedDict[int, list[str]]:
    """Load raw text split by page markers."""
    text = raw_path.read_text(encoding="utf-8")
    pages: OrderedDict[int, list[str]] = OrderedDict()
    current: int | None = None
    buffer: list[str] = []
    for line in text.splitlines():
        m = _PAGE_RE.match(line)
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


def flatten_pages(pages: OrderedDict[int, list[str]]) -> list[str]:
    """Flatten all pages into a single list of lines."""
    flat: list[str] = []
    for lines in pages.values():
        flat.extend(lines)
    return flat


# ---------- Section detection ----------


def _slugify(text: str) -> str:
    """Convert a section title to a filename-friendly slug."""
    slug = text.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    return slug


def _compute_level(number: str) -> int:
    """Compute heading level from section number (e.g. '2.1' -> 2)."""
    if not number:
        return 1
    return number.count(".") + 1


def detect_sections(flat_lines: list[str]) -> list[Section]:
    """Detect academic paper sections from flat text lines.

    Returns a list of Section objects in document order.
    """
    sections: list[Section] = []

    for idx, line in enumerate(flat_lines):
        stripped = line.strip()
        if not stripped:
            continue

        # Check numbered section pattern
        m = NUMBERED_SECTION_RE.match(stripped)
        if m:
            number = m.group(1)
            title = m.group(2).strip()
            level = _compute_level(number)
            sections.append(Section(
                number=number,
                title=title,
                level=level,
                start_line=idx,
            ))
            continue

        # Check standard un-numbered sections
        if stripped.lower() in _STANDARD_SECTIONS_LOWER:
            sections.append(Section(
                number="",
                title=stripped,
                level=1,
                start_line=idx,
            ))

    # Set end_line for each section
    for i in range(len(sections) - 1):
        sections[i].end_line = sections[i + 1].start_line
    if sections:
        sections[-1].end_line = len(flat_lines)

    # Extract content for each section
    for sec in sections:
        # Skip the heading line itself
        content_start = sec.start_line + 1
        content_lines = flat_lines[content_start:sec.end_line]
        sec.content = "\n".join(content_lines).strip()

    return sections


def extract_paper_meta(
    flat_lines: list[str], sections: list[Section]
) -> PaperMeta:
    """Extract paper title and authors from content before the first section."""
    meta = PaperMeta()
    if not sections:
        return meta

    first_section_line = sections[0].start_line
    preamble = flat_lines[:first_section_line]

    # Heuristic: title is the first non-empty line(s), authors follow
    non_empty = [ln.strip() for ln in preamble if ln.strip()]
    if non_empty:
        meta.title = non_empty[0]
        if len(non_empty) > 1:
            meta.authors = non_empty[1]
    meta.first_page_lines = preamble
    return meta


# ---------- File writing ----------


def _write_file(path: Path, content: str) -> int:
    """Write content to file, return character count."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    return len(content)


def _format_paragraphs(text: str) -> str:
    """Format raw extracted text into Markdown paragraphs.

    Joins continuation lines and separates paragraphs with blank lines.
    """
    lines = text.splitlines()
    paragraphs: list[str] = []
    buf: list[str] = []

    for line in lines:
        if line.strip():
            buf.append(line.strip())
        else:
            if buf:
                paragraphs.append(" ".join(buf))
                buf = []
    if buf:
        paragraphs.append(" ".join(buf))

    return "\n\n".join(paragraphs)


def write_section_file(sec: Section, seq: int, sections_dir: Path) -> str:
    """Write a numbered section to file. Returns the relative path (no .md)."""
    slug = _slugify(sec.title)
    fname = f"{seq:02d}-{slug}.md"
    heading_prefix = "#" * min(sec.level + 1, 4)

    md_parts: list[str] = []
    if sec.number:
        md_parts.append(f"# {sec.number} {sec.title}")
    else:
        md_parts.append(f"# {sec.title}")
    md_parts.append("")
    if sec.content:
        md_parts.append(_format_paragraphs(sec.content))
        md_parts.append("")

    content = "\n".join(md_parts).rstrip() + "\n"
    _write_file(sections_dir / fname, content)
    return f"sections/{fname[:-3]}"  # without .md extension


def write_abstract(sec: Section, out_dir: Path) -> int:
    """Write abstract.md."""
    md = ["# Abstract", "", _format_paragraphs(sec.content), ""]
    content = "\n".join(md).rstrip() + "\n"
    return _write_file(out_dir / "abstract.md", content)


def write_references(sec: Section, out_dir: Path) -> int:
    """Write references.md, preserving per-entry formatting."""
    md = ["# References", ""]
    if sec.content:
        # Keep reference entries as-is (don't merge lines aggressively)
        md.append(sec.content)
        md.append("")
    content = "\n".join(md).rstrip() + "\n"
    return _write_file(out_dir / "references.md", content)


def write_appendix(sec: Section, out_dir: Path) -> int:
    """Write appendix/appendix.md."""
    appendix_dir = out_dir / "appendix"
    md = [f"# {sec.title}", ""]
    if sec.content:
        md.append(_format_paragraphs(sec.content))
        md.append("")
    content = "\n".join(md).rstrip() + "\n"
    return _write_file(appendix_dir / "appendix.md", content)


def write_index(
    meta: PaperMeta,
    section_entries: list[tuple[str, str]],
    has_abstract: bool,
    has_references: bool,
    has_appendix: bool,
    has_cover: bool,
    out_dir: Path,
) -> int:
    """Write the root index.md with paper metadata and toctree."""
    md: list[str] = []
    md.append(f"# {meta.title}" if meta.title else "# Untitled Paper")
    md.append("")
    if has_cover:
        md.append("![Cover](images/cover.png)")
        md.append("")
    if meta.authors:
        md.append(f"**Authors:** {meta.authors}")
        md.append("")

    md.append("## Table of Contents")
    md.append("")
    if has_abstract:
        md.append("- [Abstract](abstract.md)")
    for relpath, title in section_entries:
        md.append(f"- [{title}]({relpath}.md)")
    if has_references:
        md.append("- [References](references.md)")
    if has_appendix:
        md.append("- [Appendix](appendix/appendix.md)")
    md.append("")

    md.append("```{toctree}")
    md.append(":maxdepth: 2")
    md.append(":hidden:")
    md.append("")
    if has_abstract:
        md.append("abstract")
    for relpath, _ in section_entries:
        md.append(relpath)
    if has_references:
        md.append("references")
    if has_appendix:
        md.append("appendix/appendix")
    md.append("```")

    content = "\n".join(md).rstrip() + "\n"
    return _write_file(out_dir / "index.md", content)


# ---------- Main ----------


def main() -> int:
    """Main entry point."""
    args = parse_args()
    meta_path = Path(args.meta_json).resolve()
    raw_path = Path(args.raw_txt).resolve()
    out_dir = Path(args.output_dir).resolve()
    cover_path = Path(args.cover).resolve() if args.cover else None

    if not raw_path.exists() or not meta_path.exists():
        print(
            f"[ERR] Missing prerequisite files: {raw_path} / {meta_path}",
            file=sys.stderr,
        )
        return 1

    # Load text
    pages = load_pages(raw_path)
    flat_lines = flatten_pages(pages)

    # Detect structure
    sections = detect_sections(flat_lines)
    if not sections:
        print("[WARN] No sections detected in document.", file=sys.stderr)

    meta = extract_paper_meta(flat_lines, sections)

    # Prepare output directory
    out_dir.mkdir(parents=True, exist_ok=True)
    sections_dir = out_dir / "sections"
    sections_dir.mkdir(parents=True, exist_ok=True)

    stats = {"files": 0, "chars": 0}

    # 1. Copy cover image
    has_cover = False
    if cover_path and cover_path.exists():
        img_dir = out_dir / "images"
        img_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(cover_path, img_dir / "cover.png")
        has_cover = True
        print(f"[OK] Cover copied -> {img_dir / 'cover.png'}")
    elif cover_path:
        print(f"[WARN] Cover image not found: {cover_path}")

    # 2. Categorize sections
    abstract_sec: Section | None = None
    references_sec: Section | None = None
    appendix_sec: Section | None = None
    body_sections: list[Section] = []

    for sec in sections:
        title_lower = sec.title.lower()
        if title_lower == "abstract":
            abstract_sec = sec
        elif title_lower in ("references", "bibliography"):
            references_sec = sec
        elif title_lower == "appendix":
            appendix_sec = sec
        else:
            body_sections.append(sec)

    # 3. Write abstract
    has_abstract = False
    if abstract_sec:
        chars = write_abstract(abstract_sec, out_dir)
        stats["files"] += 1
        stats["chars"] += chars
        has_abstract = True
        print(f"[OK] abstract.md ({chars} chars)")

    # 4. Write body sections
    section_entries: list[tuple[str, str]] = []
    seq = 1
    for sec in body_sections:
        relpath = write_section_file(sec, seq, sections_dir)
        display_title = f"{sec.number} {sec.title}" if sec.number else sec.title
        section_entries.append((relpath, display_title))
        stats["files"] += 1
        seq += 1
    print(f"[OK] {len(body_sections)} body sections written")

    # 5. Write references
    has_references = False
    if references_sec:
        chars = write_references(references_sec, out_dir)
        stats["files"] += 1
        stats["chars"] += chars
        has_references = True
        print(f"[OK] references.md ({chars} chars)")

    # 6. Write appendix
    has_appendix = False
    if appendix_sec:
        chars = write_appendix(appendix_sec, out_dir)
        stats["files"] += 1
        stats["chars"] += chars
        has_appendix = True
        print(f"[OK] appendix/appendix.md ({chars} chars)")

    # 7. Write index
    chars = write_index(
        meta, section_entries,
        has_abstract, has_references, has_appendix, has_cover,
        out_dir,
    )
    stats["files"] += 1
    stats["chars"] += chars
    print(f"[OK] index.md ({chars} chars)")

    # 8. Summary
    print()
    print("=" * 60)
    print("[DONE] Markdown conversion complete")
    print(f"  Total files: {stats['files']}")
    print(f"  Total chars: {stats['chars']:,}")
    print(f"  Body sections: {len(body_sections)}")
    print(f"  Abstract: {'yes' if has_abstract else 'no'}")
    print(f"  References: {'yes' if has_references else 'no'}")
    print(f"  Appendix: {'yes' if has_appendix else 'no'}")
    print(f"  Output dir: {out_dir}")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
