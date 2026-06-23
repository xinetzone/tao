# Checklist

## 目录骨架与命名规范
- [x] 一级模块目录已创建（project-reviews/、audit-reports/、insights/、session-reviews/、task-summaries/、misc/、_meta/）
- [x] task-summaries 二级子模块目录已创建（ci-cd/、documentation/、python-environment/、skills/、releases/、exploration/、world-cli/、refactoring/、misc/）
- [x] `_meta/naming-convention.md` 命名规范文档已编写，包含目录名、文件名、日期格式规则

## 原子化拆分
- [x] 大型多主题文档（>200 行或多主题）已识别并记录拆分方案
- [x] 每份大型文档已转为同名目录，内含 `index.md` 与原子单元文件
- [x] 每个原子单元文件专注单一主题，可独立阅读
- [x] 原子单元文件名使用英文 kebab-case，描述单一主题

## 模块化分类
- [x] 全部 72 份原始文件已按一级模块类型分类
- [x] task-summaries 文档已按二级主题分类
- [x] 模块内部高内聚（同类文档聚集）
- [x] 模块之间低耦合（跨模块引用通过依赖图谱记录）

## 结构化层级与命名
- [x] 目录树结构符合 spec 中定义的层级
- [x] 所有目录名为纯 ASCII 英文 kebab-case
- [x] 所有文件名遵循 `{topic}-{date}.md` 或 `{section-name}.md` 格式
- [x] 日期格式统一为 YYYYMMDD
- [x] 无中文、emoji、空格出现在目录名或文件名中

## 引用关系图谱
- [x] `_meta/dependency-graph.md` 已生成
- [x] 图谱记录每份文档的正向依赖（引用的其他文档）
- [x] 图谱记录每份文档的反向依赖（被哪些文档引用）
- [x] 图谱记录模块间依赖关系汇总
- [x] 关键依赖链使用 Mermaid 流程图可视化

## 索引与模块说明文档
- [x] 根目录 `README.md` 已编写，含总体说明、模块导航表、命名规范摘要、检索指南
- [x] 每个一级模块含 `README.md`，含功能描述、使用方法、依赖关系、维护责任人、文件清单
- [x] task-summaries 各二级子模块含 `README.md`
- [x] `_meta/module-catalog.md` 提供所有模块完整清单（路径、功能、文件数、维护者）

## 完整性检查
- [x] `_meta/migration-log.md` 已生成，覆盖全部 72 份原始文件
- [x] 每份原始文件在迁移日志中记录原始名、去向、是否拆分、拆分单元清单、校验状态
- [x] 每份原始文件标记为"完整迁移"
- [x] 无原始内容丢失（章节、表格、代码块、Mermaid 图均保留）
- [x] 项目内对 retrospectives 的引用路径已更新至模块化新路径
- [x] 文件名变更的文档已添加别名声明
