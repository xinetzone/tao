# AI 专属 Wiki 架构设计与落地复盘

**日期**: 2026-05-22
**主题**: AgentForge 项目 AI 专属 Wiki (Python & Podman) 体系建设
**目标**: 为 AI 智能体建立一套高检索命中率、职责清晰的知识库，以加速后续的问题定位与代码开发。

## 1. 核心挑战与解决思路

### 挑战
当 AI 智能体在项目中遇到未知错误（如 `pytest` 收集失败、`httpx` 请求头丢失、`Podman` 无根挂载权限拒绝）时，如果在全局搜索中大海捞针，或者面对一堆大杂烩的 Markdown 笔记，往往会导致幻觉或反复试错。

### 解决思路：四层知识架构
废弃传统的“单层扁平化 Wiki”模式，引入面向机器检索的四层知识流转架构：
1. **`integrations/` (项目映射)**：连接外部知识与本地代码（“在这个项目里它在哪”）。
2. **`issue-patterns/` (故障模式)**：按症状索引排障路径（“我遇到了这个报错，该怎么查”）。
3. **`references/` (精炼参考)**：结构化的主题概念与命令（“这个东西的原理和命令是什么”）。
4. **`sources/` (原始来源)**：未加工的抓取数据和官方文档（“我要查最原始的上下文”）。

## 2. 关键设计决策

### 决策一：单点导航路由 (Single Point Router)
没有为各个目录创建分散的入口，而是**强化了 `.agents/docs/README.md` 的总路由职责**。
- 设定了严格的 **Agent 检索约定**：`integrations -> issue-patterns -> references -> sources`。
- 将“遇到 X 问题，先看 Y，再看 Z”的逻辑硬编码在 README 中，使得 AI 每次进入 `.agents/docs` 时都能获得清晰的定向导航。

### 决策二：检索关键词约定 (Search Keyword Conventions)
为了克服 AI 在不同语境下使用同义词导致检索失败的问题，确立了强制性的模板约定：
- **`Search Keywords`**: 强制要求页面开头列出主关键词、英文术语、常见别名和错误短语。
- **`Trigger Phrases`**: 模拟真实用户或 AI 思考时的自然语言提问（如“为什么 pytest 没收集到测试？”），以提升语义检索（RAG/Embedding）的命中率。
- **中英文双写**: 针对容易漂移的术语（如 `挂载 (mount)`）强制双写。

## 3. 实施路径回顾

本次建设分为四个阶段，完全通过原子提交 (Atomic Commits) 落地，保持了主分支的干净：

1. **骨架搭建** (`65612f5`): 创建四层目录及基础 `README.md`。
2. **导航增强** (`c0f41a1`): 升级总 `README.md` 路由，统一内部链接顺序。
3. **模板升级** (`535bf83`, `f109380`): 将关键词检索约定写入 README 并升级 `reference-page-template.md`。
4. **内容填充** (`55b1efd`): 基于项目实际上下文（通过代码库检索证实项目使用了 `pytest-asyncio`, `httpx.AsyncClient` 等），产出 4 个高质量参考页（`package-index.md`, `pytest.md`, `httpx.md`, `rootless.md`）。

## 4. 后续维护建议 (Next Steps)

1. **保持克制**：不要将临时草稿或代码片段直接丢入 `references/`，请先放入 `sources/`，经过提炼再升格。
2. **持续补充故障模式**：随着项目演进，遇到新的经典报错（如 GitHub Token 刷新竞态问题），应及时补充到 `issue-patterns/python-errors.md` 中。
3. **避免人类文档污染**：严格守住 `docs/`（面向人类）与 `.agents/docs/`（面向 AI）的边界，技术实现细节和排障 SOP 留在 AI 专属区。
