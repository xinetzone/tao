# Task 2: 从 mise.toml 读取工具层期望版本

**Files:**
- Modify: `.agents/scripts/check_env.py:1-260`
- Verify: `mise.toml`

- [ ] **Step 1: 添加 TOML 读取能力**

Edit `.agents/scripts/check_env.py` imports to include `tomllib`:

```python
from __future__ import annotations

import re
import subprocess
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path
```

- [ ] **Step 2: 将固定 `TOOLS` 元组替换为工厂函数**

Replace the current global `TOOLS: tuple[ToolSpec, ...] = (...)` block with the following functions:

```python
def _tool_version(value: object) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict) and isinstance(value.get("version"), str):
        return value["version"]
    return "未声明"


def load_mise_tool_versions(project_root: Path) -> dict[str, str]:
    mise_path = project_root / "mise.toml"
    with mise_path.open("rb") as file:
        data = tomllib.load(file)

    tools = data.get("tools", {})
    if not isinstance(tools, dict):
        return {}

    return {
        "python": _tool_version(tools.get("python")),
        "uv": _tool_version(tools.get("uv")),
        "node": _tool_version(tools.get("node")),
        "defuddle": _tool_version(tools.get("npm:defuddle")),
    }


def build_tool_specs(project_root: Path) -> tuple[ToolSpec, ...]:
    versions = load_mise_tool_versions(project_root)
    python_version = versions.get("python", "未声明")
    uv_version = versions.get("uv", "未声明")
    node_version = versions.get("node", "未声明")
    defuddle_version = versions.get("defuddle", "未声明")

    return (
        ToolSpec(
            name="mise",
            command=["mise", "--version"],
            expected="已安装",
            fix="先安装 mise，再重新运行 mise run init",
            version_pattern=None,
            match_mode="available",
        ),
        ToolSpec(
            name="python",
            command=["python", "--version"],
            expected=python_version,
            fix=f"mise install python@{python_version}",
        ),
        ToolSpec(
            name="uv",
            command=["uv", "--version"],
            expected=uv_version,
            fix=f"mise install uv@{uv_version}",
        ),
        ToolSpec(
            name="node",
            command=["node", "--version"],
            expected=node_version,
            fix=f"mise install node@{node_version}",
            version_pattern=r"v?(\d+(?:\.\d+)+)",
        ),
        ToolSpec(
            name="ruff",
            command=["uv", "run", "ruff", "--version"],
            expected="0.15.14",
            fix="mise run sync",
        ),
        ToolSpec(
            name="pre-commit",
            command=["uv", "run", "pre-commit", "--version"],
            expected="4.6.0",
            fix="mise run sync",
        ),
        ToolSpec(
            name="defuddle",
            command=["mise", "x", "npm:defuddle", "--", "defuddle", "--version"],
            expected=defuddle_version,
            fix=f'mise install "npm:defuddle@{defuddle_version}"',
        ),
    )
```

- [ ] **Step 3: 更新 main 使用动态工具规格**

Replace the first line inside `main()`:

```python
    results = [check_tool(spec) for spec in TOOLS]
```

with:

```python
    project_root = Path(__file__).resolve().parents[2]
    results = [check_tool(spec) for spec in build_tool_specs(project_root)]
```

Then remove the later duplicate line:

```python
    project_root = Path(__file__).resolve().parents[2]
```

The beginning of `main()` should be:

```python
def main() -> int:
    project_root = Path(__file__).resolve().parents[2]
    results = [check_tool(spec) for spec in build_tool_specs(project_root)]
    print("AgentForge 环境校验")
    print_table(results)

    consistency_issues = check_config_consistency(project_root)
```

- [ ] **Step 4: 保持配置一致性检查使用 mise.toml**

Do not remove `check_config_consistency`. It should continue comparing `mise.toml` Python version with `pyproject.toml` `target-version` and `requires-python`.

- [ ] **Step 5: 运行脚本，确认版本期望来自 mise.toml**

Run:

```bash
python .agents/scripts/check_env.py
```

Expected: 工具表格中 Python、uv、Node、defuddle 的期望值与 `mise.toml` 中 `[tools]` 一致：`3.14.5`、`0.11.16`、`22.22.3`、`0.18.1`。

- [ ] **Step 6: 提交本任务变更**

Run:

```bash
git add .agents/scripts/check_env.py
git commit -m "refactor: derive tool baselines from mise config"
```

Expected: Git 创建一个提交，说明工具层版本基线已从 `mise.toml` 读取。
