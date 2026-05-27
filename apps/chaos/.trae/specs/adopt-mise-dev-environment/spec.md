# 基于 mise 的完整开发环境管理方案 Spec

## Why
当前项目的开发环境声明分散在 `pyproject.toml`、`scripts/init.ps1`、`README.md` 与多个 GitHub Actions 工作流中，本地与 CI 的工具安装入口不一致，容易造成版本漂移与排障成本上升。
引入 `mise` 作为统一的开发环境编排入口，可以把运行时、包管理器、格式化/静态分析工具和常用任务收敛到单一事实来源，并让团队成员与流水线共享同一套初始化与校验链路。

## What Changes
- 在项目根目录新增符合 `mise` 规范的配置文件，作为开发工具链与任务入口的单一事实来源。
- 将现有环境初始化流程升级为 `mise` 优先的自助引导链路，统一安装工具、切换版本、同步依赖并执行环境校验。
- Python 工具与项目依赖统一通过 `uv` 直接执行或同步，不引入 `pipx` 作为额外安装层。
- 为项目补充完整的 `mise` 使用文档，覆盖安装、初始化、版本升级与常见问题排查。
- 将现有 GitHub Actions 工作流调整为基于 `mise` 安装和执行项目任务，减少分散的版本声明。
- 新增环境一致性校验机制，并要求本地初始化流程与 CI 流程在关键任务前执行校验。

## Impact
- Affected specs: 开发环境初始化、文档构建、测试执行、CI/CD、外部工具引导
- Affected code: `mise.toml`、`scripts/init.ps1`、环境校验脚本、`README.md`、`docs/quickstart.md`、`docs/build-conventions.md`、`docs/contributing.md`、`docs/deploy.md`、`.github/workflows/*.yml`

## ADDED Requirements
### Requirement: 统一的 mise 工具链声明
系统 SHALL 在项目根目录提供一个符合 `mise` 规范的配置文件，集中声明项目依赖的开发工具及其精确版本，并将其作为本地开发与 CI 的共同版本基线。

#### Scenario: 本地首次安装工具链
- **WHEN** 开发者在项目根目录执行 `mise install`
- **THEN** `mise` 根据根配置文件安装项目声明的运行时、包管理器与常用开发工具
- **THEN** 安装结果可通过 `mise ls` 或等效命令核对，且不需要额外手工查找版本号

#### Scenario: 团队成员查看工具清单
- **WHEN** 开发者检查项目的 `mise` 配置
- **THEN** 能在一个位置看到 Python、`uv`、Node.js、`pre-commit`、`ruff`、文档构建依赖入口及项目要求的外部 CLI 工具版本
- **THEN** Python 工具入口使用 `uv run`、`uv tool run` 或项目虚拟环境中的命令，不通过 `pipx` 安装
- **THEN** 不再需要从多个 CI 文件与脚本文档中手工拼接版本信息

### Requirement: 一键初始化与环境收敛
系统 SHALL 提供一个可由团队成员直接执行的环境初始化脚本，基于 `mise` 完成配置信任、工具安装、版本激活、通过 `uv` 直接同步项目依赖、外部 CLI 安装与首次环境校验，并在失败时给出明确修复指引。初始化链路 SHALL NOT 使用 `pipx` 安装 Python 工具。

#### Scenario: Windows PowerShell 7 初始化
- **WHEN** 团队成员在项目根目录执行初始化脚本
- **THEN** 脚本自动检查 `mise` 是否可用，并提示缺失时的安装入口
- **THEN** 脚本自动执行配置 trust、工具安装、Python 依赖同步与外部工具初始化
- **THEN** 脚本结束前运行环境一致性校验，并输出下一步建议命令

#### Scenario: 初始化过程中出现缺失或失败
- **WHEN** `mise` 工具、外部 CLI 或依赖同步步骤失败
- **THEN** 脚本输出失败环节、建议修复命令与可重试步骤
- **THEN** 用户无需阅读实现细节即可定位常见问题

### Requirement: mise 优先的人类文档
系统 SHALL 在面向人类开发者的文档中提供 `mise` 安装与使用说明，并明确本项目推荐的环境准备、日常命令入口、版本更新流程和常见问题排查步骤。

#### Scenario: 新成员按文档接入项目
- **WHEN** 新成员阅读 `README.md` 与 `docs/` 中的相关章节
- **THEN** 能按顺序完成 `mise` 本体安装、项目工具链安装、依赖同步、测试/文档构建命令执行
- **THEN** 文档明确区分 `mise` 负责的工具层与 `uv` 负责的 Python 依赖层

#### Scenario: 团队升级工具版本
- **WHEN** 维护者需要升级 Python、`uv` 或其他开发工具版本
- **THEN** 文档说明应包含配置修改位置、锁定版本更新方法、校验步骤与回滚建议

### Requirement: 基于 mise 的 CI/CD 适配
系统 SHALL 让主要 GitHub Actions 工作流通过 `mise` 安装并激活项目所需工具，随后使用与本地一致的任务入口执行测试、Lint、文档构建和发布前校验。

#### Scenario: CI 测试流程执行
- **WHEN** `ci.yml` 在 GitHub Actions 中运行
- **THEN** 工作流通过 `mise` 安装项目声明的工具链
- **THEN** 测试、Lint 与安全检查使用 `mise` 管理的环境执行
- **THEN** Python 或 `uv` 版本不再在多个步骤中重复硬编码

#### Scenario: 文档与发布流程执行
- **WHEN** Pages、发布或打包相关工作流运行
- **THEN** 它们复用同一份 `mise` 工具声明
- **THEN** 系统级依赖（如 `graphviz`）与 `mise` 管理的工具边界清晰分离

### Requirement: 启动前环境一致性校验
系统 SHALL 提供环境一致性校验脚本，在本地初始化完成后和关键项目任务执行前检查工具版本是否满足项目声明，并在不匹配时输出期望值、当前值与修复命令。

#### Scenario: 本地版本不匹配
- **WHEN** 开发者运行环境校验脚本且本机工具版本与项目声明不一致
- **THEN** 输出至少包含工具名称、期望版本、当前版本和推荐修复命令
- **THEN** 提示开发者优先使用 `mise install`、`mise use` 或项目初始化脚本恢复一致性

#### Scenario: CI 中发现环境漂移
- **WHEN** 工作流在执行测试或构建前运行环境校验
- **THEN** 若发现工具未按项目声明安装，任务立即失败
- **THEN** 日志能直接指向 `mise` 配置或初始化步骤，而不是笼统的命令不存在错误

## MODIFIED Requirements
### Requirement: 现有环境初始化流程
项目现有的环境初始化流程必须从“手工检查 Node/npm 并单独安装 `defuddle`”升级为“以 `mise` 为统一入口的工具链初始化流程”，并保留对外部工具安装结果的明确反馈。

### Requirement: 现有 CI 工具安装流程
项目现有 GitHub Actions 中分散的 `setup-python`、`setup-uv` 与版本硬编码流程必须收敛到共享的 `mise` 工具声明，避免本地与流水线出现双重版本源。

## REMOVED Requirements
### Requirement: 无
**Reason**: 本次变更以统一和收敛现有环境管理方式为主，不移除项目已有的功能能力。
**Migration**: 现有 `uv` 工作流继续保留，但改为由 `mise` 负责提供运行时与工具版本基线。
