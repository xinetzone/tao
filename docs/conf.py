#!/usr/bin/env python3
# -----------------------------------------------------------------------------
# 文件功能概述
#
# 本文件是 Sphinx 文档构建系统的核心配置入口（conf.py）。
# 使用场景：
# 1) 本地开发：在 docs/ 目录下运行 `sphinx-build` 或 `make html` 时读取本配置，
#    用于控制扩展加载、主题外观、国际化、API 文档生成策略等。
# 2) CI / 文档托管平台：在 GitHub Actions、Read the Docs 等环境中构建文档时，
#    根据环境变量自动切换 baseurl、站点地图(sitemap)规则等。
#
# 重要说明：
# - 本文件只负责“配置”，不应引入与构建无关的重逻辑或副作用。
# - 若需兼容不同平台/环境，应优先通过环境变量或可选依赖探测来实现。
# -----------------------------------------------------------------------------
"""Sphinx configuration file for the 'AgentForge' project documentation.

This file configures the Sphinx documentation generator for the project.
It sets up the project information, extensions, HTML theme, and various other
environment-specific configurations to produce high-quality documentation.
"""

# === Standard Library Imports ===
import os
import sys
from pathlib import Path

# === Platform-Specific Configuration ===
if sys.platform == "win32":
    import asyncio
    asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy()
    )

# === Path Setup ===
def get_project_root():
    return Path(__file__).resolve().parents[1]

ROOT = get_project_root()

# ================================= 项目基本信息 =================================
project = "AgentForge"
author = "AI Dao"
copyright = "2026, AI Dao"
release = "0.1.0"

# ================================= 国际化与本地化设置 ==============================
language = "zh_CN"
locale_dirs = ["../locales/"]
gettext_compact = False

# ================================= 扩展插件配置 =================================
import importlib.util as _ilut

def _has(mod: str) -> bool:
    try:
        return _ilut.find_spec(mod) is not None
    except ModuleNotFoundError:
        return False

MYST_PARSER_ENABLED = _has("myst_parser")
MYSTX_ENABLED = _has("mystx") and _has("myst_nb")

core_exts = [
    "sphinx.ext.napoleon",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
]

optional_exts = [
    "myst_parser",
    "mystx",  # 支持 Markdown/Notebook（可选主题/解析增强，存在则启用）
    "sphinx_design",
    "sphinxcontrib.mermaid",
    "sphinx_copybutton",
    "sphinxcontrib.bibtex",
    "sphinx.ext.graphviz",
    "sphinx_sitemap",
]

extensions = core_exts.copy()
extensions.extend([e for e in optional_exts if _has(e)])

# 处理互斥扩展
if not MYSTX_ENABLED and "mystx" in extensions:
    extensions.remove("mystx")
if not MYST_PARSER_ENABLED and "myst_parser" in extensions:
    extensions.remove("myst_parser")
if MYSTX_ENABLED and "myst_parser" in extensions:
    extensions.remove("myst_parser")

# ================================= 文档构建配置 =================================
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    ".venv",
    "venv",
]

master_doc = "index"
source_suffix = {".rst": "restructuredtext"}

html_static_path = ["_static"]
html_css_files = []

html_last_updated_fmt = "%Y-%m-%d, %H:%M:%S"

# ================================= 主题与外观配置 ================================
if MYSTX_ENABLED:
    html_theme = "mystx"
elif _has("sphinx_book_theme"):
    html_theme = "sphinx_book_theme"
else:
    html_theme = "sphinx_rtd_theme"

html_title = "AgentForge"
html_copy_source = False

html_show_sourcelink = False
html_show_sphinx = False
html_show_copyright = True

html_compact_lists = True
html_compact_lists_gallery = True

# === 交叉引用配置 ===
intersphinx_mapping = {
    "python": ("https://docs.python.org/zh-cn/3.14/", None),
}

# === Copy Button 配置 ===
copybutton_exclude = ".linenos, .gp"
copybutton_selector = ":not(.prompt) > div.highlight pre"

# === 主题选项加载（从 _config.toml） ===
html_theme_options = {}
try:
    if sys.version_info >= (3, 11):
        import tomllib as _tomllib
    else:
        import tomli as _tomllib

    cfg_path = Path(__file__).parent / "_config.toml"
    if cfg_path.exists():
        _cfg = _tomllib.loads(cfg_path.read_text("utf-8"))
        html_theme_options = _cfg.get("html_theme_options", {})
except Exception:
    pass

# === BibTeX Configuration ===
bibtex_bibfiles = ["refs.bib"]

# === Sitemap Configuration ===
sitemap_url_scheme = "{lang}{version}{link}"

if os.environ.get("GITHUB_ACTIONS"):
    html_baseurl = os.environ.get("SITEMAP_URL_BASE", "https://ai-dao.github.io/")
elif not os.environ.get("READTHEDOCS"):
    html_baseurl = os.environ.get("SITEMAP_URL_BASE", "http://127.0.0.1:8000/")
    sitemap_url_scheme = "{link}"
else:
    pass

sitemap_locales = [None]

# === Additional Configuration ===
numfig = True

myst_enable_extensions = [
    "dollarmath",
    "amsmath",
    "deflist",
    "colon_fence",
    "replacements",
    "substitution",
]
myst_footnote_transition = False

templates_path = ["_templates"]
