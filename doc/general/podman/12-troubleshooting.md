---
title: 故障排除
description: Podman 常见问题诊断与解决方案，涵盖启动、网络、存储、Machine 及调试方法
---

# 故障排除

## 启动类问题

| 症状 | 可能原因 | 排查步骤 | 解决方案 |
|------|--------|---------|---------|
| 容器启动失败 | 镜像损坏/不存在 | `podman inspect IMAGE` | 重新pull镜像 |
| OCI runtime error | 运行时配置错误 | 检查containers.conf | 重装crun/runc |
| 权限拒绝 | rootless配置不完整 | 检查/etc/subuid | 添加用户映射 |

## Rootless问题排查

```bash
# 1. 检查用户命名空间
cat /etc/subuid | grep $(whoami)
cat /etc/subgid | grep $(whoami)
# 期望输出: username:100000:65536

# 2. 检查内核参数
sysctl user.max_user_namespaces
# 期望: user.max_user_namespaces = 28633

# 3. 重置rootless环境
podman system migrate
podman system reset  # 注意：会删除所有数据！

# 4. 测试基本功能
podman run --rm alpine echo "rootless works"
```

## 网络问题排查

```bash
# 容器无法访问外网
podman run --rm alpine ping -c 3 8.8.8.8
podman run --rm alpine nslookup google.com

# 检查网络后端
podman info | grep -i network

# 检查iptables/nftables规则
sudo iptables -L -n -t nat | grep PODMAN
sudo nft list ruleset | grep podman

# 重建网络
podman network rm mynet
podman network create mynet
```

## 存储问题排查

```bash
# 磁盘空间不足
podman system df          # 查看空间使用
podman system prune -a    # 清理所有未使用资源
podman image prune -a     # 清理悬空镜像

# 存储损坏
podman system check       # 检查一致性
podman system reset       # 重置（最后手段）

# 查看存储详情
podman info --format json | jq '.store'
```

## Machine问题排查（macOS/Windows）

```bash
# 启动失败
podman machine inspect    # 查看配置
podman machine rm myvm    # 删除重建
podman machine init --cpus=4 --memory=8192

# WSL问题
wsl --list --verbose      # 检查WSL状态
wsl --update              # 更新WSL

# SSH连接问题
podman machine ssh myvm   # 手动SSH测试
```

## 日志与调试

```bash
# 启用调试模式
podman --log-level=debug run alpine echo test

# 容器日志
podman logs --tail=100 -f container_name

# 系统事件
podman events --filter event=start --since 1h

# 容器进程
podman top container_name

# 资源使用
podman stats --no-stream
```

## 常见错误速查表

| 错误信息 | 解决方案 |
|---------|---------|
| `short-name resolution enforced` | 使用完整镜像名或配置registries.conf |
| `Error: OCI runtime error` | 检查运行时安装，重装crun |
| `ERRO[0000] cannot find UID/GID` | 配置/etc/subuid和/etc/subgid |
| `Error: port already in use` | 释放端口或更换映射端口 |
| `Error: statfs: no such file` | 检查卷挂载路径是否存在 |
| `Error: writing blob: storing blob` | 磁盘空间不足，清理存储 |
| `pasta failed: Cannot bind to port` | 端口<1024需sysctl配置 |
