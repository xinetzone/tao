# 8. 影响范围分析

## 8.1 直接影响文件

本次涉及的主要文件：

- `apps/chaos/src/taolib/flowkit/podman_win.py`
- `apps/chaos/src/taolib/flowkit/podman_context.py`
- `apps/chaos/src/taolib/flowkit/container.py`
- `apps/chaos/src/taolib/flowkit/__init__.py`
- `apps/chaos/src/taolib/flowkit/artifacts.py`
- `apps/chaos/src/taolib/flowkit/models.py`
- `apps/chaos/examples/flowkit/build_workflow.py`
- `apps/chaos/tests/flowkit/test_flowkit.py`

## 8.2 运行逻辑影响

整体运行逻辑影响较低：

- 多数修改是类型注解、格式化、lint 风格修复。
- `container.py` 的 list 构造方式等价替换。
- 测试文件变量改名不改变断言逻辑。
- `podman_win.py` 的 `_instances` 注解变更不影响运行时列表行为。

## 8.3 风险点

主要风险点：

1. `_instances: ClassVar[list[Any]]` 类型精度低于 `list[SSHTunnel]`。
2. 全局 `ruff format --check .` 仍可能报告无关历史文件格式问题。
3. 如果项目未来要求严格类型检查，`Any` 可能需要更精细的替代方案。
