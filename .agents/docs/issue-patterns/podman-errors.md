# Podman Error Patterns

## Pattern 1: Mount Or Path Mapping Failure

- 现象：容器内看不到预期文件，或启动时报路径不存在。
- 常见原因：宿主机路径错误、Windows 路径格式不匹配、权限或标签设置问题。
- 排查步骤：
  1. 核对宿主机实际路径。
  2. 重新检查 `podman run -v` 参数。
  3. 查看容器日志并进入容器内确认挂载结果。
- 优先命令：`podman run`, `podman exec`, `podman inspect`

## Pattern 2: Container Exits Immediately

- 现象：容器创建成功但立刻退出。
- 常见原因：入口命令错误、依赖服务缺失、环境变量未传入。
- 排查步骤：
  1. 执行 `podman logs <container>`
  2. 检查入口命令和参数
  3. 验证环境变量与挂载目录
- 优先命令：`podman logs`, `podman inspect`
