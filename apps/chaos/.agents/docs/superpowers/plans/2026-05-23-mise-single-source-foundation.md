# mise Single Source Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 加固 AgentForge 的 mise 战略底座，使 `mise.toml` 成为工具层版本单一事实来源，并确保 `mise run init` / `mise run init-check` / `mise run check-env` 作为当前唯一推荐入口稳定可用。

**Architecture:** 采用低侵入方式修改现有环境校验脚本，不重构开发环境体系。`.agents/scripts/check_env.py` 负责从 `mise.toml` 解析工具层期望版本，并继续校验 Python 依赖层工具与配置一致性；文档只做入口口径收口。

**Tech Stack:** Python 3.14、标准库 `tomllib`、`pathlib.Path`、`dataclasses`、`subprocess`、mise、uv、Invoke、Markdown。

---

## File Structure

- Modify: `.agents/scripts/check_env.py`
  - 责任：校验本地工具链可用性、版本基线、配置一致性；从 `mise.toml` 读取工具层版本。
- Modify: `README.md`
  - 责任：面向人类开发者说明当前推荐的环境初始化入口。
- Modify: `AGENTS.md`
  - 责任：面向 AI 助手说明当前唯一推荐的环境入口与禁止路径。
- Optional Modify: `docs/quickstart.md`
  - 责任：若发现仍存在历史入口描述，则统一为 `mise run init` / `mise run init-check`。
- No create: 本轮不新增代码模块，避免扩大范围。

---

## Task 1: 修复环境校验脚本基础可运行性

**Files:**
- Modify: `.agents/scripts/check_env.py:1-75`
- Verify: `.agents/scripts/check_env.py`

- [ ] **Step 1: 运行当前脚本，确认失败模式**

Run:

```bash
python .agents/scripts/check_env.py
```

Expected before fix: 如果当前代码未导入 `Path`，脚本在执行到 `Path(__file__)` 时失败，错误中包含 `NameError: name 'Path' is not defined`。如果本地工具版本不一致，也可能先输出工具表格后以非零码退出。

- [ ] **Step 2: 补充必要导入并修正历史入口提示**

Edit `.agents/scripts/check_env.py` imports and the `mise` tool fix string to match this content at the top of the file:

```python
from __future__ import annotations

import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
```

Update the `mise` `ToolSpec` block to:

```python
    ToolSpec(
        name="mise",
        command=["mise", "--version"],
        expected="已安装",
        fix="先安装 mise，再重新运行 mise run init",
        version_pattern=None,
        match_mode="available",
    ),
```

- [ ] **Step 3: 运行脚本验证基础可执行**

Run:

```bash
python .agents/scripts/check_env.py
```

Expected after fix: 脚本不再出现 `pathlib.Path` 相关未定义错误；输出标题 `AgentForge 环境校验` 和工具表格。若工具版本或依赖未安装，可返回非零码，但错误应是环境校验结果，而不是 Python 异常。

- [ ] **Step 4: 提交本任务变更**

Run:

```bash
git add .agents/scripts/check_env.py
git commit -m "fix: stabilize environment check entrypoint"
```

Expected: Git 创建一个包含 `.agents/scripts/check_env.py` 基础可运行性修复的提交。

---

## Task 2: 从 mise.toml 读取工具层期望版本

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

---

## Task 3: 收口当前推荐入口文档口径

**Files:**
- Modify: `README.md`
- Modify: `AGENTS.md`
- Optional Modify: `docs/quickstart.md`
- Verify: repository text search

- [ ] **Step 1: 搜索历史入口残留**

Run:

```bash
Select-String -Path README.md,AGENTS.md,docs\quickstart.md,.agents\scripts\check_env.py -Pattern "scripts/init.ps1|init.ps1|pipx|conda" -CaseSensitive
```

Expected: 当前态入口文档不应推荐 `scripts/init.ps1`、`pipx` 或 `conda` 作为项目依赖安装路径。若命中历史说明，需要判断是否属于禁止路径或历史记录。

- [ ] **Step 2: 更新 README 当前入口表达**

Ensure `README.md` environment section keeps this recommended path:

```markdown
如需一键完成信任、安装、依赖同步与首次环境校验，请直接运行：

```bash
mise run init
```
```

Ensure validation section includes:

```markdown
建议至少完成以下验证：

```bash
mise run check-env
mise run test
```
```

Do not add direct `pip install`、`conda install` or `pipx install` instructions.

- [ ] **Step 3: 更新 AGENTS 当前入口表达**

Ensure `AGENTS.md` contains an environment rule equivalent to:

```markdown
- **外部工具初始化**：运行 `mise run init` 安装项目所需的外部工具依赖。使用 `mise run init-check` 可仅检查依赖状态，使用 `mise run check-env` 可直接校验工具链版本。
```

Ensure it also retains the rule that Python dependencies are managed by `uv` and direct `pip` or `conda` installation is forbidden.

- [ ] **Step 4: 必要时更新 quickstart**

If `docs/quickstart.md` recommends a historical init path, replace it with:

```markdown
mise run init
```

If it only mentions `mise trust` / `mise install` / `mise run sync` as expanded manual steps, keep those steps.

- [ ] **Step 5: 再次搜索确认当前态口径一致**

Run:

```bash
Select-String -Path README.md,AGENTS.md,docs\quickstart.md,.agents\scripts\check_env.py -Pattern "scripts/init.ps1|init.ps1|pipx|conda" -CaseSensitive
```

Expected: No matches in current recommended-path sections. If matches remain only in explicit historical context, document that in the implementation summary before continuing.

- [ ] **Step 6: 提交文档口径收口**

Run:

```bash
git add README.md AGENTS.md docs/quickstart.md .agents/scripts/check_env.py
git commit -m "docs: align mise environment entrypoints"
```

Expected: Git 创建一个文档口径收口提交；若 `docs/quickstart.md` 未变更，Git 只提交实际变更文件。

---

## Task 4: 端到端验证与收尾

**Files:**
- Verify: `.agents/scripts/check_env.py`
- Verify: `mise.toml`
- Verify: `README.md`
- Verify: `AGENTS.md`

- [ ] **Step 1: 运行环境校验入口**

Run:

```bash
mise run check-env
```

Expected: 输出 `AgentForge 环境校验`，并展示工具表格。若某些工具未安装或版本不一致，应显示修复命令；脚本不应出现 Python 异常。

- [ ] **Step 2: 运行只检查初始化入口**

Run:

```bash
mise run init-check
```

Expected: 执行 `mise trust` 与 `mise run check-env`；若环境满足基线，应以 `[OK] 环境检查完成` 结束。

- [ ] **Step 3: 运行 lint**

Run:

```bash
mise run lint
```

Expected: pre-commit 全量检查通过。若由于环境缺失失败，先按 `check-env` 修复建议处理；若仍无法运行，记录具体失败原因。

- [ ] **Step 4: 运行 Python 语法检查兜底**

Run:

```bash
python -m py_compile .agents/scripts/check_env.py tasks.py
```

Expected: 命令无输出且退出码为 0。

- [ ] **Step 5: 检查未完成标记和旧入口残留**

Run:

```bash
Select-String -Path .agents\scripts\check_env.py,README.md,AGENTS.md,docs\quickstart.md -Pattern "[T]BD|[T]ODO|[待]补|[占]位|[未]定|scripts/init.ps1|init.ps1" -CaseSensitive
```

Expected: No matches. If historical context intentionally保留旧入口，应在最终总结中说明具体位置和原因。

- [ ] **Step 6: 提交验证收尾变更**

If Task 4 required file changes, run:

```bash
git add .agents/scripts/check_env.py README.md AGENTS.md docs/quickstart.md
git commit -m "chore: verify mise foundation hardening"
```

Expected: 如有变更则创建收尾提交；如无变更则跳过提交，并在最终总结中说明验证结果。

---

## Self-Review

- Spec coverage: 覆盖了 `mise run check-env` / `mise run init-check` 可运行性、历史入口收口、`mise.toml` 工具层单一事实来源、文档口径统一、验证命令。
- Placeholder scan: 本计划不包含未完成标记、延后实现描述或未定章节。
- Scope check: 本计划未扩展到完整 CI/CD 治理，符合 Spec 非目标。
- Type consistency: `ToolSpec`、`ToolResult`、`load_mise_tool_versions`、`build_tool_specs`、`check_config_consistency` 命名在各任务中保持一致。
