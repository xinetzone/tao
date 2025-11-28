#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sphinx configuration file for the 'tao' project documentation.

This file configures the Sphinx documentation generator for the tao project.
It sets up the project information, extensions, HTML theme, and various other
environment-specific configurations to produce high-quality documentation.
"""

# === Standard Library Imports ===
import os
import sys
from pathlib import Path

# === Platform-Specific Configuration ===
if sys.platform == 'win32':
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# === Path Setup ===
def get_project_root():
    """获取项目根目录的绝对路径。"""
    return Path(__file__).resolve().parents[1]

ROOT = get_project_root()
try:
    from importlib.metadata import version as _pkg_version
    release = _pkg_version("taolib")
except Exception:
    release = os.environ.get("TAOLIB_VERSION", "0.0.0")

# === 注入本地修复版 sphinx_tippy 扩展路径 ===
# 说明：为修复 Wikipedia 抓取告警，优先加载仓库内修复版扩展。
# 路径计算：从 tao 项目根(ROOT)回到 client，再进入 doc/tests/sphinx-tippy/src。
TIPPY_LOCAL_SRC = ROOT.parent / "doc" / "tests" / "sphinx-tippy" / "src"
if TIPPY_LOCAL_SRC.exists():
    # 将本地扩展源码路径插入到 sys.path 前部，确保优先导入
    sys.path.insert(0, str(TIPPY_LOCAL_SRC))
# ================================= 项目基本信息 =================================
project = "tao"
author = "xinetzone"
copyright = '2021, xinetzone'  # 版权信息
# ================================= 国际化与本地化设置 ==============================
language = 'zh_CN'       # 文档语言（中文简体）
locale_dirs = ['../locales/']  # 翻译文件存放目录
gettext_compact = False  # 是否合并子目录的PO文件（False表示不合并）

# ================================= 扩展插件配置 =================================
import importlib.util as _ilut

def _has(mod: str) -> bool:
    return _ilut.find_spec(mod) is not None

_exts = [
    # 内容格式与展示
    "mystx",  # 支持Markdown和Jupyter笔记本
    "sphinx_design",  # 提供现代化UI组件
    "sphinx.ext.napoleon",  # 支持Google和NumPy风格的文档字符串
    "sphinxcontrib.mermaid",  # 支持Mermaid图表
    
    # 代码相关
    "sphinx.ext.viewcode",
    'sphinx_copybutton',
    
    # 链接与引用
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
    'sphinxcontrib.bibtex',
    "sphinx.ext.graphviz",
    
    # 交互功能
    "sphinx_comments",
    "sphinx_tippy",
    "sphinx_thebe",
    "nbsphinx",
    
    # API文档与站点管理
    "autoapi.extension",
    'sphinx_contributors',
    "sphinx_sitemap",
]
extensions = [e for e in _exts if _has(e)]

# ================================= 文档构建配置 =================================
# 排除文件和目录模式
exclude_patterns = [
    "_build",      # 构建输出目录
    "Thumbs.db",   # 缩略图数据库
    ".DS_Store",    # macOS 系统文件
    "**.ipynb_checkpoints",  # Jupyter 笔记本检查点目录
]

# 静态资源目录，用于存放CSS、JavaScript、图片等
html_static_path = ["_static"]
html_css_files = ["local.css"]

# 文档的最后更新时间格式
html_last_updated_fmt = '%Y-%m-%d, %H:%M:%S'

# ================================= 主题与外观配置 ================================
if _has('mystx'):
    html_theme = 'mystx'
elif _has('sphinx_book_theme'):
    html_theme = 'sphinx_book_theme'
else:
    html_theme = 'alabaster'
html_title = "taolib"  # 文档标题
html_logo = "_static/images/logo.jpg"  # 文档logo
html_favicon = "_static/images/favicon.jpg"  # 文档favicon
html_copy_source = True  # 是否在文档中包含源文件链接

# ================================= thebe 交互式功能配置 =================================
use_thebe = True  # 是否开启Thebe功能（默认关闭）
thebe_config = {
    "repository_url": f"https://github.com/xinetzone/{project}",
    "repository_branch": "main",
    "selector": "div.highlight",
    # "selector": ".thebe",
    # "selector_input": "",
    # "selector_output": "",
    # "codemirror-theme": "blackboard",  # Doesn't currently work
    # "always_load": True,  # To load thebe on every page
}

# ================================= 版本切换器配置 =================================
version_switcher_json_url = "https://taolib.readthedocs.io/zh-cn/latest/_static/switcher.json"

# === 交叉引用配置 ===
# 链接到其他项目的文档
intersphinx_mapping = {
    "python": ("https://docs.python.org/3.12", None),
}

# 缩短外部链接
extlinks = {
    'daobook': ('https://daobook.github.io/%s', 'Daobook %s'),
    'xinetzone': ('https://xinetzone.github.io/%s', 'xinetzone %s'),
}

# === Copy Button 配置 ===
# 跳过Pygments生成的所有提示符
copybutton_exclude = '.linenos, .gp'
# 使用:not()排除复制按钮出现在笔记本单元格编号上
copybutton_selector = ":not(.prompt) > div.highlight pre"

# === Comments Configuration ===
comments_config = {
    "hypothesis": True,
    # "dokieli": True,
    "utterances": {
        "repo": f"xinetzone/{project}",
        "optional": "config",
    }
}

# === Tippy Configuration ===
# 丰富的悬停提示设置
tippy_rtd_urls = [
    "https://docs.readthedocs.io/en/stable/",
    "https://www.sphinx-doc.org/zh-cn/master/",
]
# tippy_enable_mathjax = True
# tippy_anchor_parent_selector = "div.content"
# tippy_logo_svg = Path("tippy-logo.svg").read_text("utf8")
# tippy_custom_tips = {
#     "https://example.com": "<p>This is a custom tip for <a>example.com</a></p>",
#     "https://atomiks.github.io/tippyjs": (
#         f"{tippy_logo_svg}<p>Using Tippy.js, the complete tooltip, popover, dropdown, "
#         "and menu solution for the web, powered by Popper.</p>"
#     ),
# }

# === 主题选项加载（从 _config.toml） ===
html_theme_options = {}
try:
    import tomllib as _tomllib
    cfg_path = Path(__file__).parent / "_config.toml"
    if cfg_path.exists():
        _cfg = _tomllib.loads(cfg_path.read_text('utf-8'))
        html_theme_options = _cfg.get('html_theme_options', {})
except Exception:
    pass

# === BibTeX Configuration ===
bibtex_bibfiles = ['refs.bib']

# === AutoAPI Configuration ===
autoapi_dirs = [str(ROOT / "src" / "taolib")]
autoapi_root = "autoapi"
autoapi_generate_api_docs = False

# === Graphviz Configuration ===
graphviz_output_format = "svg"
inheritance_graph_attrs = dict(
    rankdir="LR",
    fontsize=14,
    ratio="compress",
)
# === Sitemap Configuration ===
sitemap_url_scheme = "{lang}{version}{link}"

if os.environ.get("GITHUB_ACTIONS"):
    html_baseurl = os.environ.get("SITEMAP_URL_BASE", "https://xinetzone.github.io/")
elif not os.environ.get("READTHEDOCS"):
    html_baseurl = os.environ.get("SITEMAP_URL_BASE", "http://127.0.0.1:8000/")
    sitemap_url_scheme = "{link}"

sitemap_locales = [None]  # 语言列表

# === Custom Sidebars ===
if _has('ablog'):
    extensions.append("ablog")
html_sidebars = {
    "blog/**": [
        "navbar-logo.html",
        "search-field.html",
        "ablog/postcard.html",
        "ablog/recentposts.html",
        "ablog/tagcloud.html",
        "ablog/categories.html",
        "ablog/authors.html",
        "ablog/languages.html",
        "ablog/locations.html",
        "ablog/archives.html",
    ]
}

# === Additional Configuration ===
# 忽略特定警告
nitpick_ignore = [
    ("py:class", "docutils.nodes.document"),
    ("py:class", "docutils.parsers.rst.directives.body.Sidebar"),
]

suppress_warnings = [
    # myst-nb相关警告
    "mystnb.unknown_mime_type", 
    "mystnb.mime_priority",
    # myst相关警告
    "myst.xref_missing", 
    "myst.domains",
    # 其他常见警告
    "ref.ref",
    "autoapi.python_import_resolution", 
    "autoapi.not_readable",
]
nb_execution_mode = "cache"
# nb_ipywidgets_js = {
#     # "https://cdnjs.cloudflare.com/ajax/libs/require.js/2.3.4/require.min.js": {
#     #     "integrity": "sha256-Ae2Vz/4ePdIu6ZyI/5ZGsYnb+m0JlOmKPjt6XZ9JJkA=",
#     #     "crossorigin": "anonymous",
#     # },
#     "https://cdn.jsdelivr.net/npm/@jupyter-widgets/html-manager@*/dist/embed-amd.js": {
#         "data-jupyter-widgets-cdn": "https://cdn.jsdelivr.net/npm/",
#         "crossorigin": "anonymous",
#     },
#     "https://cdn.jsdelivr.net/npm/anywidget@*/dist/index.js": {
#         "integrity": "sha256-1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
#         "crossorigin": "anonymous",
#     }
# }
# html_js_files = [
#     # "https://cdnjs.cloudflare.com/ajax/libs/require.js/2.3.4/require.min.js",
#     "https://cdn.jsdelivr.net/npm/anywidget@*/dist/index.js"
# ]
nb_execution_allow_errors = True
nb_execution_excludepatterns = [
    "InsightHub/maple-mono/**",
    "InsightHub/iFlow/**",
]

# 数字编号配置
numfig = True

# MyST扩展配置
myst_enable_extensions = [
    "dollarmath",
    "amsmath",
    "deflist",
    # "html_admonition",
    # "html_image",
    "colon_fence",
    # "smartquotes",
    "replacements",
    # "linkify",
    "substitution",
]

# === 构建严格模式（可选） ===
nitpicky = os.environ.get("SPHINX_NITPICK", "").lower() in {"1", "true", "yes"}

# === 模板路径（如存在） ===
templates_path = ["_templates"]
