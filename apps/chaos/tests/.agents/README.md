# tests/.agents

`tests/.agents/` 是 `tests/` 目录的测试域智能体规则容器。

## 定位

- 继承根目录 `.agents/` 的全局规则体系。
- 仅补充测试目录相关的局部约定。
- 不复制根级 `.agents/` 中的技能、脚本、工作流和长期知识库职责。

## 结构

```text
.agents/
  README.md
  rules/
    testing.md
```

## 使用方式

当任务涉及 `tests/` 下的测试新增、测试修复、测试重构或测试验证时，先阅读 [`rules/testing.md`](rules/testing.md)，再结合根目录 [`../AGENTS.md`](../AGENTS.md) 执行。
