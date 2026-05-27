# Tasks
- [x] Task 1: 获取并解析 Python 3.15 更新文档
  - [x] SubTask 1.1: 使用 `defuddle` CLI 工具抓取 `https://docs.python.org/zh-cn/3.16/whatsnew/3.15.html` 的 Markdown 内容。
  - [x] SubTask 1.2: 对抓取的内容进行分类整理（语法特性、标准库变更、性能优化、安全修复、废弃功能、兼容性调整）。
- [x] Task 2: 更新项目各类规范与台账文档（遵循 AGENTS.md 约定存放）
  - [x] SubTask 2.1: 更新技术规范文档（Python 版本适配章节） - 录入核心语言特性更新。
  - [x] SubTask 2.2: 更新依赖管理文档 - 录入标准库接口变更。
  - [x] SubTask 2.3: 更新迁移指南文档 - 录入兼容性调整内容。
  - [x] SubTask 2.4: 更新技术债务追踪台账 - 录入废弃功能。
- [x] Task 3: 现有代码合规性审查
  - [x] SubTask 3.1: 结合兼容性调整与废弃功能，扫描项目中现有 Python 代码。
  - [x] SubTask 3.2: 整理不兼容代码片段及相应的整改建议。
- [x] Task 4: 生成版本适配更新报告
  - [x] SubTask 4.1: 整合上述文档更新与代码审查结果。
  - [x] SubTask 4.2: 按照项目规范，将复盘/更新报告归档至 `.agents/docs/superpowers/retrospectives/` 目录下。
- [x] Task 5: P3 流程改进
  - [x] SubTask 5.1: 建立子智能体引用策略规范 (`.agents/rules/citations.md`)
  - [x] SubTask 5.2: 将 Python 版本合规扫描脚本化 (`.agents/scripts/check_python_compat.py`)
  - [x] SubTask 5.3: AGENTS.md 增加版本升级适配触发规则
  - [x] SubTask 5.4: 建立季度版本追踪机制 (`.agents/docs/version-tracking.md`)
- [x] Task 6: P4 工具增强
  - [x] SubTask 6.1: AST 级弃用检测脚本 (`.agents/scripts/check_python_deprecations.py`)
  - [x] SubTask 6.2: defuddle 预装集成到项目环境 (`scripts/init.ps1`)

# Task Dependencies
- [Task 2] depends on [Task 1]
- [Task 3] depends on [Task 1]
- [Task 4] depends on [Task 2, Task 3]
