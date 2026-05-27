# Python Error Patterns

## Pattern 1: Optional Dependency Not Installed

- 现象：运行时出现 `ModuleNotFoundError` 或导入失败。
- 常见原因：可选依赖未安装、依赖组未同步、环境切换后锁文件未生效。
- 排查步骤：
  1. 检查 `pyproject.toml` 中对应依赖组。
  2. 检查 `uv.lock` 是否包含目标依赖。
  3. 使用 `uv run` 在项目环境内复现。
- 优先检查文件：`pyproject.toml`、`uv.lock`

## Pattern 2: Python Version Compatibility Regression

- 现象：升级 Python 版本后测试失败或 API 行为变化。
- 常见原因：标准库行为调整、第三方包兼容性不足、类型检查假设失效。
- 排查步骤：
  1. 阅读 `.agents/docs/version-tracking.md`
  2. 运行 `.agents/scripts/check_python_compat.py`
  3. 运行 `.agents/scripts/check_python_deprecations.py`
- 优先检查文件：`.agents/docs/version-tracking.md`、`.agents/scripts/`
