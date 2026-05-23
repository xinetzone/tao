# Changelog - Task Execution Summary

所有关于 **Task Execution Summary** 模块的变更都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
项目遵循 [语义化版本](https://semver.org/lang/zh-CN/) 规范。

## [Unreleased]

### Added
- 初始化模块化的变更日志

## [2.4.0] - 2026-05-20

### Changed
- Description 人工收口：基于优化实验候选描述提炼"双条件触发"机制
- 补回高价值场景锚点（Bug修复 / Sprint复盘 / 故障排查 / 学习总结）
- 明确负向边界：未完成任务、纯学习请求、模板/README 请求不触发

## [2.3.0] - 2026-05-20

### Changed
- Description 收口优化：保留高频触发词与核心场景
- 删除重复穷举描述，降低技能常驻上下文成本

## [2.2.0] - 2026-05-20

### Fixed
- 补齐主文档必需章节
- 修正 references/ 下文档链接
- 移除对远程 API 形态的默认暗示（明确对话内结构化调用方式）

## [2.1.0] - 2026-04-09

### Changed
- Description 触发能力优化：基于 20 个 eval 查询分析，覆盖率从 60% 提升至 100%

## [2.0.0] - 2026-04

### Added
- 四大核心引擎架构：信息收集 / 分析处理 / 报告生成 / 智能推荐
- 标准化 10 章报告模板（执行概览 → 改进行动）
- 三种输出详细程度：summary / standard / detailed
- 错误分级体系：Critical / Error / Warning 三级 + E001-E043 错误码
- 五维深度分析引擎：目标达成度 / 时间效能 / 资源利用 / 问题模式 / 协作效果
- Progressive Disclosure 参考文档架构（8 份 references/ 文档）
- 自动触发 / 手动触发 / 命令式调用三种激活模式
- 降级机制：数据不足时标注低置信度区域，继续生成报告
