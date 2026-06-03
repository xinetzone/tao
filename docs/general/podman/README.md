---
title: Podman 完整参考资料库
description: 基于 Podman v5.8.x 的系统性技术参考，涵盖架构、安装、核心概念、命令、网络、存储、安全、Pod、Quadlet、高级主题、迁移与故障排除。
last_updated: 2026-06-03
---

# Podman 完整参考资料库

> 基于 **Podman v5.8.x** · 适用于开发者、DevOps 工程师与系统管理员

## 版本说明

本资料库基于 Podman **v5.8.x** 系列编写，同时标注了各版本引入的关键特性。内容覆盖 Linux（主平台）、macOS 及 Windows 三端使用场景。

## 适用人群

| 角色 | 推荐起点 |
|------|----------|
| 容器新手 | 01 → 02 → 03 → 04 |
| Docker 迁移用户 | 11 → 01 → 04 |
| DevOps / SRE | 09 → 05 → 06 → 07 → 13 |
| 安全工程师 | 07 → 03（Rootless）→ 10 |
| Kubernetes 用户 | 08 → 03（Pod）→ 09 |

## 目录结构

```
podman-reference/
├── README.md                    ← 总索引（本文件）
├── 01-overview.md              ← 项目概述与架构
├── 02-installation.md          ← 安装指南
├── 03-core-concepts.md         ← 核心概念
├── 04-command-reference.md     ← 命令参考
├── 05-networking.md            ← 网络详解
├── 06-storage.md               ← 存储管理
├── 07-security.md              ← 安全特性
├── 08-pod-kubernetes.md        ← Pod与K8s集成
├── 09-quadlet-systemd.md       ← Quadlet与systemd
├── 10-advanced-topics.md       ← 高级主题
├── 11-docker-migration.md      ← Docker迁移指南
├── 12-troubleshooting.md       ← 故障排除
└── 13-configuration.md         ← 配置文件参考
```

## 章节索引

### 基础篇

| # | 章节 | 说明 |
|---|------|------|
| 01 | [项目概述与架构](./01-overview.md) | 定位、演进时间线、核心架构图、组件说明、技术栈 |
| 02 | [安装指南](./02-installation.md) | Linux/macOS/Windows 全平台安装与验证 |
| 03 | [核心概念](./03-core-concepts.md) | 容器、镜像、Pod、卷、网络、Rootless、Daemonless |

### 使用篇

| # | 章节 | 说明 |
|---|------|------|
| 04 | [命令参考](./04-command-reference.md) | 全命令速查、常用工作流、选项详解 |
| 05 | [网络详解](./05-networking.md) | Bridge/Macvlan/Host、DNS、端口映射、Netavark |
| 06 | [存储管理](./06-storage.md) | 卷、绑定挂载、overlay/fuse-overlayfs、清理策略 |

### 进阶篇

| # | 章节 | 说明 |
|---|------|------|
| 07 | [安全特性](./07-security.md) | Rootless 深入、SELinux、Seccomp、Capabilities |
| 08 | [Pod 与 K8s 集成](./08-pod-kubernetes.md) | Pod 管理、YAML 生成、kube play、兼容性 |
| 09 | [Quadlet 与 systemd](./09-quadlet-systemd.md) | .container/.pod/.network 单元、自动启动、日志 |
| 10 | [高级主题](./10-advanced-topics.md) | 多架构构建、CRIU 检查点、远程连接、性能调优 |

### 运维篇

| # | 章节 | 说明 |
|---|------|------|
| 11 | [Docker 迁移指南](./11-docker-migration.md) | 兼容性矩阵、Compose 支持、常见差异与解法 |
| 12 | [故障排除](./12-troubleshooting.md) | 常见错误、诊断命令、日志分析、社区资源 |
| 13 | [配置文件参考](./13-configuration.md) | containers.conf、storage.conf、registries.conf |

## 快速导航

```
想运行第一个容器？        → 02-installation.md → "安装验证"
想理解 Rootless 原理？    → 03-core-concepts.md → "Rootless容器"
想从 Docker 迁移？        → 11-docker-migration.md
想用 systemd 管理容器？   → 09-quadlet-systemd.md
想排查网络问题？          → 12-troubleshooting.md → 05-networking.md
想了解完整命令列表？      → 04-command-reference.md
```

## 约定

- 命令示例以 `$` 前缀表示普通用户，`#` 前缀表示 root
- 版本标注格式：`[v4.0+]` 表示该特性从 v4.0 起可用
- 配置路径默认以 Linux 为准，其他平台差异会单独说明

```{toctree}
:maxdepth: 1
:caption: 章节目录

01-overview
02-installation
03-core-concepts
04-command-reference
05-networking
06-storage
07-security
08-pod-kubernetes
09-quadlet-systemd
10-advanced-topics
11-docker-migration
12-troubleshooting
13-configuration
podman-knowledge-base-extraction
podman-task-retrospective
```
