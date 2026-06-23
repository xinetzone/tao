# Changelog - Asset Redundancy Analyzer

所有关于 **asset-redundancy-analyzer** 模块的变更都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
项目遵循 [语义化版本](https://semver.org/lang/zh-CN/) 规范。

## [Unreleased]

## [1.0.0] - 2026-06-22

### Added

- **初始版本**：静态资产冗余分析技能。
  - **6 阶段流程**：参数校验 → 文件枚举 → 引用提取 → 缺失检测 → 未引用检测 → 重复检测。
  - **四类 HTML 引用提取**：`script[src]`、`img[src]`、`link[href]`、`@font-face url()`。
  - **决策矩阵**：保留/删除/归档三选一，含理由与风险。
  - **英文注释**：避免 PowerShell 5.1 GBK 编码问题导致中文乱码。
  - **结果对象**：包含 `TotalFiles`、`ReferencedFiles`、`MissingFiles`、`UnreferencedFiles`、`DuplicateFiles`、`Decisions` 等字段。

### Verified

- **react-survey 健康检查**：2 文件 / 1 引用 / 0 缺失 / 0 未引用 / 0 重复 ✅
- **agent-insight 健康检查**：12 文件 / 11 引用 / 0 缺失 / 0 未引用 / 0 重复 ✅
- 证明 P4/P7 清理彻底，无残留冗余。

### Known Limitations

- **PowerShell 5.1 编码限制**：脚本使用英文注释，避免 GBK 读取中文导致乱码与解析失败。
- **正则提取边界**：`@font-face url()` 引用提取需用 `` `" `` 转义字符构建正则，避免 PowerShell 双引号字符串中变量展开在字符类中行为异常。
- **不检查外部 URL**：仅校验源内相对路径引用，不检查 http/https 或 CDN 引用。
