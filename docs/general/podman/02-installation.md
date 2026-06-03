---
title: 安装指南
description: Podman 在 Linux、macOS、Windows 全平台的安装方法、环境要求与验证步骤。
last_updated: 2026-06-03
---

# 02 · 安装指南

## Linux 安装

### Fedora / RHEL / CentOS Stream

```bash
# Fedora（已预装）
$ sudo dnf install -y podman

# RHEL 8+
$ sudo dnf module enable -y container-tools
$ sudo dnf install -y podman

# CentOS Stream 9
$ sudo dnf install -y podman
```

### Debian / Ubuntu

```bash
# Ubuntu 22.04+ / Debian 12+（官方仓库）
$ sudo apt-get update
$ sudo apt-get install -y podman

# Ubuntu 20.04（需添加 Kubic 仓库）
$ echo "deb https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/unstable/xUbuntu_20.04/ /" | \
    sudo tee /etc/apt/sources.list.d/podman.list
$ curl -fsSL https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/unstable/xUbuntu_20.04/Release.key | \
    sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/podman.gpg
$ sudo apt-get update
$ sudo apt-get install -y podman
```

### openSUSE

```bash
$ sudo zypper install -y podman
```

### Arch Linux

```bash
$ sudo pacman -S podman
```

### 从源码构建

```bash
$ git clone https://github.com/containers/podman.git
$ cd podman
$ make binaries
$ sudo make install
```

### Linux 环境要求

| 项目 | 最低要求 | 推荐 |
|------|---------|------|
| 内核 | 4.18+（user namespaces 支持） | 5.11+（cgroups v2 完整） |
| systemd | 230+（用户 lingering 支持） | 245+（cgroup delegate） |
| 网络 | slirp4netns 或 pasta | pasta（passt）`[v5.0+ 默认]` |
| 存储 | fuse-overlayfs（rootless） | kernel overlay（5.11+ rootless 原生） |
| cgroups | v1 可用 | v2（统一层级，推荐） |

### Rootless 前置配置

```bash
# 确认 subuid/subgid 已配置
$ grep $USER /etc/subuid
username:100000:65536

$ grep $USER /etc/subgid
username:100000:65536

# 如缺失，手动添加
$ sudo usermod --add-subuids 100000-165535 --add-subgids 100000-165535 $USER

# 启用用户 lingering（允许用户服务在注销后运行）
$ loginctl enable-linger $USER
```

---

## macOS 安装

Podman 在 macOS 上通过虚拟机运行 Linux 来提供容器能力。

### Homebrew 安装

```bash
$ brew install podman

# 初始化虚拟机
$ podman machine init

# 启动虚拟机
$ podman machine start
```

### 虚拟机配置选项

```bash
# 自定义资源
$ podman machine init \
    --cpus 4 \
    --memory 4096 \        # MB
    --disk-size 60 \       # GB
    --rootful              # 启用 root 模式（特殊需求时）

# 查看虚拟机状态
$ podman machine info
$ podman machine list
```

### Machine Provider 选择

| Provider | 平台 | 说明 |
|----------|------|------|
| **Apple Hypervisor** | Apple Silicon + Intel | 推荐，macOS 13+ 原生支持 |
| QEMU | Intel | 旧版兼容 |
| libkrun | Apple Silicon | 实验性，轻量 |

```bash
# 指定 provider（通常自动选择最优）
$ podman machine init --provider applehv
```

### macOS 环境要求

| 项目 | 要求 |
|------|------|
| 系统 | macOS 12 Monterey+（推荐 13+） |
| 芯片 | Apple Silicon (M1+) 或 Intel |
| 内存 | 最低 2GB 分配给 VM |
| 磁盘 | 最低 10GB VM 磁盘 |
| Homebrew | 最新版 |

---

## Windows 安装

Podman 在 Windows 上通过 WSL2 虚拟机运行。

### Winget 安装（推荐）

```powershell
# 安装 Podman
> winget install RedHat.Podman

# 初始化虚拟机
> podman machine init

# 启动虚拟机
> podman machine start
```

### MSI 安装包

从 [GitHub Releases](https://github.com/containers/podman/releases) 下载 `.msi` 安装包并执行。

### 虚拟机配置

```powershell
# 自定义配置
> podman machine init --cpus 4 --memory 4096 --disk-size 60

# 管理虚拟机
> podman machine list
> podman machine stop
> podman machine rm
```

### Windows 环境要求

| 项目 | 要求 |
|------|------|
| 系统 | Windows 10 版本 1903+ / Windows 11 |
| 虚拟化 | WSL2 已安装并启用 |
| 内存 | 最低 4GB（推荐 8GB+） |
| CPU | 支持虚拟化（VT-x/AMD-V） |
| 磁盘 | 最低 20GB 可用空间 |

### WSL2 前置配置

```powershell
# 确认 WSL2 已安装
> wsl --status

# 如未安装
> wsl --install

# 更新到最新内核
> wsl --update
```

---

## 安装验证

安装完成后，执行以下命令验证：

```bash
# 1. 检查版本
$ podman --version
podman version 5.8.x

# 2. 查看系统信息
$ podman info
host:
  arch: amd64
  os: linux
  cgroupVersion: v2
  ociRuntime:
    name: crun
    version: 1.x.x
  ...

# 3. 运行测试容器
$ podman run --rm docker.io/library/hello-world

Hello from Docker!
This message shows that your installation appears to be working correctly.
...

# 4. 验证 Rootless（Linux）
$ podman unshare cat /proc/self/uid_map
         0       1000          1
         1     100000      65536
```

### 常见验证问题

| 问题 | 原因 | 解决 |
|------|------|------|
| `ERRO[0000] cannot find UID/GID` | subuid/subgid 未配置 | 参见 Rootless 前置配置 |
| `machine not running` | VM 未启动（macOS/Windows） | `podman machine start` |
| 拉取镜像超时 | 网络/镜像源问题 | 配置 `registries.conf` 镜像加速 |
| `overlay not supported` | 内核不支持 rootless overlay | 安装 fuse-overlayfs |

---

## Podman Desktop 安装

[Podman Desktop](https://podman-desktop.io/) 是官方图形化管理工具，适合偏好 GUI 的用户。

### 安装方式

```bash
# macOS
$ brew install podman-desktop

# Windows
> winget install RedHat.Podman-Desktop

# Linux (Flatpak)
$ flatpak install flathub io.podman_desktop.PodmanDesktop
```

### 功能亮点

- 容器/Pod/镜像可视化管理
- 集成 Podman Machine 管理
- Kubernetes 上下文切换
- 扩展生态（Docker Compose、Kind、Lima 等）
- 内置终端

---

## 下一步

安装完成后，继续阅读 [03-核心概念](./03-core-concepts.md) 了解 Podman 的基础概念模型。
