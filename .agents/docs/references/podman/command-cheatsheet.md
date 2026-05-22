# Podman Command Cheatsheet

## Goal

为 agent 提供最常用的 Podman 命令入口，减少在排障时反复查找基础命令的成本。

## Relevance In AgentForge

- 关联模块：容器化工作流、开发环境脚本、后续可能引入的本地运行说明
- 常见触发场景：镜像构建失败、容器未启动、日志查看、挂载路径错误
- 优先检查文件：相关脚本、工作流配置、后续补充的集成说明页

## Common Commands

```bash
podman build -t my-image .
podman run --rm -it my-image
podman ps -a
podman logs <container>
podman exec -it <container> /bin/sh
podman rm -f <container>
podman image ls
```

## Common Problems

### 问题：容器存在但没有按预期启动

- 现象：`podman ps -a` 可以看到容器，但状态异常或快速退出。
- 原因：入口命令错误、环境变量缺失、挂载失败或权限不足。
- 排查步骤：先看 `podman logs`，再检查挂载参数和启动命令。
- 相关命令或代码位置：`podman logs <container>`、启动脚本或工作流文件。

## Sources

- 官方文档：待补充
- 版本：按本地或 CI 使用版本补充
- 抓取时间：待补充
