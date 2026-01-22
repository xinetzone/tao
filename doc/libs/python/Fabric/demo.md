# Fabric 示例

`````{tab-set} 
````{tab-item} remote.py
```python
"""Fabric 远程命令执行示例。

本模块演示如何通过 Fabric 的 :class:`fabric.Connection` 连接远端主机并执行命令。
示例采用“配置驱动”的方式：从同目录下的 ``ssh.toml`` 读取连接参数，建立 SSH 连接后
在远端执行 ``uname -a``（并可选执行 ``conda info``）。

配置文件 ``ssh.toml``（TOML 顶层键需与 Fabric 的 ``Connection`` 构造参数匹配）：

- host (str): 远端主机地址或域名。
- user (str): 登录用户名。
- port (int, optional): SSH 端口，默认 22。
- connect_kwargs (table, optional): Fabric/Paramiko 连接参数。
  常用字段：
  - password (str, optional): 密码认证。
  - key_filename (str, optional): 私钥路径（推荐优先使用密钥认证）。

注意：
    Fabric 的 ``Connection.run`` 通常会为每次执行创建独立的远端 shell 环境。
    如果需要在激活某个环境后再执行命令，请使用 :meth:`fabric.connection.Connection.prefix`
    或在同一次执行中串联命令，避免“激活不生效”。
"""

import tomllib
from pathlib import Path
from typing import Any

from fabric import Connection


def load_ssh_config(config_path: Path) -> dict[str, Any]:
    """从 TOML 文件读取 Fabric 的 SSH 连接配置。

    Args:
        config_path (Path): ``ssh.toml`` 文件路径。TOML 顶层键需与 Fabric 的
            :class:`fabric.Connection` 构造参数兼容（例如 ``host``、``user``、``port``、
            ``connect_kwargs``）。

    Returns:
        dict[str, Any]: 可直接用于 ``Connection(**ssh_config)`` 的配置字典。

    Raises:
        FileNotFoundError: 当 ``config_path`` 指向的文件不存在时抛出。
        OSError: 当文件无法读取（权限、I/O 错误等）时抛出。
        tomllib.TOMLDecodeError: 当 TOML 内容不合法时抛出。
    """
    with config_path.open("rb") as file_handle:
        return tomllib.load(file_handle)


def run_remote_probe(
    ssh_config: dict[str, Any],
    *,
    conda_activate_cmd: str = "source /media/pc/data/lxw/envs/anaconda3a/bin/activate py313",
) -> None:
    """连接远端并执行探测命令。

    该函数会先执行 ``uname -a`` 并打印输出；随后尝试激活指定 conda 环境，并在 conda
    可用时执行 ``conda info``。

    Args:
        ssh_config (dict[str, Any]): Fabric 的连接配置，通常由 :func:`load_ssh_config`
            读取获得。
        conda_activate_cmd (str): 远端用于激活 conda 环境的 shell 命令。
            该命令将作为 :meth:`fabric.connection.Connection.prefix` 的前缀应用，
            以确保激活对同一段命令执行生效。

    Returns:
        None

    Raises:
        fabric.exceptions.NetworkError: SSH 连接或网络异常时抛出。
        invoke.exceptions.UnexpectedExit: 当执行的远端命令返回非零退出码且未启用 ``warn`` 时抛出。
    """
    with Connection(**ssh_config) as connection:
        uname_result = connection.run("uname -a", hide=True)
        print(uname_result.stdout.strip())

        with connection.prefix(conda_activate_cmd):
            conda_exists = connection.run("command -v conda", warn=True, hide=True).ok
            if not conda_exists:
                print("remote: conda not found; skip `conda info`")
                return

            connection.run("conda info", warn=True)


def main() -> None:
    """脚本入口：加载配置并执行远端探测。"""
    config_path = Path(__file__).resolve().parent / "ssh.toml"
    ssh_config = load_ssh_config(config_path)
    run_remote_probe(ssh_config)


if __name__ == "__main__":
    main()

```
````
````{tab-item} ssh.toml
```toml
# SSH 连接配置（供 remote.py 读取并传给 Fabric Connection）
# 说明：建议优先使用密钥认证；如必须使用密码，请避免将明文密码提交到代码仓库。
host = "10.16.3.2" # 远端主机地址或域名
user = "ai"         # SSH 登录用户名
port = 22           # SSH 端口（默认 22）

[connect_kwargs]    # 传给底层 Paramiko 的连接参数（可选）
# 推荐：配置私钥路径（key_filename 指向私钥文件，而不是 known_hosts）
# key_filename = "C:/Users/<user>/.ssh/id_ed25519"
password = "123456"
```
````
`````