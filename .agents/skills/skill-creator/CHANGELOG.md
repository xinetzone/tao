# Changelog - Skill Creator

所有关于 **Skill Creator** 模块的变更都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
项目遵循 [语义化版本](https://semver.org/lang/zh-CN/) 规范。

## [Unreleased]

### Added
- 初始化模块化的变更日志

## [1.0.0] - 2026-05-20

### Added
- 技能创建全流程支持：意图捕获 → 用户访谈 → SKILL.md 撰写 → 测试评估 → 迭代优化
- 三层渐进式披露架构：Metadata → SKILL.md body → Bundled Resources
- 评估系统：并行基准测试（with-skill / baseline / old-skill）、盲对比、定量断言 + 定性审查
- 评估查看器（eval-viewer）：`generate_review.py` 生成 Outputs + Benchmark 双标签页
- Description 优化工具链：`run_loop.py` 自动迭代优化触发描述，`run_eval.py` 评估触发覆盖率
- 技能打包工具：`package_skill.py` 生成 `.skill` 分发文件
- 基准聚合脚本：`aggregate_benchmark.py` 汇总迭代统计数据
- 快速验证脚本：`quick_validate.py`

### Changed
- Windows 兼容性修复（2026-05-20）：路径分隔符、编码处理、子进程调用适配
- 技能描述收口优化：基于 eval 查询分析精简描述，降低上下文占用

## [0.1.0] - 2026-04

### Added
- 初始技能骨架：agents/ 子代理指令（analyzer / comparator / grader）
- 参考文档：`references/schemas.md` 定义 JSON 数据结构
