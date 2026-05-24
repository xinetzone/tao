# Agent Memory Dream Protocol Pilot Spec

## Goal

验证"记忆、做梦"知识协议是否能在一次真实任务收尾中低摩擦使用，并判断它是否能产生可回流、可遗忘的洞见。

## Scope

- 使用一次已完成的文档协议任务作为输入材料。
- 从任务结果中提取 1 条记忆候选。
- 使用记忆条目模板判断是否进入长期记忆。
- 使用做梦会话模板进行一次最小做梦式归纳。
- 输出至少 1 条洞见候选、遗忘建议或回流建议。

## Non-Goals

- 不实现 CLI。
- 不修改 `src/taolib/`。
- 不自动写入长期记忆。
- 不修改全局规则。
- 不把当前任务进度当作长期记忆。

## Input Material

- `.agents/docs/superpowers/specs/2026-05-24-agent-memory-dream-protocol-design.md`
- `.agents/docs/references/agent-memory-dream-protocol.md`
- `.agents/docs/templates/agent-memory-entry-template.md`
- `.agents/docs/templates/agent-dream-session-template.md`

## Deliverables

- 一条记忆候选判断记录。
- 一次最小做梦会话记录。
- 一条可回流、可遗忘或可延后观察的洞见候选。
- 一份试点验收清单。

## Risks

- 试点可能只复述协议，没有产生洞见。
- 输入记忆数量过少，做梦会话可能过早。
- 如果输出不能回流，说明协议仍需补充触发和验收标准。
