---
title: Docker迁移指南
description: 从 Docker 迁移到 Podman 的完整指南，包括兼容方案、Compose 迁移、常见问题及检查脚本
---

# Docker迁移指南

## 迁移概述

### 为什么迁移

- **安全性**：rootless 默认运行，无需 root 权限
- **资源效率**：无 daemon 进程，按需启动
- **K8s原生**：Pod 概念与 Kubernetes 一致，支持直接生成 YAML

### 迁移策略

渐进式迁移：alias兼容 → 逐步替换 → 完全迁移

### 风险评估与回退方案

- 评估现有 Docker 使用场景的兼容性
- 保留 Docker 安装作为回退
- 逐步验证各服务在 Podman 下的运行状态

## 快速兼容方案

```bash
# 方案1：Shell alias
alias docker=podman

# 方案2：Podman socket（完全兼容Docker API）
systemctl --user enable --now podman.socket
export DOCKER_HOST=unix:///run/user/$(id -u)/podman/podman.sock
# 现在docker-compose等工具可以直接使用
```

## Docker Compose迁移

docker-compose.yml → podman compose / podman kube play

### 迁移检查清单

1. **镜像名**：使用完全限定名（docker.io/library/nginx）
2. **卷权限**：添加`:Z`标签（SELinux）
3. **端口**：rootless无法绑定<1024（使用高端口或sysctl配置）
4. **网络**：确保服务在同一compose网络
5. **环境变量**：语法兼容，无需修改

## Dockerfile → Containerfile

```bash
# 重命名（两者均可使用）
mv Dockerfile Containerfile

# 最佳实践差异：
# - 使用 RUN --mount=type=cache 加速构建
# - 使用 --squash 减少层数
# - 多阶段构建使用 scratch/distroless 最终镜像
```

## 常见迁移问题解决

| 问题 | 原因 | 解决方案 |
|-----|------|--------|
| 短名称解析错误 | 镜像名不完整 | 配置unqualified-search-registries或使用完整路径 |
| Permission denied | SELinux/文件权限 | 卷添加:Z，或使用--userns=keep-id |
| 容器间无法通信 | 网络隔离 | 确保同一网络，或使用Pod |
| 端口已占用 | Docker daemon仍在运行 | `systemctl stop docker` |
| build cache不生效 | 存储驱动差异 | 使用`--layers`确保缓存启用 |
| volume数据丢失 | 路径不同 | 迁移/var/lib/docker → /var/lib/containers |

## 迁移检查脚本

```bash
#!/bin/bash
echo "=== Podman 迁移就绪检查 ==="
echo "Podman版本: $(podman --version)"
echo "运行时: $(podman info --format '{{.Host.OCIRuntime.Name}}')"
echo "存储驱动: $(podman info --format '{{.Store.GraphDriverName}}')"
echo "Rootless: $(podman info --format '{{.Host.Security.Rootless}}')"
echo "Cgroups: $(podman info --format '{{.Host.CgroupsVersion}}')"
echo ""
# 检查subuid/subgid
if grep -q "$(whoami)" /etc/subuid 2>/dev/null; then
  echo "✓ subuid配置正确"
else
  echo "✗ 缺少subuid配置"
fi
# 检查网络
if command -v pasta &>/dev/null || command -v slirp4netns &>/dev/null; then
  echo "✓ 网络工具就绪"
else
  echo "✗ 缺少网络工具(pasta/slirp4netns)"
fi
```

## alias docker=podman 的局限性

- Docker Swarm命令不支持
- docker context不完全兼容
- 部分docker插件(如buildx)不可用
- docker compose v1不兼容（需v2+）
- socket方式更可靠
