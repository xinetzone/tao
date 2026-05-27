# Tasks
- [x] Task 1: 创建项目根 `tasks.py`，使用 Python invoke 定义初始化任务。
  - [x] SubTask 1.1: 分析现有 `scripts/init.ps1` 全部行为语义，确认与 invoke 任务的映射关系。
  - [x] SubTask 1.2: 创建 `tasks.py`，定义 `init`（完整初始化）和 `init_check`（仅检查）两个 invoke 任务。
  - [x] SubTask 1.3: 实现统一的 `_run_step` 辅助函数，封装 subprocess.run + 步骤状态输出 + 修复提示。

- [x] Task 2: 在 `mise.toml` 中新增 `tasks.init` 和 `tasks.init-check` 入口。
  - [x] SubTask 2.1: 定义 `tasks.init`，调用 `uv run invoke init`。
  - [x] SubTask 2.2: 定义 `tasks.init-check`，调用 `uv run invoke init-check`。

- [x] Task 3: 更新所有文档中的初始化入口。
  - [x] SubTask 3.1: README.md 中 `pwsh -File scripts/init.ps1` → `mise run init`
  - [x] SubTask 3.2: docs/quickstart.md、docs/build-conventions.md、docs/contributing.md、docs/deploy.md 同步更新
  - [x] SubTask 3.3: 排障条目中的 `-CheckOnly` 引用 → `mise run init-check`

- [x] Task 4: 补充 Python 级别的 invoke 任务测试。
  - [x] SubTask 4.1: 为 `_run_step` 和 `_check_mise` 辅助函数编写 pytest 测试。
  - [x] SubTask 4.2: 覆盖成功执行、命令缺失、非零退出码场景。
  - [x] SubTask 4.3: 确保测试可在任意平台上运行，不依赖特定环境。

- [x] Task 5: 执行验证并回填 checklist。
  - [x] SubTask 5.1: 在当前环境运行 mise run init-check 验证检查模式。
  - [x] SubTask 5.2: 运行 pytest 确认测试通过（9/9 passed）。
  - [x] SubTask 5.3: 回填 checklist.md 验收结果。

# Task Dependencies
- [Task 2] depends on [Task 1]
- [Task 3] depends on [Task 1]
- [Task 4] depends on [Task 1]
- [Task 5] depends on [Task 2, Task 3, Task 4]
