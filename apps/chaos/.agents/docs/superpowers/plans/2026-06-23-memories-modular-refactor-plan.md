# Memories 目录模块化重构执行计划

> **生成依据**：[doc-asset-modular-refactor-framework.md](../../references/doc-asset-modular-refactor-framework.md)
> **目标目录**：`apps/chaos/.agents/docs/superpowers/memories/`
> **生成日期**：2026-06-23

## 0. 现状分析

| 指标 | 数值 |
|------|------|
| 原始文件总数 | 8（不含 README.md） |
| 行数范围 | 27-42 行 |
| 命名格式 | `YYYY-MM-DD-{topic}-{type}.md`（已统一） |
| 是否需原子化拆分 | 否（全部为小型单主题文档） |
| 是否有命名漂移 | 否（格式一致） |

**适用性判定**：根据框架 §6.2 不适用场景，memories 目录仅 8 份文件（< 10），且均为单主题短文档，**不满足框架适用条件**。

**调整决策**：虽不满足完整框架适用条件，但目录缺乏按类型/主题的模块化组织，可应用框架的**阶段 2（设计）+ 阶段 4（索引）** 子集，进行轻量级模块化（不执行原子化拆分、不执行大规模迁移）。

## 1. 分类映射表

基于框架 §3.1 分类映射提示词模板，参数化填充后执行结果：

| 原始文件名 | 行数 | 一级模块（按类型） | 是否需拆分 |
|-----------|------|-------------------|-----------|
| 2026-05-25-concept-first-documentation-second-principle.md | 27 | principles/ | 否 |
| 2026-05-25-doc-architecture-three-layers-principle.md | 27 | principles/ | 否 |
| 2026-05-25-doc-maintenance-5-steps-experience.md | 28 | experiences/ | 否 |
| 2026-05-25-myst-cross-directory-link-constraint.md | 27 | constraints/ | 否 |
| 2026-05-25-network-linking-knowledge-graph-experience.md | 28 | experiences/ | 否 |
| 2026-06-02-external-knowledge-ingestion-principle.md | 41 | principles/ | 否 |
| 2026-06-02-knowledge-ingestion-task-boundary-principle.md | 41 | principles/ | 否 |
| 2026-06-11-document-debt-governance-three-phase-methodology.md | 42 | methodologies/ | 否 |

**分类规则**（基于文件名类型后缀）：
- `principle` → `principles/`
- `experience` → `experiences/`
- `constraint` → `constraints/`
- `methodology` → `methodologies/`

## 2. 目标目录树

基于框架 §2 阶段 2 标准目录树结构，适配 memories 目录：

```
memories/
├── README.md                    # 总入口 + 导航索引（更新）
├── _meta/                       # 元数据与治理
│   ├── naming-convention.md     # 命名规范（沿用现有 + 模块化补充）
│   ├── module-catalog.md        # 模块目录清单
│   ├── dependency-graph.md      # 依赖关系图谱
│   └── migration-log.md         # 迁移日志
├── principles/                  # 原则类记忆
│   ├── README.md
│   └── *.md
├── experiences/                 # 经验类记忆
│   ├── README.md
│   └── *.md
├── constraints/                 # 约束类记忆
│   ├── README.md
│   └── *.md
└── methodologies/               # 方法论类记忆
    ├── README.md
    └── *.md
```

## 3. 执行任务清单

基于框架 5 阶段流程，适配为 4 个任务（跳过阶段 3 拆分）：

### Task 1: 创建目录骨架（阶段 2）

创建以下目录：
- `_meta/`
- `principles/`
- `experiences/`
- `constraints/`
- `methodologies/`

### Task 2: 迁移文件至对应模块（阶段 3-迁移部分）

| 原始文件名 | 迁移去向 |
|-----------|---------|
| 2026-05-25-concept-first-documentation-second-principle.md | principles/ |
| 2026-05-25-doc-architecture-three-layers-principle.md | principles/ |
| 2026-05-25-doc-maintenance-5-steps-experience.md | experiences/ |
| 2026-05-25-myst-cross-directory-link-constraint.md | constraints/ |
| 2026-05-25-network-linking-knowledge-graph-experience.md | experiences/ |
| 2026-06-02-external-knowledge-ingestion-principle.md | principles/ |
| 2026-06-02-knowledge-ingestion-task-boundary-principle.md | principles/ |
| 2026-06-11-document-debt-governance-three-phase-methodology.md | methodologies/ |

### Task 3: 编写索引与元数据文档（阶段 4）

- 更新根目录 `README.md`（总入口 + 模块导航表 + 检索指南）
- 编写 4 个模块 `README.md`（principles/、experiences/、constraints/、methodologies/）
- 编写 `_meta/naming-convention.md`（沿用现有命名规范 + 模块化补充）
- 编写 `_meta/module-catalog.md`（模块目录清单）
- 编写 `_meta/dependency-graph.md`（依赖关系图谱）
- 编写 `_meta/migration-log.md`（迁移日志，覆盖 8 份文件）

### Task 4: 引用更新与校验（阶段 5）

- 搜索项目内对 memories 文件的引用路径
- 更新引用路径至模块化新路径
- 校验迁移日志覆盖全部 8 份文件
- 校验命名规范一致性

## 4. 提示词模板实例化

### 4.1 分类映射提示词（框架 §3.1 实例化）

```
你是一个研究型子智能体。任务：对 `apps/chaos/.agents/docs/superpowers/memories/` 目录下的全部 8 份 markdown 文件建立分类映射表。

具体要求：
1. 读取每份文件的 Type 字段（principle/experience/constraint/methodology）
2. 统计每份文件的行数
3. 对每份文件进行分类：
   - 一级模块：principles/experiences/constraints/methodologies
4. 识别需要原子化拆分的文件（行数 > 400 或包含 3 个以上独立主题章节）

分类规则：
- Type 为 principle → principles/
- Type 为 experience → experiences/
- Type 为 constraint → constraints/
- Type 为 methodology → methodologies/

输出格式：返回一个完整的 markdown 表格，包含以下列：
| 原始文件名 | 行数 | 一级模块 | 是否需原子化拆分 |

请确保覆盖全部 8 份文件。这是纯研究任务，不要修改任何文件。
```

### 4.2 模块 README 提示词（框架 §3.3 实例化）

```
你是一个文档编写子智能体。任务：为 memories 模块化重构后的各模块编写 README.md 文件。

基础路径：`apps/chaos/.agents/docs/superpowers/memories/`

需要编写的 README 文件清单：

principles/（3 个文件）：
- 2026-05-25-concept-first-documentation-second-principle.md
- 2026-05-25-doc-architecture-three-layers-principle.md
- 2026-06-02-external-knowledge-ingestion-principle.md
- 2026-06-02-knowledge-ingestion-task-boundary-principle.md

experiences/（2 个文件）：
- 2026-05-25-doc-maintenance-5-steps-experience.md
- 2026-05-25-network-linking-knowledge-graph-experience.md

constraints/（1 个文件）：
- 2026-05-25-myst-cross-directory-link-constraint.md

methodologies/（1 个文件）：
- 2026-06-11-document-debt-governance-three-phase-methodology.md

每个 README.md 的格式要求：
# {模块名称}

> **维护责任人**：Leader Agent

## 模块功能
{1-2 句话描述模块用途}

## 使用方法
- **何时查阅**：{查阅场景}
- **如何引用**：使用相对路径引用

## 依赖关系
{列出引用的其他模块或文档}

## 文件清单
| 文件 | 说明 |
|------|------|
| {filename} | {简要说明} |
```

### 4.3 依赖图谱与迁移日志提示词（框架 §3.4 实例化）

```
你是一个研究型子智能体。任务：为 memories 模块化重构构建依赖关系图谱和迁移日志。

基础路径：`apps/chaos/.agents/docs/superpowers/memories/`

## 任务 1：依赖关系图谱

扫描该目录下所有 markdown 文件，查找文件内的相对路径引用（如 `../../references/xxx.md`、`../retrospectives/xxx.md`），构建依赖关系。

输出文件：`_meta/dependency-graph.md`

## 任务 2：迁移日志

迁移映射：
| 原始文件名 | 一级模块 | 迁移去向 |
|-----------|---------|---------|
| 2026-05-25-concept-first-documentation-second-principle.md | principles | principles/2026-05-25-concept-first-documentation-second-principle.md |
| 2026-05-25-doc-architecture-three-layers-principle.md | principles | principles/2026-05-25-doc-architecture-three-layers-principle.md |
| 2026-05-25-doc-maintenance-5-steps-experience.md | experiences | experiences/2026-05-25-doc-maintenance-5-steps-experience.md |
| 2026-05-25-myst-cross-directory-link-constraint.md | constraints | constraints/2026-05-25-myst-cross-directory-link-constraint.md |
| 2026-05-25-network-linking-knowledge-graph-experience.md | experiences | experiences/2026-05-25-network-linking-knowledge-graph-experience.md |
| 2026-06-02-external-knowledge-ingestion-principle.md | principles | principles/2026-06-02-external-knowledge-ingestion-principle.md |
| 2026-06-02-knowledge-ingestion-task-boundary-principle.md | principles | principles/2026-06-02-knowledge-ingestion-task-boundary-principle.md |
| 2026-06-11-document-debt-governance-three-phase-methodology.md | methodologies | methodologies/2026-06-11-document-debt-governance-three-phase-methodology.md |

输出文件：`_meta/migration-log.md`
```

### 4.4 引用更新提示词（框架 §3.5 实例化）

```
你是一个文档维护子智能体。任务：更新项目内所有对 memories 文件的引用路径。

重构规则：原扁平路径 `memories/{filename}.md` 需更新为 `memories/{module}/{filename}.md`。

搜索范围：项目内所有 .md 文件中包含 `memories/2026-` 的引用。

操作要求：
1. 用 Grep 搜索 `memories/2026-` 模式
2. 用 Read 读取每个匹配文件
3. 用 Edit 更新引用路径
4. 注意：markdown 链接格式需同时更新链接文本和链接路径
```

## 5. 质量评估标准

基于框架 §5，适配为 memories 目录的评估指标：

| 维度 | 指标 | 通过标准 |
|------|------|---------|
| 完整性 | 迁移日志覆盖率 | 100% (8/8) |
| 完整性 | 内容丢失率 | 0% |
| 一致性 | 命名规范违反数 | 0 |
| 一致性 | 目录树结构合规率 | 100% |
| 可追溯性 | 依赖图谱覆盖率 | 100% |
| 可追溯性 | 外部引用更新率 | 100% |
| 可维护性 | 模块 README 覆盖率 | 100% (4/4) |
| 可维护性 | 检索指南完整性 | 含导航表+检索指南 |

## 6. 与完整框架的差异说明

| 框架阶段 | 是否执行 | 原因 |
|---------|---------|------|
| 阶段 1 分析 | ✅ 执行 | 分类映射已完成 |
| 阶段 2 设计 | ✅ 执行 | 目录骨架 + 命名规范 |
| 阶段 3 迁移（迁移部分） | ✅ 执行 | 8 份文件迁移 |
| 阶段 3 迁移（拆分部分） | ❌ 跳过 | 全部文件 < 50 行，无拆分需求 |
| 阶段 4 索引 | ✅ 执行 | README + 元数据文档 |
| 阶段 5 校验 | ✅ 执行 | 引用更新 + 完整性校验 |

**差异原因**：memories 目录文件数少（8 < 20）、行数短（27-42 < 400）、命名已统一，不满足框架完整适用条件，仅应用框架子集进行轻量级模块化。
