# Overview

**Goal:** 将已确认的“记忆、做梦”知识协议从独立文档资产推进为可发现、可试用、可验证、可回流的 AgentForge 认知协议。

**Architecture:** 实施分为四个串联文档单元：先确认协议四件套已经存在并与设计一致，再把参考协议页接入 AI 文档导航，然后创建一个最小 `.trae` 试点工作台，最后用试点结果决定是否回流到规则、模板或参考页。整个过程只修改 `.agents/docs/` 与 `.trae/` 下的文档资产，不触碰 `src/taolib/` 运行时代码。

**Tech Stack:** Markdown, Mermaid, AgentForge `.agents/` conventions, `.trae` workspace structure, mise task runner, pre-commit
