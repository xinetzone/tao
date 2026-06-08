# Podman In AgentForge

## Goal

说明 Podman 相关知识在 AgentForge 中的当前落点，帮助 agent 判断何时需要参考容器文档。

## Current Integration

### FlowKit 模块 (`src/taolib/flowkit/`)

Podman 容器管理能力已集成到 `taolib.flowkit` 包中，包含以下核心模块：

| 模块 | 路径 | 功能 |
|------|------|------|
| `ContainerRun` | `flowkit/podman_context.py` | 同步/异步上下文管理器，支持容器生命周期管理、多命令串行/并行执行 |
| `PodmanSSHClient` | `flowkit/podman_win.py` | Windows SSH 隧道适配器，自动建立 TCP 隧道连接 Podman VM |
| CLI 容器管理 | `flowkit/container.py` | 基于 `subprocess` 的 CLI 风格容器构建与运行 |

#### 关键 API

```python
from taolib.flowkit import ContainerRun, ContainerRunError, ExecResult
from pathlib import Path

# 同步上下文管理器
with ContainerRun(
    host_path=Path.cwd(),
    name="my-container",
    target="/workspace",
    working_dir="/workspace",
    image="python:3.14-slim",
) as cr:
    # 主命令默认为 sleep infinity 保活
    # 通过 exec() 在容器内执行命令
    result: ExecResult = cr.exec(["python", "--version"])

    # exec_many() 并行执行多个子命令
    results: list[ExecResult] = cr.exec_many([
        ["pip", "list"],
        ["python", "-c", "print(42)"],
    ])

    exit_code = cr.wait()  # 等待主命令结束

# 异步上下文管理器
async def main():
    async with ContainerRun(
        host_path=Path.cwd(),
        name="async-container",
        target="/workspace",
        working_dir="/workspace",
        image="python:3.14-slim",
    ) as cr:
        await cr.async_exec(["pip", "list"])
        await cr.async_exec_many([["cmd1"], ["cmd2"]])
        await cr.async_wait()
```

### 依赖配置

`pyproject.toml` 中 `flowkit` 可选依赖组包含：

- `nuitka>=0.19,<1` — Nuitka 编译配置
- `podman>=5.8.0` — Podman Python SDK

安装方式：`pip install taolib[flowkit]`

## Related References

- `../issue-patterns/podman-errors.md`
- `../references/podman/command-cheatsheet.md`
- `../references/podman/windows-setup.md`
- `../references/podman/podman-py-sdk.md`
- `../rules/containerization.md`
