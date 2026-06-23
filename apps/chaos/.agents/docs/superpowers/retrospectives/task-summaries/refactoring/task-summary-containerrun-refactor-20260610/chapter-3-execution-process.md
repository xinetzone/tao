# 第三章：执行过程详解

### 3.1 执行阶段划分

| 阶段 | 名称 | 主要活动 |
|------|------|---------|
| Round 1 | run_kwargs 透传 | 新增字段、展开到 `containers.run()`、文档更新 |
| Round 2 | 字段可选化 | `host_path`/`target`/`working_dir`/`name` 改为可选，`_start()` 条件化重写 |
| Round 3 | start_container 开关 | 新增字段，`_start()` 中早期 return 跳过容器创建 |
| Round 4 | network_mode 显式暴露 | 新增字段，条件化加入 `run_params` |
| Round 5 | 全面注释 | 为 7 处关键逻辑补充中文注释，移除遗留调试代码 |
| 穿插 | 技术答疑 | bridge vs host 网络模式；ContainerRun 慢的根因分析 |

### 3.2 各阶段详细记录

#### Round 1：run_kwargs 透传

**阶段目标**：解决 `containers.run()` 参数硬编码问题。

**核心改动**：
- L69：文档新增 `run_kwargs` 说明
- L135：新增 `run_kwargs: dict[str, Any] = field(default_factory=dict)`
- L383：`**self.run_kwargs` 展开到最后

**设计考量**：`run_kwargs` 放在 `run_params.update()` 最后执行，允许用户覆盖所有固定参数。若传入与固定参数同名的键，Python 会抛出 `TypeError`，这是预期行为（防止意外覆盖核心参数）。

#### Round 2：字段可选化

**阶段目标**：将 5 个必填字段缩减为仅 `image` 必填。

**核心改动**：
- L127-131：4 个字段改为 `Optional`，默认 `None`
- L314-331：客户端创建分叉——有 `host_path` 走路径转换，无则直接 `PodmanClient`
- L334-348：bind 挂载条件化
- L352-357：旧容器清理条件化
- L366-383：`run_params` 字典动态构建
- L411-413：`_cleanup()` 增加 `hasattr(self._pctx.ctx, "_tunnel")` 防御

**设计考量**：运行时参数构建采用"先建字典、条件加入、最后 merge"的三段式模式，比"条件分支中直接调用"更清晰，每个参数的条件独立可读。

#### Round 3：start_container 开关

**阶段目标**：支持仅建立客户端连接、不创建容器的轻量模式。

**核心改动**：
- L71：文档新增 `start_container` 说明
- L137：新增 `start_container: bool = True`
- L359-362：容器清理之后、参数构建之前，直接 `return`

**排错**：Round 2 中 `_pctx` 的创建移入了 `host_path` 分支内部，导致 `_cleanup()` 中 `self._pctx` 可能为 `None` 时 `self._pctx.ctx._tunnel` 访问失败。增加了 `hasattr(self._pctx.ctx, "_tunnel")` 检查。

#### Round 4：network_mode 显式暴露

**阶段目标**：将常用的网络模式参数提升为一级字段。

**核心改动**：
- L70：文档新增 `network_mode` 说明
- L136：新增 `network_mode: str | None = None`
- L380-381：条件化加入 `run_params`

**设计考量**：`network_mode` 默认 `None`（不传入 `containers.run()`），由 Podman 使用默认值（bridge）。用户显式设置后才生效。

#### Round 5：全面注释

**阶段目标**：为全部核心逻辑补充详尽中文注释，提升代码可读性和可维护性。

**注释覆盖**：

| 位置 | 新增内容 |
|------|---------|
| `_start()` | 五阶段执行流程注释、平台分支说明、挂载类型说明、参数构建逻辑 |
| `_cleanup()` | 清理顺序说明、Windows SSH 隧道特殊处理原因 |
| `wait()` | 流式日志原理、SDK 版本兼容处理 |
| `exec()` | workdir 为 None 的默认行为、bytes/str 输出兼容 |
| `_win_to_unix()` | 路径转换背景、盘符映射逻辑 |
| `_get_active_podman_machine()` | `podman machine list` 输出格式、解析规则 |
| `_get_podman_context()` | 平台差异原因、Window/Linux 分支说明 |

同时移除了 `_get_podman_context()` 中遗留的 `print(f"ctx: {kwargs}")` 调试代码。
