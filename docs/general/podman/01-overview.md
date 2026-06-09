---
title: 项目概述与架构
description: Podman 的定位、版本演进、核心架构、关键组件与技术栈全景。
last_updated: 2026-06-03
---

# 01 · 项目概述与架构

## 项目定位

**Podman**（Pod Manager）是下一代开源容器引擎，由 Red Hat 主导开发，2018 年正式发布。其设计目标是提供完全兼容 Docker CLI 的容器管理体验，同时在架构层面实现三大核心差异化：

| 差异化要素 | 含义 |
|-----------|------|
| **Daemonless** | 无中心守护进程，每个容器作为独立进程运行，由调用者直接管理 |
| **Rootless** | 原生支持非 root 用户运行容器，无需特权提升 |
| **Kubernetes 原生** | 内置 Pod 概念，可直接生成/消费 K8s YAML |

项目仓库：`github.com/containers/podman`
许可证：Apache-2.0
主要语言：Go

---

## 版本演进时间线

| 版本 | 时间 | 里程碑 |
|------|------|--------|
| v0.x | 2017-2018 | 前身 kpod/libpod 实验阶段 |
| v1.0 | 2019-01 | 首个稳定版；容器/镜像基础管理 |
| v2.0 | 2020-06 | 引入 REST API；支持 podman-remote |
| v3.0 | 2021-02 | 网络栈迁移至 Netavark/Aardvark-dns；短名称别名 |
| v4.0 | 2022-02 | Quadlet 集成 systemd；podman machine 重构；`--sdnotify` |
| v4.5 | 2023-04 | 多架构 manifest 增强；farm build |
| v5.0 | 2024-03 | Pasta(passt) 默认网络；Hypervisor 框架统一；SQLite DB 默认 |
| v5.4 | 2024-12 | Quadlet `.build`/`.image` 支持；`podman compose` 内置 |
| v5.8 | 2025-Q4 | 增量镜像拉取；compose 完善；Windows ARM 预览 |

---

## 核心架构

```
┌──────────────────────────────────────────────────────────────────┐
│                        用户界面层                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────┐ │
│  │  podman CLI  │  │ REST API     │  │ Podman Desktop (GUI)   │ │
│  └──────┬───────┘  └──────┬───────┘  └───────────┬────────────┘ │
│         │                  │                      │              │
├─────────┴──────────────────┴──────────────────────┴──────────────┤
│                      libpod 核心引擎                              │
│  ┌────────────┐ ┌────────────┐ ┌──────────┐ ┌────────────────┐ │
│  │ Container  │ │   Image    │ │   Pod    │ │    Network     │ │
│  │  Manager   │ │  Manager   │ │ Manager  │ │   Manager      │ │
│  └─────┬──────┘ └─────┬──────┘ └────┬─────┘ └───────┬────────┘ │
├────────┴───────────────┴─────────────┴───────────────┴───────────┤
│                      基础设施层                                    │
│  ┌──────────────┐  ┌──────────────────┐  ┌────────────────────┐ │
│  │    conmon    │  │ containers/      │  │   Netavark /       │ │
│  │  (监控器)    │  │  storage + image │  │   Aardvark-dns    │ │
│  └──────┬───────┘  └────────┬─────────┘  └────────────────────┘ │
├─────────┴────────────────────┴───────────────────────────────────┤
│                      OCI 运行时层                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────────┐  │
│  │   crun   │  │   runc   │  │   kata   │  │   youki        │  │
│  │ (默认)   │  │          │  │(安全沙箱)│  │  (Rust实现)    │  │
│  └──────────┘  └──────────┘  └──────────┘  └────────────────┘  │
├──────────────────────────────────────────────────────────────────┤
│                      Linux 内核层                                  │
│  namespaces · cgroups v1/v2 · seccomp · SELinux/AppArmor         │
│  OverlayFS · FUSE · netfilter · veth                             │
└──────────────────────────────────────────────────────────────────┘
```

---

## 关键组件说明

### libpod

Podman 的核心库，负责容器和 Pod 的完整生命周期管理。提供 Go API 与 REST API 双接口。

- 容器创建、启动、停止、删除
- 资源限制（cgroups）配置
- 健康检查调度
- 状态持久化（BoltDB → SQLite）

### conmon（Container Monitor）

轻量级 C 语言监控进程，每个容器对应一个 conmon 实例：

- 持有容器 stdin/stdout/stderr 的文件描述符
- 实现 `--detach` 的关键——Podman 退出后 conmon 继续运行
- 监控容器退出状态并通知 systemd（如有）
- 日志写入（k8s-file / journald / json-file）

### containers/storage

统一的镜像/容器存储层管理库：

- 分层存储（Layer）：overlay、fuse-overlayfs、vfs、btrfs
- Copy-on-Write 语义
- Rootless 存储路径：`~/.local/share/containers/storage/`
- Root 存储路径：`/var/lib/containers/storage/`

### containers/image

镜像传输与格式转换库：

- 支持协议：docker://、oci:、dir:、docker-archive:、oci-archive:
- 签名验证（sigstore/GPG）
- 多架构 manifest list 处理

### containers/common

共享配置与工具库：

- `containers.conf`：全局行为配置
- `registries.conf`：仓库搜索/镜像/阻止列表
- `storage.conf`：存储驱动与路径配置
- `policy.json`：镜像信任策略

---

## 技术栈清单

| 领域 | 技术 |
|------|------|
| 主语言 | Go 1.21+ |
| 隔离 | Linux user/pid/net/mnt/uts/ipc namespaces |
| 资源控制 | cgroups v1 / v2（推荐 v2） |
| 容器规范 | OCI Runtime Spec 1.1 · OCI Image Spec 1.0 · OCI Distribution Spec |
| 网络 | Netavark（Rust） · Aardvark-dns · Pasta/passt · CNI（旧） |
| 存储 | OverlayFS · fuse-overlayfs（rootless）· VFS · Btrfs |
| 进程管理 | systemd · conmon · conmon-rs（Rust 重写，实验） |
| 安全 | seccomp · SELinux · AppArmor · Linux capabilities |
| 检查点/恢复 | CRIU（Checkpoint/Restore In Userspace） |
| 远程 | SSH 隧道 · REST over Unix socket · TCP（TLS） |
| 构建 | Buildah（共享代码库） |
| 桌面 | Podman Desktop（Electron + TypeScript） |

---

## 八大功能模块概览

### 1. 容器生命周期管理

创建、启动、停止、重启、暂停、恢复、删除、重命名。支持 `--restart` 策略与健康检查（`--health-cmd`）。

### 2. 镜像管理

拉取、推送、构建、标记、导入导出、签名验证。支持多架构构建（`podman manifest` / `podman farm build`）。

### 3. 网络管理

创建自定义网络、连接/断开容器、端口映射、DNS 解析。Netavark 为默认后端 `[v4.0+]`。

### 4. 存储管理

命名卷创建与挂载、绑定挂载、tmpfs、卷驱动插件、存储清理（`podman system prune`）。

### 5. Pod 管理

Pod 创建/启动/停止、容器分组、共享网络/PID 命名空间、infra 容器管理。

### 6. Quadlet / systemd 集成 `[v4.4+]`

声明式 `.container`/`.pod`/`.network`/`.volume` 单元文件，systemd generator 自动转换为 service 单元。

### 7. 健康检查

内置健康检查调度器，支持 `--health-cmd`、`--health-interval`、`--health-retries`、`--health-start-period`。

### 8. Kubernetes 集成

`podman kube generate` 导出 YAML、`podman kube play` 部署 YAML、ConfigMap/Secret 支持。

---

## Podman vs Docker 对比

| 维度 | Podman | Docker |
|------|--------|--------|
| 架构 | Daemonless，Fork/Exec 模型 | Client/Server，dockerd 守护进程 |
| 安全 | 原生 Rootless，无 SUID | 需 root 或 docker 组（rootless 为附加功能） |
| Pod | 一等公民，内置支持 | 不支持（需 Docker Compose 模拟） |
| systemd | 原生 Quadlet 集成 | 需手动编写 service 文件 |
| 资源占用 | 无常驻进程，空闲时零开销 | dockerd 常驻，基础内存 ~50MB |
| CLI 兼容 | `alias docker=podman` 即可替代 | — |
| Compose | `podman compose`（调用外部引擎） | `docker compose`（内置插件） |
| 构建 | 共享 Buildah 引擎 | BuildKit |
| 远程 | SSH 原生支持 | 需 TLS 配置或 context |
| K8s YAML | `kube generate/play` 内置 | 不支持 |

---

## 应用场景

1. **本地开发与测试**：替代 Docker Desktop，无需商业许可
2. **CI/CD 流水线**：Rootless 运行，无需特权容器
3. **边缘计算 / IoT**：轻量无守护进程，适合资源受限环境
4. **Kubernetes 本地预演**：Pod + kube play 模拟集群行为
5. **合规受限环境**：无 root 要求，满足安全合规
6. **systemd 服务容器化**：Quadlet 实现声明式容器服务管理
7. **多架构镜像构建**：farm build 跨平台构建流水线
8. **容器迁移/检查点**：CRIU 实现容器热迁移
