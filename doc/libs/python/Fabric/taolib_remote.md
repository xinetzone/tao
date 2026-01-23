# taolib.remote：可复用的远端执行与探测接口

文档版本：2026.01  
最后更新：2026-01-23  
模块：{py:mod}`taolib.remote`

`taolib.remote` 模块将 `Fabric + SSH` 的核心能力抽象为可复用、可测试的接口。它旨在解决项目中重复的 SSH 连接配置、环境上下文管理以及远端环境探测问题，并提供统一的异常处理机制。

```{note}
本文档采用 MyST Markdown 格式。避免使用 `file:///` 协议引用本地文件，而是推荐使用 Sphinx 交叉引用（如 `{py:func}`）以保持跨平台与跨环境的一致性。
```

## 核心特性

- **配置管理**：支持从 TOML 文件读取 SSH 配置，并提供脱敏与缓存机制。
- **环境探测**：标准化的远端环境检查流程（系统信息 -> Conda 环境 -> 业务命令）。
- **上下文管理**：提供 `remote_prefixes` 轻松管理多层 Shell 环境（如 `source ...` 或 `conda activate ...`）。
- **可测试性**：通过 `ConnectionFactory` 注入机制，支持在单元测试中替换真实的 SSH 连接。
- **异常归一化**：统一封装底层库（Fabric/Invoke）的异常，并处理 Windows 平台特有的中断信号问题。

## 安装与依赖

本模块依赖 `fabric` 进行实际的 SSH 连接。

- **运行时依赖**：`fabric`（可选）。只有在未注入自定义 `connection_factory` 且使用默认工厂时才会导入。
- **安装命令**：
  ```bash
  pip install fabric
  ```

## 快速开始

### 1. 准备配置文件

创建一个 TOML 配置文件（例如 `ssh.toml`）：

```toml
host = "example.com"
user = "alice"
port = 22

[connect_kwargs]
key_filename = "~/.ssh/id_rsa"
# 推荐使用密钥认证；如果必须使用密码，请勿提交到代码仓库
# password = "secret"
```

### 2. 使用 `probe_remote` 进行探测

这是最简单的使用方式，适合一次性任务。

```python
from pathlib import Path
from taolib.remote import load_ssh_config, probe_remote

# 1. 读取配置
config = load_ssh_config(Path("ssh.toml"))

# 2. 执行探测
# 默认流程：uname -> 检查 conda -> 执行 probe_cmd
report = probe_remote(config, probe_cmd="python --version")

# 3. 查看结果
print(f"远端系统: {report.uname}")
print(f"Conda 可用: {report.conda_available}")
if report.probe_attempted:
    print(f"命令执行成功: {report.probe_ok}")
```

## 核心组件与 API

### 1. SSH 配置管理 (`config`)

提供配置的加载、缓存与安全脱敏。

- **加载配置**：{py:func}`taolib.remote.load_ssh_config(path) <taolib.remote.config.load_ssh_config>`
  - 读取 TOML 文件并返回 `SshConfig` 字典。
  - 内部实现了 LRU 缓存，避免重复读取文件。
  - 返回值为深拷贝对象，修改它不会影响缓存。

- **配置脱敏**：{py:func}`taolib.remote.redact_ssh_config(config) <taolib.remote.config.redact_ssh_config>`
  - 将 `connect_kwargs.password` 替换为 `"***"`。
  - 适用于日志打印或错误报告场景。

- **清理缓存**：{py:func}`taolib.remote.clear_ssh_config_cache() <taolib.remote.config.clear_ssh_config_cache>`
  - 清空配置读取的内部缓存。

### 2. 远端探测器 (`RemoteProber`)

{py:class}`taolib.remote.RemoteProber` 是面向对象的探测执行器，推荐在复杂业务逻辑或需要复用配置的场景下使用。

#### 使用示例

```python
from taolib.remote import RemoteProber, RemoteProbeCommands, RemoteProbeRunOptions, load_ssh_config

# 定义命令集
commands = RemoteProbeCommands(
    tools_env_cmd="source /etc/profile",
    conda_activate_cmd="conda activate myenv",
    probe_cmd="python -c 'import torch; print(torch.__version__)'"
)

# 定义运行选项
options = RemoteProbeRunOptions(
    raise_on_conda_missing=True,  # 如果没有 conda 直接抛出异常
    run_kwargs={"timeout": 10}    # 设置 SSH 超时
)

# 实例化并执行
prober = RemoteProber(
    commands=commands, 
    options=options
)
config = load_ssh_config("ssh.toml")
report = prober.probe(config)
```

#### 数据模型

- **`RemoteProbeCommands`**：定义探测过程中使用的所有 Shell 命令。
  - `uname_cmd`: 获取系统信息（默认 `uname -a`）。
  - `check_conda_cmd`: 检查 Conda 是否存在（默认 `command -v conda`）。
  - `tools_env_cmd`: 基础环境初始化（如加载环境变量）。
  - `conda_activate_cmd`: Conda 环境激活命令。
  - `probe_cmd`: 核心业务探测命令。

- **`RemoteProbeRunOptions`**：定义执行行为。
  - `encoding`: 输出编码（默认 `utf-8`）。
  - `run_kwargs`: 传递给底层 `Connection.run` 的参数（如 `timeout`, `pty`）。
  - `raise_on_*`: 控制是否在探测失败时抛出异常。

- **`RemoteProbeReport`**：结构化的探测结果。
  - `uname`: 系统信息。
  - `conda_available`: 是否检测到 Conda。
  - `probe_attempted`: 是否尝试执行了业务命令。
  - `probe_ok`: 业务命令是否成功（退出码 0）。

### 3. 会话与上下文 (`session`)

Fabric 的 `Connection.run` 默认是无状态的。`taolib.remote` 提供了上下文管理器来模拟持久化的 Shell 环境。

- **`remote_prefixes`**：{py:func}`taolib.remote.remote_prefixes`
  - 在 `with` 块内的所有 `run` 调用都会自动附加指定的前缀命令（如 `source script.sh && ...`）。
  - 支持嵌套和多个前缀叠加。

下面是直接配合 Fabric 的 `Connection` 的示例（`ssh.toml` 按你的环境填写）。

```python
from fabric import Connection
from taolib.remote import load_ssh_config, remote_prefixes

ssh_config = load_ssh_config("ssh.toml")
conn = Connection(**ssh_config)

tools_env_cmd = "source /path/to/conda.sh"
conda_activate_cmd = "conda activate py310"

with remote_prefixes(conn, tools_env_cmd, conda_activate_cmd):
    conn.run("python -V")
```

### 4. 异常处理 (`errors`)

模块定义了统一的异常基类 {py:class}`taolib.remote.errors.RemoteError`，便于上层业务捕获。

- {py:class}`taolib.remote.RemoteDependencyError`：缺少 `fabric` 库。
- {py:class}`taolib.remote.RemoteConfigError`：配置文件解析失败或缺少关键字段。
- {py:class}`taolib.remote.RemoteExecutionError`：远端命令执行失败（当配置了 `raise_on_*` 时）。

## 环境变量配置

模块支持通过环境变量覆盖默认命令和编码设置，方便在 CI/CD 或容器环境中全局调整。

| 环境变量 | 对应的 Python 常量 | 默认值 |
| :--- | :--- | :--- |
| `TAOLIB_REMOTE_TOOLS_ENV_CMD` | `DEFAULT_TOOLS_ENV_CMD` | `:` (空操作) |
| `TAOLIB_REMOTE_CONDA_ACTIVATE_CMD` | `DEFAULT_CONDA_ACTIVATE_CMD` | `:` (空操作) |
| `TAOLIB_REMOTE_PROBE_CMD` | `DEFAULT_PROBE_CMD` | `python -V` |
| `TAOLIB_REMOTE_ENCODING` | `DEFAULT_ENCODING` | `utf-8` |

## 最佳实践与注意事项

1.  **Windows 平台的中断处理**
    - 在 Windows 上使用 `invoke`/`fabric` 时，`Ctrl+C` 有时会引发 `ValueError: I/O operation on closed file` 而不是标准的 `KeyboardInterrupt`。
    - `taolib.remote` 内部的执行器已通过 `run_remote_handling_interrupt` 自动处理了此情况，将异常归一化为 `KeyboardInterrupt`。

2.  **依赖注入与测试**
    - 在编写单元测试时，不要直接依赖真实的 SSH 连接。
    - 使用 `connection_factory` 参数注入一个模拟的 Connection 对象（需满足 `ConnectionLike` 协议）。

    ```python
    class MockConnection:
        def run(self, cmd, **kwargs):
            return MockResult(stdout="Linux", ok=True)
        # ... 实现其他必要方法
    
    # 测试时注入
    probe_remote(config, connection_factory=lambda **k: MockConnection())
    ```

3.  **安全性**
    - 始终使用 `redact_ssh_config` 对配置进行脱敏后再记录日志。
    - 生产环境建议通过密钥（Key-based）认证，避免在 TOML 中明文存储密码。

## 变更日志

### 2026.01 更新
- **重构**：引入 `RemoteProber` 类，提供更强的可配置性和扩展性。
- **新增**：`RemoteProbeCommands` 和 `RemoteProbeRunOptions` 数据类，规范化参数传递。
- **改进**：增加环境变量支持，允许通过 Env 覆盖默认命令。
- **兼容性**：保留 `probe_remote` 函数作为快捷接口，但内部已重构为使用 `RemoteProber`。
- **文档**：全面重写文档，移除过时描述，增加对新接口和最佳实践的说明。
