#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# 文件功能概述
#
# 本文件是 Sphinx 文档构建系统的核心配置入口（conf.py）。
# 使用场景：
# 1) 本地开发：在 doc/ 目录下运行 `sphinx-build` 或 `make html` 时读取本配置，
#    用于控制扩展加载、主题外观、国际化、API 文档生成策略等。
# 2) CI / 文档托管平台：在 GitHub Actions、Read the Docs 等环境中构建文档时，
#    根据环境变量自动切换 baseurl、站点地图(sitemap)规则等。
#
# 重要说明：
# - 本文件只负责“配置”，不应引入与构建无关的重逻辑或副作用。
# - 若需兼容不同平台/环境，应优先通过环境变量或可选依赖探测来实现。
# -----------------------------------------------------------------------------
"""Sphinx configuration file for the 'tao' project documentation.

This file configures the Sphinx documentation generator for the tao project.
It sets up the project information, extensions, HTML theme, and various other
environment-specific configurations to produce high-quality documentation.
"""

# === Standard Library Imports ===
import os  # 提供环境变量读取、路径等系统功能
import sys  # 提供运行平台判断、模块搜索路径等能力
from pathlib import Path

# === Platform-Specific Configuration ===
if sys.platform == 'win32':
    # Windows 平台下的事件循环策略选择：
    # - 一些依赖/扩展在 ProactorEventLoop 下可能出现兼容性问题（例如子进程/IO 行为差异）
    # - WindowsSelectorEventLoopPolicy 更接近传统 selector 语义，兼容性更好
    import asyncio  # Windows 环境下按需导入，避免非 Windows 平台增加额外依赖
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  # 设置事件循环策略

# === Path Setup ===
def get_project_root():
    """获取项目根目录的绝对路径。

    约定：
    - 当前 conf.py 位于 doc/ 目录下；
    - 因此项目根目录一般为 doc 的上一级目录（parents[1]）。
    """
    return Path(__file__).resolve().parents[1]  # 以 conf.py 为锚点计算项目根目录

ROOT = get_project_root()  # 项目根目录绝对路径（用于派生 AutoAPI、扩展源码路径等）
try:
    # 优先从已安装的发行包元数据读取版本号（适用于已安装到环境的场景）
    from importlib.metadata import version as _pkg_version
    release = _pkg_version("taolib")  # 文档显示的发行版本号（Sphinx 内置变量 release）
except Exception:
    # 若未安装包（例如仅检出源码构建），则回退到环境变量或默认值
    release = os.environ.get("TAOLIB_VERSION", "0.0.0")  # 可通过 TAOLIB_VERSION 覆盖显示版本

# === 注入本地修复版 sphinx_tippy 扩展路径 ===
# 说明：为修复 Wikipedia 抓取告警，优先加载仓库内修复版扩展。
# 路径计算：从 tao 项目根(ROOT)回到 client，再进入 doc/tests/sphinx-tippy/src。
# 实现原理：
# - Sphinx 扩展以 Python 模块形式导入，导入优先级由 sys.path 决定；
# - 将“本地修复版扩展源码目录”插入 sys.path 头部，即可覆盖同名已安装包；
# - 仅当目录存在时启用，避免在缺少测试目录的环境（如发布包）报错。
TIPPY_LOCAL_SRC = ROOT.parent / "doc" / "tests" / "sphinx-tippy" / "src"  # 本地扩展源码目录
if TIPPY_LOCAL_SRC.exists():
    # 将本地扩展源码路径插入到 sys.path 前部，确保优先导入
    sys.path.insert(0, str(TIPPY_LOCAL_SRC))  # 修改模块搜索路径（只改变导入优先级，不改变功能）
# ================================= 项目基本信息 =================================
project = "tao"  # 项目名：用于标题、仓库链接拼接等（Sphinx 内置变量）
author = "xinetzone"  # 作者信息：用于文档元数据展示
copyright = '2021, xinetzone'  # 版权信息：用于文档页脚或元信息
# ================================= 国际化与本地化设置 ==============================
language = 'zh_CN'  # 文档语言：如 'zh_CN' / 'en' 等（影响内置文本与翻译选择）
locale_dirs = ['../locales/']  # gettext 翻译目录：相对 doc/ 的路径列表
gettext_compact = False  # PO 文件组织：False 表示按目录拆分，便于维护大型文档

# ================================= 扩展插件配置 =================================
import importlib.util as _ilut

def _has(mod: str) -> bool:
    """判断可选依赖（模块）是否可用。

    设计目的：
    - 文档构建环境可能精简，仅安装部分扩展；
    - 通过探测模块是否存在，动态决定 extensions 列表，避免 ImportError 中断构建。
    """
    try:
        return _ilut.find_spec(mod) is not None  # 能找到 spec 即表示模块可导入（通常已安装）
    except ModuleNotFoundError:
        # 当父包缺失或命名空间解析异常时，统一视为不可用
        return False

_exts = [
    # 内容格式与展示
    "mystx",  # 支持 Markdown/Notebook（可选主题/解析增强，存在则启用）
    "sphinx_design",  # 提供现代化 UI 组件（卡片、网格、按钮等）
    "sphinx.ext.napoleon",  # 解析 Google/NumPy 风格 docstring
    "sphinxcontrib.mermaid",  # 支持 Mermaid 图表渲染
    
    # 代码相关
    "sphinx.ext.viewcode",  # 在文档中展示源码并提供跳转
    'sphinx_copybutton',  # 为代码块提供“一键复制”按钮
    
    # 链接与引用
    "sphinx.ext.extlinks",  # 统一管理外部链接模板（缩短写法）
    "sphinx.ext.intersphinx",  # 关联其他项目文档，实现跨项目引用
    'sphinxcontrib.bibtex',  # BibTeX 引用支持
    "sphinx.ext.graphviz",  # Graphviz 支持（例如继承图、关系图等）
    
    # 交互功能
    "sphinx_comments",  # 文档评论系统（Hypothesis/Utterances 等）
    "sphinx_tippy",  # 悬停提示（Tooltip）增强
    "sphinx_thebe",  # Thebe：将代码块变为可执行单元（通常依赖 Binder/Jupyter）
    "nbsphinx",  # 直接渲染 .ipynb 到 Sphinx 文档
    
    # API文档与站点管理
    "autoapi.extension",  # 自动从源码生成 API 文档（可选）
    'sphinx_contributors',  # 贡献者信息展示（可选）
    "sphinx_sitemap",  # 生成 sitemap.xml，利于 SEO/站点收录
]
# extensions 是 Sphinx 的核心配置项：列出启用的扩展模块。
# 这里采用“可用即启用”的策略：环境安装了哪些扩展，就加载哪些，增强构建的可移植性。
extensions = [e for e in _exts if _has(e)]  # 过滤不可用扩展，避免构建报错

# ================================= 文档构建配置 =================================
# 排除文件和目录模式
exclude_patterns = [
    "_build",      # 构建输出目录
    "Thumbs.db",   # 缩略图数据库
    ".DS_Store",    # macOS 系统文件
    "**.ipynb_checkpoints",  # Jupyter 笔记本检查点目录
]

# 静态资源目录，用于存放CSS、JavaScript、图片等
html_static_path = ["_static"]  # 静态资源目录列表：相对 doc/ 的路径
html_css_files = ["local.css"]  # 额外加载的 CSS 文件：位于 html_static_path 下

# 文档的最后更新时间格式
html_last_updated_fmt = '%Y-%m-%d, %H:%M:%S'  # 页面“最后更新”时间显示格式

# ================================= 主题与外观配置 ================================
if _has('mystx'):
    html_theme = 'mystx'  # 优先使用 mystx 主题（若已安装）
elif _has('sphinx_book_theme'):
    html_theme = 'sphinx_book_theme'  # 次选 sphinx-book-theme（常用于书籍风格文档）
else:
    html_theme = 'alabaster'  # 兜底主题：Sphinx 内置轻量主题
html_title = "taolib"  # HTML 标题：显示在浏览器标签/页面顶部
html_logo = "_static/images/logo.jpg"  # Logo 路径：相对 doc/，通常位于 _static/
html_favicon = "_static/images/favicon.jpg"  # Favicon 路径：浏览器标签图标
html_copy_source = True  # 是否提供“查看源文件”入口（便于溯源与调试）

# ================================= thebe 交互式功能配置 =================================
# Thebe 说明：
# - 将代码块转为可交互执行（需要前端加载 thebe，并通常依赖 Binder/Jupyter 后端）
# - 若站点不提供执行环境，也可保持开启但不展示实际运行效果（取决于主题/前端配置）
use_thebe = True  # 是否开启 Thebe 功能：True/False
thebe_config = {
    "repository_url": f"https://github.com/xinetzone/{project}",  # 代码仓库地址：用于定位内容来源
    "repository_branch": "main",  # 仓库分支：通常为 main/master
    "selector": "div.highlight",  # 代码块选择器：匹配需要转为可执行的代码块容器
    # "selector": ".thebe",
    # "selector_input": "",
    # "selector_output": "",
    # "codemirror-theme": "blackboard",  # Doesn't currently work
    # "always_load": True,  # To load thebe on every page
}

# ================================= 版本切换器配置 =================================
version_switcher_json_url = "https://taolib.readthedocs.io/zh-cn/latest/_static/switcher.json"  # 版本切换数据源（JSON）

# === 交叉引用配置 ===
# 链接到其他项目的文档
intersphinx_mapping = {
    "python": ("https://docs.python.org/3.12", None),  # 映射名称 -> (对象库存放站点, inventory)
}

# 缩短外部链接
extlinks = {
    'daobook': ('https://daobook.github.io/%s', 'Daobook %s'),  # :daobook:`path` -> https://daobook.github.io/path
    'xinetzone': ('https://xinetzone.github.io/%s', 'xinetzone %s'),  # :xinetzone:`path` -> https://xinetzone.github.io/path
}

# === Copy Button 配置 ===
# 跳过Pygments生成的所有提示符
copybutton_exclude = '.linenos, .gp'  # 不显示复制按钮的元素选择器（行号、提示符等）
# 使用:not()排除复制按钮出现在笔记本单元格编号上
copybutton_selector = ":not(.prompt) > div.highlight pre"  # 复制按钮应用的代码块选择器

# === Comments Configuration ===
comments_config = {
    "hypothesis": True,  # 启用 Hypothesis 评论（需前端可访问其服务）
    # "dokieli": True,
    "utterances": {
        "repo": f"xinetzone/{project}",  # Utterances 绑定的 GitHub 仓库（issue 作为评论存储）
        "optional": "config",  # 可选配置：由 sphinx_comments 扩展解析
    }
}

# === Tippy Configuration ===
# 丰富的悬停提示设置
tippy_rtd_urls = [
    "https://docs.readthedocs.io/en/stable/",  # Read the Docs 文档：用于 tooltip 内容抓取/解析
    "https://www.sphinx-doc.org/zh-cn/master/",  # Sphinx 文档：用于 tooltip 内容抓取/解析
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
html_theme_options = {}  # 主题选项：由主题定义具体可用项，默认空 dict
try:
    # tomllib：Python 3.11+ 标准库。若运行在更低版本或解析失败，则忽略并使用默认值。
    import tomllib as _tomllib
    cfg_path = Path(__file__).parent / "_config.toml"  # doc/_config.toml：集中存放主题/站点个性化配置
    if cfg_path.exists():
        _cfg = _tomllib.loads(cfg_path.read_text('utf-8'))  # 读取并解析 TOML 文本
        html_theme_options = _cfg.get('html_theme_options', {})  # 从 TOML 中提取主题选项
except Exception:
    # 容错策略：配置解析失败不应阻塞文档构建（避免 CI 因非关键配置中断）
    pass

# === BibTeX Configuration ===
bibtex_bibfiles = ['refs.bib']  # BibTeX 数据文件列表：相对 doc/ 的路径

# === AutoAPI Configuration ===
autoapi_dirs = [str(ROOT / "src" / "taolib")]  # 扫描源码目录：用于提取 API 文档对象
autoapi_root = "api"  # AutoAPI 输出根目录：生成的 rst/页面会放在该子目录下
autoapi_generate_api_docs = True  # 是否自动生成 API 文档：False 表示仅配置而不自动生成

# === Graphviz Configuration ===
graphviz_output_format = "svg"  # Graphviz 输出格式：推荐 svg（清晰、可缩放）
# inheritance_graph_attrs = dict(
#     rankdir="LR",
#     fontsize=14,
#     ratio="compress",
# )

# === Mermaid Configuration ===
# 确保 Mermaid 图表在加载时初始化，并使用最大宽度
mermaid_init_js = """
// 自定义错误处理
mermaid.parseError = function(err, hash) {
    console.error('Mermaid rendering error:', err);
    // 可以在此处添加逻辑将错误显示在页面上，或者仅记录
    // 默认情况下 Mermaid 会显示语法错误
};

mermaid.initialize({
    startOnLoad: true,
    theme: 'default',
    securityLevel: 'loose',
    flowchart: { useMaxWidth: true, htmlLabels: true },
    gantt: { useMaxWidth: true },
    sequence: { useMaxWidth: true },
    journey: { useMaxWidth: true },
    er: { useMaxWidth: true },
    pie: { useMaxWidth: true },
    requirement: { useMaxWidth: true },
    gitGraph: { useMaxWidth: true },
});
"""

# === Sitemap Configuration ===
# sitemap 说明：
# - sphinx_sitemap 根据 html_baseurl 与 sitemap_url_scheme 生成 sitemap.xml；
# - url_scheme 支持格式化占位符，如 {lang}/{version}/{link} 等（由扩展定义）。
sitemap_url_scheme = "{lang}{version}{link}"  # 默认 URL 规则：包含语言与版本前缀（适合多语言/多版本站点）

if os.environ.get("GITHUB_ACTIONS"):
    # CI 环境：通常需要生成可公开访问的绝对 URL（用于 sitemap 及 canonical 链接）
    html_baseurl = os.environ.get("SITEMAP_URL_BASE", "https://xinetzone.github.io/")  # 站点根 URL
elif not os.environ.get("READTHEDOCS"):
    # 本地构建（且非 Read the Docs）：默认指向本地预览地址，且 URL 规则不加语言/版本前缀
    html_baseurl = os.environ.get("SITEMAP_URL_BASE", "http://127.0.0.1:8000/")  # 本地预览 baseurl
    sitemap_url_scheme = "{link}"  # 本地预览通常不带 {lang}/{version} 前缀，避免链接不匹配
else:
    # Read the Docs 环境：一般由 RTD 注入 baseurl/canonical 策略，此处保持默认或由环境覆盖
    pass

sitemap_locales = [None]  # sitemap 语言列表：None 表示使用当前 language 或不区分

# === Custom Sidebars ===
if _has('ablog'):
    # ablog 可选：若安装则启用博客侧边栏模板。未安装时不影响普通文档构建。
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
    ("py:class", "docutils.nodes.document"),  # 某些 docutils 内部对象不必强制可解析
    ("py:class", "docutils.parsers.rst.directives.body.Sidebar"),  # 侧边栏类型在严格模式下可忽略
]

suppress_warnings = [
    # myst-nb相关警告
    "mystnb.unknown_mime_type",  # 未知 mime 类型警告（常见于富输出）
    "mystnb.mime_priority",  # mime 优先级选择警告
    # myst相关警告
    "myst.xref_missing",  # MyST 交叉引用缺失警告
    "myst.domains",  # MyST 域解析相关警告
    # 其他常见警告
    "ref.ref",  # 引用解析相关的通用警告
    "autoapi.python_import_resolution",  # AutoAPI 解析导入路径的告警（部分环境可忽略）
    "autoapi.not_readable",  # AutoAPI 读取源码不可读告警（例如权限/编码问题）
    "tippy.wiki",  # Wikipedia 抓取失败告警（离线/内网环境常见）
]
nb_execution_mode = "cache"  # Notebook 执行模式：cache 表示缓存执行结果，提高增量构建速度
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
nb_execution_allow_errors = True  # Notebook 执行是否允许错误：True 表示遇到异常仍继续构建
nb_execution_excludepatterns = [
    "InsightHub/maple-mono/**",  # 排除执行的路径模式：避免耗时/不稳定内容影响构建
    "InsightHub/iFlow/**",  # 排除执行的路径模式：避免第三方/实验性内容影响构建
]

# 数字编号配置
numfig = True  # 是否为图、表、代码块等启用自动编号（True/False）

# MyST扩展配置
myst_enable_extensions = [
    "dollarmath",  # 支持 $...$ 行内数学
    "amsmath",  # 支持 AMS 数学环境
    "deflist",  # 支持定义列表语法
    # "html_admonition",
    # "html_image",
    "colon_fence",  # 支持 ::: 围栏（常用于提示块/自定义容器）
    # "smartquotes",
    "replacements",  # 支持文本替换（例如 (c) -> ©）
    # "linkify",
    "substitution",  # 支持替换语法（类似 RST substitution）
]

# === 构建严格模式（可选） ===
nitpicky = os.environ.get("SPHINX_NITPICK", "").lower() in {"1", "true", "yes"}  # 严格引用检查开关（环境变量控制）

# === 模板路径（如存在） ===
templates_path = ["_templates"]  # Jinja2 模板目录：用于覆盖/扩展主题模板
