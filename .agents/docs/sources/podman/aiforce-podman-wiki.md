# Aiforce Podman Wiki Source

## Source

- 来源链接：<https://acntxq6xf8pe.aiforce.cloud/app/app_4jwk79sp6p8gg>
- 页面主题：Podman Wiki
- 页面版本标识：v5.8.x
- 抓取时间：2026-05-23

## Extracted Outline

- Podman 项目概述
- Podman vs Docker
- 核心功能
- 技术架构
- 代码解析与命令示例
- 使用指南
- 常见问题

## Key Facts

- Podman 是由 Red Hat 容器团队主导开发的开源容器管理工具，属于 containers 组织核心项目之一。
- Podman 的核心定位是 Daemonless、Rootless、Docker CLI 兼容和 Kubernetes 原生。
- Podman 支持容器生命周期管理、镜像管理、网络管理、存储管理、Pod 管理、Quadlet、健康检查和 Kubernetes 集成。
- Podman 与 Docker 的关键差异包括是否依赖守护进程、Rootless 支持、Pod 支持、systemd 集成、资源占用和架构模型。
- Podman 核心架构由 Podman CLI、libpod、conmon、containers/storage、containers/image、containers/common 和 OCI Runtime 组成。
- 常用命令覆盖 `podman run`、`podman build`、`podman pod`、`podman machine`、`podman quadlet` 和 `podman kube play`。

## Topics For Stable References

- Podman 概览：项目定位、适用场景、与 Docker 的差异。
- Podman 架构：libpod、conmon、存储、镜像、OCI Runtime 的职责边界。
- Podman 工作流：容器创建、镜像构建、Pod 管理、Quadlet 和 Kubernetes YAML 的常见使用路径。
- Podman 排障：Rootless 权限、网络解析、存储驱动、Docker Compose 兼容和系统自启动。
