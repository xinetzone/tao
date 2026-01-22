# taolib.remote：可复用的远端执行接口(暂不稳定)

文档版本：2026.01  
最后修改：2026-01-22  
模块：{py:mod}`taolib.remote`

本页将 `Fabric + SSH` 的常用能力抽象为可复用接口，便于在不同项目中复用，并保持可测试、可配置、可注入的设计。

```{note}
本文档避免使用 `file:///` 协议引用本地文件路径：该协议在不同文档站点/IDE/浏览器中的行为不一致，可能触发本地文件访问的安全限制，也会降低跨平台（Windows/Linux/macOS）与跨环境（CI、远程文档站点）的一致性。

同时，本文使用 MyST Markdown 的 Sphinx 交叉引用写法（如 {py:func}`taolib.remote.probe_remote`），避免直接链接到本地源码文件。
```

## 安装建议

- 运行时依赖：`fabric`（可选依赖，只有在未注入 `connection_factory` 时才会按需导入）
- 配置安全：避免在仓库中提交明文密码；推荐使用密钥认证（`connect_kwargs.key_filename`）

## 导出与模块

- 模块入口：{py:mod}`taolib.remote`
  - 常量：{py:data}`taolib.remote.DEFAULT_TOOLS_ENV_CMD`、{py:data}`taolib.remote.DEFAULT_CONDA_ACTIVATE_CMD`、{py:data}`taolib.remote.DEFAULT_PROBE_CMD`、{py:data}`taolib.remote.DEFAULT_ENCODING`
  - 异常：{py:class}`taolib.remote.errors.RemoteConfigError`、{py:class}`taolib.remote.errors.RemoteDependencyError`、{py:class}`taolib.remote.errors.RemoteExecutionError`
  - 类型/模型：{py:class}`taolib.remote.probe_models.RemoteProbeCommands`、{py:class}`taolib.remote.probe_models.RemoteProbeReport`、{py:class}`taolib.remote.probe_models.RemoteProbeRunOptions`、{py:class}`taolib.remote.probe_runner.RemoteProber`
  - 配置：{py:class}`taolib.remote.config.SshConfig`、{py:func}`taolib.remote.config.load_ssh_config`、{py:func}`taolib.remote.config.redact_ssh_config`、{py:func}`taolib.remote.config.clear_ssh_config_cache`
  - 接口：{py:func}`taolib.remote.probe_remote`、{py:func}`taolib.remote.session.remote_prefixes`

## 默认值与常量

- 默认命令与编码定义在 {py:mod}`taolib.remote.probe_models`
  - {py:data}`taolib.remote.probe_models.DEFAULT_TOOLS_ENV_CMD` = `":"`
  - {py:data}`taolib.remote.probe_models.DEFAULT_CONDA_ACTIVATE_CMD` = `":"`
  - {py:data}`taolib.remote.probe_models.DEFAULT_PROBE_CMD` = `"python -V"`
  - {py:data}`taolib.remote.probe_models.DEFAULT_ENCODING` = `"utf-8"`

## 类型与数据模型

- `SshConfig`（TypedDict, total=False）见 {py:class}`taolib.remote.config.SshConfig`
  - `host: str`、`user: str`、`port: int`、`connect_kwargs: dict[str, Any]`
- `RunResult` 协议见 {py:class}`taolib.remote.connection.RunResult`
  - `stdout: str`、`ok: bool`
- `ConnectionLike` 协议见 {py:class}`taolib.remote.connection.ConnectionLike`
  - `prefix(cmd) -> ContextManager`、`run(cmd, **kwargs) -> RunResult`
- `RemoteProbeReport`（dataclass, frozen, slots）见 {py:class}`taolib.remote.probe_models.RemoteProbeReport`
  - 字段：`uname: str`、`conda_available: bool`、`probe_attempted: bool`、`probe_ok: bool | None`
- `RemoteProbeCommands`（dataclass, frozen, slots）见 {py:class}`taolib.remote.probe_models.RemoteProbeCommands`
  - `tools_env_cmd`、`conda_activate_cmd`、`uname_cmd`、`check_conda_cmd`、`probe_cmd`
- `RemoteProbeRunOptions`（dataclass, frozen, slots）见 {py:class}`taolib.remote.probe_models.RemoteProbeRunOptions`
  - `encoding: str`、`run_kwargs: Mapping[str, Any] | None`、`raise_on_conda_missing: bool`、`raise_on_probe_failure: bool`
  - 方法：{py:meth}`taolib.remote.probe_models.RemoteProbeRunOptions.merged_run_kwargs`（将 `encoding` 合并到 `run_kwargs`）

## 配置读取与脱敏

- {py:func}`taolib.remote.config.load_ssh_config` -> `SshConfig`
  - 读取 TOML；内部 LRU 缓存；对外返回深拷贝，避免共享引用污染
  - 失败时抛 {py:class}`taolib.remote.errors.RemoteConfigError`（解析失败/读文件失败/非 table）
- {py:func}`taolib.remote.config.redact_ssh_config` -> `dict[str, Any]`
  - 原则：只将 `connect_kwargs.password` 替换为 `"***"`；其余结构保持不变；不修改入参对象
- {py:func}`taolib.remote.config.clear_ssh_config_cache` -> `None`
  - 清空底层 TOML 读取的 LRU 缓存

## 连接抽象与注入

- `ConnectionFactory = Callable[..., ConnectionLike]` 见 {py:data}`taolib.remote.connection.ConnectionFactory`
- {py:func}`taolib.remote.connection.fabric_connection_factory` -> `ConnectionFactory`
  - 按需导入 `fabric.Connection`；缺失时抛 `RemoteDependencyError`
- 通过 `probe_remote(..., connection_factory=...)` 注入自定义连接（便于单测/替换 Fabric）

## 会话前缀

- `remote_prefixes(connection: SupportsPrefix, *prefix_cmds: str) -> Iterator[None]`  
  见 {py:func}`taolib.remote.session.remote_prefixes`
  - 使用 ExitStack 顺序叠加多个 `prefix`；空字符串在 `strip` 后跳过
  - 作用域限定在 `with` 代码块期间的后续远端执行

## 探测接口与执行器

- 兼容层 {py:func}`taolib.remote.probe_remote` -> `RemoteProbeReport`
  - 参数同下方执行器；内部委托到 `probe_runner.probe_remote` 保持历史签名
- 执行器与流程见 {py:class}`taolib.remote.probe_runner.RemoteProber`
  - 校验：{py:func}`taolib.remote.probe_runner.validate_ssh_config_minimal` 要求 `host/user` 为非空字符串
  - 中断：{py:func}`taolib.remote.probe_runner.run_remote_handling_interrupt` 在 Windows 上把 `ValueError("...closed file...")` 统一映射为 `KeyboardInterrupt`
  - 方法：{py:meth}`taolib.remote.probe_runner.RemoteProber.probe` 流程：
    - 连接后执行 `uname_cmd`（`hide=True`），需 `ok=True` 且 `stdout` 非空，否则抛 `RemoteExecutionError`
    - 进入 `with remote_prefixes(tools_env_cmd, conda_activate_cmd)` 上下文
    - 检查 `conda`（`warn=True, hide=True`）：
      - 不可用且 `raise_on_conda_missing=True` 时抛 `RemoteExecutionError`
      - 否则返回 `RemoteProbeReport(uname, conda_available=False, probe_attempted=False, probe_ok=None)`
    - 执行 `probe_cmd`（`warn=True`）：
      - 若失败且 `raise_on_probe_failure=True` 时抛 `RemoteExecutionError`
      - 否则返回 `RemoteProbeReport(uname, conda_available=True, probe_attempted=True, probe_ok=bool(ok))`

## 异常模型

- {py:class}`taolib.remote.errors.RemoteError`（基类）
- {py:class}`taolib.remote.errors.RemoteDependencyError`（依赖缺失或不可用）
- {py:class}`taolib.remote.errors.RemoteConfigError`（配置读取/校验失败）
- {py:class}`taolib.remote.errors.RemoteExecutionError`（远端命令执行失败；可携带 `command`）

## 使用示例

### 快速开始

```python
from pathlib import Path
from taolib.remote import load_ssh_config, probe_remote

cfg = load_ssh_config(Path("ssh.toml"))
report = probe_remote(cfg, probe_cmd="python -V")
print(report.uname)           # 远端内核/系统信息
print(report.conda_available) # 是否检测到 conda
print(report.probe_attempted) # 是否实际执行 probe_cmd
print(report.probe_ok)        # 探测结果（可能为 None）
```

### 自定义运行参数与严格模式

```python
from taolib.remote import probe_remote, DEFAULT_PROBE_CMD
conda_activate_cmd = "source /media/pc/data/lxw/envs/anaconda3a/bin/activate py313"

report = probe_remote(
    {"host": "example.com", "user": "alice", "connect_kwargs": {"key_filename": "~/.ssh/id_rsa"}},
    probe_cmd=DEFAULT_PROBE_CMD,
    tools_env_cmd=":",
    conda_activate_cmd=conda_activate_cmd,
    run_kwargs={"hide": True, "warn": True, "timeout": 30},
    raise_on_conda_missing=True,
    raise_on_probe_failure=True,
)
```

### 使用前缀共享上下文

```python
from taolib.remote import remote_prefixes
# connection: 满足 ConnectionLike 协议的对象（如 fabric.Connection）
with remote_prefixes(connection, ":", ":"):
    res = connection.run("python -V", hide=True)
    assert res.ok
```

## 最佳实践

- 将环境准备命令放在 `tools_env_cmd/conda_activate_cmd` 中，并在 `probe_cmd` 中只保留业务命令
- 通过 `run_kwargs` 统一控制 `encoding/hide/warn/timeout` 等选项，避免在业务代码中散落参数
- 在测试中注入 `connection_factory`，以 FakeConnection 覆盖远端依赖，实现稳定单测
- 通过 `redact_ssh_config` 打印/记录配置时进行脱敏，避免泄露密码
- 需要刷新配置缓存时调用 `clear_ssh_config_cache`

## 已知限制与注意事项

- Fabric 的 `Connection.run` 通常不会在不同 `run` 之间共享远端 shell 状态；如需共享上下文，应使用 `remote_prefixes`（本质为每次 `run` 增加前缀）
- 本接口仅约束了最小的 Connection 协议（`prefix/run`），更复杂能力（上传/下载/pty/sudo 等）需按需扩展
- 在 Windows 上中断 `invoke/fabric` 的运行时，底层有时会抛出 `ValueError: I/O operation on closed file`；框架会将这类异常视作中断并统一转为 `KeyboardInterrupt` 重新抛出，便于调用方一致处理（见 `run_remote_handling_interrupt`）

## 配置示例（ssh.toml）

```toml
host = "example.com"
user = "alice"
port = 22
[connect_kwargs]
key_filename = "~/.ssh/id_rsa"
# password = "请勿提交到仓库，改用密钥或外部管理"
```

## 变更记录（与旧文档相比）

- 新增：执行器 {py:class}`taolib.remote.probe_runner.RemoteProber`；兼容层 {py:func}`taolib.remote.probe_remote` 保持旧签名
- 新增：异常模型与 {py:class}`taolib.remote.errors.RemoteExecutionError`
- 新增：连接协议 {py:class}`taolib.remote.connection.ConnectionLike` / {py:class}`taolib.remote.connection.RunResult` 与 {py:func}`taolib.remote.connection.fabric_connection_factory`
- 新增：{py:func}`taolib.remote.config.clear_ssh_config_cache`；完善 {py:func}`taolib.remote.config.redact_ssh_config` 的脱敏说明
