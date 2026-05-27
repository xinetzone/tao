# 2026-05 项目级变更日志

所有关于 **AgentForge** 项目级别的跨模块变更都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
项目遵循 [语义化版本](https://semver.org/lang/zh-CN/) 规范。

## [Unreleased]
### Added
- 引入模块化的变更日志管理机制，按照模块与时间（项目级）拆分 CHANGELOG。
- 新增 `taolib.github_app` GitHub App 安装令牌管理层，支持请求级覆盖头、环境降级、进程内缓存、单飞刷新与 CLI 诊断输出。
- 新增 `docs/github-app-token-override.md` 学习笔记，沉淀 GitHub App 安装令牌覆盖头的背景、迁移要点与工程启发。
- 新增 `.agents/docs/superpowers/retrospectives/2026-05-22-github-app-installation-token-override-testing.md`，记录专项测试、并发指标与残余风险。
- 新增 `.agents/docs/superpowers/retrospectives/task-summary-ci-pipeline-systematic-fix-20260527.md`，记录 CI 流水线 6 轮链式故障的系统性修复过程与经验总结。

### Changed
- 构建后端从 `setuptools.build_meta` + `setuptools-scm` 迁移至 `pdm.backend`，启用 `[tool.pdm.version] source = "scm"` 动态版本派生，统一文档与实际配置。
- 清理遗留构建钩子 `.pdm_build.py` 与 `[tool.setuptools_scm]` 配置段。
- Ruff `target-version` 从 `py313` 升级为 `py314`，与项目 `requires-python = ">=3.14"` 对齐。
- 移除 `optional-dependencies.task` 中零引用的 `metaflow` 死依赖。
- 容器测试环境 `Containerfile.test` 移除 `SETUPTOOLS_SCM_PRETEND_VERSION`（pdm-backend 无 git 时自动回退 `0.0.0`）。
- 更新 `docs/tech/build-conventions.md` 补充 pdm-backend 原生能力与 `write_to` 路径说明。
- 更新 `docs/index.md` 与 `README.md`，补充 GitHub App 令牌治理入口、专项测试入口与文档导航。
- 更新 `.github/workflows/ci.yml`，在全量测试前显式执行 `tests/github_app` 专项校验，提升 GitHub App 认证层回归可见性。
- 升级 `codecov/codecov-action` 从 v4 到 v5，消除 Node.js 20 弃用警告，并适配 v5 参数变更（`file` → `files`）。
- 清理 `.temp/` 目录：移除 PDF 评估项目的 29 个临时产物（脚本、数据、评估输出、书籍工作副本），输出已归档至 `docs/general/philosophy/laozi-boshu/`，脚本模式已沉淀为 `pdf-to-markdown` skill。

### Fixed
- 修复 pdf-to-markdown CI 测试因 fpdf2+pdfplumber CJK 文本提取不可靠导致失败的问题（通过 fixture 注入绕过 PDF 提取管线）。
- 修复 ruff format lint 失败（Round 1 修改的测试文件未预先格式化）。
- 修复 github-app 可选依赖（httpx/PyJWT/PyGithub）在 `mise.toml` 和 `Containerfile.test` 中缺失的问题（`uv sync --group test` 未加 `--extra github-app`）。
- 修复 `check_env.py` 中 `ruff_target_for_python` 硬编码 `supported_minor=13` 导致 CI lint 因 Ruff `target-version=py314` 校验失败的问题（已更新为 14）。
- 修复 Ruff `target-version` 从 `py313` 升级为 `py314` 后触发 16 个文件格式重排与 2 处 UP037（quoted-annotation）lint 错误的 CI 失败。
- 修复 `.agents/docs/superpowers/retrospectives/task-summary-ci-pipeline-systematic-fix-20260527.md` 中 trailing-whitespace 导致的 pre-commit hook 失败。
- 修复 `mise.toml` 与 `Containerfile.test` 中 `sh` 执行 `sync-test-deps.sh` 因 dash 不支持 `set -o pipefail` 导致 CI security job 失败的问题（改为 `bash`）。
- 修复 `Containerfile.test` 中 pdm-backend 构建时因 `LICENSE` 文件未复制到 Docker 缓存层导致容器测试 job 失败的问题。
