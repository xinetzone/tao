# AI Docs Navigation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 `.agents/docs/README.md` 升级为 AI 知识库总导航页，为现有 wiki 提供目录地图、按场景导航、检索约定和放置规则。

**Architecture:** 本次只修改 `.agents/docs/README.md` 一个文件，保留原有“AI 文档边界”说明，并在其后补充新导航结构。通过单入口文档把 `references`、`issue-patterns`、`integrations`、`sources` 和 `superpowers` 串联起来，避免再新增独立索引页。

**Tech Stack:** Markdown, AgentForge `.agents/` conventions, VS Code diagnostics, Git

---

### Task 1: Rewrite `.agents/docs/README.md` As The Single Navigation Hub

**Files:**
- Modify: `.agents/docs/README.md`

- [ ] **Step 1: Capture the current file as the baseline**

Run:
```bash
Get-Content c:\Users\xinzo\OneDrive\Desktop\AI\Dao\spaces\AgentForge\.agents\docs\README.md
```

Expected: the current file only contains the AI-docs boundary explanation and a short `约定` section.

- [ ] **Step 2: Replace the file with the new navigation structure**

Update `.agents/docs/README.md` to exactly:
```md
# 🤖 AI 专属文档 (AI-Specific Documentation)

该目录 (`.agents/docs/`) 是专门为 AI 智能体保留的知识库和分析文档存储区。

## 目录用途
与 `docs/`（面向人类开发者）不同，这里的文档旨在帮助 AI 更好地理解系统上下文、存储架构分析结果或沉淀执行过程中的知识图谱。通过这种物理隔离，我们确保了人类开发者的阅读体验不会被 AI 生成的冗长或高密度的机器可读数据所干扰。

## 知识区地图

| 目录 | 解决的问题 | 适合存放的内容 | 何时优先阅读 |
|------|------------|----------------|--------------|
| [`references/`](./references/) | 解释概念、命令和主题知识 | 提炼后的稳定知识页、速查页、主题说明 | 当你已经知道问题领域，但需要背景知识、命令或概念说明时 |
| [`issue-patterns/`](./issue-patterns/) | 提供按症状组织的排障路径 | 常见故障模式、触发条件、排查步骤、优先检查文件 | 当你已经遇到报错、失败或异常现象时 |
| [`integrations/`](./integrations/) | 说明外部知识与仓库代码的映射关系 | “在 AgentForge 里哪里相关”的导航页、代码落点说明 | 当你需要先判断问题与仓库中哪些模块、脚本或配置有关时 |
| [`sources/`](./sources/) | 保留原始资料和追溯入口 | 官方文档摘录、抓取结果、工作底稿 | 当你需要追溯原文、版本、抓取时间或尚未提炼的资料时 |
| [`superpowers/`](./superpowers/) | 沉淀历史设计、计划和复盘 | specs、plans、retrospectives 等长期资产 | 当你要理解历史决策、实施计划或复盘结论时 |

## 按场景导航

如果你遇到 Python 依赖、版本或测试问题：

1. 先看 [`integrations/python-in-agentforge.md`](./integrations/python-in-agentforge.md)
2. 再看 [`issue-patterns/python-errors.md`](./issue-patterns/python-errors.md)
3. 最后看 [`references/python/`](./references/python/)

如果你遇到 GitHub App 或 Python 模块排障问题：

1. 先看 [`integrations/python-in-agentforge.md`](./integrations/python-in-agentforge.md)
2. 再定位到 `src/taolib/github_app/` 和 `tests/github_app/`
3. 需要补背景时再看 [`references/python/package-index.md`](./references/python/package-index.md)

如果你遇到 Podman 运行、挂载或日志问题：

1. 先看 [`integrations/podman-in-agentforge.md`](./integrations/podman-in-agentforge.md)
2. 再看 [`issue-patterns/podman-errors.md`](./issue-patterns/podman-errors.md)
3. 最后看 [`references/podman/`](./references/podman/)

如果你需要追溯原始资料或官方文档：

1. 先确认对应主题是否已有提炼页
2. 若提炼页不足，再进入 [`sources/`](./sources/)
3. 只在需要原文、版本或抓取上下文时停留在 `sources/`

如果你需要理解历史设计、计划或复盘：

1. 进入 [`superpowers/`](./superpowers/)
2. 先看 `specs/` 理解设计意图
3. 再看 `plans/` 和 `retrospectives/` 理解执行路径和结果

## Agent 检索约定

为减少盲目翻找，agent 默认按以下顺序检索：

1. 先看 [`integrations/`](./integrations/)，判断问题与仓库的相关落点
2. 再看 [`issue-patterns/`](./issue-patterns/)，获取常见故障和排查路径
3. 再看 [`references/`](./references/)，补充概念、命令和背景知识
4. 最后看 [`sources/`](./sources/)，追溯原始资料
5. 若任务属于设计、规划或复盘，转到 [`superpowers/`](./superpowers/)

## 新增页面放置规则

- 原始抓取、网页摘录、工作底稿放在 [`sources/`](./sources/)
- 提炼后的稳定知识页放在 [`references/`](./references/)
- 以症状和排查路径为中心的页面放在 [`issue-patterns/`](./issue-patterns/)
- 将外部知识映射到仓库结构的页面放在 [`integrations/`](./integrations/)
- 设计、计划、复盘和长期经验沉淀继续放在 [`superpowers/`](./superpowers/)

## 约定

- 智能体可在此自由创建需要的 `.md` 或其他格式数据文档。
- 人类开发者通常无需直接阅读本目录下的内容。
- 新增 wiki 页面前，优先判断其属于 `references`、`issue-patterns`、`integrations` 还是 `sources`，避免混放。
```

- [ ] **Step 3: Verify the content matches the intended structure**

Run:
```bash
Get-Content c:\Users\xinzo\OneDrive\Desktop\AI\Dao\spaces\AgentForge\.agents\docs\README.md
```

Expected: the file contains `知识区地图`、`按场景导航`、`Agent 检索约定`、`新增页面放置规则` 四个新增区块，并保留原始边界说明。

- [ ] **Step 4: Run diagnostics on the edited file**

Check:
```text
file:///c:/Users/xinzo/OneDrive/Desktop/AI/Dao/spaces/AgentForge/.agents/docs/README.md
```

Expected: no Markdown diagnostics requiring immediate fixes.

- [ ] **Step 5: Commit**

```bash
git add .agents/docs/README.md
git commit -m "docs(agents): add AI docs navigation rules"
```

---

### Task 2: Validate Navigation Consistency Against Existing Wiki Entrypoints

**Files:**
- Modify: `.agents/docs/README.md`

- [ ] **Step 1: Inspect the linked entry files**

Run:
```bash
Get-Content c:\Users\xinzo\OneDrive\Desktop\AI\Dao\spaces\AgentForge\.agents\docs\integrations\python-in-agentforge.md
Get-Content c:\Users\xinzo\OneDrive\Desktop\AI\Dao\spaces\AgentForge\.agents\docs\issue-patterns\python-errors.md
Get-Content c:\Users\xinzo\OneDrive\Desktop\AI\Dao\spaces\AgentForge\.agents\docs\references\python\package-index.md
Get-Content c:\Users\xinzo\OneDrive\Desktop\AI\Dao\spaces\AgentForge\.agents\docs\integrations\podman-in-agentforge.md
Get-Content c:\Users\xinzo\OneDrive\Desktop\AI\Dao\spaces\AgentForge\.agents\docs\issue-patterns\podman-errors.md
Get-Content c:\Users\xinzo\OneDrive\Desktop\AI\Dao\spaces\AgentForge\.agents\docs\references\podman\command-cheatsheet.md
```

Expected: the linked files exist and their roles match the navigation order written in `.agents/docs/README.md`.

- [ ] **Step 2: Adjust any mismatched wording in `.agents/docs/README.md`**

If the inspection shows the README wording is too strong or mismatched, constrain the edits to these exact patterns:

```md
如果你遇到 Python 依赖、版本或测试问题：
1. 先看 [`integrations/python-in-agentforge.md`](./integrations/python-in-agentforge.md)
2. 再看 [`issue-patterns/python-errors.md`](./issue-patterns/python-errors.md)
3. 最后看 [`references/python/`](./references/python/)
```

```md
如果你遇到 Podman 运行、挂载或日志问题：
1. 先看 [`integrations/podman-in-agentforge.md`](./integrations/podman-in-agentforge.md)
2. 再看 [`issue-patterns/podman-errors.md`](./issue-patterns/podman-errors.md)
3. 最后看 [`references/podman/`](./references/podman/)
```

Do not add new directories, new files, or new navigation branches in this task.

- [ ] **Step 3: Run a final diff check**

Run:
```bash
git diff -- .agents/docs/README.md
```

Expected: the diff only shows the README upgrade and no unrelated file changes.

- [ ] **Step 4: Commit any final wording adjustment if needed**

If Step 2 changed the file after Task 1 commit, run:
```bash
git add .agents/docs/README.md
git commit -m "docs(agents): refine AI docs navigation wording"
```

If Step 2 made no changes, skip this step.
