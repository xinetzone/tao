# 📖 项目介绍

## 定位

**taolib** 是 AgentForge 项目的核心 Python 包，定位为 **AI 驱动开发模板库**（AI-Driven Development Template Library）。

它不仅是一个可安装的 Python 库，更是一套可复用的工程化骨架。其目标是为人类开发者与 AI 智能体的协作提供标准化的基础设施，降低沟通成本、统一执行规范，并确保项目在长期演进中保持结构清晰、规则一致。

## 核心能力

### 1. GitHub App Token 管理

提供生产级的 GitHub App 安装令牌生命周期管理：

- **自动签发**：基于 RSA 私钥动态生成 JWT，向 GitHub API 请求安装令牌
- **策略感知**：支持 `X-GitHub-Stateless-S2S-Token` 请求级覆盖头，在 Stateful 与 Stateless Token 之间灵活切换
- **环境适配**：自动识别 GitHub Cloud 与 GitHub Enterprise Server（GHES）环境，在 GHES 场景下自动降级策略
- **Singleflight 缓存**：通过内存缓存与异步锁机制，避免并发场景下的重复请求与令牌竞争

相关模块：`taolib.github_app`

### 2. 智能体契约体系

项目通过 `.agents/` 目录与 `AGENTS.md` 构建了完整的 AI 协作契约：

- **上下文路由**：AI 助手按任务类型自动路由到对应规范文件（前端、后端、技能开发等）
- **人机隔离**：`.agents/docs/` 专门面向 AI，与面向人类的 `docs/` 物理隔离，防止上下文污染
- **知识沉淀**：技能规格、复盘报告等长期资产统一归档，形成可复用的知识图谱
- **双向同步**：`.agents/` 发生结构性变更时，自动同步更新 `docs/` 中的人类可读说明

### 3. 文档构建基础设施

深度集成 Sphinx / MyST Parser / Jupyter Book 生态：

- 支持 MyST Markdown 全特性（指令、角色、交叉引用等）
- 内置 Mermaid 图表渲染、代码复制按钮、BibTeX 文献引用
- 多层级模块化日志追踪（项目级、技能级、月度变更）
- Read the Docs 与 GitHub Pages 双托管就绪

## 设计哲学

> **极致简约、大道至简**

本项目以马王堆帛书版《道德经》为哲学底座，将"反者道之动，弱者道之用"作为底层设计逻辑的重要依据。

```{mermaid}
flowchart LR
    A["马王堆帛书《道德经》"] --> B["哲学内核"]
    B --> C["极简设计原则"]
    C --> D["技术实施方案"]
    D --> E["业务场景落地"]
```

这一主路径体现了从原始文本内涵到技术与业务落地的完整映射：

- **少即是多**：目录分层最小化、规则表达最简化，去除任何无必要的抽象层
- **顺势而为**：工具链选型遵循社区主流趋势（mise / uv / ruff / pytest），不逆势造轮子
- **虚实相生**：AI 专属资产与人类文档物理隔离，却在变更时双向同步，形成有机整体

## 快速导航

| 文档 | 说明 |
|------|------|
| [快速开始](quickstart.md) | 环境初始化与首次接入指南 |
| [核心功能](features.md) | 目录结构、`.agents/` 详解与权限规范 |
| [GitHub App Token 覆盖头](github-app-token-override.md) | S2S Token 策略、兼容性约束与工程启发 |
| {doc}`API 参考 </tech/api/taolib/index>` | `taolib` 各模块的类、函数与 CLI 用法（由 sphinx-autoapi 自动生成） |
| [构建约定](build-conventions.md) | PDM、uv、mise 配置与日常构建命令 |
| [部署指南](deploy.md) | 文档托管、CI/CD 与发布流程 |
| [贡献规范](contributing.md) | PR 流程、代码审查与测试要求 |
| [更新日志](changelog.md) | 项目级变更索引与月度变更记录 |
