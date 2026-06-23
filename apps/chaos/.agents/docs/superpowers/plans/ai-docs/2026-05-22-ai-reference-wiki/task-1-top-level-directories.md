# Task 1: Create Top-Level Wiki Directories And Index Pages

**Files:**
- Create: `.agents/docs/references/README.md`
- Create: `.agents/docs/issue-patterns/README.md`
- Create: `.agents/docs/integrations/README.md`
- Create: `.agents/docs/sources/README.md`
- Create: `.agents/docs/templates/reference-page-template.md`

- [ ] **Step 1: Create the directory skeleton**

Run:
```bash
New-Item -ItemType Directory -Force `
  c:\Users\xinzo\OneDrive\Desktop\AI\Dao\spaces\AgentForge\.agents\docs\references, `
  c:\Users\xinzo\OneDrive\Desktop\AI\Dao\spaces\AgentForge\.agents\docs\issue-patterns, `
  c:\Users\xinzo\OneDrive\Desktop\AI\Dao\spaces\AgentForge\.agents\docs\integrations, `
  c:\Users\xinzo\OneDrive\Desktop\AI\Dao\spaces\AgentForge\.agents\docs\sources, `
  c:\Users\xinzo\OneDrive\Desktop\AI\Dao\spaces\AgentForge\.agents\docs\templates
```

- [ ] **Step 2: Write `references/README.md`**

Create `.agents/docs/references/README.md`:
```md
# AI Reference Wiki

该目录存放经过提炼、适合 agent 直接阅读的主题知识页。

## 目录职责

- `python/`：沉淀 Python 包、运行时特性与排障相关的参考知识。
- `podman/`：沉淀 Podman 命令、容器场景和常见故障的参考知识。

## 使用原则

- 优先放“已经提炼过”的知识，不直接堆原始抓取结果。
- 页面尽量围绕单一主题，避免一个文件混入多个问题域。
- 如果内容仍是原始资料，放到 `../sources/`。

## 当前入口

- [Python](./python/README.md)
- [Podman](./podman/README.md)
```

- [ ] **Step 3: Write `issue-patterns/README.md`**

Create `.agents/docs/issue-patterns/README.md`:
```md
# Issue Patterns

该目录存放按“现象 -> 原因 -> 排查 -> 定位文件/命令”组织的故障模式文档。

## 目录职责

- `python-errors.md`：记录 Python 依赖、测试、类型、版本适配等问题的排查模式。
- `podman-errors.md`：记录 Podman 构建、运行、挂载、网络、权限等问题的排查模式。

## 使用原则

- 一条问题模式只描述一个主要故障。
- 优先写清楚触发条件、排查步骤和优先检查的文件。
- 避免把大段概念说明塞进这里，概念说明应放到 `../references/`。
```

- [ ] **Step 4: Write `integrations/README.md`**

Create `.agents/docs/integrations/README.md`:
```md
# Integrations

该目录存放外部知识与 AgentForge 仓库内部实现之间的映射说明。

## 目录职责

- `python-in-agentforge.md`：说明 Python 相关知识在仓库中的模块落点和排查入口。
- `podman-in-agentforge.md`：说明 Podman 相关知识在仓库中的脚本、工作流或运行环境映射。

## 使用原则

- 回答“这个知识在项目里哪里相关”。
- 明确优先检查的代码、脚本、配置文件和工作流。
- 不重复撰写外部知识本身，尽量链接到 `../references/`。
```

- [ ] **Step 5: Write `sources/README.md`**

Create `.agents/docs/sources/README.md`:
```md
# Raw Sources

该目录存放尚未完全提炼的原始资料、抓取结果或工作底稿。

## 目录职责

- `python/`：存放 Python 包官方文档摘录、抓取页面或初步整理材料。
- `podman/`：存放 Podman 官方文档摘录、抓取页面或初步整理材料。

## 使用原则

- 原始资料不作为 agent 默认优先阅读入口。
- 每份资料尽量记录来源链接、版本和抓取时间。
- 当资料被整理成稳定知识后，应在 `../references/` 中生成精炼页面。
```

- [ ] **Step 6: Write `reference-page-template.md`**

Create `.agents/docs/templates/reference-page-template.md`:
```md
# Topic Title

## Goal

一句话说明该页解决什么问题。

## Relevance In AgentForge

- 关联模块：
- 常见触发场景：
- 优先检查文件：

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

- [ ] **Step 7: Review the top-level pages**

Run:
```bash
Get-ChildItem c:\Users\xinzo\OneDrive\Desktop\AI\Dao\spaces\AgentForge\.agents\docs -Recurse `
  | Where-Object { $_.FullName -match "references|issue-patterns|integrations|sources|templates" } `
  | Select-Object FullName
```

Expected: newly created directories and five Markdown files are listed.

- [ ] **Step 8: Commit**

```bash
git add .agents/docs/references .agents/docs/issue-patterns .agents/docs/integrations .agents/docs/sources .agents/docs/templates
git commit -m "docs: add AI reference wiki root structure"
```
