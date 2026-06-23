# 5. 关键决策复盘

## 5.1 使用 `uv run --no-sync`

### 问题

直接运行 `uv run ruff check .` 时触发 `.pdm-build` 文件锁错误。

### 决策

改用：

```powershell
uv run --no-sync ruff check .
```

### 原因

该命令可以跳过包同步 / 构建流程，直接使用当前环境运行 Ruff，避免 `.pdm-build` 锁冲突。

### 结果

成功继续 lint 修复流程。

## 5.2 不全量格式化无关文件

### 问题

全局格式检查发现部分 `.agents/scripts` 和其他测试文件存在历史格式问题。

### 决策

只格式化与本次 diagnostics 和实际修改相关的文件。

### 原因

用户目标是修复当前 diagnostics，不应扩大修改范围，避免引入无关 diff。

### 结果

保持变更聚焦，降低回归风险。

## 5.3 移除 future annotations 后使用 `ClassVar[list[Any]]`

### 问题

`SSHTunnel` 类内部定义：

```python
_instances: ClassVar[list[SSHTunnel]] = []
```

在没有 `from __future__ import annotations` 的情况下，类体内无法直接引用尚未完成定义的 `SSHTunnel`。

尝试使用字符串前向引用：

```python
_instances: ClassVar[list["SSHTunnel"]] = []
```

但 Ruff 在 Python 3.13+ 目标下报告 `UP037`，要求移除引号。

### 决策

改为：

```python
_instances: ClassVar[list[Any]] = []
```

### 原因

- 避免类体内前向引用运行时求值问题。
- 满足 Ruff 规则。
- `_instances` 是内部清理注册表，实际只存放 `SSHTunnel` 实例，运行逻辑不受影响。

### 结果

`podman_win.py` 单文件 lint 与 format 均通过。
