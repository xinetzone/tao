#!/usr/bin/env python3
"""Check N×N cross-links between philosophy documents.

Scans docs/general/philosophy/ for all .md files (excluding index.md
and cultivation/ subdirectory), then verifies that each document's
"延伸阅读" section contains links to every other philosophy document.

Usage:
    python .agents/scripts/check-philosophy-links.py
"""

import re
import sys
from pathlib import Path


def find_project_root() -> Path:
    """Locate project root by searching upward for pyproject.toml."""
    current = Path(__file__).resolve().parent
    while current != current.parent:
        if (current / "pyproject.toml").exists():
            return current
        current = current.parent
    raise FileNotFoundError("Cannot find project root (pyproject.toml)")


def get_philosophy_docs(philosophy_dir: Path) -> dict[str, Path]:
    """Get all philosophy .md files, excluding index.md and cultivation/.

    Returns dict mapping filename stem to full path.
    """
    docs: dict[str, Path] = {}
    for md_file in sorted(philosophy_dir.rglob("*.md")):
        # Exclude index.md at any level
        if md_file.name == "index.md":
            continue
        # Exclude cultivation/ subdirectory
        rel_parts = md_file.relative_to(philosophy_dir).parts
        if "cultivation" in rel_parts:
            continue
        docs[md_file.stem] = md_file
    return docs


def extract_further_reading(content: str) -> str:
    """Extract the 延伸阅读 section from document content."""
    # Match ## N. 延伸阅读 or ## 延伸阅读
    match = re.search(r"^##\s+.*延伸阅读", content, re.MULTILINE)
    if not match:
        return ""
    return content[match.start() :]


def check_link_present(section: str, target_stem: str) -> bool:
    """Check if the section contains a link reference to target_stem.

    Matches patterns like:
        target.md, ../dir/target.md, dir/target, target)
    """
    pattern = re.escape(target_stem) + r"(?:\.md)?(?:\b|[/)\"\]])"
    return bool(re.search(pattern, section))


def main() -> None:
    project_root = find_project_root()
    philosophy_dir = project_root / "docs" / "general" / "philosophy"

    if not philosophy_dir.exists():
        print(f"Error: philosophy directory not found: {philosophy_dir}")
        sys.exit(1)

    docs = get_philosophy_docs(philosophy_dir)
    stems = sorted(docs.keys())

    if not stems:
        print("No philosophy documents found.")
        sys.exit(1)

    n = len(stems)
    missing_count = 0

    for source_stem in stems:
        source_path = docs[source_stem]
        content = source_path.read_text(encoding="utf-8")
        section = extract_further_reading(content)

        if not section:
            print(f"[{source_stem}] 缺少延伸阅读部分")
            missing_count += n - 1
            continue

        missing = []
        for target_stem in stems:
            if target_stem == source_stem:
                continue
            if not check_link_present(section, target_stem):
                missing.append(target_stem)

        if missing:
            print(f"[{source_stem}] 缺少指向: [{', '.join(missing)}]")
            missing_count += len(missing)

    if missing_count == 0:
        print(f"All {n}x{n} links verified")
    else:
        print(f"\n共 {missing_count} 个缺失链接")
        sys.exit(1)


if __name__ == "__main__":
    main()
