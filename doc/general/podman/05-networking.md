---
title: Podman 网络详解
description: 深入解析 Podman 网络架构，包括网络模式、Rootless 网络、DNS 服务发现、端口映射及多网络配置
---

# Podman 网络详解

## 网络架构概述

### Netavark vs CNI

Podman 4.0 起默认使用 **Netavark** 作为网络后端，取代了之前的 CNI（Container Network Interface）。

| 特性 | Netavark（v4.0+ 默认） | CNI（旧后端） |
|------|----------------------|-------------|
| 语言 | Rust | Go（多个插件） |
| 性能 | 更高（单进程） | 较低（多插件链） |
| DNS | 内置 aardvark-dns | 需额外 dnsname 插件 |
| IPv6 | 原生完整支持 | 部分支持 |
| 维护状态 | 活跃开发 | 仅维护模式 |
| 配置格式 | JSON | JSON（conflist） |
| 防火墙 | nftables/iptables | 仅 iptables |

### 网络栈选择建议

- **新安装**：使用 Netavark（默认，无需额外配置）
- **旧系统迁移**：升级到 Podman 4.0+ 后执行 `podman system reset` 切换
- **查看当前后端**：`podman info --format '{{.Host.NetworkBackend}}'`

---

## 网络模式详解

### Bridge（默认模式）

创建虚拟网桥，容器通过 NAT 与外部通信，同一网桥上的容器可直接互通。

```bash
# 创建自定义 bridge 网络
podman network create --subnet=10.89.0.0/24 --gateway=10.89.0.1 mynet

# 在自定义网络中运行容器
podman run -d --name web --net mynet nginx
podman run -d --name api --net mynet myapi

# 容器间可通过名称互通
podman exec api curl http://web:80
```

**特点：**
- 容器获得独立 IP，隔离性好
- 通过 NAT 访问外部网络
- 同网络容器通过内置 DNS 互发现
- 支持端口映射暴露服务

### Host（主机网络）

容器直接使用主机网络栈，无网络隔离，性能最佳。

```bash
# 使用主机网络
podman run -d --net host nginx

# 容器直接监听主机端口 80
curl http://localhost:80
```

**特点：**
- 无网络隔离，容器与主机共享所有网络接口
- 最高网络性能（无 NAT 开销）
- 无法使用端口映射（`-p` 无效）
- 适用于高性能网络应用

### Macvlan

容器获得独立 MAC 地址和 IP，直接接入物理网络，对外表现为独立主机。

```bash
# 创建 macvlan 网络
podman network create -d macvlan \
  --subnet=192.168.1.0/24 \
  --gateway=192.168.1.1 \
  -o parent=eth0 \
  macvlan-net

# 运行容器（获得物理网络 IP）
podman run -d --net macvlan-net --ip 192.168.1.100 nginx
```

**特点：**
- 容器拥有独立 MAC 和 IP
- 直接接入物理网络，无 NAT
- 外部设备可直接访问容器
- 限制：容器与主机之间默认不互通

### IPvlan

与 Macvlan 类似，但所有容器共享主机 MAC 地址，仅分配独立 IP。

```bash
# 创建 ipvlan 网络（L2 模式）
podman network create -d ipvlan \
  --subnet=192.168.1.0/24 \
  --gateway=192.168.1.1 \
  -o parent=eth0 \
  ipvlan-net
```

**特点：**
- 共享 MAC，独立 IP
- 适用于限制 MAC 数量的网络环境
- 支持 L2 和 L3 模式

### None（无网络）

容器无任何网络接口（除 loopback），完全网络隔离。

```bash
podman run --net none myapp
```

**适用场景：** 纯计算任务、安全敏感的离线处理。

### Container（共享网络命名空间）

容器共享另一个容器的网络命名空间，两者拥有相同的网络栈。

```bash
# 启动第一个容器
podman run -d --name web -p 8080:80 nginx

# 第二个容器共享 web 的网络
podman run -d --net container:web --name sidecar mymonitor
```

**适用场景：** Sidecar 模式、网络调试、服务网格代理。

---

## Rootless 网络

### Pasta（Podman 5.0+ 默认）

**pasta**（Pack A Subtle Tap Abstraction）是 Podman 5.0 引入的默认 rootless 网络方案。

```bash
# 使用 pasta（默认，无需额外配置）
podman run -d -p 8080:80 nginx

# 显式指定
podman run --network pasta nginx
```

**优势：**
- 高性能，接近 root 模式性能
- 低延迟端口映射
- 完整 IPv6 支持
- 支持 ICMP（ping）
- 无需额外进程

### Slirp4netns（旧方案）

```bash
# 显式使用 slirp4netns
podman run --network slirp4netns nginx

# 配置选项
podman run --network slirp4netns:port_handler=rootlesskit nginx
```

### 对比表

| 特性 | Pasta | Slirp4netns |
|------|-------|------------|
| 延迟 | 低（~0.1ms 额外开销） | 中（~0.5ms） |
| 吞吐量 | 接近主机性能 | 约主机 70% |
| IPv6 | 完整支持 | 有限支持 |
| ICMP | 支持 | 不支持 |
| 配置复杂度 | 低（自动） | 中 |
| 最低要求 | 内核 5.7+ | 内核 4.18+ |
| 资源占用 | 极低 | 低 |

---

## DNS 与服务发现

### 内置 DNS（aardvark-dns）

Netavark 网络后端配合 **aardvark-dns** 提供容器 DNS 解析，同一网络中的容器可通过名称互相访问。

```bash
# 创建网络
podman network create appnet

# 运行数据库
podman run -d --name postgres --net appnet postgres:16

# 运行应用（可通过 "postgres" 名称访问数据库）
podman run -d --name app --net appnet -e DB_HOST=postgres myapp
```

### 容器间名称互通

- 同一用户定义网络内的容器自动注册 DNS
- 默认 bridge 网络（`podman`）**不支持**名称解析
- 容器名和网络别名均可用于解析

```bash
# 使用网络别名
podman run -d --name db --net appnet --network-alias database postgres:16

# 通过别名访问
podman exec app ping database
```

### 自定义 DNS 配置

```bash
# 指定 DNS 服务器
podman run --dns 8.8.8.8 --dns 8.8.4.4 myapp

# 指定 DNS 搜索域
podman run --dns-search example.com myapp

# 添加 hosts 条目
podman run --add-host myhost:192.168.1.100 myapp
```

### 网络级 DNS 设置

```bash
# 创建网络时指定 DNS（Netavark）
podman network create --dns 8.8.8.8 mynet

# 禁用网络 DNS
podman network create --disable-dns mynet
```

---

## 端口映射

### 基础映射

```bash
# 单端口映射
podman run -d -p 8080:80 nginx

# 映射 TCP 和 UDP
podman run -d -p 8080:80/tcp -p 5353:53/udp myapp
```

### 范围映射

```bash
# 端口范围
podman run -d -p 8080-8090:80-90 myapp

# 等效于 8080→80, 8081→81, ... 8090→90
```

### 指定接口

```bash
# 仅监听 localhost
podman run -d -p 127.0.0.1:8080:80 nginx

# 指定网卡 IP
podman run -d -p 192.168.1.10:8080:80 nginx
```

### IPv6 映射

```bash
# IPv6 地址绑定
podman run -d -p '[::1]:8080:80' nginx

# 双栈监听
podman run -d -p 8080:80 -p '[::]:8080:80' nginx
```

### 随机端口

```bash
# 自动分配主机端口
podman run -d -p 80 nginx

# 查看分配的端口
podman port mycontainer
# 输出: 80/tcp -> 0.0.0.0:43210
```

### Rootless 端口限制

默认 rootless 模式无法绑定 1024 以下端口：

```bash
# 失败：权限不足
podman run -d -p 80:80 nginx

# 解决方案 1：使用高位端口
podman run -d -p 8080:80 nginx

# 解决方案 2：调整内核参数（需 root）
sudo sysctl net.ipv4.ip_unprivileged_port_start=80

# 解决方案 3：永久生效
echo "net.ipv4.ip_unprivileged_port_start=80" | sudo tee /etc/sysctl.d/podman-bindlow.conf
sudo sysctl --system
```

---

## 多网络容器

容器可同时连接多个网络，实现网络分段和跨网络通信。

```bash
# 创建多个网络
podman network create frontend --subnet 10.89.1.0/24
podman network create backend --subnet 10.89.2.0/24

# 容器连接多个网络
podman run -d --name gateway --net frontend --net backend nginx

# 仅连接前端网络的容器
podman run -d --name web --net frontend mywebapp

# 仅连接后端网络的容器
podman run -d --name db --net backend postgres

# gateway 可同时与 web 和 db 通信
# web 和 db 之间无法直接通信
```

### 动态连接网络

```bash
# 运行后连接额外网络
podman network connect backend web

# 断开网络
podman network disconnect frontend db
```

---

## IPv6 支持

```bash
# 创建 IPv6 网络
podman network create --ipv6 --subnet fd00::/64 mynet6

# 双栈网络（IPv4 + IPv6）
podman network create \
  --subnet 10.89.0.0/24 \
  --ipv6 --subnet fd00:dead:beef::/64 \
  dualstack

# 运行容器
podman run -d --net mynet6 nginx

# 验证 IPv6 连通
podman exec mycontainer ping6 fd00::1
```

### IPv6 端口映射

```bash
# 映射 IPv6 端口
podman run -d -p '[::]:8080:80' nginx

# 仅本地 IPv6
podman run -d -p '[::1]:8080:80' nginx
```
