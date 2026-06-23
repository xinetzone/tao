# Tasks

## Phase 1: 准备与分类映射

- [x] Task 1: 建立原始文件清单与分类映射表
  - [x] SubTask 1.1: 读取全部 72 份原始文件头部，提取报告类型、日期、主题
  - [x] SubTask 1.2: 按一级模块（project-reviews/audit-reports/insights/session-reviews/task-summaries/misc）分类
  - [x] SubTask 1.3: 对 task-summaries 按二级主题（ci-cd/documentation/python-environment/skills/releases/exploration/world-cli/refactoring/misc）分类
  - [x] SubTask 1.4: 识别需原子化拆分的大型文档（>200 行或多主题），记录拆分方案

## Phase 2: 目录骨架与命名规范

- [x] Task 2: 创建目录骨架与命名规范文档
  - [x] SubTask 2.1: 创建一级模块目录（project-reviews/、audit-reports/、insights/、session-reviews/、task-summaries/、misc/、_meta/）
  - [x] SubTask 2.2: 创建 task-summaries 二级子模块目录（ci-cd/、documentation/、python-environment/、skills/、releases/、exploration/、world-cli/、refactoring/、misc/）
  - [x] SubTask 2.3: 编写 `_meta/naming-convention.md` 命名规范文档

## Phase 3: 文件迁移与原子化拆分

- [x] Task 3: 迁移小型单主题文档（不拆分）
  - [x] SubTask 3.1: 迁移 project-reviews 单文件文档
  - [x] SubTask 3.2: 迁移 audit-reports 单文件文档
  - [x] SubTask 3.3: 迁移 insights 单文件文档
  - [x] SubTask 3.4: 迁移 session-reviews 单文件文档
  - [x] SubTask 3.5: 迁移 task-summaries 至对应主题子模块
  - [x] SubTask 3.6: 迁移 misc 文档

- [x] Task 4: 原子化拆分大型多主题文档
  - [x] SubTask 4.1: 拆分 `agentforge-project-retrospective-20260523.md` 为目录 + 原子单元
  - [x] SubTask 4.2: 拆分 `audit-report-superpowers-memory-debt-20260611.md` 为目录 + 原子单元
  - [x] SubTask 4.3: 拆分 `task-summary-lint-python313-20260609.md` 为目录 + 原子单元
  - [x] SubTask 4.4: 拆分 `task-summary-agentforge-collaboration-system-20260524.md` 为目录 + 原子单元
  - [x] SubTask 4.5: 拆分 `task-summary-containerrun-refactor-20260610.md` 为目录 + 原子单元
  - [x] SubTask 4.6: 其余 200-400 行文档保持单文件（标准模板章节非独立主题）

## Phase 4: 索引与模块说明文档

- [x] Task 5: 编写模块说明文档（各模块 README.md）
  - [x] SubTask 5.1: 编写 `project-reviews/README.md`
  - [x] SubTask 5.2: 编写 `audit-reports/README.md`
  - [x] SubTask 5.3: 编写 `insights/README.md`
  - [x] SubTask 5.4: 编写 `session-reviews/README.md`
  - [x] SubTask 5.5: 编写 `task-summaries/README.md` 及各二级子模块 README.md
  - [x] SubTask 5.6: 编写 `misc/README.md`

- [x] Task 6: 编写总入口索引与元数据文档
  - [x] SubTask 6.1: 编写根目录 `README.md`（总入口 + 导航 + 检索指南）
  - [x] SubTask 6.2: 编写 `_meta/module-catalog.md`（模块目录清单）
  - [x] SubTask 6.3: 编写 `_meta/dependency-graph.md`（依赖关系图谱）
  - [x] SubTask 6.4: 编写 `_meta/migration-log.md`（迁移日志）

## Phase 5: 引用更新与完整性检查

- [x] Task 7: 更新项目内对 retrospectives 的引用路径
  - [x] SubTask 7.1: 搜索项目内所有引用 retrospectives 文件的文档
  - [x] SubTask 7.2: 更新引用路径至模块化新路径
  - [x] SubTask 7.3: 在迁移后文件头部添加别名声明（如文件名变更）

- [x] Task 8: 完整性检查与校验
  - [x] SubTask 8.1: 校验迁移日志覆盖全部 72 份原始文件
  - [x] SubTask 8.2: 校验每份原始内容完整迁移（无信息丢失）
  - [x] SubTask 8.3: 校验所有模块 README.md 完整且文件清单准确
  - [x] SubTask 8.4: 校验依赖图谱与实际引用一致
  - [x] SubTask 8.5: 校验命名规范一致性（纯 ASCII、kebab-case、日期格式）

# Task Dependencies

- [Task 2] depends on [Task 1]
- [Task 3] depends on [Task 2]
- [Task 4] depends on [Task 2]
- [Task 3] 与 [Task 4] 可并行执行
- [Task 5] depends on [Task 3, Task 4]
- [Task 6] depends on [Task 5]
- [Task 7] depends on [Task 3, Task 4]
- [Task 8] depends on [Task 6, Task 7]
