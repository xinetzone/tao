# === Path setup ========================================================================
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.extend([str(ROOT/'doc')])
from utils.links import icon_links

# == Project 信息 ================================================================
project = 'tao' # 项目名称
author = 'xinetzone' # 文档的作者
copyright = '2021, xinetzone' # 版权信息

# == 国际化输出 ========================================================================
language = 'zh_CN'
locale_dirs = ['../locales/']  # po files will be created in this directory
gettext_compact = False  # optional: avoid file concatenation in sub directories.

# 通用配置
# =========================================================================================
# 表示 Sphinx 扩展的模块名称的字符串列表。它们可以是
# Sphinx 自带的插件（命名为 'sphinx.ext.*'）或您自定义的插件。
extensions = [
    "myst_nb",
    "sphinx_design",
]

# 在此添加包含模板的任何路径，相对于此目录。
templates_path = ['_templates']

# 相对于源目录的模式列表，用于匹配在查找源文件时要忽略的文件和目录。
# 此模式还会影响 html_static_path 和 html_extra_path。
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# == HTML 输出 ========================================================================
# 用于 HTML 和 HTML Help 页面的主题
html_theme = 'xyzstyle' # 使用的主题名称
html_logo = "_static/images/logo.jpg"
html_title = "Sphinx xyzstyle Theme"
html_copy_source = True
html_favicon = "_static/images/favicon.jpg"
html_last_updated_fmt = '%Y-%m-%d, %H:%M:%S' # 文档的最后更新时间格式
# 在此添加包含自定义静态文件（如样式表）的任何路径，相对于此目录。
# 它们会在内置静态文件之后被复制，因此名为 "default.css" 的文件将覆盖内置的 "default.css"。
html_static_path = ['_static']
html_css_files = ["custom.css"]


# == 主题选项 ================================================================
# 选项字典，影响所选主题的外观和感觉。这些选项是特定于主题的。内置主题所理解的选项在此处进行了描述。
html_theme_options = {
    "use_sidenotes": True,  # 启用侧边注释/页边注释。
    "repository_url": "https://github.com/xinetzone/tao",
    "use_repository_button": True,  # 显示“在 GitHub 上查看”按钮。
    "announcement": "👋欢迎进入编程视界！👋", # 公告横幅
    "use_source_button": True,  # 显示“查看源代码”按钮。
    "use_edit_page_button": True,  # 显示“编辑此页”按钮。
    "use_issues_button": True,  # 显示“报告问题”按钮。
    # 图标链接是一组图像和图标，每个图标都链接到一个页面或外部网站。
    # 如果你希望展示社交媒体图标、GitHub 徽章或项目标志，它们会很有帮助。
    "icon_links": icon_links,
}

# 配置用于交互的启动按钮
# 这些按钮将在页面底部显示，可用于启动笔记本或演示。
extensions.append("sphinx_thebe")
html_theme_options.update({
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
})

