---
title: 核心概念
description: Podman 的基础概念模型——容器、镜像、Pod、卷、网络、Registry、Rootless、Daemonless 架构与 conmon 监控器。
last_updated: 2026-06-03
---

# 03 · 核心概念

## 容器（Container）

### 定义

容器是一个隔离的进程集合，共享主机内核但拥有独立的文件系统、网络栈、进程树和资源配额。Podman 容器完全遵循 **OCI Runtime Specification**。

### Fork/Exec 模型 vs Client/Server 模型

```
┌─ Docker 模型（Client/Server）─────────────────────┐
│                                                    │
│  docker CLI ──→ dockerd (守护进程) ──→ containerd  │
│                     ↓                              │
│               runc (容器进程)                       │
└────────────────────────────────────────────────────┘

┌─ Podman 模型（Fork/Exec）─────────────────────────┐
│                                                    │
│  podman CLI ──→ 直接 fork ──→ conmon ──→ OCI Runtime │
│       ↑                          ↓                 │
│       └── 退出后无残留 ←── 容器进程独立运行          │
└────────────────────────────────────────────────────┘
```

**关键区别：**

| 方面 | Docker | Podman |
|------|--------|--------|
| 进程模型 | 所有容器是 dockerd 的子进程 | 每个容器是独立进程树 |
| 单点故障 | dockerd 崩溃 → 所有容器受影响 | 无单点故障 |
| 权限 | dockerd 以 root 运行 | 调用者权限即容器权限 |
| 重启影响 | 升级 dockerd 需重启所有容器 | 升级 podman 不影响运行中容器 |

### 容器状态机

```
Created → Running → Paused → Running → Stopped → Removing → (deleted)
    ↓                                      ↑
    └──────────── Stopped ─────────────────┘
```

### 容器标识

- **ID**：64 字符 SHA256 哈希，通常用前 12 位即可唯一标识
- **Name**：人类可读名称，可自定义或自动生成

---

## 镜像（Image）

### OCI 镜像格式

Podman 使用 **OCI Image Specification** 定义的镜像格式，与 Docker 镜像完全兼容。

### 镜像层（Layer）

```
┌──────────────────────────────┐
│  Container Layer (R/W)       │  ← 容器写入层（Copy-on-Write）
├──────────────────────────────┤
│  Layer 4: COPY app/ .        │
├──────────────────────────────┤
│  Layer 3: RUN pip install    │
├──────────────────────────────┤
│  Layer 2: RUN apt-get        │
├──────────────────────────────┤
│  Layer 1: Base Image (Ubuntu)│
└──────────────────────────────┘
```

- 每层是只读的文件系统差异（diff）
- 层通过 Content-addressable 哈希标识，支持跨镜像共享
- 容器运行时在顶部添加可写层

### Containerfile / Dockerfile

```dockerfile
# Podman 同时支持 Containerfile 和 Dockerfile
FROM docker.io/library/python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

EXPOSE 8000
CMD ["python", "app.py"]
```

### 镜像标识

- **Tag**：`registry/repository:tag`（如 `docker.io/library/nginx:1.25`）
- **Digest**：`registry/repository@sha256:abcdef...`（不可变引用）

---

## Pod

### 定义

Pod 是 Podman 的一等公民概念，直接借鉴 Kubernetes Pod 语义：**一组共享特定 Linux 命名空间的容器集合**。

### Pod 结构

```
┌─────────────────── Pod "webapp" ────────────────────┐
│                                                      │
│  ┌──────────────┐                                   │
│  │ Infra Container │  ← 维持命名空间存活             │
│  │ (k8s.gcr.io/   │     持有网络配置                 │
│  │  pause:3.9)     │     端口映射绑定在此             │
│  └──────┬───────────┘                               │
│         │ 共享: net, uts, ipc [可选: pid]            │
│  ┌──────┴──────┐  ┌──────────────┐                  │
│  │   nginx     │  │   php-fpm    │                  │
│  │  :80 → Pod  │  │  :9000       │                  │
│  └─────────────┘  └──────────────┘                  │
│                                                      │
└──────────────────────────────────────────────────────┘
```

### 共享的命名空间

| 命名空间 | 默认共享 | 效果 |
|----------|---------|------|
| Network | 是 | Pod 内容器通过 localhost 互通 |
| UTS | 是 | 共享 hostname |
| IPC | 是 | 共享 System V IPC / POSIX 消息队列 |
| PID | 否 | 可选，启用后可 `ps` 看到所有容器进程 |
| Mount | 否 | 各容器独立文件系统 |
| User | 否 | 各容器独立 UID 映射 |

### Pod 基本操作

```bash
# 创建 Pod
$ podman pod create --name webapp -p 8080:80

# 向 Pod 添加容器
$ podman run -d --pod webapp --name web nginx:1.25
$ podman run -d --pod webapp --name app php:8.2-fpm

# Pod 内容器通过 localhost 通信
$ podman exec web curl localhost:9000
```

---

## 卷（Volume）

### 卷类型

| 类型 | 说明 | 生命周期 |
|------|------|---------|
| **命名卷** | Podman 管理的持久化存储 | 独立于容器，需手动删除 |
| **绑定挂载** | 主机目录直接映射到容器 | 与主机目录同步 |
| **tmpfs** | 内存文件系统 | 容器停止即消失 |
| **image 卷** | 从另一镜像挂载 `[v4.5+]` | 只读 |

### 使用示例

```bash
# 命名卷
$ podman volume create mydata
$ podman run -v mydata:/data alpine

# 绑定挂载
$ podman run -v /host/path:/container/path:Z alpine

# tmpfs
$ podman run --tmpfs /tmp:size=100m alpine

# 只读挂载
$ podman run -v mydata:/data:ro alpine
```

### SELinux 标签

在启用 SELinux 的系统上，绑定挂载需要标签选项：

- `:z`（小写）：共享标签，多容器可访问
- `:Z`（大写）：私有标签，仅当前容器可访问

---

## 网络（Network）

### 网络模式

| 模式 | 说明 | 适用场景 |
|------|------|---------|
| **bridge** | 默认，容器在虚拟网桥上 | 通用场景 |
| **host** | 容器直接使用主机网络栈 | 高性能网络 |
| **none** | 无网络连接 | 安全隔离 |
| **macvlan** | 容器拥有独立 MAC 地址 | 需要 L2 直连的场景 |
| **pasta** | Rootless 默认 `[v5.0+]` | Rootless 用户空间网络 |
| **slirp4netns** | 旧版 Rootless 网络 | 兼容旧系统 |

### 网络栈演进

```
v1.x-v3.x:  CNI (Container Network Interface) 插件
v4.0+:       Netavark (Rust 原生) + Aardvark-dns
v5.0+:       Pasta/passt 替代 slirp4netns 作为 rootless 默认
```

### 端口映射

```bash
# 基本映射
$ podman run -p 8080:80 nginx           # hostPort:containerPort

# 指定协议
$ podman run -p 8080:80/tcp nginx

# 指定绑定地址
$ podman run -p 127.0.0.1:8080:80 nginx

# 范围映射
$ podman run -p 8080-8090:80-90 nginx
```

---

## Registry（镜像仓库）

### 概念

Registry 是遵循 OCI Distribution Specification 的镜像分发服务。

### 常见 Registry

| Registry | 地址 | 说明 |
|----------|------|------|
| Docker Hub | docker.io | 最大公共仓库 |
| Red Hat Quay | quay.io | Red Hat 官方 |
| GitHub GHCR | ghcr.io | GitHub 容器仓库 |
| 私有 Registry | 自建 | Harbor、Zot、Distribution |

### 镜像引用格式

```
[transport://]registry/repository[:tag|@digest]

示例：
docker.io/library/nginx:1.25
quay.io/podman/hello:latest
localhost:5000/myapp@sha256:abc123...
```

### 短名称（Short Name）

Podman 支持短名称别名，避免歧义：

```bash
$ podman pull nginx
# 首次会提示选择 registry，选择后记录到
# ~/.cache/containers/short-name-aliases.conf
```

---

## Rootless 容器

### 原理

Rootless 允许非特权用户运行容器，利用 Linux **User Namespace** 实现权限映射。

### 权限映射

```
┌─── 主机视角 ──────────────────────────────────────┐
│  用户: alice (UID 1000)                           │
│  subuid 范围: 100000-165535                        │
└───────────────────────────────────────────────────┘
              ↓ User Namespace 映射
┌─── 容器视角 ──────────────────────────────────────┐
│  UID 0 (root in container) → 主机 UID 1000        │
│  UID 1-65535               → 主机 UID 100000-165535│
└───────────────────────────────────────────────────┘
```

### 关键文件

| 文件 | 作用 |
|------|------|
| `/etc/subuid` | 定义用户可用的 UID 从属范围 |
| `/etc/subgid` | 定义用户可用的 GID 从属范围 |
| `~/.config/containers/` | 用户级配置目录 |
| `~/.local/share/containers/` | 用户级存储目录 |

### Rootless 限制与解法

| 限制 | 原因 | 解法 |
|------|------|------|
| 不能绑定 <1024 端口 | 非特权限制 | `sysctl net.ipv4.ip_unprivileged_port_start=80` |
| Overlay 性能稍低 | fuse-overlayfs 用户态 | 内核 5.11+ 原生支持 rootless overlay |
| 无法使用 `--privileged` 完整能力 | User NS 限制 | 仅影响极少数场景 |
| 无法 ping（某些系统） | 需 `net.ipv4.ping_group_range` | 内核设置或 sysctl 配置 |

---

## Daemonless 架构

### 设计哲学

传统容器运行时采用守护进程架构（如 dockerd），Podman 彻底消除了这一层：

```
传统模型:
  用户 → CLI → 守护进程(常驻) → 运行时 → 容器

Podman 模型:
  用户 → CLI → 直接调用 → conmon → 运行时 → 容器
                  ↓
            CLI 退出，无残留
```

### 优势

1. **无单点故障**：没有守护进程崩溃导致全部容器不可用的风险
2. **零空闲开销**：不运行容器时不占用任何系统资源
3. **无缝升级**：升级 Podman 二进制不影响运行中的容器
4. **systemd 友好**：每个容器可以是独立的 systemd 服务
5. **审计清晰**：容器进程直接关联到调用用户

### 后台容器如何存活

```
$ podman run -d nginx

执行流程：
1. podman 进程 fork 出 conmon
2. conmon fork 出 OCI runtime (crun)
3. crun 创建容器进程后退出
4. conmon 持有容器 stdio FD，监控进程状态
5. podman 进程退出
6. 容器继续运行，conmon 继续监控
```

---

## conmon（Container Monitor）

### 角色

conmon 是用 C 语言编写的轻量级容器监控进程，是 Podman Daemonless 架构的关键组件。

### 职责

```
┌─────────────────────────────────────────┐
│               conmon                     │
├─────────────────────────────────────────┤
│  1. 持有容器的 stdin/stdout/stderr FD   │
│  2. 将容器日志写入文件/journald         │
│  3. 监控容器主进程退出码               │
│  4. 通知 systemd 容器就绪（sd_notify） │
│  5. 支持 exec 进入容器                 │
│  6. 处理 OOM 事件                       │
└─────────────────────────────────────────┘
```

### 生命周期

```
podman run
    │
    ├─ fork → conmon
    │            │
    │            ├─ fork → crun/runc → 创建容器
    │            │                      │
    │            │                      └─ 容器主进程 PID 1
    │            │
    │            └─ 进入监控循环
    │                  │
    └─ 退出            │
                       │
              容器运行中... conmon 持续监控
                       │
              容器退出 → conmon 记录退出码 → conmon 退出
```

### conmon-rs

`conmon-rs` 是 conmon 的 Rust 重写版本 `[实验性]`，提供：

- 更好的内存安全性
- 异步 I/O 支持
- 未来可能成为默认

---

## 概念关系图

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  Registry ──pull──→ Image ──create──→ Container         │
│                       │                    │            │
│                       │ layers             │ uses       │
│                       ↓                    ↓            │
│                    Storage              Volume          │
│                                            │            │
│                                            │            │
│  Pod ←─── groups ──── Container(s)         │            │
│   │                       │                │            │
│   │ shares                │ connects       │ mounts     │
│   ↓                       ↓                ↓            │
│  Network NS          Network            Host FS        │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 下一步

掌握核心概念后，继续阅读 [04-命令参考](./04-command-reference.md) 学习 Podman 的完整命令体系。
