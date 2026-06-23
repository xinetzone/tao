# Rule Frontmatter Template

## Usage

用于为 `.agents/rules/` 下的规则文件添加 YAML frontmatter,支持两类字段:

1. **`paths`**(既有字段):glob 条件加载,控制规则在哪些文件路径下自动生效。
2. **`usage_feedback`**(新增字段):记录 Agent 使用规则时的反馈信号,形成"Agent 实际使用 → 反馈累积 → 规则改进"的闭环。

本模板源自 Context Hub 洞察(见 `retrospectives/insights-context-hub-20260622.md`),目的是补齐 AgentForge 反馈闭环中最弱的一环——规则质量评估缺少 Agent 实际使用数据。

## When to Use

- 新建规则文件时:直接复制精简版作为起始 frontmatter。
- 现有规则文件改造时:在文件头部插入 frontmatter,不影响既有正文。
- 试点反馈闭环时:选 3-5 个高频规则(如 `python.md`、`documentation.md`)启用完整版,让 Agent 主动更新 `usage_feedback`。

## Template — 精简版(推荐起步)

最小可用 frontmatter,所有规则文件统一加上,为未来反馈闭环预留位置。

```yaml
---
paths:
  - "src/**/*.py"
  - "tests/**/*.py"
usage_feedback:
  total_invocations: 0
  success_count: 0
  failure_count: 0
  last_invoked: null
  agent_notes: []
---

# 规则标题
```

## Template — 完整版(试点规则使用)

带完整字段和示例数据,适用于希望深度跟踪质量的规则。

```yaml
---
paths:
  - "src/taolib/**/*.py"
  - "tests/**/*.py"
  - "pyproject.toml"
usage_feedback:
  total_invocations: 12
  success_count: 10
  failure_count: 2
  last_invoked: 2026-06-22
  failure_reasons:
    - reason: "uv sync 在 Windows 下偶发权限错误"
      count: 2
      last_seen: 2026-06-20
      workaround: "改用 uv sync --no-cache 或关闭杀毒软件实时扫描"
  agent_notes:
    - timestamp: 2026-06-22
      agent: "claude-code"
      note: "规则 §3.2 关于 uv add 的部分,在 monorepo 下需要补充 --package 参数说明"
    - timestamp: 2026-06-18
      agent: "codex"
      note: "pyproject.toml 的 [tool.uv.sources] 段示例已过时,建议更新到 uv 0.4+ 语法"
---

# 规则标题
```

## Field Reference

### `paths`(既有字段)

| 属性 | 说明 |
|------|------|
| 类型 | list of glob patterns |
| 作用 | 控制规则在哪些文件路径下自动生效 |
| 维护 | 人工维护 |
| 示例 | `"src/**/*.py"`、`"pyproject.toml"` |

### `usage_feedback`(新增字段)

| 子字段 | 类型 | 说明 | 维护方式 |
|--------|------|------|----------|
| `total_invocations` | int | 规则被引用总次数 | Agent 自动累加 |
| `success_count` | int | 规则应用后任务成功的次数 | Agent 自动累加 |
| `failure_count` | int | 规则应用后任务失败的次数 | Agent 自动累加 |
| `last_invoked` | date / null | 最后一次被引用的日期(YYYY-MM-DD) | Agent 自动更新 |
| `failure_reasons` | list | 失败原因明细 | Agent 记录,人工审阅 |
| `failure_reasons[].reason` | string | 失败原因描述 | Agent 记录 |
| `failure_reasons[].count` | int | 该原因出现次数 | Agent 累加 |
| `failure_reasons[].last_seen` | date | 该原因最后出现日期 | Agent 更新 |
| `failure_reasons[].workaround` | string | 临时解决方案或规避方法 | Agent 或人工补充 |
| `agent_notes` | list | Agent 发现的规则缺口或过时内容 | Agent 主动标注 |
| `agent_notes[].timestamp` | date | 标注时间 | Agent 记录 |
| `agent_notes[].agent` | string | 标注来源(claude-code / codex / gemini-cli 等) | Agent 记录 |
| `agent_notes[].note` | string | 具体观察或建议 | Agent 记录 |

## Design Principles

1. **与既有 `paths:` 字段共存** — 不破坏现有 frontmatter 约定,可同时存在。
2. **`null` / `[]` 作为初始值** — 区分"未启用"和"零次使用",避免歧义。
3. **`failure_reasons` 带 `workaround`** — 让失败记录也能反哺规则改进,不只是统计。
4. **`agent_notes` 带 `timestamp` 和 `agent`** — 区分不同 Agent、不同时间点的观察,支持多 Agent 协同标注。
5. **机器可读 + 人工可审** — YAML 结构化,Agent 可更新,维护者可阅读。
6. **渐进可选** — 不强制所有规则启用,可分批试点。

## Adoption Roadmap

| 阶段 | 范围 | 动作 |
|------|------|------|
| 起步 | 全部规则文件 | 统一加上精简版 frontmatter(空 usage_feedback) |
| 试点 | 3-5 个高频规则 | 让 Agent 主动更新 usage_feedback,累积数据 |
| 成熟 | 全部规则 | 基于累积数据做规则质量审计,识别高失败率或过时规则 |
| 演进 | 规则演化流程 | 将 usage_feedback 纳入 `rule-evolution.md` 的准入标准 |

## Anti-Patterns

避免以下做法:

| 反模式 | 后果 | 正确做法 |
|--------|------|----------|
| 跳过精简版直接上完整版 | 数据空缺,维护负担大 | 从精简版起步,按需升级 |
| 人工编造 usage_feedback 数据 | 数据失真,误导决策 | 数据必须来自 Agent 实际使用 |
| 只记录成功不记录失败 | 失去改进信号 | failure_reasons 比 success_count 更有价值 |
| 让 usage_feedback 字段无限膨胀 | 文件难以维护 | 定期归档旧 notes,只保留近 3 个月 |
| 把 usage_feedback 当作绩效考核 | 诱发数据造假 | 仅用于规则质量改进,不用于人考核 |

## Example — 应用到 python.md

改造前(当前状态):

```markdown
# Python 开发规则

本文档定义 Python 开发环境、依赖管理与代码风格的统一规范...
```

改造后(加上 frontmatter):

```yaml
---
paths:
  - "src/taolib/**/*.py"
  - "tests/**/*.py"
  - "pyproject.toml"
usage_feedback:
  total_invocations: 0
  success_count: 0
  failure_count: 0
  last_invoked: null
  agent_notes: []
---

# Python 开发规则

本文档定义 Python 开发环境、依赖管理与代码风格的统一规范...
```

## Sources

- **设计来源**:`retrospectives/insights-context-hub-20260622.md` §3.4「对 AgentForge 的启示」
- **既有 frontmatter 约定**:`rules/browser-agent.md`(paths 字段示例)
- **跨工具桥接参考**:`AGENTS.md` §7「跨工具目录桥接」中 `.agents/rules/` 与 Claude Code `.claude/rules/` 的条件加载机制对齐
