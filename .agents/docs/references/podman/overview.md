# Podman Overview

## Search Keywords

- 主关键词：Podman
- 英文术语：daemonless container engine, rootless containers, Docker-compatible CLI, OCI runtime, Kubernetes YAML
- 常见别名：无守护进程容器引擎, Docker 替代方案, Red Hat Podman
- 错误短语：podman 和 docker 区别, podman daemonless, podman rootless, podman kube play, podman quadlet

## Goal

说明 Podman 的定位、核心价值、适用场景，以及它与 Docker 的主要差异。

## Relevance In AgentForge

- 关联模块：本地容器化开发、CI/CD 容器构建、后续容器运行脚本、Podman 集成说明。
- 常见触发场景：需要选择 Docker 或 Podman、排查 Podman 权限问题、为 systemd 管理容器服务、在本地复现 Kubernetes YAML。
- 优先检查文件：容器启动脚本、`Containerfile`、Podman 相关集成文档和排障文档。

## Trigger Phrases

- Podman 是什么，和 Docker 有什么区别？
- 为什么 Podman 不需要守护进程？
- Podman rootless 适合什么场景？
- Podman 能不能运行 Kubernetes YAML？
- 什么时候应该用 Quadlet？

## Key Concepts

- **Daemonless**：Podman 不依赖常驻守护进程，命令通常以 fork/exec 模型直接调用底层容器运行链路，降低单点故障和守护进程提权风险。
- **Rootless**：Podman 原生支持普通用户运行容器，常用于开发环境、CI 任务和安全要求较高的运行场景。
- **Docker-compatible CLI**：Podman 命令与 Docker 命令高度相似，常见 `run`、`build`、`ps`、`logs`、`exec`、`rm` 等命令迁移成本较低。
- **Pod**：Podman 原生支持 Kubernetes 风格的 Pod 概念，Pod 内容器可共享网络命名空间，便于本地模拟多容器组合。
- **Quadlet**：Podman 与 systemd 集成的声明式方式，可用 `.container`、`.pod`、`.kube`、`.network`、`.volume` 等文件描述容器服务。
- **OCI 兼容**：Podman 支持 OCI Runtime Spec 和 OCI Image Spec，可使用 `runc`、`crun` 等运行时。

## Core Capabilities

| 能力 | 说明 | 常用入口 |
|------|------|----------|
| 容器生命周期管理 | 创建、运行、停止、删除和检查容器 | `podman run`, `podman stop`, `podman rm`, `podman inspect` |
| 镜像管理 | 拉取、构建、推送、删除镜像 | `podman pull`, `podman build`, `podman push`, `podman rmi` |
| 网络管理 | 创建网络、端口映射、DNS 和隔离 | `podman network`, `-p`, `--network` |
| 存储管理 | 管理卷、绑定挂载和存储驱动 | `podman volume`, `-v`, `--mount` |
| Pod 管理 | 创建和运行容器组 | `podman pod create`, `podman pod start`, `podman pod ps` |
| Quadlet | 用 systemd 声明式管理容器服务 | `.container`, `.pod`, `.kube` |
| 健康检查 | 监控容器健康状态并配合重启策略 | `HEALTHCHECK`, `--health-*` |
| Kubernetes 集成 | 本地运行或生成 Kubernetes YAML | `podman kube play`, `podman generate kube` |

## Podman vs Docker

| 对比项 | Podman | Docker |
|--------|--------|--------|
| 架构模型 | Daemonless，偏 fork/exec 模型 | Client/Server，依赖 `dockerd` |
| Rootless | 原生支持，安全模型更靠前 | 支持但通常需要额外配置 |
| Pod | 原生支持 Kubernetes 风格 Pod | 不原生支持 Pod |
| systemd 集成 | 原生支持 Quadlet | 通常依赖额外脚本或工具 |
| 资源占用 | 无守护进程常驻开销 | 守护进程常驻，占用更高 |
| CLI 迁移 | 与 Docker 常用命令高度兼容 | Docker 原生命令 |

## Typical Use Cases

- 云原生开发和本地容器调试。
- CI/CD 流水线中的镜像构建与测试运行。
- Rootless 安全容器运行。
- Kubernetes YAML 本地验证。
- systemd 管理的长期运行容器服务。
- 边缘计算或资源受限环境中的轻量容器运行。

## Common Problems

### 问题：迁移 Docker 命令到 Podman 后行为不完全一致

- 现象：常见 Docker 命令可以运行，但网络、卷权限、Compose 或后台服务行为与 Docker 不同。
- 原因：Podman 架构不依赖守护进程，并且 rootless、网络后端、存储驱动和 Compose 支持方式与 Docker 有差异。
- 排查步骤：先判断差异是否来自 rootless 权限、网络后端、挂载标签或 systemd 管理方式，再查对应主题页。
- 相关命令或代码位置：`podman info`、`podman system connection list`、容器启动脚本。

### 问题：不知道该用 Pod、Compose、Quadlet 还是 Kubernetes YAML

- 现象：需要运行多容器应用，但不确定使用哪种组织方式。
- 原因：Podman 支持多种编排入口，适用场景不同。
- 排查步骤：本地短期组合优先看 `podman pod`；已有 Kubernetes YAML 优先用 `podman kube play`；系统服务化优先使用 Quadlet；兼容 Docker Compose 时再评估 `podman-compose` 或 Docker Compose provider。
- 相关命令或代码位置：`podman pod create`、`podman kube play`、Quadlet 单元文件。

## Sources

- 页面来源：<https://acntxq6xf8pe.aiforce.cloud/app/app_4jwk79sp6p8gg>
- 本地来源摘要：../../sources/podman/aiforce-podman-wiki.md
- 页面版本标识：v5.8.x
- 抓取时间：2026-05-23
