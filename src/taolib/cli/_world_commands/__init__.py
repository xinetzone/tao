"""World CLI 子命令包。

本包收录所有 ``world`` 命令的子命令处理模块。
每个子命令模块应导出：

- ``register_<name>_parser(subparsers)``：注册 argparse 子命令参数。
- ``handle_<name>(args) -> int``：执行子命令逻辑，返回退出码。
"""
