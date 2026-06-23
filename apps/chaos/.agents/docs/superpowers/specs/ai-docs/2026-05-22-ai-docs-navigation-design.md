# AI Docs Navigation Design

## Goal

增强 `AgentForge` 中 `.agents/docs/README.md` 的职责，使其从“AI 文档目录说明页”升级为“AI 知识库总导航页”，在不新增独立索引层级的前提下，同时承担以下作用：

- 作为 `.agents/docs/` 的统一入口
- 为 agent 提供按场景检索的阅读顺序
- 固化新建 wiki 的放置规则与检索约定

本次设计的核心目标不是新增更多文档，而是让现有 wiki 结构更容易被 agent 正确使用，降低“知道有资料但不知道先读哪一类”的定位成本。

## Background

当前 `.agents/docs/` 已经具备两类基础能力：

1. 顶层目录说明：现有 [README.md](file:///c:/Users/xinzo/OneDrive/Desktop/AI/Dao/spaces/AgentForge/.agents/docs/README.md) 能解释 `.agents/docs/` 与面向人类的 `docs/` 的边界。
2. 参考 wiki 骨架：已新增以下知识区：
   - `references/`
   - `issue-patterns/`
   - `integrations/`
   - `sources/`
   - `superpowers/`

但当前仍存在一个明显缺口：`.agents/docs/README.md` 还没有吸收新 wiki 的结构信息，导致使用者只能“看到有目录”，却无法快速理解：

- 不同目录分别解决什么问题
- 遇到具体问题时应该先读哪一类页面
- 新增页面时应该放到哪个目录

如果不补这一层总导航，后续随着 Python 包、Podman 和其他知识不断增加，agent 的检索路径会再次变得依赖猜测。

## Scope

- 升级 `.agents/docs/README.md`
- 保留现有“AI 文档边界”说明
- 新增覆盖整个 `.agents/docs/` 的知识区地图
- 新增按场景组织的导航说明
- 新增 agent 默认检索顺序约定
- 新增新增页面放置规则

## Non-Goals

- 本次不新增独立 wiki 索引页
- 本次不重命名已有目录或 Markdown 文件
- 本次不引入前缀命名系统、标签系统或自动索引脚本
- 本次不修改 `references/README.md`、`issue-patterns/README.md` 等子目录入口页
- 本次不调整 `superpowers/` 的设计文档与复盘归档职责

## Design Principles

1. 单入口优先：优先增强 `.agents/docs/README.md`，避免新建额外入口页增加认知层级。
2. 导航先于解释：优先回答“先看哪里”，再解释目录职责。
3. 场景驱动：按问题类型组织阅读顺序，而不是只按目录名罗列。
4. 约定显式化：把检索路径和放置规则写成文档约定，减少后续漂移。
5. 最小改动：不改变已落地的 wiki 骨架，只补上总导航层。

## Options Considered

### Option A: 仅补目录链接

做法：

- 在 `.agents/docs/README.md` 中列出 `references/`、`issue-patterns/`、`integrations/`、`sources/`、`superpowers/` 的跳转链接

优点：

- 变更最小
- 维护成本低

缺点：

- 不能回答“什么问题先看什么”
- 只能提供目录可见性，无法提供检索策略

### Option B: 总 README + 检索约定

做法：

- 升级 `.agents/docs/README.md`
- 同时加入目录地图、按场景导航、检索约定和放置规则

优点：

- 单一入口即可覆盖“看哪里”和“怎么找”
- 最符合当前已建成的 wiki 结构
- 不增加新入口层级

缺点：

- `README.md` 会比现在更长

### Option C: 总 README + 检索约定 + 命名前缀体系

做法：

- 在 Option B 基础上，为后续文档增加前缀命名或标签规则

优点：

- 长期机器检索可能更稳定

缺点：

- 会对现有命名体系引入额外约束
- 当前收益不足以覆盖复杂度

## Recommendation

采用 Option B。

这是当前最平衡的方案：

- 不引入新的入口页面
- 不打乱刚建立的目录结构
- 能直接提升 agent 的检索准确率
- 便于后续继续扩展 Python、Podman 及其他主题

## Proposed Structure

建议将 `.agents/docs/README.md` 调整为以下结构：

1. `目录用途`
2. `知识区地图`
3. `按场景导航`
4. `Agent 检索约定`
5. `新增页面放置规则`

## Section Responsibilities

### 1. `目录用途`

保留现有说明，继续强调：

- `.agents/docs/` 是 AI 专属知识区
- 与 `docs/` 的人类文档边界保持清晰分离

这一部分应继续作为总入口的背景说明，不需要大幅扩写。

### 2. `知识区地图`

建议用表格概括主要目录：

- `references/`
- `issue-patterns/`
- `integrations/`
- `sources/`
- `superpowers/`

每一行应至少回答三个问题：

- 这类目录解决什么问题
- 适合放什么文档
- 什么时候应该优先阅读

该表格的作用是把目录语义从“名称”变成“用途”。

### 3. `按场景导航`

这是本次增强的核心部分，建议用“问题场景 -> 推荐阅读顺序”的格式呈现。

至少覆盖以下场景：

- Python 依赖、版本、测试问题
- GitHub App / Python 模块排障问题
- Podman 运行、挂载、日志问题
- 需要追溯原始资料或官方文档时
- 需要查看历史设计、计划和复盘时

建议呈现方式如下：

```text
如果你遇到 Python 依赖或测试问题：
1. 先看 `integrations/python-in-agentforge.md`
2. 再看 `issue-patterns/python-errors.md`
3. 最后看 `references/python/`
```

该区块的目标是把“按目录浏览”升级为“按任务检索”。

### 4. `Agent 检索约定`

这一节应明确默认检索顺序，建议写成规则化的短列表：

1. 先看 `integrations/`，判断问题与仓库的相关落点
2. 再看 `issue-patterns/`，获取常见故障与排查路径
3. 再看 `references/`，补充概念、命令和背景知识
4. 最后看 `sources/`，追溯原始资料
5. 若任务是设计、规划或复盘，转到 `superpowers/`

这会为后续 agent 使用 `.agents/docs/` 提供稳定的检索习惯。

### 5. `新增页面放置规则`

这一节要把现有目录边界固化成显式规则：

- 原始抓取、网页摘录、工作底稿放 `sources/`
- 提炼后的稳定知识放 `references/`
- 以症状和排查路径为中心的页面放 `issue-patterns/`
- 将外部知识映射到仓库结构的页面放 `integrations/`
- 设计、计划、复盘和长期经验沉淀继续放 `superpowers/`

这部分的目标是降低后续新增页面时的放置歧义。

## Example Navigation Rules

建议在文档中给出几条足够具体的示例规则，例如：

- 遇到“依赖不存在或导入失败”时：先看 `integrations/python-in-agentforge.md`，再看 `issue-patterns/python-errors.md`
- 遇到“Podman 容器未启动或挂载异常”时：先看 `integrations/podman-in-agentforge.md`，再看 `issue-patterns/podman-errors.md`
- 遇到“想理解某个 Python 包为何存在于仓库中”时：先看 `integrations/python-in-agentforge.md`，再看 `references/python/package-index.md`
- 只有在需要追溯原文、版本或抓取材料时才进入 `sources/`

## Change Strategy

建议采用“原地增强”策略：

- 直接修改现有 `.agents/docs/README.md`
- 保留现有顶部定位说明
- 在其后补充新结构

不建议新建 `wiki-index.md` 或其他总导航页，因为那会导致以下问题：

- 总入口职责被拆散
- `.agents/docs/README.md` 仍然保留旧状态，形成双入口
- 后续维护者难以判断应优先更新哪个文件

## Risks

- 如果“按场景导航”写得过泛，会退化成另一份普通目录说明
- 如果“检索约定”与子目录实际内容不匹配，会误导 agent
- 如果将来新增主题但不更新总导航，README 会失去时效性

## Acceptance Criteria

- `.agents/docs/README.md` 能同时说明目录边界与 wiki 使用方式
- 文档中明确包含知识区地图
- 文档中明确包含按场景导航
- 文档中明确包含 agent 默认检索顺序
- 文档中明确包含新增页面放置规则
- 不新增独立索引页
- 不修改现有目录和文件命名体系
