# 🤖 AI 专属文档 (AI-Specific Documentation)

该目录 (`.agents/docs/`) 是专门为 AI 智能体保留的知识库和分析文档存储区。

## 目录用途
与 `docs/`（面向人类开发者）不同，这里的文档旨在帮助 AI 更好地理解系统上下文、存储架构分析结果或沉淀执行过程中的知识图谱。通过这种物理隔离，我们确保了人类开发者的阅读体验不会被 AI 生成的冗长或高密度的机器可读数据所干扰。

## 知识区地图

| 目录 | 解决的问题 | 适合存放的内容 | 何时优先阅读 |
|------|------------|----------------|--------------|
| [`references/`](./references/) | 解释概念、命令和主题知识 | 提炼后的稳定知识页、速查页、主题说明 | 当你已经知道问题领域，但需要背景知识、命令或概念说明时 |
| [`issue-patterns/`](./issue-patterns/) | 提供按症状组织的排障路径 | 常见故障模式、触发条件、排查步骤、优先检查文件 | 当你已经遇到报错、失败或异常现象时 |
| [`integrations/`](./integrations/) | 说明外部知识与仓库代码的映射关系 | “在 AgentForge 里哪里相关”的导航页、代码落点说明 | 当你需要先判断问题与仓库中哪些模块、脚本或配置有关时 |
| [`sources/`](./sources/) | 保留原始资料和追溯入口 | 官方文档摘录、抓取结果、工作底稿 | 当你需要追溯原文、版本、抓取时间或尚未提炼的资料时 |
| [`superpowers/`](./superpowers/) | 沉淀历史设计、计划和复盘 | specs、plans、retrospectives 等长期资产 | 当你要理解历史决策、实施计划或复盘结论时 |

## 按场景导航

如果你遇到 Python 依赖、版本或测试问题：

1. 先看 [`integrations/python-in-agentforge.md`](./integrations/python-in-agentforge.md)
2. 再看 [`issue-patterns/python-errors.md`](./issue-patterns/python-errors.md)
3. 最后看 [`references/python/`](./references/python/)

如果你遇到 GitHub App 或 Python 模块排障问题：

1. 先看 [`integrations/python-in-agentforge.md`](./integrations/python-in-agentforge.md)
2. 再定位到 `src/taolib/github_app/` 和 `tests/github_app/`
3. 需要补背景时再看 [`references/python/package-index.md`](./references/python/package-index.md)

如果你遇到 Podman 运行、挂载或日志问题：

1. 先看 [`integrations/podman-in-agentforge.md`](./integrations/podman-in-agentforge.md)
2. 再看 [`issue-patterns/podman-errors.md`](./issue-patterns/podman-errors.md)
3. 最后看 [`references/podman/`](./references/podman/)

如果你需要追溯原始资料或官方文档：

1. 先确认对应主题是否已有提炼页
2. 若提炼页不足，再进入 [`sources/`](./sources/)
3. 只在需要原文、版本或抓取上下文时停留在 `sources/`

如果你需要理解历史设计、计划或复盘：

1. 进入 [`superpowers/`](./superpowers/)
2. 先看 `specs/` 理解设计意图
3. 再看 `plans/` 和 `retrospectives/` 理解执行路径和结果

## Agent 检索约定

为减少盲目翻找，agent 默认按以下顺序检索：

1. 先看 [`integrations/`](./integrations/)，判断问题与仓库的相关落点
2. 再看 [`issue-patterns/`](./issue-patterns/)，获取常见故障和排查路径
3. 再看 [`references/`](./references/)，补充概念、命令和背景知识
4. 最后看 [`sources/`](./sources/)，追溯原始资料
5. 若任务属于设计、规划或复盘，转到 [`superpowers/`](./superpowers/)

## 新增页面放置规则

- 原始抓取、网页摘录、工作底稿放在 [`sources/`](./sources/)
- 提炼后的稳定知识页放在 [`references/`](./references/)
- 以症状和排查路径为中心的页面放在 [`issue-patterns/`](./issue-patterns/)
- 将外部知识映射到仓库结构的页面放在 [`integrations/`](./integrations/)
- 设计、计划、复盘和长期经验沉淀继续放在 [`superpowers/`](./superpowers/)

## 检索关键词约定

为提升 agent 的检索命中率，后续新增 wiki 页面应遵循以下规则：

- 页面标题优先使用主关键词，不使用 `notes`、`misc`、`advanced`、`实践记录` 这类弱语义标题
- 新页面优先复用固定章节名，避免在不同页面中混用 `Goal`、`Purpose`、`Why This Exists` 等近义表达
- 每个参考页应包含 `Search Keywords` 区块，用于集中收纳主关键词、英文术语、常见别名和错误短语
- 每个参考页应包含 `Trigger Phrases` 区块，用于覆盖用户或 agent 可能提出的自然语言问题
- 首次出现的重要术语建议采用中英文双写，例如 `挂载 (mount)`、`依赖组 (dependency group)`
- 错误页应同时覆盖“现象词”和“原因词”，例如报错短语、失败现象和定位线索

## 约定

- 智能体可在此自由创建需要的 `.md` 或其他格式数据文档。
- 人类开发者通常无需直接阅读本目录下的内容。
- 新增 wiki 页面前，优先判断其属于 `references`、`issue-patterns`、`integrations` 还是 `sources`，避免混放。
