# 9. 推荐目录结构：从最小到完整的渐进路径

## 9.1 最小版本（项目初期）

只建一个文件：

```txt
AGENTS.md
```

内容仅包含：

```md
# AGENTS.md

## Project
Brief project description.

## Commands
- Install:
- Dev:
- Lint:
- Typecheck:
- Test:
- Build:

## Rules
- Follow existing patterns.
- Prefer minimal changes.
- Do not add dependencies without approval.
- Do not commit, push, deploy, or run migrations unless explicitly asked.
- Never expose secrets.

## Workflow
1. Inspect relevant code.
2. Make a short plan for non-trivial changes.
3. Implement focused changes.
4. Run relevant checks.
5. Summarize changes and validation.
```

## 9.2 中等版本（项目复杂度提升后）

```
AGENTS.md
.agents/
  workflows/
  context/
  policies/
```

## 9.3 完整版本（多智能体 / 大型项目）

```
AGENTS.md
.agents/
  README.md
  roles/
  workflows/
  context/
  policies/
  templates/
  skills/
  docs/
  scripts/
```

不要一开始就过度设计。**先 Markdown，后 schema；先轻量，后自动化。**

## 9.4 AgentForge Spec v0.1 五级渐进式复杂度模型

AgentForge 规范将上述渐进路径系统化为五个明确的 Level：

```
Level 0 → AGENTS.md（单文件，Codex 兼容）
Level 1 → + .agents/rules/（领域规则拆分）
Level 2 → + .agents/ 完整目录（skills, workflows, scripts, templates, docs）
Level 3 → + world.toml（世界声明 + kernel/fragments 分层）
Level 4 → + 多世界继承 + roles/teams（协作元模型）
```

各级别适用场景与核心收益：

| 级别 | 适用场景 | 典型规模 | 核心收益 |
|------|---------|---------|---------|
| Level 0 | 个人项目/快速原型 | 1人/<10文件 | 5秒上手，AI行为基线约束 |
| Level 1 | 团队协作 | 2-5人/中型代码库 | 按领域隔离规则 |
| Level 2 | 技能驱动 | 5-20人/含自动化 | 技能+工作流标准化管理 |
| Level 3 | 治理级 | 20+人/开源 | 内核保护+可插拔能力 |
| Level 4 | 多团队/monorepo | 多团队/多子项目 | 规则继承+覆盖控制+角色治理 |

**五大设计目标**：
1. **渐进采纳**：从单文件（Level 0）到完整治理（Level 4），每级独立可用
2. **向下兼容**：Level 0 格式兼容 OpenAI Codex CLI 的 `AGENTS.md`
3. **向上扩展**：高级特性不破坏低级用法
4. **工具无关**：纯文件约定，不绑定特定 AI 工具
5. **物理隔离**：人类文档（`docs/`）与 AI 知识库（`.agents/docs/`）分离
