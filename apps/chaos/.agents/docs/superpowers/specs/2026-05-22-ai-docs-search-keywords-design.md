# AI Docs Search Keyword Convention Design

## Goal

为 `AgentForge` 的 AI 知识库补充一套更强的“检索关键词约定”，让后续新增页面在标题、章节、关键词和触发短语层面更容易被 agent 命中。

本次设计的目标是，在不引入复杂元数据系统、不批量重写现有页面的前提下，通过增强总 README 和模板文件，让后续文档天然具备更好的检索友好性。

具体目标如下：

- 在 `.agents/docs/README.md` 中明确检索关键词约定
- 在 `.agents/docs/templates/reference-page-template.md` 中固化检索友好的页面结构
- 约束标题命名、固定章节名、关键词字段和触发短语的写法
- 提升中英文混合检索、错误短语检索和场景化问题检索的命中率

## Background

当前 `.agents/docs/` 已经形成两层重要约定：

1. **目录级约定**
   - 已建立 `integrations -> issue-patterns -> references -> sources -> superpowers` 的推荐检索顺序
   - `.agents/docs/README.md` 已升级为总导航页

2. **页面级模板**
   - 已存在 `reference-page-template.md`
   - 当前模板包含 `Goal`、`Relevance In AgentForge`、`Key Concepts`、`Common Problems`、`Commands Or Snippets`、`Sources`

这些基础已经足够支撑“读哪里”的问题，但对“怎么让页面本身更容易被命中”还缺少显式规则。当前缺口主要体现在：

- 页面标题可能过于抽象，不利于关键词命中
- 章节名仍有自由发挥空间，后续容易出现同义标题漂移
- 缺少对别名、英文术语、报错短语的统一收纳方式
- 缺少“用户会怎么问”这一层触发短语设计

因此，需要把“检索友好”从一种写作建议，提升为一套明确的文档约定。

## Scope

- 修改 `.agents/docs/README.md`
- 修改 `.agents/docs/templates/reference-page-template.md`
- 在总 README 中新增“检索关键词约定”区块
- 在模板中新增适合 agent 检索的固定区块
- 明确标题、章节、关键词、触发短语和中英文双写规则

## Non-Goals

- 本次不批量修改现有知识页内容
- 本次不新增 frontmatter、YAML 元数据或标签系统
- 本次不引入自动索引脚本或搜索构建工具
- 本次不改变现有目录结构
- 本次不重命名已有文件

## Design Principles

1. 低侵入：只增强总 README 与模板，不强迫现有页面立即重构。
2. 高复用：把规则写进模板，让后续新页面自动继承一致结构。
3. 检索优先：优先为 agent 的关键词匹配和问题召回服务，而不是追求写作自由度。
4. 中英兼容：兼顾中文问题描述、英文技术术语和错误短语检索。
5. 结构稳定：通过固定章节名降低同义标题漂移。

## Options Considered

### Option A: 轻量关键词清单

做法：

- 仅在 `.agents/docs/README.md` 增加一节“检索关键词约定”
- 模板只加很少的说明

优点：

- 变更最小
- 落地快

缺点：

- 规则约束力弱
- 新页面仍然容易因为模板不足而写散

### Option B: 结构化检索约定

做法：

- 在 `.agents/docs/README.md` 中写总规则
- 在 `reference-page-template.md` 中加入固定检索区块

优点：

- 总规则和写作模板形成闭环
- 适合逐步演进，不需要立即重写旧页面
- 最符合当前仓库的文档治理风格

缺点：

- 模板会更规范化，写作者自由度略低

### Option C: 结构化约定 + 示例页校准

做法：

- 在 Option B 的基础上，再重写 1-2 个现有页面作为样例

优点：

- 最直观
- 后续复制成本更低

缺点：

- 这次范围会从“规则”扩展到“内容页改写”
- 容易超出当前任务边界

## Recommendation

采用 Option B。

这是当前最平衡的方案：

- 能把规则写清楚
- 能让模板直接落实规则
- 不会把任务范围扩大到现有内容页重构

## Proposed Changes

建议做两处增强：

### 1. 在 `.agents/docs/README.md` 新增 `检索关键词约定`

这一节建议覆盖以下规则：

- 标题命名规则
- 固定章节名规则
- 关键词收纳规则
- 触发短语规则
- 中英文双写规则

### 2. 在 `reference-page-template.md` 中新增检索区块

建议模板结构调整为：

1. `# Topic Title`
2. `## Search Keywords`
3. `## Goal`
4. `## Relevance In AgentForge`
5. `## Trigger Phrases`
6. `## Key Concepts`
7. `## Common Problems`
8. `## Commands Or Snippets`
9. `## Sources`

## Rules

### 标题命名规则

页面标题应优先使用最稳定、最常被检索的主关键词：

- 包页优先使用真实包名，如 `pytest`、`httpx`
- 主题页优先使用技术域 + 核心概念，如 `Podman Rootless`
- 问题模式页应显式带问题域，如 `Python Error Patterns`

应避免：

- `notes`
- `misc`
- `advanced`
- `实践记录`
- `一些问题`

这类弱语义标题会显著降低检索命中率。

### 固定章节名规则

为减少同义标题漂移，模板页应优先使用固定章节名，不建议自由替换为近义表达。

优先保留：

- `Search Keywords`
- `Goal`
- `Relevance In AgentForge`
- `Trigger Phrases`
- `Key Concepts`
- `Common Problems`
- `Commands Or Snippets`
- `Sources`

这意味着不建议在不同页面中混用：

- `Goal` / `Purpose` / `Why This Exists`
- `Common Problems` / `Troubleshooting` / `Pitfalls`

### 关键词收纳规则

每个参考页应新增 `Search Keywords` 区块，并至少包含以下四类信息：

1. 主关键词
2. 英文术语
3. 常见别名
4. 典型报错或问题短语

建议写法：

```md
## Search Keywords

- 主关键词：pytest
- 英文术语：fixture, test collection
- 常见别名：pytests
- 错误短语：test collection failed, fixture not found
```

该区块的作用不是写解释，而是集中堆叠“最可能被检索到的词”。

### 触发短语规则

每个参考页应新增 `Trigger Phrases` 区块，用自然语言描述用户或 agent 可能提出的问题。

建议数量：

- 3 到 8 条

建议示例：

```md
## Trigger Phrases

- 为什么 pytest 没收集到测试？
- fixture not found 是什么意思？
- 如何排查 test collection failed？
```

这一节的目标是覆盖自然语言检索，而不是术语检索。

### 中英文双写规则

对于容易出现中英混搜的术语，正文首次出现时建议采用中文 + 英文双写形式，例如：

- 挂载 (mount)
- 依赖组 (dependency group)
- 无状态令牌 (stateless token)

这样可以提高：

- 中文问题命中率
- 英文术语检索命中率
- 混合场景下的召回稳定性

### 项目相关性字段规则

`Relevance In AgentForge` 区块继续保留，但建议将其视为检索锚点，而不是单纯的背景信息。

至少保持以下字段：

- 关联模块
- 常见触发场景
- 优先检查文件

这些字段有助于 agent 从术语页跳回仓库结构。

## README Section Shape

建议在 `.agents/docs/README.md` 中新增一个简洁但明确的区块：

### `检索关键词约定`

建议至少包含以下条目：

- 页面标题优先使用主关键词，不使用弱语义标题
- 新页面优先复用固定章节名
- 每个参考页应包含 `Search Keywords`
- 每个参考页应包含 `Trigger Phrases`
- 首次出现的重要术语建议采用中英文双写
- 错误页应同时覆盖“现象词”和“原因词”

这一节的定位是“总规则摘要”，不是模板细节全文复制。

## Template Shape

建议把模板更新为如下结构：

```md
# Topic Title

## Search Keywords

- 主关键词：
- 英文术语：
- 常见别名：
- 错误短语：

## Goal

一句话说明该页解决什么问题，并尽量包含主关键词。

## Relevance In AgentForge

- 关联模块：
- 常见触发场景：
- 优先检查文件：

## Trigger Phrases

- 用户可能会如何提问 1
- 用户可能会如何提问 2

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

## Risks

- 如果规则写得过重，模板可能变得僵硬
- 如果 README 规则和模板不同步，后续会出现两套标准
- 如果不在后续新页面中执行这些约定，规则会迅速失效

## Acceptance Criteria

- `.agents/docs/README.md` 中新增“检索关键词约定”区块
- `reference-page-template.md` 中新增 `Search Keywords`
- `reference-page-template.md` 中新增 `Trigger Phrases`
- 模板继续保留 `Relevance In AgentForge`
- 模板继续保留 `Common Problems`
- 规则明确约束标题命名、固定章节名和中英文双写
- 不新增新的目录层级、标签系统或自动索引脚本
