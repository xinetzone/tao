"""pytest 配置与共享 fixtures：动态生成含中文章节标题的测试 PDF。"""

from __future__ import annotations

from pathlib import Path

import pytest

SKILL_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = SKILL_DIR / "scripts"
SCHEMA_PATH = SKILL_DIR / "schemas" / "page-meta.schema.json"


def _detect_cjk_font() -> Path | None:
    """探测平台可用的中文 TTF/TTC 字体。"""
    candidates = [
        Path(r"C:\Windows\Fonts\simhei.ttf"),
        Path(r"C:\Windows\Fonts\simsun.ttc"),
        Path(r"C:\Windows\Fonts\msyh.ttc"),
        Path("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"),
        Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
        Path("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"),
        Path("/System/Library/Fonts/PingFang.ttc"),
        Path("/System/Library/Fonts/STHeiti Light.ttc"),
    ]
    for p in candidates:
        if p.exists():
            return p
    return None


@pytest.fixture
def skill_scripts_dir() -> Path:
    """返回技能脚本目录。"""
    return SCRIPTS_DIR


@pytest.fixture
def schema_path() -> Path:
    """返回 page-meta.schema.json 路径。"""
    return SCHEMA_PATH


@pytest.fixture
def output_dir(tmp_path: Path) -> Path:
    """返回临时输出目录。"""
    d = tmp_path / "output"
    d.mkdir()
    return d


@pytest.fixture
def sample_pdf(tmp_path: Path) -> Path:
    """使用 fpdf2 + 系统中文字体动态生成测试 PDF。

    生成的 PDF 满足 pdf_extract.py 中的正则要求：
      - 篇标题：``德经注读`` / ``道经注读``
      - 章节标题：``一、...（今38章）`` / ``二、...（今39章）`` / ``一、...（今1章）``
      - 同时包含德经和道经双篇，满足 pdf_to_markdown.py 的转换要求

    若运行环境缺少 fpdf2 或中文字体，则跳过测试。
    """
    try:
        from fpdf import FPDF  # type: ignore[import-not-found]
    except ImportError:
        pytest.skip("fpdf2 not installed")

    font_path = _detect_cjk_font()
    if font_path is None:
        pytest.skip("No CJK font available on this system")

    pdf = FPDF()
    pdf.add_font("CJK", "", str(font_path))

    # Page 1：德经篇标题 + 第一章
    pdf.add_page()
    pdf.set_font("CJK", size=16)
    pdf.cell(text="德经注读")
    pdf.ln(12)
    pdf.set_font("CJK", size=12)
    pdf.cell(text="一、道德是这样沦丧的（今38章）")
    pdf.ln(10)
    pdf.multi_cell(w=0, text="上德不德，是以有德。下德不失德，是以无德。")

    # Page 2：第二章（德经）
    pdf.add_page()
    pdf.set_font("CJK", size=12)
    pdf.cell(text="二、昔之得一者（今39章）")
    pdf.ln(10)
    pdf.multi_cell(w=0, text="昔之得一者：天得一以清，地得一以宁。")

    # Page 3：道经篇标题 + 第一章（道经）
    pdf.add_page()
    pdf.set_font("CJK", size=16)
    pdf.cell(text="道经注读")
    pdf.ln(12)
    pdf.set_font("CJK", size=12)
    pdf.cell(text="一、道可道（今1章）")
    pdf.ln(10)
    pdf.multi_cell(w=0, text="道可道，非恒道。名可名，非恒名。")

    out_path = tmp_path / "sample.pdf"
    pdf.output(str(out_path))
    return out_path
