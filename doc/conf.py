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

# == HTML主题选项 ========================================================================
html_theme_options = {
    "repository_url": "https://github.com/xinetzone/xyzstyle",
    "use_repository_button": True,  # 显示“在 GitHub 上查看”按钮。
    "use_sidenotes": True,  # 启用侧边注释/页边注释。
}
