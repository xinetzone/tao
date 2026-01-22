# taolib.remote：可复用的远端执行接口

本页将 `Fabric + SSH` 的常用能力抽象为可复用接口，便于在不同项目中复用，并保持可测试、可配置、可注入的设计。

## 安装建议

- 运行时依赖：`fabric`（可选依赖，只有在未注入 `connection_factory` 时才会按需导入）
- 配置安全：避免在仓库中提交明文密码；推荐使用密钥认证（`connect_kwargs.key_filename`）

## 功能模块

- 配置读取：`taolib.remote.load_ssh_config`（带缓存；返回深拷贝避免污染缓存）
- 配置脱敏：`taolib.remote.redact_ssh_config`（避免日志/打印泄露密码；不修改入参）
- 上下文前缀：`taolib.remote.remote_prefixes`（叠加多个 prefix，确保在同一上下文生效）
- 探测流程：`taolib.remote.probe_remote`（uname -> conda 检查 -> 自定义探测命令）

## 快速开始

```python
from taolib.remote import load_ssh_config, probe_remote

cfg = load_ssh_config("ssh.toml")
report = probe_remote(cfg, probe_cmd="python -V")
print(report.uname)
print(report.probe_ok)
```

## 最佳实践

- 将环境准备命令放在 `tools_env_cmd/conda_activate_cmd` 中，并在 `probe_cmd` 中只保留业务命令
- 通过 `run_kwargs` 统一控制 `encoding/hide/warn/timeout` 等选项，避免在业务代码中散落参数
- 在测试中注入 `connection_factory`，以 FakeConnection 覆盖远端依赖，实现稳定单测

## 已知限制与注意事项

- Fabric 的 `Connection.run` 通常不会在不同 `run` 之间共享远端 shell 状态；如需共享上下文，应使用 `remote_prefixes`（本质为为每次 `run` 增加前缀）
- 本接口仅约束了最小的 Connection 协议（`prefix/run`），更复杂能力（上传/下载/pty/sudo 等）需按需扩展
- 在 Windows 上中断 `invoke/fabric` 的运行时，底层有时会抛出 `ValueError: I/O operation on closed file`；`probe_remote` 会将这类异常视作中断并转为 `KeyboardInterrupt` 重新抛出，便于调用方一致处理。
