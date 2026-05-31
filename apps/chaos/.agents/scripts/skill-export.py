#!/usr/bin/env python3
"""Export AgentForge skills with platform-specific path variable adaptation.

AgentForge skills use ``{baseDir}`` as the path variable pointing to the
current skill directory. Different agent runtimes use different conventions:

- Claude Code: ``${CLAUDE_SKILL_DIR}``
- OpenAI Codex: original path is preserved (Codex injects absolute paths)
- Generic / default: keep ``{baseDir}`` untouched

This script reads a skill directory tree, rewrites textual files
(SKILL.md plus ``.md`` / ``.py`` / ``.sh`` and similar text resources)
to swap the path variable for the target platform, copies binary
resources verbatim, and writes the result into the output directory
preserving the original folder structure.

Usage:
    # Export a single skill
    python skill-export.py <skill-path> --platform claude --output-dir <dir>

    # Batch export every skill under .agents/skills/
    python skill-export.py --all --platform claude --output-dir <dir>

    # Show help
    python skill-export.py --help
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

# Path variable token used by AgentForge skills.
BASE_DIR_TOKEN = "{baseDir}"

# Supported export platforms and their replacement strings.
# A value of ``None`` means "do not rewrite, keep the original token".
PLATFORM_REPLACEMENTS: dict[str, str | None] = {
    "claude": "${CLAUDE_SKILL_DIR}",
    "codex": None,  # Codex auto-injects absolute paths; keep token as-is.
    "generic": None,  # Default: keep `{baseDir}` untouched.
}

# File suffixes that are treated as text and subject to token rewriting.
TEXT_SUFFIXES: frozenset[str] = frozenset(
    {
        ".md",
        ".py",
        ".sh",
        ".toml",
        ".json",
        ".yaml",
        ".yml",
        ".txt",
        ".cfg",
        ".ini",
        ".env",
    }
)

# Directory name conventions.
SKILLS_DIRNAME = "skills"
AGENTS_DIRNAME = ".agents"


def find_project_root() -> Path:
    """Locate project root by walking upward for ``pyproject.toml``."""
    current = Path(__file__).resolve().parent
    while current != current.parent:
        if (current / "pyproject.toml").exists():
            return current
        current = current.parent
    raise FileNotFoundError("Cannot find project root (pyproject.toml)")


def find_skills_root() -> Path:
    """Resolve the canonical ``.agents/skills/`` directory."""
    project_root = find_project_root()
    skills_root = project_root / AGENTS_DIRNAME / SKILLS_DIRNAME
    if not skills_root.is_dir():
        raise FileNotFoundError(f"Skills root not found: {skills_root}")
    return skills_root


def is_text_file(path: Path) -> bool:
    """Return True when ``path`` should be treated as a text resource.

    The decision uses the file suffix first; if the suffix is unknown
    we attempt to decode the first kilobyte as UTF-8 to avoid mangling
    binary blobs (images, archives, fonts, ...).
    """
    if path.suffix.lower() in TEXT_SUFFIXES:
        return True
    try:
        with path.open("rb") as fh:
            sample = fh.read(1024)
        if not sample:
            return True
        if b"\x00" in sample:
            return False
        sample.decode("utf-8")
        return True
    except OSError, UnicodeDecodeError:
        return False


def rewrite_text(content: str, replacement: str | None) -> str:
    """Rewrite ``{baseDir}`` occurrences according to ``replacement``."""
    if replacement is None:
        return content
    return content.replace(BASE_DIR_TOKEN, replacement)


def export_skill(skill_dir: Path, output_dir: Path, platform: str) -> int:
    """Export a single skill directory to ``output_dir/<skill-name>/``.

    Returns the number of files written.
    """
    if not skill_dir.is_dir():
        raise NotADirectoryError(f"Skill path is not a directory: {skill_dir}")

    if platform not in PLATFORM_REPLACEMENTS:
        raise ValueError(
            f"Unsupported platform: {platform!r}. "
            f"Choose one of: {sorted(PLATFORM_REPLACEMENTS)}"
        )

    replacement = PLATFORM_REPLACEMENTS[platform]
    target_root = output_dir / skill_dir.name
    target_root.mkdir(parents=True, exist_ok=True)

    written = 0
    for src in skill_dir.rglob("*"):
        rel = src.relative_to(skill_dir)
        dst = target_root / rel
        if src.is_dir():
            dst.mkdir(parents=True, exist_ok=True)
            continue

        dst.parent.mkdir(parents=True, exist_ok=True)
        if is_text_file(src):
            try:
                content = src.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                # Defensive fallback: copy verbatim if decode fails.
                shutil.copy2(src, dst)
                written += 1
                continue
            new_content = rewrite_text(content, replacement)
            dst.write_text(new_content, encoding="utf-8")
        else:
            shutil.copy2(src, dst)
        written += 1

    return written


def iter_skill_dirs(skills_root: Path) -> list[Path]:
    """Return every immediate skill directory under ``skills_root``.

    Hidden directories (starting with ``.``) are skipped because they
    typically hold validation configs rather than skills.
    """
    return sorted(
        p for p in skills_root.iterdir() if p.is_dir() and not p.name.startswith(".")
    )


def build_arg_parser() -> argparse.ArgumentParser:
    """Construct the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="skill-export.py",
        description=(
            "Export AgentForge skills with platform-specific path variable "
            "adaptation. Rewrites '{baseDir}' inside text files to the target "
            "platform's convention while preserving the original folder layout."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  # Export a single skill for Claude Code\n"
            "  python skill-export.py .agents/skills/zhihu-global-search "
            "--platform claude --output-dir dist/claude\n\n"
            "  # Batch export every skill (generic format)\n"
            "  python skill-export.py --all --platform generic "
            "--output-dir dist/skills\n"
        ),
    )
    parser.add_argument(
        "skill_path",
        nargs="?",
        help=("Path to a single skill directory to export. Omit when --all is used."),
    )
    parser.add_argument(
        "--all",
        dest="export_all",
        action="store_true",
        help="Export every skill under .agents/skills/.",
    )
    parser.add_argument(
        "--platform",
        choices=sorted(PLATFORM_REPLACEMENTS),
        default="generic",
        help=(
            "Target platform path variable convention. "
            "claude -> ${CLAUDE_SKILL_DIR}; codex -> keep original; "
            "generic -> keep '{baseDir}' (default)."
        ),
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Output directory; the skill folder is placed beneath it.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    if args.export_all and args.skill_path:
        parser.error("--all is mutually exclusive with a positional skill path")
    if not args.export_all and not args.skill_path:
        parser.error("provide a skill path or use --all")

    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.export_all:
        skills_root = find_skills_root()
        skill_dirs = iter_skill_dirs(skills_root)
        if not skill_dirs:
            print(f"No skills found under {skills_root}", file=sys.stderr)
            return 1
        total_files = 0
        for skill_dir in skill_dirs:
            count = export_skill(skill_dir, output_dir, args.platform)
            total_files += count
            print(f"[{args.platform}] exported {skill_dir.name} ({count} files)")
        print(f"Done: {len(skill_dirs)} skills, {total_files} files -> {output_dir}")
        return 0

    skill_dir = Path(args.skill_path).resolve()
    count = export_skill(skill_dir, output_dir, args.platform)
    print(
        f"[{args.platform}] exported {skill_dir.name} ({count} files) -> "
        f"{output_dir / skill_dir.name}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
