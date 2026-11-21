---
title: 安全特性
description: Podman 安全模型、SELinux策略、Capabilities管理、Seccomp配置、镜像签名与安全最佳实践
---

# 安全特性

## Rootless安全模型

### 用户命名空间（User Namespace）原理

Rootless Podman 利用 Linux User Namespace 将容器内的 root (UID 0) 映射为宿主机上的普通用户，实现无特权运行容器。容器内进程以为自己是 root，但在宿主机上实际以非特权 UID 运行。

### subuid/subgid 映射配置

```bash
# /etc/subuid
user1:100000:65536
# /etc/subgid
user1:100000:65536
```

- 格式：`用户名:起始UID:数量`
- 每个用户分配独立的 UID/GID 范围
- 容器内 UID 0 映射为宿主机上的起始 UID

### Rootless vs Root 安全边界对比

| 特性 | Rootless | Root |
|------|----------|------|
| 宿主机权限 | 普通用户 | root |
| 容器逃逸影响 | 仅限当前用户 | 完全接管宿主机 |
| 端口绑定 | >1024（或配置 net.ipv4.ip_unprivileged_port_start） | 任意端口 |
| 文件系统访问 | 受限于用户权限 | 无限制 |
| 网络模式 | slirp4netns / pasta | 完整 CNI/netavark |

### 攻击面分析

- **无daemon = 无SPOF**：每个容器独立进程，不存在单一故障点
- **无root = 最小权限**：即使容器被攻破，攻击者仅获得普通用户权限
- **无长驻进程**：减少攻击窗口，降低被利用的可能性

## SELinux容器策略

### 卷标签

- `:Z` 标签（专用）— 只有此容器可以访问卷内容
  ```bash
  podman run -v /data:/app:Z nginx
  ```
- `:z` 标签（共享）— 多个容器可以共享访问
  ```bash
  podman run -v /shared:/app:z nginx
  ```

### 容器SELinux类型

- `container_t`：容器进程运行的默认类型
- `container_file_t`：容器可访问文件的默认标签

### 特殊配置

- 禁用SELinux（不推荐）：`--security-opt label=disable`
- 自定义标签：`--security-opt label=type:my_container_t`

## Capabilities管理

### Podman默认capabilities

Podman 默认授予容器以下 14 个 capabilities：

- AUDIT_WRITE
- CHOWN
- DAC_OVERRIDE
- FOWNER
- FSETID
- KILL
- MKNOD
- NET_BIND_SERVICE
- NET_RAW
- SETFCAP
- SETGID
- SETPCAP
- SETUID
- SYS_CHROOT

### 最小权限实践

```bash
# 删除所有capabilities
podman run --cap-drop=ALL nginx

# 仅添加必需
podman run --cap-drop=ALL --cap-add=NET_BIND_SERVICE nginx
```

### 特殊capabilities说明

| Capability | 用途 | 风险 |
|-----------|------|------|
| SYS_ADMIN | 挂载文件系统、配置命名空间等 | 极高，几乎等同root |
| NET_ADMIN | 网络配置、防火墙规则等 | 高，可修改网络栈 |
| SYS_PTRACE | 调试进程、读取其他进程内存 | 高，可窥探其他容器 |

## Seccomp配置

### 默认seccomp profile位置

- 系统级：`/usr/share/containers/seccomp.json`
- 用户级：`~/.config/containers/seccomp.json`

### 自定义seccomp profile

```bash
podman run --security-opt seccomp=/path/to/profile.json nginx
```

### Profile结构

```json
{
  "defaultAction": "SCMP_ACT_ERRNO",
  "architectures": ["SCMP_ARCH_X86_64", "SCMP_ARCH_X86"],
  "syscalls": [
    {
      "names": ["read", "write", "open", "close"],
      "action": "SCMP_ACT_ALLOW"
    }
  ]
}
```

- `defaultAction`：未匹配系统调用的默认行为
- `syscalls`：允许或拒绝的系统调用列表
- `architectures`：适用的CPU架构

### 禁用seccomp（不推荐）

```bash
podman run --security-opt seccomp=unconfined nginx
```

## 只读容器

```bash
# 只读根文件系统
podman run --read-only nginx

# 只读 + tmpfs（可写临时目录）
podman run --read-only --tmpfs /tmp --tmpfs /run nginx

# no-new-privileges（防止提权）
podman run --security-opt no-new-privileges nginx
```

## 镜像签名与验证

### Policy.json 配置

```json
{
  "default": [{"type": "insecureAcceptAnything"}],
  "transports": {
    "docker": {
      "registry.example.com": [
        {"type": "sigstoreSigned", "keyPath": "/path/to/cosign.pub"}
      ]
    }
  }
}
```

### Cosign签名工作流

```bash
cosign generate-key-pair
cosign sign --key cosign.key registry/image:tag
cosign verify --key cosign.pub registry/image:tag
```

### 无密钥签名（Sigstore OIDC）

利用 Sigstore 的 Fulcio CA 和 Rekor 透明日志，通过 OIDC 身份验证实现无需管理密钥的签名：

```bash
cosign sign registry/image:tag  # 自动触发OIDC认证
```

## Registries安全配置

```toml
# /etc/containers/registries.conf
unqualified-search-registries = ["docker.io", "quay.io"]

[[registry]]
prefix = "docker.io"
location = "docker.io"

[[registry.mirror]]
location = "mirror.example.com"
insecure = false

# 阻止不安全的仓库
[[registry]]
prefix = "untrusted-registry.com"
blocked = true
```

## 安全最佳实践清单

1. 使用rootless模式
2. 删除所有capabilities，仅添加必需
3. 启用no-new-privileges
4. 使用只读根文件系统
5. 启用镜像签名验证
6. 配置seccomp profile
7. 使用SELinux标签保护卷
8. 定期扫描漏洞（Trivy/Grype）
9. 使用最小基础镜像（distroless/scratch）
10. 限制资源（cgroups）
