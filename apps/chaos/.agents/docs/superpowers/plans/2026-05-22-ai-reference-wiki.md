# AI Reference Wiki Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 `.agents/docs/` 下创建一套面向 AI 的参考 wiki 骨架，覆盖 `references`、`issue-patterns`、`integrations`、`sources` 和 `templates` 五类文档资产。

**Architecture:** 保持现有 `docs/` 与 `.agents/docs/` 的边界不变，只在 `.agents/docs/` 下新增参考知识区。通过分层目录、各级 `README.md`、种子页和统一模板，形成“导航页 + 主题页 + 来源页”的稳定结构，方便 agent 快速检索与后续持续补充内容。

**Tech Stack:** Markdown, AgentForge `.agents/` conventions, VS Code diagnostics

---

### Task 1: Create Top-Level Wiki Directories And Index Pages

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

---

### Task 2: Add Python And Podman Reference Entry Points

**Files:**
- Create: `.agents/docs/references/python/README.md`
- Create: `.agents/docs/references/python/package-index.md`
- Create: `.agents/docs/references/podman/README.md`
- Create: `.agents/docs/references/podman/command-cheatsheet.md`

- [ ] **Step 1: Create the topic directories**

Run:
```bash
New-Item -ItemType Directory -Force `
  c:\Users\xinzo\OneDrive\Desktop\AI\Dao\spaces\AgentForge\.agents\docs\references\python, `
  c:\Users\xinzo\OneDrive\Desktop\AI\Dao\spaces\AgentForge\.agents\docs\references\podman
```

- [ ] **Step 2: Write `references/python/README.md`**

Create `.agents/docs/references/python/README.md`:
```md
# Python References

该目录存放与 AgentForge 排障和实现相关的 Python 参考知识。

## 建议收录范围

- 常用依赖包，如 `pytest`、`httpx`、`pydantic`
- Python 版本兼容与类型系统要点
- 测试、异步、打包和依赖管理相关知识

## 当前页面

- [Package Index](./package-index.md)
```

- [ ] **Step 3: Write `references/python/package-index.md`**

Create `.agents/docs/references/python/package-index.md`:
```md
# Python Package Index

## Goal

记录 AgentForge 中值得为 agent 建立专门参考页的 Python 包与主题。

## Relevance In AgentForge

- 关联模块：`src/taolib/`、`tests/`、`pyproject.toml`
- 常见触发场景：依赖升级、测试失败、类型问题、网络请求行为变化
- 优先检查文件：`pyproject.toml`、`src/taolib/github_app/`、`tests/github_app/`

## Current Candidates

- `pytest`：测试组织、夹具、异步测试。
- `httpx`：GitHub App HTTP 客户端相关请求行为。
- `PyJWT`：GitHub App JWT 签发与认证链路。
- `PyGithub`：对象化 GitHub API 访问适配层。

## Next Suggested Pages

- `pytest.md`
- `httpx.md`
- `pyjwt.md`
- `pygithub.md`

## Sources

- 官方文档：待补充
- 版本：按仓库依赖锁定版本补充
- 抓取时间：待补充
```

- [ ] **Step 4: Write `references/podman/README.md`**

Create `.agents/docs/references/podman/README.md`:
```md
# Podman References

该目录存放与容器构建、运行、挂载、网络和权限相关的 Podman 参考知识。

## 建议收录范围

- 常用命令速查
- 与 Docker 的差异点
- Rootless、挂载、网络和排障要点

## 当前页面

- [Command Cheatsheet](./command-cheatsheet.md)
```

- [ ] **Step 5: Write `references/podman/command-cheatsheet.md`**

Create `.agents/docs/references/podman/command-cheatsheet.md`:
```md
# Podman Command Cheatsheet

## Goal

为 agent 提供最常用的 Podman 命令入口，减少在排障时反复查找基础命令的成本。

## Relevance In AgentForge

- 关联模块：容器化工作流、开发环境脚本、后续可能引入的本地运行说明
- 常见触发场景：镜像构建失败、容器未启动、日志查看、挂载路径错误
- 优先检查文件：相关脚本、工作流配置、后续补充的集成说明页

## Common Commands

```bash
podman build -t my-image .
podman run --rm -it my-image
podman ps -a
podman logs <container>
podman exec -it <container> /bin/sh
podman rm -f <container>
podman image ls
```

## Common Problems

### 问题：容器存在但没有按预期启动

- 现象：`podman ps -a` 可以看到容器，但状态异常或快速退出。
- 原因：入口命令错误、环境变量缺失、挂载失败或权限不足。
- 排查步骤：先看 `podman logs`，再检查挂载参数和启动命令。
- 相关命令或代码位置：`podman logs <container>`、启动脚本或工作流文件。

## Sources

- 官方文档：待补充
- 版本：按本地或 CI 使用版本补充
- 抓取时间：待补充
```

- [ ] **Step 6: Run a quick file check**

Run:
```bash
Get-ChildItem c:\Users\xinzo\OneDrive\Desktop\AI\Dao\spaces\AgentForge\.agents\docs\references -Recurse `
  | Select-Object FullName
```

Expected: `python/README.md`, `python/package-index.md`, `podman/README.md`, and `podman/command-cheatsheet.md` are present.

- [ ] **Step 7: Commit**

```bash
git add .agents/docs/references/python .agents/docs/references/podman
git commit -m "docs: add Python and Podman reference entry pages"
```

---

### Task 3: Add Issue Patterns And Project Integration Pages

**Files:**
- Create: `.agents/docs/issue-patterns/python-errors.md`
- Create: `.agents/docs/issue-patterns/podman-errors.md`
- Create: `.agents/docs/integrations/python-in-agentforge.md`
- Create: `.agents/docs/integrations/podman-in-agentforge.md`

- [ ] **Step 1: Write `python-errors.md`**

Create `.agents/docs/issue-patterns/python-errors.md`:
```md
# Python Error Patterns

## Pattern 1: Optional Dependency Not Installed

- 现象：运行时出现 `ModuleNotFoundError` 或导入失败。
- 常见原因：可选依赖未安装、依赖组未同步、环境切换后锁文件未生效。
- 排查步骤：
  1. 检查 `pyproject.toml` 中对应依赖组。
  2. 检查 `uv.lock` 是否包含目标依赖。
  3. 使用 `uv run` 在项目环境内复现。
- 优先检查文件：`pyproject.toml`、`uv.lock`

## Pattern 2: Python Version Compatibility Regression

- 现象：升级 Python 版本后测试失败或 API 行为变化。
- 常见原因：标准库行为调整、第三方包兼容性不足、类型检查假设失效。
- 排查步骤：
  1. 阅读 `.agents/docs/version-tracking.md`
  2. 运行 `.agents/scripts/check_python_compat.py`
  3. 运行 `.agents/scripts/check_python_deprecations.py`
- 优先检查文件：`.agents/docs/version-tracking.md`、`.agents/scripts/`
```

- [ ] **Step 2: Write `podman-errors.md`**

Create `.agents/docs/issue-patterns/podman-errors.md`:
```md
# Podman Error Patterns

## Pattern 1: Mount Or Path Mapping Failure

- 现象：容器内看不到预期文件，或启动时报路径不存在。
- 常见原因：宿主机路径错误、Windows 路径格式不匹配、权限或标签设置问题。
- 排查步骤：
  1. 核对宿主机实际路径。
  2. 重新检查 `podman run -v` 参数。
  3. 查看容器日志并进入容器内确认挂载结果。
- 优先命令：`podman run`, `podman exec`, `podman inspect`

## Pattern 2: Container Exits Immediately

- 现象：容器创建成功但立刻退出。
- 常见原因：入口命令错误、依赖服务缺失、环境变量未传入。
- 排查步骤：
  1. 执行 `podman logs <container>`
  2. 检查入口命令和参数
  3. 验证环境变量与挂载目录
- 优先命令：`podman logs`, `podman inspect`
```

- [ ] **Step 3: Write `python-in-agentforge.md`**

Create `.agents/docs/integrations/python-in-agentforge.md`:
```md
# Python In AgentForge

## Goal

说明 Python 相关外部知识在 AgentForge 仓库中的主要落点，帮助 agent 快速从问题跳到代码和配置。

## Primary Files

- `pyproject.toml`：依赖组、Python 版本范围和工具配置入口。
- `src/taolib/`：核心 Python 代码。
- `tests/`：行为验证与回归测试。
- `.agents/docs/version-tracking.md`：Python 版本适配知识沉淀。

## Common Navigation Paths

- 依赖问题：先看 `pyproject.toml` 与 `uv.lock`
- GitHub App 认证问题：先看 `src/taolib/github_app/`
- 测试失败：先看 `tests/github_app/` 和对应模块
- 版本兼容问题：先看 `.agents/docs/version-tracking.md` 与 `.agents/scripts/`

## Related References

- `../references/python/package-index.md`
- `../issue-patterns/python-errors.md`
```

- [ ] **Step 4: Write `podman-in-agentforge.md`**

Create `.agents/docs/integrations/podman-in-agentforge.md`:
```md
# Podman In AgentForge

## Goal

说明 Podman 相关知识在 AgentForge 中的当前和潜在落点，帮助 agent 判断何时需要参考容器文档。

## Current Assessment

- 当前仓库中尚未形成明显的 Podman 专用脚本或完整容器工作流。
- Podman 相关知识目前更适合作为通用运行环境与排障能力储备。

## Suggested Future Mapping

- 若后续引入本地容器开发脚本，优先记录到 `scripts/`
- 若后续引入 CI 容器构建流程，优先记录到 `.github/workflows/`
- 若后续引入开发文档，再同步到面向人类的 `docs/`

## Related References

- `../references/podman/command-cheatsheet.md`
- `../issue-patterns/podman-errors.md`
```

- [ ] **Step 5: Run a structure check**

Run:
```bash
Get-ChildItem c:\Users\xinzo\OneDrive\Desktop\AI\Dao\spaces\AgentForge\.agents\docs\issue-patterns, `
  c:\Users\xinzo\OneDrive\Desktop\AI\Dao\spaces\AgentForge\.agents\docs\integrations `
  | Select-Object FullName
```

Expected: the four new Markdown files are listed.

- [ ] **Step 6: Commit**

```bash
git add .agents/docs/issue-patterns .agents/docs/integrations
git commit -m "docs: add issue patterns and integration maps for AI wiki"
```

---

### Task 4: Add Raw Source Topic Entrypoints And Validate The Structure

**Files:**
- Create: `.agents/docs/sources/python/README.md`
- Create: `.agents/docs/sources/podman/README.md`

- [ ] **Step 1: Create the raw source topic directories**

Run:
```bash
New-Item -ItemType Directory -Force `
  c:\Users\xinzo\OneDrive\Desktop\AI\Dao\spaces\AgentForge\.agents\docs\sources\python, `
  c:\Users\xinzo\OneDrive\Desktop\AI\Dao\spaces\AgentForge\.agents\docs\sources\podman
```

- [ ] **Step 2: Write `sources/python/README.md`**

Create `.agents/docs/sources/python/README.md`:
```md
# Python Raw Sources

该目录用于存放 Python 官方文档摘录、网页抓取结果和整理前的工作底稿。

## 使用规则

- 保留原始来源链接
- 标注抓取时间和版本
- 整理完成后，在 `../../references/python/` 中创建精炼页面
```

- [ ] **Step 3: Write `sources/podman/README.md`**

Create `.agents/docs/sources/podman/README.md`:
```md
# Podman Raw Sources

该目录用于存放 Podman 官方文档摘录、网页抓取结果和整理前的工作底稿。

## 使用规则

- 保留原始来源链接
- 标注抓取时间和版本
- 整理完成后，在 `../../references/podman/` 中创建精炼页面
```

- [ ] **Step 4: Run diagnostics on the new Markdown files**

Check with the editor diagnostics tool for:

```text
file:///c:/Users/xinzo/OneDrive/Desktop/AI/Dao/spaces/AgentForge/.agents/docs/references/README.md
file:///c:/Users/xinzo/OneDrive/Desktop/AI/Dao/spaces/AgentForge/.agents/docs/references/python/README.md
file:///c:/Users/xinzo/OneDrive/Desktop/AI/Dao/spaces/AgentForge/.agents/docs/references/python/package-index.md
file:///c:/Users/xinzo/OneDrive/Desktop/AI/Dao/spaces/AgentForge/.agents/docs/references/podman/README.md
file:///c:/Users/xinzo/OneDrive/Desktop/AI/Dao/spaces/AgentForge/.agents/docs/references/podman/command-cheatsheet.md
file:///c:/Users/xinzo/OneDrive/Desktop/AI/Dao/spaces/AgentForge/.agents/docs/issue-patterns/README.md
file:///c:/Users/xinzo/OneDrive/Desktop/AI/Dao/spaces/AgentForge/.agents/docs/issue-patterns/python-errors.md
file:///c:/Users/xinzo/OneDrive/Desktop/AI/Dao/spaces/AgentForge/.agents/docs/issue-patterns/podman-errors.md
file:///c:/Users/xinzo/OneDrive/Desktop/AI/Dao/spaces/AgentForge/.agents/docs/integrations/README.md
file:///c:/Users/xinzo/OneDrive/Desktop/AI/Dao/spaces/AgentForge/.agents/docs/integrations/python-in-agentforge.md
file:///c:/Users/xinzo/OneDrive/Desktop/AI/Dao/spaces/AgentForge/.agents/docs/integrations/podman-in-agentforge.md
file:///c:/Users/xinzo/OneDrive/Desktop/AI/Dao/spaces/AgentForge/.agents/docs/sources/README.md
file:///c:/Users/xinzo/OneDrive/Desktop/AI/Dao/spaces/AgentForge/.agents/docs/sources/python/README.md
file:///c:/Users/xinzo/OneDrive/Desktop/AI/Dao/spaces/AgentForge/.agents/docs/sources/podman/README.md
file:///c:/Users/xinzo/OneDrive/Desktop/AI/Dao/spaces/AgentForge/.agents/docs/templates/reference-page-template.md
```

Expected: no Markdown diagnostics requiring immediate fixes.

- [ ] **Step 5: Run a final tree check**

Run:
```bash
Get-ChildItem c:\Users\xinzo\OneDrive\Desktop\AI\Dao\spaces\AgentForge\.agents\docs -Recurse `
  | Where-Object { $_.FullName -match "references|issue-patterns|integrations|sources|templates" } `
  | Select-Object FullName
```

Expected: the final output includes all planned directories and files, with no unexpected extra locations outside `.agents/docs/`.

- [ ] **Step 6: Commit**

```bash
git add .agents/docs/sources .agents/docs/templates
git commit -m "docs: add source staging area and template for AI wiki"
```

---

### Task 5: Optional Follow-Up Seed Pages

**Files:**
- Create: `.agents/docs/references/python/pytest.md`
- Create: `.agents/docs/references/python/httpx.md`
- Create: `.agents/docs/references/podman/rootless.md`

- [ ] **Step 1: Decide whether to keep the first iteration minimal**

If the goal is only to land the approved skeleton, skip this task.

If adding seed pages now, continue with the next steps.

- [ ] **Step 2: Write `pytest.md`**

Create `.agents/docs/references/python/pytest.md`:
```md
# pytest

## Goal

沉淀 AgentForge 中与测试失败排查最相关的 `pytest` 使用知识。

## Relevance In AgentForge

- 关联模块：`tests/`
- 常见触发场景：单元测试失败、夹具行为异常、异步测试问题
- 优先检查文件：`tests/github_app/`

## Key Concepts

- 夹具用于共享测试准备逻辑
- `pytest.mark.asyncio` 用于异步测试

## Sources

- 官方文档：待补充
- 版本：待补充
- 抓取时间：待补充
```

- [ ] **Step 3: Write `httpx.md`**

Create `.agents/docs/references/python/httpx.md`:
```md
# httpx

## Goal

沉淀 AgentForge 中与 HTTP 请求行为和客户端交互最相关的 `httpx` 使用知识。

## Relevance In AgentForge

- 关联模块：`src/taolib/github_app/client.py`
- 常见触发场景：请求头异常、超时、响应解析失败
- 优先检查文件：`src/taolib/github_app/client.py`

## Key Concepts

- 请求头注入
- 异步请求与响应对象

## Sources

- 官方文档：待补充
- 版本：待补充
- 抓取时间：待补充
```

- [ ] **Step 4: Write `rootless.md`**

Create `.agents/docs/references/podman/rootless.md`:
```md
# Podman Rootless

## Goal

沉淀 rootless 模式下最常见的 Podman 使用限制与排障要点。

## Relevance In AgentForge

- 关联模块：本地开发环境与潜在容器运行脚本
- 常见触发场景：权限不足、挂载异常、网络行为差异
- 优先检查文件：后续容器脚本与集成说明页

## Key Concepts

- rootless 依赖当前用户权限
- 挂载与网络行为可能与 rootful 模式不同

## Sources

- 官方文档：待补充
- 版本：待补充
- 抓取时间：待补充
```

- [ ] **Step 5: Commit**

```bash
git add .agents/docs/references/python/pytest.md .agents/docs/references/python/httpx.md .agents/docs/references/podman/rootless.md
git commit -m "docs: add optional seed reference pages for AI wiki"
```
