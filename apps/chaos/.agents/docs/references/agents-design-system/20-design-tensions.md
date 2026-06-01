# 20. 设计张力与反思

## 20.1 张力一：复杂度 vs 简约性

设计哲学声称"大道至简"，但实际体系相当复杂——world.toml 有 kernel/fragments/capabilities/memory 四层、11 个 rules 文件、4 个角色、registry 机制。对于小团队或个人项目，治理成本可能超过开发效率收益。**关键问题**：什么场景下复杂体系才能真正值回票价？

## 20.2 张力二：跨工具兼容性

AI 编码工具生态正在走向事实标准化（Codex 用 AGENTS.md、Anthropic 用 CLAUDE.md、Cursor 用 .cursor/rules/）。AgentForge 的 AGENTS.md 名称与 Codex 约定重合，但内容结构远超 Codex 预期——其他 AI 工具读取时可能无法理解路由表和 `.agents/` 的深层引用。

## 20.3 张力三：docs/ vs .agents/docs/ 双轨隔离

人类看 `docs/`，AI 看 `.agents/docs/`，物理隔离设计前卫，但实际中很多知识是通用的（如架构说明、API 文档），是否需要两套？主流做法是在同一文档中用 `<!-- AI: ... -->` 标注或 frontmatter 区分受众。

## 20.4 张力四：通用标准 vs 内部治理体系

AgentForge 本质上在定义"AI 原生操作系统"的文件约定层——`world.toml` ≈ 操作系统描述、`kernel/` ≈ 微内核、`fragments/` ≈ 内核模块、`capabilities/` ≈ 用户态应用、`roles/teams/` ≈ 权限与进程模型、`registry.toml` ≈ 包管理器源配置、`memory/` ≈ 持久化存储。理念有前瞻性，但采纳门槛远高于主流"一个文件搞定"方案。**核心战略问题**：是成为通用标准，还是作为项目自身的内部治理体系？
