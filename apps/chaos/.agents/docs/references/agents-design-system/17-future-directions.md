# 17. 未来方向

## 17.1 从 Markdown 到 Schema 的三阶段演进路径

**第一阶段**：人类可读 Markdown。先建一个 `AGENTS.md`，内容极简但有效。

**第二阶段**：Markdown + YAML frontmatter。例如：

```md
---
name: reviewer
type: role
applies_to:
  - pull_request
  - code_review
requires:
  - git_diff
---

# Reviewer Agent

...
```

**第三阶段**：结构化 schema。例如：

```yaml
name: reviewer
type: role
inputs:
  - diff
  - test_results
outputs:
  - review_findings
permissions:
  shell: false
  write_files: false
```

不要太早进入第三阶段，否则会让配置系统比项目本身还复杂。

## 17.2 可能的行业标准

我觉得未来比较可能形成这样的事实标准：

```
AGENTS.md
```

作为通用入口，类似 `README.md`、`LICENSE`、`CONTRIBUTING.md`。然后 `.agents/` 成为高级扩展目录，类似 `.github/`、`.vscode/`、`.devcontainer/`。

长期看可能会有这些能力：

1. **Agent instruction discovery** — 工具自动查找 `AGENTS.md`
2. **Scoped instructions** — 子目录覆盖父目录规则
3. **Role-based instruction loading** — reviewer/coder/tester 加载不同上下文
4. **Permission metadata** — 哪些命令允许，哪些需要确认
5. **Task workflow metadata** — feature/bugfix/refactor 的标准流程
6. **Evaluation hooks** — Agent 改完代码后自动跑什么检查
7. **MCP/tool binding** — `.agents/tools/` 描述可用工具与限制

## 17.3 对 AgentForge 这类项目的启发

对于偏 Agent 平台 / 多 Agent 框架的项目，`AGENTS.md + .agents/` 可以进一步升级成"Agent-native repository protocol"：

```
AGENTS.md
.agents/
  registry.yaml
  roles/
  workflows/
  tools/
  memory/
  evals/
```

可能出现更细粒度的设计：

```
.agents/
  agents/
    planner.agent.md
    coder.agent.md
    reviewer.agent.md
    tester.agent.md

  workflows/
    implement-feature.workflow.md
    review-pr.workflow.md

  evals/
    coding-quality.eval.md
    regression.eval.md

  tools/
    filesystem.tool.md
    shell.tool.md
    github.tool.md
```

这时 `.agents/` 不只是文档，而是接近可执行配置。

如果要让 `AGENTS.md` + `.agents/` 成为更通用的标准，可能需要：
1. 一份规范的 JSON Schema 定义
2. 与 MCP 的工具注册机制打通
3. 编辑器/IDE 的原生支持（类似 Cursor 对 `.cursorrules` 的识别）

最大的风险不是"过度设计"，而是**运行时迟迟不来导致治理层变成死文档**。最大的机会是**率先建立跨平台技能标准**，让 `.agents/skills/` 成为 AI 时代的 `package.json`。
