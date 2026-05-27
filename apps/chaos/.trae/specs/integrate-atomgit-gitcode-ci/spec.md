# AtomGit + GitCode CI/CD 集成规范

## Why
当前项目仅适配 GitHub 托管与 GitHub Actions CI/CD，GitCode 注册流程繁琐但提供更贴合国内开发场景的 CI/CD 能力。本项目需新增对 AtomGit 代码托管平台的支持，同时集成 GitCode Pipeline CI/CD 能力，扩展项目的多平台兼容性与自动化交付覆盖。

## What Changes
- 验证并确保项目与 AtomGit 平台的全流程 Git 操作兼容（无代码改动，以文档适配为主）
- 在 `.gitcode/workflows/` 目录下创建符合 GitCode Pipeline 规范的 CI 工作流文件
- 覆盖代码拉取、依赖安装、构建编译、单元测试、静态代码扫描全流程
- 更新项目部署说明文档，补充 AtomGit + GitCode CI 使用指引

## Impact
- Affected specs: 无（新增能力，不修改现有规范）
- Affected code:
  - 新增 `.gitcode/workflows/ci.yml` — GitCode CI 主工作流
  - 修改 `docs/` 下的部署/运维相关文档（补充多平台说明）
  - 无现有代码破坏性变更

## ADDED Requirements

### Requirement: AtomGit 平台 Git 操作兼容
项目 SHALL 确保可在 AtomGit 平台正常完成仓库克隆、推送、拉取、分支管理等全流程 Git 操作，兼容平台的协作规则（PR/MR 流程、分支保护等）。

#### Scenario: 从 AtomGit 克隆仓库并推送代码
- **GIVEN** 项目已推送至 AtomGit 平台
- **WHEN** 开发者执行 `git clone <atomgit-remote-url>`
- **THEN** 仓库完整克隆到本地，包含所有分支和提交历史
- **AND** 开发者可在本地提交并成功推送至 AtomGit 远程仓库

#### Scenario: 无 GitHub 强依赖阻断
- **GIVEN** 项目仓库托管于 AtomGit 平台
- **WHEN** 执行 `git` 操作（clone/push/pull/fetch）
- **THEN** 不应出现依赖 GitHub 特定域名/API 的错误
- **AND** `.gitignore`、Git hooks、配置文件等均不包含 GitHub 绝对 URL 硬编码

### Requirement: GitCode CI 工作流配置
项目 SHALL 在 `.gitcode/workflows/` 目录下提供符合 GitCode Pipeline 规范的 CI 工作流 YAML 文件，覆盖以下流水线阶段：

#### Scenario: 代码拉取与 Python 环境准备
- **WHEN** 工作流被触发（push / pull_request / workflow_dispatch）
- **THEN** 系统通过 `checkout-action` 拉取仓库代码至 `repo_workspace`
- **AND** 通过 `setup-python` 配置 Python 3.14 运行环境

#### Scenario: 依赖安装
- **WHEN** Python 环境就绪
- **THEN** 安装 `uv` 包管理器
- **AND** 执行 `uv sync --group test` 同步测试依赖

#### Scenario: 静态代码扫描
- **WHEN** 依赖安装完成
- **THEN** 执行 `ruff check` 进行代码规范检查
- **AND** 检查结果作为 CI 报告输出

#### Scenario: 单元测试与覆盖率
- **WHEN** 静态扫描通过
- **THEN** 执行 `pytest` 运行完整测试套件并生成覆盖率报告
- **AND** 覆盖率不低于 80%（与项目现有标准一致）

#### Scenario: 构建编译
- **WHEN** 测试通过
- **THEN** 执行 `uv build` 构建 Python 包
- **AND** 构建产物作为工件（artifact）上传保存

### Requirement: 平台文档更新
项目 SHALL 在部署说明文档中补充 AtomGit 平台使用指引、GitCode CI 工作流的触发规则与维护说明。

#### Scenario: AtomGit 使用指引
- **GIVEN** 开发者阅读部署文档
- **WHEN** 查看平台支持章节
- **THEN** 应包含 AtomGit 仓库配置步骤、远程地址设置、协作流程说明

#### Scenario: GitCode CI 触达与维护说明
- **GIVEN** 开发者阅读 CI/CD 章节
- **WHEN** 查看 GitCode Pipeline 说明
- **THEN** 应包含工作流触发规则（push/pull_request/manual）、配置说明、维护指引
