# Task Execution Summary Description Compression Design

## Goal

在不明显损失触发覆盖面的前提下，压缩 `task-execution-summary` 的 frontmatter `description`，降低常驻上下文成本。

## Chosen Approach

采用方案 C：双层触发。

- 第一层使用总括句覆盖“已完成任务的总结、复盘、回顾、经验沉淀”
- 第二层保留少量高频关键词和高频任务场景，避免触发语义过度抽象

## Scope

- 仅修改 `SKILL.md` 的 `description`
- 可同步补一条版本记录

## Non-Goals

- 不调整正文结构
- 不修改 `evals/`
- 不重写其他 references 文档
- 不改变技能能力边界

## Validation

- 保留显式触发词：`总结`、`复盘`、`回顾`、`报告`、`postmortem`
- 保留隐式触发意图：`做得怎么样`、`有什么收获`、`下次怎么做`
- 保留高频任务域：开发、项目管理、故障排查、研究、学习
- 明显缩短 `description` 长度，删除重复穷举
