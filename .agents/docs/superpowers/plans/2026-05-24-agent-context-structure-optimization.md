# Agent Context Structure Optimization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将智能体入口契约压缩为轻量路由，并将高频细则拆分到专题规则文件，降低默认上下文消耗。

**Architecture:** `AGENTS.md` 作为最高优先级入口，仅保留不可违背规则、任务路由和索引；`.agents/rules/` 承载上下文节省、文档治理、Python 规则等专题细则；`.agents/README.md` 保持目录说明职责并补充规则导航。

**Tech Stack:** Markdown、Mermaid、项目既有 `.agents/` 文档体系。

---

### Task 1: 新增专题规则文件

**Files:**
- Create: `.agents/rules/context-economy.md`
- Create: `.agents/rules/documentation.md`
- Create: `.agents/rules/python.md`

- [ ] 新增 `context-economy.md`，承载先搜后读、长材料预处理、输出预算、稳定摘要沉淀等规则。
- [ ] 新增 `documentation.md`，承载人类文档与 AI 文档边界、spec/plan/retrospective 归档、临时产物、同步机制等规则。
- [ ] 新增 `python.md`，承载 uv、Python 导入、版本适配路由等规则。

### Task 2: 精简入口契约

**Files:**
- Modify: `AGENTS.md`

- [ ] 将 `AGENTS.md` 改为最高优先级入口和路由索引。
- [ ] 删除或下沉路径独立性、Python 导入、文档归档、中间产物治理的长细则。
- [ ] 在上下文路由中加入上下文节省、文档治理、Python 开发/适配对应规则。
- [ ] 保留哲学驱动、Mermaid 优先、中文沟通、uv 等不可违背核心约束。

### Task 3: 更新 `.agents/README.md` 导航

**Files:**
- Modify: `.agents/README.md`

- [ ] 在阅读导航中说明 `rules/` 已承载 context-economy、documentation、python、skills 等专题规则。
- [ ] 避免大幅扩写，只补充必要导航。

### Task 4: 验证文档结构

**Files:**
- Read: `AGENTS.md`
- Read: `.agents/README.md`
- Read: `.agents/rules/context-economy.md`
- Read: `.agents/rules/documentation.md`
- Read: `.agents/rules/python.md`

- [ ] 检查所有项目内链接为相对路径。
- [ ] 检查 Mermaid 使用基础语法。
- [ ] 检查无 TBD/TODO 占位。
- [ ] 运行 `git status --short` 确认改动范围。
