# Task 1: 修复环境校验脚本基础可运行性

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
