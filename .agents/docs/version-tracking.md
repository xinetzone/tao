# Python 版本变更追踪机制

## 目的

建立季度性 Python 版本变更追踪机制，确保项目始终对上游 Python 生态的关键变更保持敏感，避免版本升级时出现意外的不兼容。

## 触发条件

以下任一条件满足时，应触发版本追踪任务：

1. Python 官方发布新的 What's New 文档（如 `3.16/whatsnew/3.15.html` 上线）
2. Python 发布新版本 RC（Release Candidate）
3. 距上次版本追踪已超过 3 个月（季度检查）
4. 用户主动发起"/spec 系统学习 Python X.X 更新文档"

## 执行流程

采用已验证的 **"抓取→分类→并行同步→审查→汇总"五步法**：

| 步骤 | 工具/方法 | 产出 |
|------|----------|------|
| 1. 抓取 | `defuddle parse <官方URL> --md` | 原始 Markdown 文档 |
| 2. 分类 | 语义分析（语法特性/标准库/安全/废弃/兼容性） | 分类摘要 |
| 3. 并行同步 | 子智能体分配：技术规范/依赖管理/迁移指南/技术债务 | 4 份更新文档 |
| 4. 审查 | `check_python_compat.py` 自动化扫描 + 人工复核 | 合规性报告 |
| 5. 汇总 | 整合 → 综合报告 → 归档 retrospectives/ | 复盘 + 改进行动 |

## 文档位置

| 文档 | 路径 | 更新频率 |
|------|------|---------|
| 版本适配技术规范 | `.agents/docs/python-version-adaptation.md` | 按版本 |
| 依赖管理 | `.agents/docs/dependency-management.md` | 按版本 |
| 迁移指南 | `.agents/docs/migration-guide.md` | 按版本 |
| 技术债务台账 | `.agents/docs/tech-debt-tracker.md` | 持续追加 |
| 合规扫描脚本 | `.agents/scripts/check_python_compat.py` | 按需更新规则 |

## 历史记录

| 日期 | Python 版本 | 追踪报告 |
|------|------------|---------|
| 2026-05-23 | 3.14 | [python-3.14-adaptation.md](python-3.14-adaptation.md) |
| 2026-05-21 | 3.15 | [python315-adaptation-20260521.md](superpowers/retrospectives/python315-adaptation-20260521.md) |

## 下一次检查：2026-08-21（或 Python 3.16 RC 发布时，以先到者为准）
