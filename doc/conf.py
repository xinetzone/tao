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

# === Local Imports ===
from utils.links import icon_links

# === Project Information ===
project = 'tao'  # 项目名称
author = 'xinetzone'  # 文档作者
copyright = '2021, xinetzone'  # 版权信息

# === Internationalization ===
language = 'zh_CN'
locale_dirs = ['../locales/']  # 翻译文件路径
gettext_compact = False  # 为每个翻译创建单独的.po文件

# === Core Configuration ===
# 扩展模块列表
extensions = [
    # 内容格式与展示
    "myst_nb",  # 支持Markdown和Jupyter笔记本
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
    
    # API文档与站点管理
    "autoapi.extension",  # 自动生成API文档
    'sphinx_contributors',  # 渲染GitHub仓库贡献者列表
    "sphinx_sitemap",  # 生成站点地图
    
    # 自定义扩展
    "_ext.rtd_version",  # 版本切换器下拉菜单
]

# 模板路径
templates_path = ['_templates']

# 排除文件模式
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# === Cross-Reference Configuration ===
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

# === Copy Button Configuration ===
# 跳过Pygments生成的所有提示符
copybutton_exclude = '.linenos, .gp'
# 使用:not()排除复制按钮出现在笔记本单元格编号上
copybutton_selector = ":not(.prompt) > div.highlight pre"

# === HTML Output Configuration ===
# HTML主题设置
html_theme = 'xyzstyle'  # 使用的主题名称
html_logo = "_static/images/logo.jpg"
html_title = "Sphinx xyzstyle Theme"
html_copy_source = True
html_favicon = "_static/images/favicon.jpg"
html_last_updated_fmt = '%Y-%m-%d, %H:%M:%S'  # 文档的最后更新时间格式

# 静态文件路径
html_static_path = ['_static']
html_css_files = ["css/custom.css", "css/tippy.css"]

# === Theme Options ===
html_theme_options = {
    # 界面功能
    "use_sidenotes": True,  # 启用侧边注释/页边注释
    "back_to_top_button": True,  # 显示"返回顶部"按钮
    
    # 仓库相关按钮
    "repository_url": f"https://github.com/xinetzone/{project}",
    "use_repository_button": True,  # 显示"在GitHub上查看"按钮
    "use_source_button": True,  # 显示"查看源代码"按钮
    "use_edit_page_button": True,  # 显示"编辑此页"按钮
    "use_issues_button": True,  # 显示"报告问题"按钮
    
    # 其他界面元素
    "announcement": "👋欢迎进入编程视界！👋",  # 公告横幅
    "icon_links": icon_links,  # 图标链接
    
    # 交互式功能
    "repository_branch": "main",
    "path_to_docs": "doc",
    "launch_buttons": {
        "binderhub_url": "https://mybinder.org",
        "colab_url": "https://colab.research.google.com/",
        "deepnote_url": "https://deepnote.com/",
        "notebook_interface": "jupyterlab",
        "thebe": True,
        # "jupyterhub_url": "https://datahub.berkeley.edu",  # For testing
    },
    
    # 版本切换器
    "primary_sidebar_end": ["version-switcher"],
}

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

# === Thebe Configuration ===
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

# === LaTeX 字体配置 ===
# 确保LaTeX能正确显示中文和特殊符号
latex_engine = 'xelatex'  # 使用xelatex引擎支持UTF-8
latex_elements = {
    'preamble': r"""
\usepackage{xeCJK}
\setCJKmainfont{Maple Mono NF CN}
\setCJKsansfont{WenQuanYi Micro Hei}
\setCJKmonofont{Maple Mono NF CN}
"""
}
