---
title: 高级主题
description: Podman 高级使用场景，包括 CI/CD 集成、多架构构建、供应链安全、性能调优等
---

# 高级主题

## CI/CD集成

### GitHub Actions

```yaml
- uses: redhat-actions/buildah-build@v2
  with:
    image: myapp
    tags: latest ${{ github.sha }}
    containerfiles: ./Containerfile
- uses: redhat-actions/podman-login@v1
- uses: redhat-actions/push-to-registry@v2
```

### GitLab CI

podman login + build + push 流程

### Jenkins

Pipeline 中使用 podman agent

### Rootless CI

无特权环境构建，不需要DinD

## 多架构构建

### QEMU模拟构建

```bash
sudo dnf install qemu-user-static
buildah build --jobs=4 \
  --platform=linux/amd64,linux/arm64,linux/ppc64le,linux/s390x \
  --manifest myimage .
```

### 分离构建+Manifest合并

各架构独立构建后用manifest合并：

```bash
podman manifest create myimage:latest
podman manifest add myimage:latest docker://registry/myimage:amd64
podman manifest add myimage:latest docker://registry/myimage:arm64
podman manifest push --all myimage:latest docker://registry/myimage:latest
```

> 注意：推送必须用`--all`，否则仅推送本机架构

## Podman Machine深入

### Provider对比

| Provider | 平台 | 性能 | 特点 |
|----------|------|------|------|
| QEMU | Linux/macOS/Windows | 中等 | 通用，跨平台 |
| Apple HV | macOS | 高 | 原生虚拟化，低延迟 |
| HyperV | Windows | 高 | 原生虚拟化 |
| WSL2 | Windows | 高 | 轻量，与Windows集成好 |

### 资源配置

```bash
podman machine init --cpus=4 --memory=8192 --disk-size=100
```

### 文件共享

- **9p**：传统方案，兼容性好但性能一般
- **virtiofs**（推荐）：低延迟高吞吐

### 配置修改

```bash
podman machine set --mount-type=virtiofs
```

## 容器供应链安全

### Cosign密钥签名

```bash
cosign sign --key cosign.key registry/image
```

### 无密钥签名（Sigstore OIDC）

使用 Sigstore 的 OIDC 身份验证进行无密钥签名，适合 CI/CD 环境。

### CI/CD管道自动签名

在 CI/CD 流水线中集成 cosign 自动签名步骤。

### SBOM生成

```bash
syft registry/myimage -o spdx
```

### 漏洞扫描工具对比

| 工具 | 特点 |
|------|------|
| Trivy | 最完整，支持多种扫描目标 |
| Grype | 与Syft集成良好 |
| Clair | 企业级，适合大规模部署 |

### Policy.json启用sigstore验证

在 `policy.json` 中配置 `sigstoreSigned` 类型以启用签名验证。

## 性能调优

### 运行时选择

- **crun**（C实现）：启动快20-30%，内存少50%
- **runc**（Go实现）：稳定性好

配置默认运行时：

```toml
# containers.conf
[engine]
runtime = "crun"
```

### 存储优化

overlay2最佳，配置metacopy=on：

```toml
[storage.options.overlay]
mountopt = "nodev,metacopy=on"
```

### 网络优化

- **Pasta**（Podman 5.0+默认）> slirp4netns
- Host网络模式性能最优

### 启动优化

- 使用精简基础镜像（alpine/distroless/scratch）
- 预拉取镜像避免网络延迟
- 使用read-only文件系统

### Cgroups v2配置

内存限制、CPU配额、stats监控：

```bash
podman run --memory=512m --cpus=2 myimage
podman stats --no-stream
```

## 健康检查

```bash
# Containerfile中定义
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost/ || exit 1

# 运行时指定
podman run --health-cmd="curl -f http://localhost/" \
  --health-interval=30s --health-timeout=10s \
  --health-retries=3 nginx

# 查看健康状态
podman inspect --format='{{.State.Health.Status}}' container_name
podman healthcheck run container_name
```

## 容器检查点与恢复（CRIU）

```bash
# 创建检查点
podman container checkpoint my-container

# 恢复
podman container restore my-container

# 迁移容器到另一台机器
podman container checkpoint --export=/tmp/checkpoint.tar my-container
# 在目标机器
podman container restore --import=/tmp/checkpoint.tar
```
