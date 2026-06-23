# 附录

### 附录 A：文件变更清单

| 文件路径 | 操作类型 | 关键变更 |
|---------|---------|---------|
| `apps/chaos/src/taolib/flowkit/podman_context.py` | 修改 | 新增 3 字段、4 字段改为可选、7 处注释补充、移除 1 处调试代码 |
| `.temp/task-summary-containerrun-refactor-20260610.md` | 创建 | 本报告 |
| `.temp/insights-containerrun-refactor-20260610.md` | 创建 | 深度洞察 |

### 附录 B：术语表

| 术语 | 说明 |
|------|------|
| Bind Mount | 将宿主机目录直接映射到容器内的挂载方式 |
| Named Volume | 由 Podman/Docker 管理的持久化存储卷 |
| Detach Mode | 容器在后台运行，不阻塞当前终端 |
| Bridge Network | 默认网络模式，容器通过虚拟网桥 NAT 通信 |
| Host Network | 容器直接使用宿主机网络栈，无网络隔离 |
