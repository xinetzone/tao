"""pdf-to-markdown 技能集成测试：通过 subprocess 端到端验证脚本流水线。"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def _run_extract(
    script: Path, pdf_path: Path, output_dir: Path
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(script),
            str(pdf_path),
            "--output-dir",
            str(output_dir),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def _run_convert(
    script: Path, meta_path: Path, raw_path: Path, md_output: Path
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(script),
            str(meta_path),
            str(raw_path),
            "--output-dir",
            str(md_output),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def test_extract_produces_meta_json(
    sample_pdf: Path, output_dir: Path, skill_scripts_dir: Path
) -> None:
    """运行 pdf_extract.py，验证输出包含 pdf_page_meta.json 且字段齐全。"""
    script = skill_scripts_dir / "pdf_extract.py"
    result = _run_extract(script, sample_pdf, output_dir)
    assert result.returncode == 0, f"Extract failed: {result.stderr}"

    meta_path = output_dir / "pdf_page_meta.json"
    assert meta_path.exists(), "pdf_page_meta.json should be produced"

    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    assert isinstance(meta, dict)
    assert meta.get("total_pages", 0) >= 1
    assert isinstance(meta.get("headings"), list)


def test_extract_produces_raw_text(
    sample_pdf: Path, output_dir: Path, skill_scripts_dir: Path
) -> None:
    """验证 pdf_raw_text.txt 非空。"""
    script = skill_scripts_dir / "pdf_extract.py"
    result = _run_extract(script, sample_pdf, output_dir)
    assert result.returncode == 0, f"Extract failed: {result.stderr}"

    raw_path = output_dir / "pdf_raw_text.txt"
    assert raw_path.exists(), "pdf_raw_text.txt should be produced"
    content = raw_path.read_text(encoding="utf-8")
    assert len(content) > 0, "raw text should not be empty"


def test_markdown_conversion(
    sample_meta_json: Path, sample_raw_text: Path, output_dir: Path, skill_scripts_dir: Path
) -> None:
    """运行 Markdown 转换流水线，验证输出目录至少包含一个 .md 文件。"""
    convert_script = skill_scripts_dir / "pdf_to_markdown.py"
    md_output = output_dir / "markdown"
    md_output.mkdir(exist_ok=True)

    result = _run_convert(convert_script, sample_meta_json, sample_raw_text, md_output)
    assert result.returncode == 0, f"Convert failed: {result.stderr}"

    md_files = list(md_output.rglob("*.md"))
    assert len(md_files) >= 1, "Should produce at least one .md file"


def test_no_crlf_in_output(
    sample_meta_json: Path, sample_raw_text: Path, output_dir: Path, skill_scripts_dir: Path
) -> None:
    """验证所有输出 Markdown 文件均不包含 CRLF 换行。"""
    convert_script = skill_scripts_dir / "pdf_to_markdown.py"
    md_output = output_dir / "markdown"
    md_output.mkdir(exist_ok=True)

    convert_result = _run_convert(convert_script, sample_meta_json, sample_raw_text, md_output)
    assert convert_result.returncode == 0, f"Convert failed: {convert_result.stderr}"

    for md_file in md_output.rglob("*.md"):
        raw_bytes = md_file.read_bytes()
        assert b"\r\n" not in raw_bytes, f"CRLF found in {md_file.name}"
