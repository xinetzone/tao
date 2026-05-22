# Tasks
- [x] Task 1: 盘点现有工具链并建立 `mise` 单一事实来源。
  - [x] SubTask 1.1: 汇总当前项目在 `pyproject.toml`、`scripts/init.ps1`、`.pre-commit-config.yaml` 与 GitHub Actions 中使用的运行时、包管理器、Lint/格式化与外部 CLI。
  - [x] SubTask 1.2: 设计根目录 `mise` 配置文件的结构，明确需要锁定的工具、精确版本、常用任务入口与环境变量约定。
  - [x] SubTask 1.3: 明确哪些工具继续由 `uv` 管理 Python 包依赖，哪些工具改由 `mise` 负责安装与切换版本，并确认不引入 `pipx` 安装层。

- [x] Task 2: 实现基于 `mise` 的初始化与环境校验链路。
  - [x] SubTask 2.1: 将现有 `scripts/init.ps1` 重构为 `mise` 优先的初始化脚本，串联 trust、install、`uv` 直接依赖同步、外部工具安装与结果汇总，不使用 `pipx`。
  - [x] SubTask 2.2: 新增环境一致性校验脚本，校验关键工具版本并输出“期望值 / 当前值 / 修复命令”。
  - [x] SubTask 2.3: 定义本地常用命令在执行前触发环境校验的机制，保证启动前先做版本一致性检查。

- [x] Task 3: 补齐面向人类开发者的 `mise` 文档。
  - [x] SubTask 3.1: 更新 `README.md` 的环境依赖与安装步骤，使其改为 `mise` 优先的接入路径。
  - [x] SubTask 3.2: 更新 `docs/quickstart.md`、`docs/build-conventions.md`、`docs/contributing.md` 与 `docs/deploy.md` 中涉及环境准备和命令执行的章节。
  - [x] SubTask 3.3: 增补 `mise` 本体安装指引、版本升级流程、常见问题排查与恢复步骤。

- [x] Task 4: 让 CI/CD 工作流与本地环境共享同一套 `mise` 工具声明。
  - [x] SubTask 4.1: 调整 `ci.yml`、`pages.yml`、`python-publish.yml` 与 `release.yml` 的工具安装步骤，使其通过 `mise` 安装并激活运行环境。
  - [x] SubTask 4.2: 统一测试、Lint、文档构建与发布前校验的命令入口，减少 workflow 中分散的版本硬编码。
  - [x] SubTask 4.3: 保留必要的系统级依赖安装步骤，并与 `mise` 管理的工具边界明确区分。

- [x] Task 5: 验证 `mise` 方案满足交付要求。
  - [x] SubTask 5.1: 本地验证初始化脚本与环境校验脚本的成功路径和典型失败提示。
  - [x] SubTask 5.2: 校验 GitHub Actions YAML、项目文档引用与任务入口描述的一致性。
  - [x] SubTask 5.3: 将验收结果回填到 `checklist.md`，确保每项要求都有对应实现与验证证据。

# Task Dependencies
- [Task 2] depends on [Task 1]
- [Task 3] depends on [Task 1, Task 2]
- [Task 4] depends on [Task 1]
- [Task 5] depends on [Task 2, Task 3, Task 4]
