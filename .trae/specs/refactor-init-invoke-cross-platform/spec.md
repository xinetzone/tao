# 环境初始化跨平台 Invoke 重构 Spec

## Why
当前 `scripts/init.ps1` 以 PowerShell 实现环境初始化，天然耦合 Windows 平台，无法在 Linux/macOS 上直接运行。项目已在 `docs/tasks.py` 中成功使用 Python `invoke` 包实现跨平台文档构建任务，应采用相同模式将初始化流程迁移到 Python invoke 任务，彻底消除平台锁定。

## What Changes
- 新建项目根目录 `tasks.py`，使用 Python `invoke` 包定义 `init` 和 `init-check` 两个顶层任务，替代 `scripts/init.ps1` 的全部功能。
- Python 原生跨平台：`sys.platform` 检测 Windows/Linux/macOS，`pathlib.Path` 处理路径，`subprocess.run` 执行外部命令——无需任何条件分支。
- 保留核心初始化链路：`mise trust` → `mise install` → `mise run sync` → `mise run check-env`，以及 `-CheckOnly` 等价行为（`init-check` 任务）。
- 在 `mise.toml` 中新增 `tasks.init` / `tasks.init-check` 任务入口，作为统一调用方式。
- 更新所有文档引用：`pwsh -File scripts/init.ps1` → `mise run init` / `mise run init-check`。
- 保留 `scripts/init.ps1` 原文件不动（向后兼容），但不再推荐使用。

## Impact
- Affected specs: 环境初始化、跨平台开发环境接入、开发者文档、初始化验证
- Affected code: **新建** `tasks.py`（项目根）、`mise.toml`（新增 init 任务）、`README.md`、`docs/quickstart.md`、`docs/build-conventions.md`、`docs/contributing.md`、`docs/deploy.md`

## ADDED Requirements
### Requirement: 基于 Python invoke 的跨平台初始化
系统 SHALL 在项目根目录提供 `tasks.py`，使用 Python `invoke` 包定义环境初始化任务，在 Windows、Linux、macOS 上无需额外运行时即可执行。

#### Scenario: 开发者执行完整初始化
- **WHEN** 开发者在任意操作系统上执行 `mise run init`（或 `uv run invoke init`）
- **THEN** invoke 任务顺序执行 `mise trust` → `mise install` → `mise run sync` → `mise run check-env`
- **THEN** 每步执行结果以 `[STEP]` / `[OK]` / `[FAIL]` 格式输出
- **THEN** 任一命令失败时输出 `[FIX]` 修复提示并中止后续步骤

#### Scenario: 开发者仅执行环境检查
- **WHEN** 开发者执行 `mise run init-check`（等价原 `-CheckOnly`）
- **THEN** invoke 任务仅执行 `mise trust` → `mise run check-env`
- **THEN** 不执行 `mise install` 和 `mise run sync`

#### Scenario: mise 未安装
- **WHEN** 当前环境未安装 `mise` 命令
- **THEN** 任务输出 `[ERROR] 未检测到 mise` 及安装链接提示
- **THEN** 返回非零退出码

### Requirement: invoke 任务与 mise 任务入口集成
系统 SHALL 在 `mise.toml` 中定义 `tasks.init` 和 `tasks.init-check`，让开发者可以通过 `mise run init` / `mise run init-check` 统一调用初始化流程。

#### Scenario: mise run init 调用链路
- **WHEN** 开发者执行 `mise run init`
- **THEN** mise 激活 Python 环境后调用 `uv run invoke init`
- **THEN** 前置依赖 `check-env` 确保工具链就绪后才执行初始化

### Requirement: 跨平台适配说明
系统 SHALL 在所有涉及初始化流程的面向开发者文档中，将调用方式从 `pwsh -File scripts/init.ps1` 更新为 `mise run init` / `mise run init-check`，并说明 Python invoke 方案的跨平台特性。

#### Scenario: 开发者查阅初始化文档
- **WHEN** 开发者阅读 README.md / quickstart.md / build-conventions.md / contributing.md / deploy.md
- **THEN** 初始化入口统一为 `mise run init`
- **THEN** 检查模式入口统一为 `mise run init-check`
- **THEN** 文档说明该方案在 Windows/Linux/macOS 上均可运行

## MODIFIED Requirements
### Requirement: 现有环境初始化流程
项目环境初始化从 `scripts/init.ps1`（PowerShell 平台锁定）迁移到 `tasks.py`（Python invoke 跨平台），保留全部行为语义：mise 检测、trust/install/sync/check-env 流程、检查模式、步骤状态输出和修复提示。

### Requirement: 初始化文档入口
所有文档中的初始化入口从 `pwsh -File scripts/init.ps1` / `pwsh -File scripts/init.ps1 -CheckOnly` 迁移到 `mise run init` / `mise run init-check`，并说明基于 Python invoke 的跨平台实现方案。

## REMOVED Requirements
### Requirement: PowerShell 专属初始化执行假设
**Reason**: PowerShell 脚本仅在 Windows 上原生可用，Linux/macOS 需要额外安装 pwsh，增加了不必要的平台依赖。
**Migration**: 迁移到 Python invoke 任务，利用项目已有的 Python + invoke 依赖实现零额外依赖的跨平台初始化。
