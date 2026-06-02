# Tasks

- [x] Task 1: 创建萃取文档目录结构与索引入口
  - 创建 `apps/chaos/.agents/docs/references/ai-libs/` 目录
  - 创建 `README.md` 索引导航文件，提供五篇文档的概览与跳转链接
  - 如 `apps/chaos/.agents/docs/references/` 已存在索引文件，按既有格式补充入口

- [x] Task 2: 编写 LangChain 核心架构分析文档
  - 文件路径：`apps/chaos/.agents/docs/references/ai-libs/01-langchain-core-analysis.md`
  - 内容要求：
    - 项目概览与定位（基础抽象层、Runnable 协议、LCEL）
    - 核心模块深度分析：消息系统、工具调用框架（BaseTool/StructuredTool）、提示词模板系统、回调/追踪系统、输出解析器
    - 架构图（Mermaid 类图展示 Runnable/BaseTool/BaseMessage 等核心抽象）
    - 关键代码示例提炼（如 LCEL 链式编排、自定义工具、消息流处理）
    - 大模型集成方案与多 Provider 支持机制
    - 适用业务场景与局限性分析

- [x] Task 3: 编写 LangGraph 核心架构分析文档
  - 文件路径：`apps/chaos/.agents/docs/references/ai-libs/02-langgraph-core-analysis.md`
  - 内容要求：
    - 项目概览与定位（状态化工作流引擎、BSP 计算模型）
    - 核心模块深度分析：StateGraph 构建器、Channel 系统（LastValue/BinaryOperatorAggregate/NamedBarrierValue/DeltaChannel）、Pregel 运行时引擎（BSP 循环、任务调度、写入应用）
    - 检查点/持久化系统详解（BaseCheckpointSaver、Memory/SQLite/PostgreSQL 后端）
    - 流式处理系统（StreamMode 分类、StreamMux 多流合并、Transformers）
    - 多智能体/子图支持（嵌套编译、命名空间隔离、时间旅行）
    - 架构图（Mermaid 序列图展示 BSP 循环、类图展示 Channel 层级）
    - 关键代码示例（StateGraph 定义、条件路由、中断与恢复、子图嵌套）
    - 适用业务场景与局限性分析

- [x] Task 4: 编写 DeepAgents 核心架构分析文档
  - 文件路径：`apps/chaos/.agents/docs/references/ai-libs/03-deepagents-core-analysis.md`
  - 内容要求：
    - 项目概览与定位（厚夹具代理框架、LangGraph 上层封装）
    - 核心模块深度分析：八大中间件系统（TodoList/Filesystem/Skills/SubAgent/Summarization/Memory/Rubric/AsyncSubAgent）、后端协议体系（CompositeBackend/StateBackend/FilesystemBackend/HarborSandbox）
    - 子代理系统详解（同步/已编译/异步三种模式、状态过滤、结果提取）
    - 技能(Skills)系统（SKILL.md 规范、渐进披露、多源合并）
    - CLI 部署工具（init/dev/deploy 全生命周期）
    - ACP 协议集成（人机协作、多模态支持）
    - 架构图（Mermaid 流程图展示中间件洋葱模型、CompositeBackend 路由）
    - 关键代码示例（create_deep_agent 装配流程、自定义中间件、技能定义）
    - 适用业务场景与局限性分析

- [x] Task 5: 编写三库横向对比与技术关联分析文档
  - 文件路径：`apps/chaos/.agents/docs/references/ai-libs/04-cross-comparison.md`
  - 内容要求：
    - 三库技术继承关系图（Mermaid 依赖拓扑）
    - 八大维度结构化对比表：
      1. 核心设计理念与定位
      2. 状态管理机制
      3. 多智能体协作模式
      4. 工作流编排能力
      5. 工具调用框架
      6. 大模型集成方案
      7. 部署与运维能力
      8. 优势与局限性
    - 互操作性分析（三库组合使用的典型模式）
    - 版本兼容性边界说明
    - 场景选型决策树/指南（何时单独使用某个库、何时组合使用）

- [x] Task 6: 编写可复用技术组件与设计模式参考手册
  - 文件路径：`apps/chaos/.agents/docs/references/ai-libs/05-reusable-patterns.md`
  - 内容要求：
    - 提炼 8-10 个可复用的核心设计模式，每个模式包含：
      - 模式名称与来源库
      - 解决的问题
      - 结构说明（含 Mermaid 类图/序列图）
      - 核心代码示例
      - 在 AgentForge 项目中的潜在应用场景
    - 建议提炼的模式：
      1. 中间件洋葱模型（DeepAgents）
      2. Channel 更新策略多态（LangGraph）
      3. BSP 超级步模型（LangGraph）
      4. CompositeBackend 路由模式（DeepAgents）
      5. Runnable 协议链式编排（LangChain）
      6. 检查点不可变日志（LangGraph）
      7. 渐进披露模式（DeepAgents Skills）
      8. 异步子代理任务委派（DeepAgents）
    - 技术组件复用清单（哪些组件可直接复用、哪些需适配）

# Task Dependencies
- Task 2、Task 3、Task 4 相互独立，可并行执行
- Task 5 依赖 Task 2、Task 3、Task 4（需要先完成各库的单库分析）
- Task 6 依赖 Task 2、Task 3、Task 4（需要先完成各库分析才能提炼共性模式）
- Task 1 可与 Task 2/3/4 并行执行
