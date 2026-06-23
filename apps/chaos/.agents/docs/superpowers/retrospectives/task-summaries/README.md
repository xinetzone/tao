# 任务总结模块（总入口）

> **维护责任人**：Leader Agent

## 模块功能

存放各类任务执行总结报告，按主题划分为 9 个二级子模块，覆盖 CI/CD、文档治理、Python 环境、技能资产、版本发布、探索任务、World CLI、代码重构与其他任务，是 retrospectives 目录中规模最大的复盘资产集合。

## 使用方法

- **何时查阅**：需要回顾具体任务执行过程、提炼任务级经验、查找特定主题的任务总结时查阅
- **如何引用**：使用相对路径引用子模块，如 `[CI/CD 任务总结](./ci-cd/README.md)`

## 依赖关系

- 关联 `project-reviews/`（任务总结为项目级复盘提供素材）
- 关联 `insights/`（部分任务总结配套洞察报告）
- 关联 `audit-reports/`（治理类任务总结源自审计结论）

## 二级子模块清单

| 子模块 | 用途 |
|--------|------|
| [`ci-cd/`](./ci-cd/README.md) | CI/CD 流水线修复、lint 与链接校验、Windows CI 治理等任务总结 |
| [`documentation/`](./documentation/README.md) | 文档治理、目录边界、双轨重构、规则演化等任务总结 |
| [`python-environment/`](./python-environment/README.md) | Python 环境管理、lint 修复、PDM/mise 迁移、Python 3.13+ 适配等任务总结 |
| [`skills/`](./skills/README.md) | 技能资产开发、Windows 兼容性修复、生态验证脚本等任务总结 |
| [`releases/`](./releases/README.md) | 版本发布任务总结，涵盖 v0.3.0 至 v0.7.0 及后续改进 |
| [`exploration/`](./exploration/README.md) | 探索性任务总结，含行业对齐、知识萃取、参考完整性检查等 |
| [`world-cli/`](./world-cli/README.md) | World CLI 分发系统、层级规范、多表面探索等任务总结 |
| [`refactoring/`](./refactoring/README.md) | 代码重构任务总结，含 ContainerRun 重构、跨模块导入重构等 |
| [`misc/`](./misc/README.md) | 其他任务总结，含协作体系搭建、PDF 工具评估、知乎集成等 |

## 文件清单

本目录仅包含 9 个二级子模块目录，具体文件清单见各子模块 README。
