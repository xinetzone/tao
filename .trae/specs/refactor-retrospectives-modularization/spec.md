# Retrospectives 模块化重构 Spec

## Why

`apps/chaos/.agents/docs/superpowers/retrospectives/` 目录当前以扁平结构存放 72 份复盘文档，存在四类问题：
1. **类型混杂**：项目复盘、审计报告、洞察、会话复盘、任务总结等 6 种类型混存于同一层，检索成本高。
2. **大型文档未原子化**：部分文档（如 `agentforge-project-retrospective-20260523.md`、`audit-report-superpowers-memory-debt-20260611.md`）超过 300 行且覆盖多个独立主题，难以按需引用。
3. **命名格式漂移**：审计报告（`audit-report-superpowers-memory-debt-20260611.md` §S2）已识别 4 种命名变体并存。
4. **缺乏索引与依赖图谱**：无模块说明、无引用关系图、无迁移日志，维护与查阅成本高。

本次重构通过原子化拆分、模块化归类、结构化层级、依赖图谱与索引文档建设，将复盘区改造为高内聚低耦合的可维护知识资产。

## What Changes

- **原子化拆分**：对覆盖多主题的大型文档（>200 行或含多个独立章节），按主题拆分为独立原子单元，每单元专注单一主题；原文档转为目录形式，内含 `index.md` 索引与原子单元文件。
- **模块化归类**：按文档类型建立一级模块（`project-reviews/`、`audit-reports/`、`insights/`、`session-reviews/`、`task-summaries/`、`misc/`）；任务总结模块内部按主题建立二级子模块（`ci-cd/`、`documentation/`、`python-environment/`、`skills/`、`releases/`、`exploration/`、`world-cli/`、`refactoring/`、`misc/`）。
- **结构化层级**：设计统一目录树；制定命名规范（英文 kebab-case，`{topic}-{date}` 格式，日期 YYYYMMDD）。
- **引用关系图谱**：扫描所有文档内的相对路径引用，生成 `_meta/dependency-graph.md`，记录模块间与文档间依赖。
- **索引与模块说明**：根目录 `README.md` 作为总入口与导航；每个模块含 `README.md` 说明模块功能、使用方法、依赖关系、维护责任人；`_meta/module-catalog.md` 提供完整模块清单。
- **完整性检查**：`_meta/migration-log.md` 记录每份原始文件的迁移去向，确保零信息丢失。
- **BREAKING**：原扁平目录结构变更，所有外部引用 `retrospectives/{filename}.md` 的路径需更新为模块化路径。

## Impact

- **Affected specs**: 无直接影响其他 spec，但 `audit-report-superpowers-memory-debt-20260611.md` 中记录的记忆债务（S2 格式漂移、S3 目录失衡）将被本次重构解决。
- **Affected code**: 无代码改动，纯文档资产重构。
- **Affected references**: 项目内引用 retrospectives 文件的文档（如 `documentation.md`、`rule-evolution.md`、其他复盘文档内的交叉引用）需同步更新路径。
- **Affected docs**: `apps/chaos/.agents/docs/superpowers/retrospectives/` 全目录（72 文件）。

## ADDED Requirements

### Requirement: 原子化拆分

系统 SHALL 对覆盖多主题的大型复盘文档执行原子化拆分，每个原子单元专注单一主题或功能点。

#### Scenario: 大型多主题文档拆分
- **WHEN** 一份复盘文档行数超过 200 行且包含 3 个以上独立主题章节
- **THEN** 该文档转为同名目录，目录内含 `index.md`（概述与原子单元索引）与按主题命名的原子单元文件
- **AND** 每个原子单元文件专注单一主题，可独立阅读

#### Scenario: 小型单主题文档保留
- **WHEN** 一份复盘文档行数不超过 200 行或仅覆盖单一主题
- **THEN** 保持单文件形式，不进行拆分

#### Scenario: 原子单元命名
- **WHEN** 创建原子单元文件
- **THEN** 文件名使用英文 kebab-case，描述单一主题（如 `spec-achievement.md`、`engineering-maturity.md`）

### Requirement: 模块化分类体系

系统 SHALL 按文档类型建立一级模块，任务总结模块内部按主题建立二级子模块，确保模块内部高内聚、模块之间低耦合。

#### Scenario: 一级模块分类
- **WHEN** 对复盘文档进行归类
- **THEN** 按类型分配至以下一级模块：
  - `project-reviews/`：项目级阶段性复盘
  - `audit-reports/`：质量审计与债务评估报告
  - `insights/`：技术洞察与设计反思
  - `session-reviews/`：单次会话复盘
  - `task-summaries/`：任务执行总结
  - `misc/`：无法归入上述类型的其他复盘

#### Scenario: 任务总结二级主题分类
- **WHEN** 文档归类至 `task-summaries/`
- **THEN** 按主题分配至以下二级子模块：
  - `ci-cd/`：CI 流水线、lint、构建修复
  - `documentation/`：文档治理、边界重构、changelog
  - `python-environment/`：Python 版本适配、依赖管理、lint
  - `skills/`：技能资产开发与校验
  - `releases/`：版本发布与后续改进
  - `exploration/`：探索任务与知识循环
  - `world-cli/`：World CLI 分发与层级规范
  - `refactoring/`：代码重构任务
  - `misc/`：无法归入上述主题的任务总结

### Requirement: 结构化目录与命名规范

系统 SHALL 设计合理的目录树结构并制定统一的命名规范，命名具有描述性且符合行业标准。

#### Scenario: 目录树结构
- **WHEN** 重构完成
- **THEN** 目录树遵循以下结构：
  ```
  retrospectives/
  ├── README.md                    # 总入口 + 导航索引
  ├── _meta/                       # 元数据与治理
  │   ├── module-catalog.md       # 模块目录
  │   ├── dependency-graph.md     # 依赖关系图谱
  │   ├── naming-convention.md    # 命名规范
  │   └── migration-log.md        # 迁移日志
  ├── project-reviews/             # 项目级复盘模块
  │   ├── README.md
  │   └── {topic}-{date}/         # 原子化目录
  ├── audit-reports/
  ├── insights/
  ├── session-reviews/
  ├── task-summaries/
  │   ├── README.md
  │   └── {theme}/                # 主题子模块
  └── misc/
  ```

#### Scenario: 命名规范
- **WHEN** 命名目录或文件
- **THEN** 遵循以下规则：
  - 目录名：纯 ASCII 英文 kebab-case
  - 文件名：`{topic}-{date}.md` 或 `{section-name}.md`（原子单元）
  - 日期格式：YYYYMMDD（如 `20260523`）
  - 禁止中文、emoji、空格

### Requirement: 引用关系图谱

系统 SHALL 扫描所有复盘文档内的相对路径引用，建立清晰的依赖图谱，确保引用关系明确且可追溯。

#### Scenario: 依赖图谱生成
- **WHEN** 重构完成
- **THEN** `_meta/dependency-graph.md` 记录：
  - 每份文档引用的其他复盘文档（正向依赖）
  - 每份文档被哪些文档引用（反向依赖）
  - 模块间依赖关系汇总
- **AND** 图谱使用 Mermaid 流程图可视化关键依赖链

### Requirement: 索引与模块说明文档

系统 SHALL 生成完整的目录索引和模块说明文档，模块说明包含模块功能描述、使用方法、依赖关系及维护责任人。

#### Scenario: 总入口索引
- **WHEN** 重构完成
- **THEN** 根目录 `README.md` 包含：
  - 目录总体说明
  - 模块导航表（模块名、用途、文件数、入口链接）
  - 命名规范摘要
  - 检索指南

#### Scenario: 模块说明文档
- **WHEN** 每个一级模块与二级子模块
- **THEN** 含 `README.md`，包含：
  - 模块功能描述
  - 使用方法（何时查阅、如何引用）
  - 依赖关系（引用的其他模块或文档）
  - 维护责任人（默认为 Leader Agent）
  - 文件清单

#### Scenario: 模块目录清单
- **WHEN** 重构完成
- **THEN** `_meta/module-catalog.md` 提供所有模块的完整清单，含模块路径、功能、文件数、维护者

### Requirement: 完整性检查

系统 SHALL 进行完整性检查，确保所有原始内容均已妥善迁移且无信息丢失。

#### Scenario: 迁移日志
- **WHEN** 每份原始文件迁移
- **THEN** 在 `_meta/migration-log.md` 记录：
  - 原始文件名
  - 迁移去向（目标路径）
  - 是否拆分（是/否）
  - 拆分后的原子单元清单
  - 内容校验状态（完整/部分丢失）

#### Scenario: 完整性校验
- **WHEN** 重构完成
- **THEN** 迁移日志覆盖全部 72 份原始文件
- **AND** 每份文件标记为"完整迁移"
- **AND** 无原始内容丢失

## MODIFIED Requirements

### Requirement: 复盘文档归档位置

`documentation.md` §2 规定复盘报告归档至 `.agents/docs/superpowers/retrospectives/`。本次重构后，该目录内部结构模块化，但顶层路径不变，归档规则的外部接口保持兼容。

#### Scenario: 新增复盘归档
- **WHEN** 新增复盘文档
- **THEN** 按文档类型归入对应一级模块，按主题归入二级子模块，遵循命名规范
- **AND** 更新对应模块的 `README.md` 文件清单

## REMOVED Requirements

无删除项。本次重构为内部重组，不删除任何原始内容，仅改变组织形式。
