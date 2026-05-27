"""taolib 的命令行入口集合。

本包以一个子模块为一个子命令，例如 :mod:`taolib.cli.github_app`
提供 ``taolib-github-app`` 命令，该命令由 :func:`taolib.cli.github_app.main` 驱动。
新增子命令时应保持“一文件 = 一命令 = 一主入口”的约定。
"""
