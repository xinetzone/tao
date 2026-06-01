# 21. 工程落地差距

| 方向 | AgentForge 现状 | 主流做法 | 差距 |
|------|----------------|----------|------|
| 条件加载 | 路由表（依赖AI主动） | glob frontmatter（工具自动） | 可叠加 glob |
| 强制执行 | 全是指导性 Markdown | hooks+permissions | 缺"约定变强制"层 |
| 技能参数 | SKILL.md 静态 | frontmatter+$ARGUMENTS | 缺动态参数 |
| 子智能体记忆 | 手动沉淀模板 | 自动维护 MEMORY.md | 缺自动化闭环 |
| 跨工具兼容 | 仅自研 | AGENTS.md 30+工具通用 | 入口兼容，目录需桥接 |
