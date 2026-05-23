# Tasks

- [x] Task 1: 审查并消除 GitHub 硬编码依赖，确保 AtomGit 兼容
  - [x] 审查项目配置文件中的 GitHub 绝对 URL 引用（pyproject.toml、README.md、CI 配置等）
  - [x] 检查 `.gitignore`、`.git/hooks/`、`.agents/` 中的平台特定依赖
  - [x] 验证 `git remote` 操作不依赖 GitHub 特定域名
  - [x] 记录审查结果，标记已确认无问题的项

- [x] Task 2: 创建 `.gitcode/workflows/ci.yml` 工作流文件
  - [x] 定义工作流触发规则：push to main、pull_request to main、workflow_dispatch 手动触发
  - [x] 配置 `lint` 作业：checkout → setup-python 3.14 → 安装 uv → 同步依赖 → ruff check
  - [x] 配置 `test` 作业：checkout → setup-python 3.14 → 安装 uv → 同步依赖 → pytest + coverage
  - [x] 配置 `build` 作业：checkout → setup-python 3.14 → 安装 uv → 同步依赖 → uv build
  - [x] 设置作业间依赖关系（test 依赖 lint，build 依赖 test）
  - [x] 确保工作流使用 GitCode 平台标准：runner 为 `euleros-2.10.1`、使用 `checkout-action` 和 `setup-python` 内置动作

- [x] Task 3: 更新项目部署说明文档
  - [x] 在 `docs/` 目录中的 `deploy.md` 补充 AtomGit 平台使用指引
  - [x] 补充 GitCode CI 工作流触发规则说明、配置结构解释、维护指引
  - [x] 补充从 AtomGit 克隆、推送、协作的基础操作示例

- [x] Task 4: 验证 GitCode CI 工作流可执行性
  - [x] CI 工作流中 `ruff check` 命令与项目现有配置一致
  - [x] 确认 workflow 引用的内置 action 版本号（`checkout-action@0.0.1`、`setup-python@0.0.1`）与 GitCode 官方文档一致
  - [x] 确认 `setup-python` 支持指定 `python-version: "3.14"` 下载对应版本
  - [x] 验证 `uv build` 产物路径（`dist/`）与构建步骤匹配

# Task Dependencies
- Task 2 依赖 Task 1（需先确认无平台硬编码，再编写 CI）
- Task 3 可与 Task 1、Task 2 并行
- Task 4 依赖 Task 2（需 CI 文件就绪后验证）
