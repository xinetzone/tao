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
sys.path.extend([str(ROOT/'doc')])
from taolib import get_version  # 引入获取版本号的函数
# ================================= 项目基本信息 =================================
project = "tao"  # 文档项目名称
author = "xinetzone"    # 文档作者
release = get_version("taolib")  # 获取taolib主题的版本号
copyright = '2021, xinetzone'  # 版权信息
# ================================= 国际化与本地化设置 ==============================
language = 'zh_CN'       # 文档语言（中文简体）
locale_dirs = ['../locales/']  # 翻译文件存放目录
gettext_compact = False  # 是否合并子目录的PO文件（False表示不合并）

# ================================= 扩展插件配置 =================================
extensions = [
    # 内容格式与展示
    "mystx",  # 支持Markdown和Jupyter笔记本
    "sphinx_design",  # 提供现代化UI组件
    "sphinx.ext.napoleon",  # 支持Google和NumPy风格的文档字符串
    "sphinxcontrib.mermaid",  # 支持Mermaid图表
    
    # 代码相关
    "sphinx.ext.viewcode",  # 添加到高亮源代码的链接
    'sphinx_copybutton',  # 为代码块添加复制按钮
    
    # 链接与引用
    "sphinx.ext.extlinks",  # 缩短外部链接
    "sphinx.ext.intersphinx",  # 链接到其他文档
    'sphinxcontrib.bibtex',  # 支持BibTeX参考文献
    "sphinx.ext.graphviz",  # 嵌入Graphviz图
    
    # 交互功能
    "sphinx_comments",  # 添加评论和注释功能
    "sphinx_tippy",  # 展示丰富的悬停提示
    "sphinx_thebe",  # 配置交互式启动按钮
    "nbsphinx",  # 支持Jupyter组件
    
    # API文档与站点管理
    "autoapi.extension",  # 自动生成API文档
    'sphinx_contributors',  # 渲染GitHub仓库贡献者列表
    "sphinx_sitemap",  # 生成站点地图
]

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

# 文档的最后更新时间格式
html_last_updated_fmt = '%Y-%m-%d, %H:%M:%S'

# ================================= 主题与外观配置 ================================
html_theme = 'mystx'            # 使用的主题名称
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
    "sphinx": ("https://daobook.github.io/sphinx/", None),
    "pst": ("https://daobook.github.io/pydata-sphinx-theme/", None),
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

# === BibTeX Configuration ===
bibtex_bibfiles = ['refs.bib']

# === AutoAPI Configuration ===
autoapi_dirs = [f"../src/{project}lib"]
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

# 环境特定的sitemap配置
if not os.environ.get("READTHEDOCS"):
    html_baseurl = os.environ.get("SITEMAP_URL_BASE", "http://127.0.0.1:8000/")
    sitemap_url_scheme = "{link}"
elif os.environ.get("GITHUB_ACTIONS"):
    html_baseurl = os.environ.get("SITEMAP_URL_BASE", "https://xinetzone.github.io/")

sitemap_locales = [None]  # 语言列表

# === Custom Sidebars ===
html_sidebars = {
    "reference/blog/*": [
        "navbar-logo.html",
        "search-field.html",
        "ablog/postcard.html",
        "ablog/recentposts.html",
        "ablog/tagcloud.html",
        "ablog/categories.html",
        "ablog/archives.html",
        "sbt-sidebar-nav.html",
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
