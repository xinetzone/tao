# 10. 改进建议与后续行动

## 10.1 已完成 P0：记录项目标准验证命令

已在 `apps/chaos/.agents/rules/python.md` 中补充标准验证命令：

```powershell
uv run --no-sync ruff check .
uv run --no-sync ruff format --check .
uv run --no-sync pytest tests/flowkit/test_flowkit.py
```

落地价值：减少后续任务中反复探索验证命令的成本，并统一 Python 相关修改后的验证入口。

## 10.2 已完成 P1：统一处理历史格式问题

已单独执行"格式化基线清理"，只格式化以下历史格式漂移文件，未混入功能修复：

- `.agents/scripts/check_env.py`
- `.agents/scripts/check_py_syntax.py`
- `.agents/scripts/validate_roles.py`
- `tests/test_validate_roles.py`

执行命令：

```powershell
uv run --no-sync ruff format .agents/scripts/check_env.py .agents/scripts/check_py_syntax.py .agents/scripts/validate_roles.py tests/test_validate_roles.py
```

验证命令与结果：

```powershell
uv run --no-sync ruff format --check .agents/scripts/check_env.py .agents/scripts/check_py_syntax.py .agents/scripts/validate_roles.py tests/test_validate_roles.py
uv run --no-sync ruff check .agents/scripts/check_env.py .agents/scripts/check_py_syntax.py .agents/scripts/validate_roles.py tests/test_validate_roles.py
```

```text
4 files already formatted
All checks passed!
```

## 10.3 已完成 P1：明确 Python 3.13+ 注解策略

已在 `apps/chaos/.agents/rules/python.md` 中补充 Python 3.13+ 注解策略：

- 项目代码不使用 `from __future__ import annotations`。
- 默认不使用字符串形式的类型注解；如 Ruff 可提供自动修复，应遵循 Ruff 的注解现代化建议。
- 类体内避免直接使用尚未完成定义的类名进行自引用注解。
- 返回当前实例类型时优先使用 `typing.Self`。
- 仅在类型无法稳定表达、外部库类型不可用，或为避免运行时前向引用求值问题时使用 `Any`；使用范围应尽量收敛到内部实现细节。

## 10.4 已完成 P2：增加 targeted check 分层指引

已在 `apps/chaos/.agents/rules/python.md` 中补充 targeted check 分层指引，区分以下验证粒度：

- 全量检查命令
- 单包 / 单目录检查命令
- 单文件检查命令
- 跳过同步 / 构建的快速测试命令

新增示例：

```powershell
# 全量检查
uv run --no-sync ruff check .
uv run --no-sync ruff format --check .

# 单包 / 单目录检查
uv run --no-sync ruff check src/taolib/flowkit tests/flowkit
uv run --no-sync ruff format --check src/taolib/flowkit tests/flowkit

# 单文件检查
uv run --no-sync ruff check src/taolib/flowkit/podman_win.py
uv run --no-sync ruff format --check src/taolib/flowkit/podman_win.py

# 跳过同步 / 构建的快速测试
uv run --no-sync pytest tests/flowkit/test_flowkit.py
```

执行原则：优先选择全量检查；当全量检查受本地文件锁、构建缓存或无关历史问题阻塞时，降级到单包、单目录或单文件检查，并在结果中明确说明降级原因。
