# Podman Rootless

## Search Keywords

- 主关键词：Podman Rootless
- 英文术语：rootless containers, user namespaces, subuid, subgid
- 常见别名：无根容器, 非 root 运行
- 错误短语：cannot setup namespace, permission denied, permission denied for volume mount, subuid not configured

## Goal

说明 Podman 在无 root 权限 (Rootless) 环境下的工作原理、挂载权限坑点及故障排查路径。

## Relevance In AgentForge

- 关联模块：CI/CD 流水线中的容器构建与运行、本地开发环境的容器化部署。
- 常见触发场景：启动容器失败提示权限不足、宿主机目录挂载到容器后无法读写。
- 优先检查文件：容器启动脚本、`Containerfile`

## Trigger Phrases

- 为什么 Podman rootless 挂载目录后容器里看不到文件或没有写权限？
- Podman 报 cannot setup namespace 怎么解决？
- 怎么把容器里的端口映射到主机的特权端口 (低于 1024)？

## Key Concepts

- **User Namespaces**: Rootless Podman 依赖 Linux 的用户命名空间技术。容器内的 root 用户实际上映射到宿主机上的一个普通非特权用户。
- **subuid / subgid**: 用于配置宿主机用户可以使用的从属 UID 和 GID 范围。这是 rootless 模式正常运行的基础。
- **UID 映射 (UID mapping)**: 当你将宿主机的目录挂载到容器内时，由于 UID 的映射关系，容器内的进程可能对该目录没有读写权限。

## Common Problems

### 问题：挂载卷权限拒绝 (Permission denied for volume mount)

- 现象：将宿主机目录通过 `-v` 挂载到容器后，容器内应用报错 `Permission denied`，无法读取或写入挂载的目录。
- 原因：在 Rootless 模式下，宿主机的目录属主是你当前的普通用户。但是映射到容器内后，这个 UID 可能变成了容器里的 root (UID 0)，而容器内的应用如果使用非 root 用户（如 UID 1000）运行，就会因为 UID 不匹配而没有权限。
- 排查步骤：
  1. 使用 Podman 的特殊挂载后缀 `:Z`（针对 SELinux 环境）或 `:U`。特别是在非 SELinux 环境下，加上 `:U` 可以让 Podman 自动根据容器内部的 UID 修改宿主机目录的属主（注意：这会改变宿主机的权限）。
  2. 或者，在运行容器时使用 `--userns=keep-id`，让容器内的用户与宿主机的当前用户保持一致的 UID。
- 相关命令或代码位置：`podman run -v ...` 命令行参数。

### 问题：命名空间设置失败 (cannot setup namespace)

- 现象：运行 Podman 报错 `Error: cannot setup namespace using newuidmap: exit status 1`。
- 原因：宿主机的 `/etc/subuid` 或 `/etc/subgid` 未配置当前用户的从属 ID 范围。
- 排查步骤：
  1. 检查文件：`cat /etc/subuid`，确认是否有你的用户名。
  2. 如果没有，使用 `usermod --add-subuids 100000-165535 --add-subgids 100000-165535 <username>` 添加（需要 root 权限）。

## Commands Or Snippets

```bash
# 使用 :U 解决 rootless 挂载权限问题
podman run -d --name myapp -v /host/data:/container/data:U myimage

# 保持当前用户 ID (适用于开发环境的挂载)
podman run -it --rm --userns=keep-id -v $(pwd):/workspace myimage bash
```

## Sources

- 官方文档：[Podman Rootless Tutorial](https://github.com/containers/podman/blob/main/docs/tutorials/rootless_tutorial.md)
- 版本：N/A
- 抓取时间：N/A