# 第五章：问题与解决方案

### 5.1 问题总览

| # | 问题标题 | 严重程度 | 解决状态 |
|---|---------|---------|---------|
| I1 | `containers.run()` 参数硬编码 | 🟡 中 | ✅ 已解决 |
| I2 | 必填字段限定使用场景 | 🟡 中 | ✅ 已解决 |
| I3 | ContainerRun 比 PodmanClient 慢 | 🟡 中 | ✅ 已解决 |
| I4 | `_cleanup()` 无 host_path 时崩溃 | 🔴 严重 | ✅ 已解决 |
| I5 | `run_kwargs` 参数冲突风险 | 🟢 低 | ⚠️ 已记录约束 |

### 5.2 问题详情

#### 问题 I1：containers.run() 参数硬编码

**问题分类**：技术 - 架构设计问题

**问题描述**：`_start()` 中 `containers.run()` 的参数是硬编码的，用户无法传递 `environment`、`ports`、`privileged`、`user` 等参数。

**根本原因**：`ContainerRun` 设计时只考虑了最常用的挂载场景，未预留扩展性。

**解决方案**：新增 `run_kwargs: dict[str, Any]` 字段，以 `**self.run_kwargs` 展开到 `containers.run()` 调用末尾。

**经验教训**：任何 SDK 包装类都应预留透传机制（`**kwargs` 或显式 `xxx_kwargs` 字段），因为 SDK 参数集会随着版本演进而变化。

#### 问题 I3：ContainerRun 比直接 PodmanClient 慢

**问题分类**：技术 - 性能瓶颈

**问题描述**：用户对比发现通过 SSH 连接时，`ContainerRun` 比直接 `PodmanClient` + `ping()` 慢很多。

**排查过程**：
1. 确认 `client_kwargs={"base_url": ..., "identity": ...}` 在两种方案中完全一致
2. 追踪 `_start()` → `containers.run()` 调用链
3. 发现 `containers.run()` 涉及：镜像检查、容器进程创建、`sleep infinity` 命令执行——这是连接建立后的重操作，而非连接本身慢

**根本原因**：`ContainerRun._start()` 一定会执行 `containers.run()`，这比 `ping()` 重几个数量级。

**解决方案**：新增 `start_container: bool = True`，设为 `False` 时跳过容器创建，仅管理客户端生命周期。

#### 问题 I4：无 host_path 时 _cleanup() 崩溃

**问题分类**：技术 - 代码缺陷

**问题描述**：Round 2 中将 `_pctx` 创建移入 `host_path is not None` 分支内部，导致无 host_path 时 `_pctx` 为 `None`。`_cleanup()` 中访问 `None.ctx` 会抛出 `AttributeError`。

**根本原因**：`_pctx` 的生命周期从"一定存在"变为"条件存在"，但 `_cleanup()` 未同步更新防御逻辑。

**解决方案**：在 `_cleanup()` 中增加 `self._pctx is not None and hasattr(self._pctx.ctx, "_tunnel")` 两重检查。

**经验教训**：将必走流程改为条件流程时，必须扫描所有下游消费者，逐一检查是否需要增加空值保护。
