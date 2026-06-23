# 7. 验证记录

## 7.1 Ruff lint 验证

关键文件验证：

```powershell
uv run --no-sync ruff check src/taolib/flowkit/podman_win.py
```

结果：

```text
All checks passed!
```

## 7.2 Ruff format 验证

```powershell
uv run --no-sync ruff format --check src/taolib/flowkit/podman_win.py
```

结果：

```text
1 file already formatted
```

## 7.3 单元测试验证

```powershell
uv run --no-sync pytest tests/flowkit/test_flowkit.py
```

结果：

```text
20 passed in 0.84s
```

## 7.4 全局 future import 搜索验证

搜索目标：

```regex
^from __future__ import annotations$
```

范围：

```text
d:\spaces\AgentForge\apps\chaos/**/*.py
```

结果：

```text
No matches found
```
