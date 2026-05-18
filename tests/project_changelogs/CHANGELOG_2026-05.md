# 项目级变更日志 - 2026年5月

本文件记录 2026 年 5 月的项目级别（跨模块）变更。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
项目遵循 [语义化版本](https://semver.org/lang/zh-CN/) 规范。

## [未发布] - 2026-05

### 修改

- **项目复盘与去重优化**（2026-05）：
  - 删除 `pytest.ini`，pytest 配置统一至 `pyproject.toml` 的 `[tool.pytest.ini_options]` 段，消除配置覆盖风险
  - 统一各文件中 Python 版本声明：`README.md`、`AGENTS.md` 与 `pyproject.toml` 的 `requires-python` 保持一致
  - 精简 `AGENTS.md` 核心功能速览，改为引用 `README.md`，消除逐字重复
  - 整合 `specs/` 目录至 `.trae/specs/multi_agent_system/`，所有设计文档集中管理
  - 合并 `doc/scripts/` 至 `scripts/` 目录，消除分散存放
  - 新增 `reports/README.md` 解释报告来源与时效性
  - 在 `doc/index.md` 中补充 `.qoder/repowiki/` 自动生成文档的参考说明

- **目录结构优化**：
  - 将文档文件组织到 `doc/` 目录的子目录中
  - 创建 `doc/user_guide/`、`doc/api_reference/`、`doc/developer_guide/`、`doc/architecture/` 目录
  - 创建 `configs/` 目录用于存放配置文件
  - 更新 README.md 和 AGENTS.md 中的文档链接

- **CHANGELOG 拆分**（2026-05）：
  - 将 `CHANGELOG.md` 按功能模块拆分为多个文件，迁移至 `tests/` 目录下各模块测试子目录中
  - 保留根目录 `CHANGELOG.md` 作为导航索引文件
  - 更新 `doc/architecture/directory_structure.md` 中关于 CHANGELOG 的描述
