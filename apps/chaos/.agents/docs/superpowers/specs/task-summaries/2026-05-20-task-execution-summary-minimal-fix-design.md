# Task Execution Summary Minimal Fix Design

## Goal

对 `task-execution-summary` 技能做最小范围纠偏，消除会误导模型执行的文档内容，并补齐仓库要求的主文档结构。

## Scope

- 修正 `SKILL.md` 中的失效链接
- 在 `SKILL.md` 中补充输入输出、依赖、部署、版本记录等必要章节
- 将 `references/api-reference.md` 从虚构远程 API 规范改为技能内参数参考
- 统一 `references/execution-flow.md` 的参数口径，以 `task_name` 为必填标识

## Non-Goals

- 不重写技能定位和整体触发策略
- 不调整 `evals/` 结构
- 不重构其他 reference 文档
- 不引入新的工具、命令或外部服务

## Approach

1. 保留现有目录与大部分正文内容，只做定点修正。
2. 让 `SKILL.md` 成为合规入口文档，外部 reference 只承载补充说明。
3. 删除所有会让模型误以为存在公网服务、认证体系和正式 HTTP 端点的表述。
4. 统一自然语言调用、结构化调用、错误码含义三处术语。

## Risks

- 参考文档之间历史表述较多，可能仍有少量旧术语残留。
- `examples-v2.md` 仍保留“请求/响应”风格示例，但不在本次最小修复范围内。

## Validation

- 检查 `SKILL.md` 到 `references/` 的链接是否有效
- 检查 `task_name` 是否在主文档、参数参考、执行流程中保持一致
- 检查是否已移除虚构远程 API、认证和速率限制描述
