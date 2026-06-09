# Chaos 构建后端迁移到 scikit-build-core Spec

## Why
当前 `apps/chaos/pyproject.toml` 使用 PDM 构建后端，存在构建运行速度慢、进程容易被锁定的问题。迁移到 `scikit-build-core` 旨在提升本地与生产打包稳定性，同时保持项目发布、安装和运行行为不变。

## What Changes
- 梳理并迁移现有 PDM 构建后端配置：`[build-system]`、`[tool.pdm.version]`、`[tool.pdm.build]` 及相关项目元数据。
- 将 `apps/chaos/pyproject.toml` 的构建后端改为 `scikit_build_core.build`，并移除 PDM 后端专属配置。
- 按 `scikit-build-core` 规范配置源码包路径、wheel/sdist 打包范围、动态版本来源与必要构建依赖。
- 处理项目当前无根级 `CMakeLists.txt`、无主包 C/C++ 扩展的事实，避免引入无效 C/C++ 构建规则；如后端要求 CMake 项目，则采用官方支持的纯 Python wheel 配置方式。
- 执行构建、安装、生产打包与产物一致性验证，确认迁移不破坏发布产物。
- 更新已有构建文档或项目说明中的后端与构建命令说明，不新增无必要文档文件。

## Impact
- Affected specs: Python 构建、包发布、依赖安装、CI/CD 构建流程。
- Affected code: `apps/chaos/pyproject.toml`，可能涉及已有构建文档、CI 配置或锁文件。

## ADDED Requirements
### Requirement: 使用 scikit-build-core 构建后端
The system SHALL use `scikit-build-core` as the PEP 517 build backend for `apps/chaos`.

#### Scenario: 构建后端识别成功
- **WHEN** 读取 `apps/chaos/pyproject.toml` 的 `[build-system]`
- **THEN** `build-backend` 为 `scikit_build_core.build`
- **AND** `requires` 包含构建 `scikit-build-core` 项目所需依赖
- **AND** 不再包含 `pdm-backend` 作为构建后端依赖

### Requirement: 保留原有项目元数据
The system SHALL preserve existing PEP 621 project metadata, dependencies, optional dependencies, scripts, URLs, Python version constraints, Ruff configuration, Pytest configuration, and Coverage configuration.

#### Scenario: 元数据迁移后保持一致
- **WHEN** 比较迁移前后的项目元数据与非构建工具配置
- **THEN** 包名、作者、维护者、描述、依赖、可选依赖、脚本入口、测试配置和 lint 配置保持语义一致

### Requirement: 保留包内容与源码布局
The system SHALL package the Python sources from `src/taolib` using the existing `src` layout.

#### Scenario: wheel 内容包含 taolib 包
- **WHEN** 执行 wheel 构建
- **THEN** 构建产物包含 `taolib` 包及其包内资源
- **AND** 不包含无关目录、临时产物或测试缓存

### Requirement: 支持动态版本
The system SHALL preserve the existing SCM-derived dynamic version behavior or provide an equivalent `scikit-build-core` compatible configuration.

#### Scenario: 版本生成可用
- **WHEN** 在 Git 工作树中执行构建
- **THEN** 分发包元数据包含可解析版本
- **AND** 若需要写入版本文件，则 `src/taolib/_version.py` 的行为与原配置目标一致

### Requirement: 兼容纯 Python 项目现状
The system SHALL not require a root-level CMake project unless the package actually builds C/C++ extensions.

#### Scenario: 无 C/C++ 扩展时构建成功
- **WHEN** 项目没有根级 `CMakeLists.txt` 且主包无 C/C++ 扩展
- **THEN** 构建配置仍能生成有效 sdist 和 wheel
- **AND** 不引入空的、伪造的或无效的扩展编译规则

### Requirement: 构建性能与锁定问题验证
The system SHALL verify that local build operations complete without the PDM backend lock issue and record relative build results.

#### Scenario: 构建验证通过
- **WHEN** 执行本地构建测试、依赖安装测试和生产环境打包测试
- **THEN** 命令成功完成
- **AND** 没有复现原 PDM 后端进程锁死问题
- **AND** 输出可用于判断构建速度是否有改善

## MODIFIED Requirements
### Requirement: 构建配置归属
The project build configuration SHALL be owned by `scikit-build-core` rather than PDM backend-specific sections.

#### Scenario: PDM 构建配置移除
- **WHEN** 搜索 `apps/chaos/pyproject.toml`
- **THEN** 不存在 `[tool.pdm.build]` 或 PDM 后端专属构建配置
- **AND** 仅保留与依赖管理无冲突的非后端配置（如确有必要）

## REMOVED Requirements
### Requirement: PDM backend 构建
**Reason**: PDM backend 当前存在速度慢与进程锁定问题，不再作为该项目构建后端。
**Migration**: 将 `[build-system]` 与相关 `[tool.pdm.*]` 构建配置迁移为 `scikit-build-core` 官方配置，并通过构建与安装验证确认产物一致。