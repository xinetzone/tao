---
title: Podman 存储管理
description: 深入解析 Podman 存储驱动选型、storage.conf 配置、卷管理、镜像层缓存及性能优化策略
---

# Podman 存储管理

## 存储驱动

### Overlay（推荐）

**Overlay** 是 Podman 在 root 模式下的默认存储驱动，利用内核 OverlayFS 实现高效分层存储。

**原理：** 通过联合挂载将多个只读层（lower）与一个可写层（upper）叠加为统一视图。写操作采用 Copy-on-Write（CoW）策略。

**挂载选项：**

| 选项 | 说明 |
|------|------|
| `metacopy=on` | 仅复制文件元数据而非全部数据，显著加速 CoW |
| `volatile` | 跳过同步写入，提升性能（容器崩溃可能丢数据） |
| `nodev` | 禁止在挂载中创建设备文件 |

```bash
# 查看当前存储驱动
podman info --format '{{.Store.GraphDriverName}}'

# 验证 overlay 支持
cat /proc/filesystems | grep overlay
```

**适用场景：** Root 模式、现代内核（4.0+）、通用生产环境。

### Fuse-overlayfs

**Fuse-overlayfs** 是 rootless 模式的默认选择，在用户空间实现 OverlayFS 语义。

```bash
# 检查是否安装
which fuse-overlayfs

# 安装（Fedora/RHEL）
sudo dnf install fuse-overlayfs

# 安装（Ubuntu/Debian）
sudo apt install fuse-overlayfs
```

**特点：**
- 用户空间实现，无需内核 overlay 权限
- 性能低于内核 overlay（约 10-30% 开销）
- 支持 rootless 用户命名空间
- 需要 FUSE 设备（`/dev/fuse`）

**适用场景：** Rootless 环境（无内核 overlay 权限时）。

> **注意：** 内核 5.11+ 支持 rootless 原生 overlay（无需 fuse-overlayfs），Podman 会自动检测并使用。

### VFS

**VFS**（Virtual File System）是最简单的存储驱动，每层通过完整复制实现。

```bash
# 强制使用 VFS
podman --storage-driver vfs run nginx
```

**特点：**
- 无内核依赖，任何文件系统都支持
- 每层完整复制，磁盘消耗极大
- 性能最差（无 CoW 优化）
- 兼容性最好

**适用场景：** 无 overlay/fuse 支持的特殊环境、CI 容器嵌套、调试用途。

### Btrfs/ZFS

利用高级文件系统的原生快照和克隆特性。

**Btrfs：**
```bash
# 使用 btrfs 驱动（需 btrfs 文件系统）
# 在 storage.conf 中配置
# [storage]
# driver = "btrfs"
```

**ZFS：**
```bash
# 使用 zfs 驱动（需 ZFS 文件系统）
# [storage]
# driver = "zfs"
```

**特点：**
- 快照、克隆、压缩、去重
- 亚毫秒级快照创建
- 适合高密度容器部署
- 需要特定文件系统支持

**适用场景：** 高密度 PaaS 平台、需要快照管理的环境。

---

## storage.conf 配置

### 配置文件位置

| 路径 | 作用域 |
|------|--------|
| `/etc/containers/storage.conf` | 系统全局（root） |
| `~/.config/containers/storage.conf` | 用户级（rootless） |
| `/usr/share/containers/storage.conf` | 默认值（不建议修改） |

### 完整配置示例

```toml
[storage]
# 存储驱动选择
driver = "overlay"

# 镜像和容器层的存储位置（root 模式）
graphroot = "/var/lib/containers/storage"

# 运行时数据（lock文件等）
runroot = "/run/containers/storage"

# Rootless 用户的存储路径由 XDG 变量决定
# 默认: ~/.local/share/containers/storage

[storage.options]
# 用户可映射的 UID/GID 数量（rootless）
size = ""

# 附加镜像存储（只读，共享层）
additionalimagestores = [
  "/var/lib/shared-images"
]

[storage.options.overlay]
# overlay 挂载选项
mountopt = "nodev,metacopy=on"

# 容器可写层大小限制（需 quota 支持）
size = ""

# 强制使用 fuse-overlayfs（即使内核支持原生 overlay）
force_mask = ""

[storage.options.thinpool]
# devicemapper thinpool 配置（已不推荐）
# autoextend_percent = "20"
# autoextend_threshold = "80"
```

### Rootless 配置示例

```toml
[storage]
driver = "overlay"
graphroot = "/home/user/.local/share/containers/storage"
runroot = "/run/user/1000/containers"

[storage.options.overlay]
# 内核 5.11+ 可用原生 overlay
# mount_program = "/usr/bin/fuse-overlayfs"  # 旧内核需要
mountopt = "nodev,metacopy=on"
```

---

## 卷管理

### 命名卷

```bash
# 创建命名卷
podman volume create mydata

# 使用命名卷
podman run -d -v mydata:/app/data --name app myimage

# 查看卷信息
podman volume inspect mydata

# 卷数据位于
# Root: /var/lib/containers/storage/volumes/mydata/_data
# Rootless: ~/.local/share/containers/storage/volumes/mydata/_data
```

### 绑定挂载

```bash
# 基础绑定挂载
podman run -v /host/path:/container/path myimage

# 只读挂载
podman run -v /host/path:/container/path:ro myimage

# 带 SELinux 标签
podman run -v /host/path:/container/path:Z myimage
```

### tmpfs 挂载

```bash
# 基础 tmpfs
podman run --tmpfs /tmp myimage

# 限制大小
podman run --tmpfs /tmp:size=100m myimage

# 指定选项
podman run --tmpfs /tmp:size=100m,noexec,nosuid myimage
```

### SELinux 标签

在启用 SELinux 的系统上，绑定挂载需要正确的安全标签：

| 标签 | 说明 | 使用场景 |
|------|------|---------|
| `:Z` | 专用标签（`container_file_t`） | 仅此容器可访问，最安全 |
| `:z` | 共享标签（`container_share_t`） | 多个容器共享访问 |

```bash
# 专用标签（推荐：仅此容器可访问）
podman run -v /data/app1:/app/data:Z myapp

# 共享标签（多容器共享）
podman run -v /data/shared:/shared:z app1
podman run -v /data/shared:/shared:z app2

# 注意：:Z 会递归修改目录标签，对主机系统目录使用可能导致问题
# 永远不要对 /home, /usr, /etc 等系统目录使用 :Z
```

### NFS 卷

```bash
# 创建 NFS 卷
podman volume create --driver local \
  --opt type=nfs \
  --opt o=addr=nfs-server.example.com,rw,nfsvers=4 \
  --opt device=:/export/data \
  nfs-vol

# 使用 NFS 卷
podman run -d -v nfs-vol:/data myapp

# CIFS/SMB 卷
podman volume create --driver local \
  --opt type=cifs \
  --opt o=addr=smb-server,username=user,password=pass \
  --opt device=//smb-server/share \
  smb-vol
```

### 卷备份与恢复

```bash
# 备份卷数据
podman run --rm -v mydata:/source:ro -v /backup:/backup alpine \
  tar czf /backup/mydata-backup.tar.gz -C /source .

# 恢复卷数据
podman volume create mydata-restored
podman run --rm -v mydata-restored:/target -v /backup:/backup alpine \
  tar xzf /backup/mydata-backup.tar.gz -C /target
```

---

## 镜像层管理

### 层缓存机制

Podman 构建镜像时利用层缓存避免重复构建：

```dockerfile
# 优化层缓存的 Containerfile 示例
FROM python:3.12-slim

# 不常变化的层放在前面
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 经常变化的层放在后面
COPY . .
CMD ["python", "app.py"]
```

```bash
# 构建时使用缓存（默认行为）
podman build -t myapp .

# 禁用缓存
podman build --no-cache -t myapp .

# 从远程注册表获取缓存
podman build --cache-from=registry.example.com/myapp:cache -t myapp .

# 查看镜像层历史
podman history myapp:latest

# 查看镜像大小明细
podman image tree myapp:latest
```

### 清理策略

```bash
# 删除悬挂镜像（无标签、无引用）
podman image prune

# 删除所有未被容器使用的镜像
podman image prune -a

# 按时间过滤
podman image prune --filter until=720h  # 30天前

# 系统级清理（容器+镜像+卷+网络）
podman system prune --all --volumes

# 仅清理构建缓存
podman builder prune
```

### 存储配额设置

```bash
# 通过 storage.conf 设置容器可写层大小限制
# [storage.options.overlay]
# size = "10G"

# 运行时指定（需驱动支持）
podman run --storage-opt size=5G myapp
```

---

## 存储性能对比表

| 驱动 | 写入性能 | 内存占用 | 磁盘效率 | 适用场景 |
|------|---------|---------|---------|---------|
| overlay | 高 | 低 | 高（共享层） | 通用推荐 |
| fuse-overlayfs | 中 | 低 | 高 | rootless |
| vfs | 低 | 高 | 低（完整复制） | 特殊环境 |
| btrfs | 高 | 中 | 中 | 快照需求 |
| zfs | 高 | 中-高 | 高（去重+压缩） | 高密度 PaaS |

### 性能优化建议

1. **生产环境**：使用 overlay + XFS（性能最佳组合）
2. **Rootless**：内核 5.11+ 使用原生 overlay，旧内核用 fuse-overlayfs
3. **CI/CD**：开启 `volatile` 挂载选项，牺牲崩溃一致性换取速度
4. **大量小文件**：启用 `metacopy=on` 减少元数据复制开销
5. **存储空间**：定期执行 `podman system prune` 清理悬挂层
6. **共享基础层**：使用 `additionalimagestores` 多用户共享只读镜像层
