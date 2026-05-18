# 项目级变更日志 - 2026年4月 (v0.5.5)

本文件记录 v0.5.5（2026-04-06）的项目级别（跨模块）变更。各功能模块的详细变更请参见对应模块的 CHANGELOG。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
项目遵循 [语义化版本](https://semver.org/lang/zh-CN/) 规范。

## [0.5.5] - 2026-04-06

本版本是一次重大功能扩展，将 taolib 从单一配置管理库升级为企业级全栈微服务平台。
新增 8 个后端服务模块，建立完整的认证体系、数据管道和容器化部署架构。

### 新增（项目级）

- **新增 `taolib.testing.site` 博客/CMS 平台**
  - FastAPI + SQLAlchemy 架构、Markdown 渲染、RSS/Atom Feed 生成
- **pyproject.toml**：新增 13 个可选依赖组（analytics、file-storage、oauth、email-service、rate-limiter、site 等）
- **部署架构**：Podman Compose 编排重构，容器文件迁移到 `deploy/services/`
- **测试套件扩展**：新增 analytics、oauth、file_storage、email_service、task_queue 测试模块（25+ 测试文件），迁移至 `tests/testing/` 目录
- 新增 Ruff 配置到 `pyproject.toml`（代码检查 + 格式化）
- 新增 pytest 和 coverage 配置到 `pyproject.toml`
- **CI/CD 增强**：添加测试覆盖率阈值检查（>= 80%）
- **性能基准测试增强**：`tests/testing/perf_remote_bench.py` 新增功能正确性验证和历史性能对比

### 修改（项目级）

- 统一测试框架文档：CLAUDE.md 和 AGENTS.md 测试命令统一使用 pytest
- Sphinx 版本约束从 `==8.2.3` 改为 `>=8.2.3`（灵活版本）
- **架构优化**：`taolib.testing.doc` 模块解耦重构
  - 将 `_make_project_namespace` 提取为模块级函数
  - 新增 `ProjectConfigValidator` 类
  - 新增配置验证异常（`ValueError`、`TypeError`）

### 修复（项目级）

- 移除 `.pre-commit-config.yaml` 中不兼容的 Poetry hook（项目使用 PDM）

### 移除

- 移除 `.pre-commit-config.yaml` 中的 Poetry hook

### 安全（项目级）

- `taolib.testing/remote/ssh.toml` 示例配置移除明文密码，改为占位符
