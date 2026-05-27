# AI Docs Search Keyword Convention Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为 `.agents/docs` 建立可执行的检索关键词约定，通过增强总 README 和参考页模板，让后续新增页面更利于 agent 检索。

**Architecture:** 本次只修改两个 Markdown 文件：`.agents/docs/README.md` 和 `.agents/docs/templates/reference-page-template.md`。前者承载总规则摘要，后者承载具体写作骨架；二者共同形成“总规则 + 模板落地”的闭环，而不修改现有内容页。

**Tech Stack:** Markdown, AgentForge `.agents/` conventions, VS Code diagnostics, Git

---

### Task 1: Add Search Keyword Rules To `.agents/docs/README.md`

**Files:**
- Modify: `.agents/docs/README.md`

- [ ] **Step 1: Read the current README**

Run:
```bash
Get-Content c:\Users\xinzo\OneDrive\Desktop\AI\Dao\spaces\AgentForge\.agents\docs\README.md
```

Expected: the file already contains `知识区地图`、`按场景导航`、`Agent 检索约定`、`新增页面放置规则` and ends with `约定`.

- [ ] **Step 2: Insert the `检索关键词约定` section before `## 约定`**

Update `.agents/docs/README.md` by inserting this exact block immediately before the existing `## 约定` heading:
```md
## 检索关键词约定

为提升 agent 的检索命中率，后续新增 wiki 页面应遵循以下规则：

- 页面标题优先使用主关键词，不使用 `notes`、`misc`、`advanced`、`实践记录` 这类弱语义标题
- 新页面优先复用固定章节名，避免在不同页面中混用 `Goal`、`Purpose`、`Why This Exists` 等近义表达
- 每个参考页应包含 `Search Keywords` 区块，用于集中收纳主关键词、英文术语、常见别名和错误短语
- 每个参考页应包含 `Trigger Phrases` 区块，用于覆盖用户或 agent 可能提出的自然语言问题
- 首次出现的重要术语建议采用中英文双写，例如 `挂载 (mount)`、`依赖组 (dependency group)`
- 错误页应同时覆盖“现象词”和“原因词”，例如报错短语、失败现象和定位线索
```

- [ ] **Step 3: Verify the inserted section is in the correct position**

Run:
```bash
Get-Content c:\Users\xinzo\OneDrive\Desktop\AI\Dao\spaces\AgentForge\.agents\docs\README.md
```

Expected: the new `## 检索关键词约定` section appears after `## 新增页面放置规则` and before `## 约定`.

- [ ] **Step 4: Run diagnostics on the README**

Check:
```text
file:///c:/Users/xinzo/OneDrive/Desktop/AI/Dao/spaces/AgentForge/.agents/docs/README.md
```

Expected: no Markdown diagnostics requiring immediate fixes.

- [ ] **Step 5: Commit**

```bash
git add .agents/docs/README.md
git commit -m "docs(agents): add search keyword rules"
```

---

### Task 2: Upgrade The Reference Page Template For Search-Friendly Writing

**Files:**
- Modify: `.agents/docs/templates/reference-page-template.md`

- [ ] **Step 1: Read the current template**

Run:
```bash
Get-Content c:\Users\xinzo\OneDrive\Desktop\AI\Dao\spaces\AgentForge\.agents\docs\templates\reference-page-template.md
```

Expected: the file currently starts with `# Topic Title`, then `Goal`, `Relevance In AgentForge`, `Key Concepts`, `Common Problems`, `Commands Or Snippets`, `Sources`.

- [ ] **Step 2: Replace the template with the search-friendly version**

Update `.agents/docs/templates/reference-page-template.md` to exactly:
```md
# Topic Title

## Search Keywords

- 主关键词：
- 英文术语：
- 常见别名：
- 错误短语：

## Goal

一句话说明该页解决什么问题，并尽量包含主关键词。

## Relevance In AgentForge

- 关联模块：
- 常见触发场景：
- 优先检查文件：

## Trigger Phrases

- 用户可能会如何提问 1
- 用户可能会如何提问 2

## Key Concepts

- 概念 A：
- 概念 B：

## Common Problems

### 问题：示例

- 现象：
- 原因：
- 排查步骤：
- 相关命令或代码位置：

## Commands Or Snippets

```bash
# example
```

## Sources

- 官方文档：
- 版本：
- 抓取时间：
```

- [ ] **Step 3: Verify the new structure**

Run:
```bash
Get-Content c:\Users\xinzo\OneDrive\Desktop\AI\Dao\spaces\AgentForge\.agents\docs\templates\reference-page-template.md
```

Expected: the template now contains `Search Keywords` and `Trigger Phrases`, while still preserving `Relevance In AgentForge`, `Common Problems`, and `Sources`.

- [ ] **Step 4: Run diagnostics on the template**

Check:
```text
file:///c:/Users/xinzo/OneDrive/Desktop/AI/Dao/spaces/AgentForge/.agents/docs/templates/reference-page-template.md
```

Expected: no Markdown diagnostics requiring immediate fixes.

- [ ] **Step 5: Commit**

```bash
git add .agents/docs/templates/reference-page-template.md
git commit -m "docs(agents): update wiki template for searchability"
```

---

### Task 3: Validate Rule-Template Consistency

**Files:**
- Modify: `.agents/docs/README.md`
- Modify: `.agents/docs/templates/reference-page-template.md`

- [ ] **Step 1: Compare the README rules with the template structure**

Run:
```bash
Get-Content c:\Users\xinzo\OneDrive\Desktop\AI\Dao\spaces\AgentForge\.agents\docs\README.md
Get-Content c:\Users\xinzo\OneDrive\Desktop\AI\Dao\spaces\AgentForge\.agents\docs\templates\reference-page-template.md
```

Expected: the README rules explicitly mention `Search Keywords`, `Trigger Phrases`, fixed section names, and bilingual terminology; the template exposes those exact structures.

- [ ] **Step 2: If needed, make only wording-level alignment edits**

If there is any mismatch, keep the edits constrained to the following intended language:

```md
- 每个参考页应包含 `Search Keywords` 区块，用于集中收纳主关键词、英文术语、常见别名和错误短语
- 每个参考页应包含 `Trigger Phrases` 区块，用于覆盖用户或 agent 可能提出的自然语言问题
```

```md
## Search Keywords

- 主关键词：
- 英文术语：
- 常见别名：
- 错误短语：
```

Do not add new files, directories, metadata systems, or sample pages in this task.

- [ ] **Step 3: Run a focused diff check**

Run:
```bash
git diff -- .agents/docs/README.md .agents/docs/templates/reference-page-template.md
```

Expected: the diff only shows the new README rule block and the template structure upgrade.

- [ ] **Step 4: Run final diagnostics on both files**

Check:
```text
file:///c:/Users/xinzo/OneDrive/Desktop/AI/Dao/spaces/AgentForge/.agents/docs/README.md
file:///c:/Users/xinzo/OneDrive/Desktop/AI/Dao/spaces/AgentForge/.agents/docs/templates/reference-page-template.md
```

Expected: both files have no diagnostics requiring immediate fixes.

- [ ] **Step 5: Commit any final wording refinement if Step 2 changed files after earlier commits**

If Step 2 produced any additional edits, run:
```bash
git add .agents/docs/README.md .agents/docs/templates/reference-page-template.md
git commit -m "docs(agents): align search keyword rules and template"
```

If Step 2 made no changes, skip this step.
