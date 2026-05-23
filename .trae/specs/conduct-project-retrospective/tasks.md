# Tasks

- [x] Task 1: 收集项目复盘依据材料：识别并读取项目目标、需求、规格、变更记录、文档、代码结构、测试配置、日志与历史任务材料。
  - [x] SubTask 1.1: 梳理项目根目录、`.trae/specs/`、`.agents/`、`docs/`、`README.md`、`CHANGELOG.md` 等可用依据来源
  - [x] SubTask 1.2: 提取目标、需求、里程碑、交付成果、质量标准、风险问题与协作信息
  - [x] SubTask 1.3: 标注资料来源、证据强度与信息缺口

- [x] Task 2: 完成项目目标复盘：对照预设目标、核心指标与需求说明，核验交付成果完成度并分析未达成原因。
  - [x] SubTask 2.1: 建立目标、需求、核心指标与交付成果映射表
  - [x] SubTask 2.2: 标注每项交付成果的完成状态与核验证据
  - [x] SubTask 2.3: 分析未完成、部分完成或无法核验事项的具体原因

- [x] Task 3: 完成执行过程复盘：梳理项目全周期规划、资源配置、沟通协作链路与里程碑完成情况。
  - [x] SubTask 3.1: 汇总项目阶段、任务推进路径与关键里程碑
  - [x] SubTask 3.2: 分析计划与实际执行偏差
  - [x] SubTask 3.3: 识别进度延误、资源错配、沟通断层等问题诱因

- [x] Task 4: 完成风险与问题复盘：汇总风险点、突发问题、应对措施，并评估处置效果。
  - [x] SubTask 4.1: 建立风险与问题清单
  - [x] SubTask 4.2: 记录每类问题的应对措施与结果
  - [x] SubTask 4.3: 总结风险预判、响应机制与处置流程的优化方向

- [x] Task 5: 完成成果质量复盘：核验产品、代码、文档等交付成果质量，梳理缺陷并分析根因。
  - [x] SubTask 5.1: 识别主要交付成果与质量标准
  - [x] SubTask 5.2: 运行或读取适用的验证结果，包括测试、静态检查、兼容性检查或文档一致性检查
  - [x] SubTask 5.3: 归纳质量缺陷、影响范围与根因

- [x] Task 6: 完成团队协作复盘：总结协作效率、责任落实、跨角色堵点与改进方案。
  - [x] SubTask 6.1: 从项目材料中识别参与方、职责边界与协作链路
  - [x] SubTask 6.2: 分析责任落实、交接、评审与沟通机制中的堵点
  - [x] SubTask 6.3: 提炼提升协作效率的可执行方案

- [x] Task 7: 输出并归档完整复盘报告：形成覆盖六大模块的 Markdown 报告并保存至规定目录。
  - [x] SubTask 7.1: 撰写项目整体成效总结、核心问题清单、经验教训与改进方案
  - [x] SubTask 7.2: 明确后续整改与能力提升行动项，包括责任对象、触发条件与验收方式
  - [x] SubTask 7.3: 将报告保存至 `.agents/docs/superpowers/retrospectives/`

- [x] Task 8: 验证复盘报告完整性：依据 checklist.md 检查报告结构、证据链、结论边界与归档位置。
  - [x] SubTask 8.1: 确认报告覆盖用户要求的六个结构化流程
  - [x] SubTask 8.2: 确认低置信度判断已标注且没有无依据断言
  - [x] SubTask 8.3: 确认行动项具备可执行性与可验收性

# Task Dependencies

- Task 2 depends on Task 1
- Task 3 depends on Task 1
- Task 4 depends on Task 1
- Task 5 depends on Task 1
- Task 6 depends on Task 1
- Task 7 depends on Task 2, Task 3, Task 4, Task 5, Task 6
- Task 8 depends on Task 7
