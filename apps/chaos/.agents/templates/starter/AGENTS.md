# 🤖 智能体全局契约 (AGENTS Manifest)

> 本文件兼容 AGENTS.md 开放标准——OpenAI Codex、Cursor、Copilot 等 30+ 工具原生支持。
> AgentForge 扩展（.agents/ 目录、world.toml）完全可选，零依赖即可使用本文件。

## 全局核心规则

- **沟通语言**：使用中文与用户交流。
- **按需读取**：执行特定领域任务前，只读取与当前任务直接相关的 `.agents/` 规范。
- **代码修改**：遵循"约定优于配置"，优先参考现有代码风格和项目架构。

## 上下文路由

遇到以下任务时，先读取对应规范，再执行任务。

| 任务类型 | 必读入口 |
|---|---|
| Python 开发 | `.agents/rules/python.md` |
| 前端开发 | `.agents/rules/frontend.md` |
| 后端开发 | `.agents/rules/backend.md` |
| 文档治理 | `.agents/rules/documentation.md` |
