# 项目独立性规则

> **核心原则**：项目必须能够独立于开发者本地环境运行——在任何合规机器上执行 `git clone` 后即可完成构建、测试与部署，不依赖绝对路径、不绑定特定用户目录、不硬编码本机环境变量。

## 1. 路径引用原则

### 1.1 绝对路径禁令

以下场景中 **禁止** 使用绝对路径（含 `C:\Users\xxx\`、`/Users/xxx/`、`/home/xxx/` 等形式）：

| 禁止场景 | 说明 |
|---|---|
| **源代码中的文件读写** | `open()`、`Path()`、`importlib` 等操作不得使用绝对路径 |
| **配置文件中的路径值** | `world.toml`、`constraints.toml`、`pyproject.toml` 中所有路径字段必须可跨机移植 |
| **文档中的链接引用** | Markdown/RST 文档中引用项目内文件时禁止绝对路径 |
| **CI/CD workflow** | GitHub Actions yml 中 `working-directory`、`path` 等字段禁止包含用户目录 |
| **Shell 脚本/命令** | 终端命令、Mise tasks、Makefile 中禁止含个人用户路径 |
| **Python `sys.path` 操作** | 禁止通过 `sys.path.insert(0, '/absolute/path')` 注入绝对路径 |

### 1.2 相对路径优先

所有项目内引用遵循"从当前文件出发"的相对路径规则：

| 引用场景 | 路径基准 | 示例 |
|---|---|---|
| Python 包内导入 | 使用相对导入 (`. ` / `..`) | `from ..core import config` |
| 同目录文档链接 | 基于当前文件的相对路径 | `[规则](./rules/python.md)` |
| 跨目录文档链接 | 基于当前文件的相对路径，使用 `../` 上溯 | `[Spec](../specs/agentforge-spec-v0.2.md)` |
| 配置文件内部引用 | 基于配置文件所在目录 | `path = "./src/taolib"` |
| CI/CD 路径 | 基于 `$GITHUB_WORKSPACE` | `working-directory: ./apps/chaos` |

### 1.3 项目根变量约定

当相对路径不够直观（如跨越层级过深）时，统一使用以下语义变量 **仅作为文档描述**，实际代码中仍使用相对路径：

| 变量 | 含义 | 使用场景 |
|---|---|---|
| `<WORKSPACE_ROOT>` | 项目仓库根目录 (`AgentForge/`) | 文档中描述路径结构时使用 |
| `$PROJECT_ROOT` | 同 `<WORKSPACE_ROOT>`，用于 Shell/CI 上下文 | CI 脚本、Mise tasks 中引用 |

> **注意**：`<WORKSPACE_ROOT>` 和 `$PROJECT_ROOT` 仅是文档描述约定，**不得**直接出现在 Python 代码中作为路径字面量。代码中应通过 `pathlib.Path(__file__).parent` 等方式动态推导项目根。

## 2. 模块间引用规范

### 2.1 同子项目内部引用（apps/chaos/ 内）

```
apps/chaos/
├── src/taolib/          ← 核心库
├── tests/               ← 测试套件
├── specs/               ← 规范文档
└── .agents/             ← AI 配置资产
```

| 引用方向 | 规范 | 示例 |
|---|---|---|
| `tests/` → `src/taolib/` | 使用 `PYTHONPATH` 或 `uv run pytest`，不硬编码路径 | `uv run pytest tests/` |
| `specs/` → `src/taolib/` | 文档中引用代码时使用仓库根相对路径 | `` [`world.py`](apps/chaos/src/taolib/world.py) `` |
| `src/taolib/` 内部模块间 | Python 相对导入 | `from .core import World` |

### 2.2 跨子项目引用（chaos ↔ rebirth）

chaos 与 rebirth 是 **独立工作区**，跨区引用遵循以下边界：

| 引用方向 | 允许？ | 规范 |
|---|---|---|
| chaos 代码引用 rebirth 文件 | **禁止** | rebirth 是 git submodule，其内容可能随上游更新而变化 |
| chaos 文档引用 rebirth 文件 | **允许**（仅文档链接） | 使用仓库根相对路径，如 `[rebirth/README.md](rebirth/README.md)` |
| rebirth 引用 chaos 文件 | **禁止** | rebirth 应能独立存在（clone `worldsprout/worldsprout` 后自包含） |
| CI 脚本引用两区 | **允许** | 使用 `$GITHUB_WORKSPACE` 前缀的相对路径 |

### 2.3 Git 子模块引用（rebirth/ 下）

```
rebirth/
├── worldsprout/    ← git submodule (github.com/worldsprout/worldsprout)
├── spec/           ← git submodule (github.com/worldsprout/spec)
└── .github/        ← git submodule (github.com/worldsprout/.github)
```

| 规范 | 说明 |
|---|---|
| 子模块内部引用 | 使用子模块内部相对路径，不依赖父仓库路径 |
| 父仓库引用子模块 | 通过子模块路径引用（如 `rebirth/worldsprout/AGENTS.md`），不假设子模块的绝对路径 |
| 子模块更新 | 子模块内部文件变更通过 `git submodule update --remote` 拉取，不由父仓库直接编辑 |

### 2.4 配置文件间引用

| 配置场景 | 规范 | 正例 |
|---|---|---|
| `pyproject.toml` 中包路径 | 使用相对路径 | `packages = ["src/taolib"]` |
| `world.toml` 中 registry 路径 | 相对于 `world.toml` 所在目录 | `registry = "./registry.toml"` |
| CI yml 中 `working-directory` | 相对于 `$GITHUB_WORKSPACE` | `working-directory: ./apps/chaos` |
| Sphinx `conf.py` 中路径 | 相对于 `conf.py` 所在目录 | `html_static_path = ["_static"]` |

## 3. 正反例对照表

### 3.1 Python 代码路径

| 场景 | 正例 | 反例 |
|---|---|---|
| 读取同目录数据文件 | `Path(__file__).parent / "data.json"` | `Path("C:/Users/xinzo/data.json")` |
| 动态推导项目根 | `Path(__file__).resolve().parents[2]` | `PROJECT_ROOT = "/Users/xinzo/AgentForge"` |
| 包内模块导入 | `from ..core import World` | `from apps.chaos.src.taolib.core import World` |
| 测试中导入被测模块 | `uv run pytest tests/ -p no:cacheprovider` | `sys.path.insert(0, "C:/Users/xinzo/AgentForge/apps/chaos/src")` |
| 打开配置文件 | `open(Path(__file__).parent / "../config.toml")` | `open("/home/xinzo/.config/world.toml")` |

### 3.2 Markdown / 文档链接

| 场景 | 正例 | 反例 |
|---|---|---|
| 引用同目录文档 | `[规则](rules/python.md)` | `[规则](C:/Users/xinzo/.agents/rules/python.md)` |
| 引用上级目录 | `[Spec](../specs/agentforge-spec.md)` | `[Spec](/Users/xinzo/AgentForge/apps/chaos/specs/...)` |
| 引用仓库根文件 | `[README](../../README.md)` | `[README](file:///D:/spaces/AgentForge/README.md)` |
| 跨工作区引用 | `[脱胎规则](rebirth/README.md)`（从根 AGENTS.md） | `[脱胎规则](/d/spaces/AgentForge/rebirth/README.md)` |

### 3.3 TOML / YAML 配置文件

| 场景 | 正例 | 反例 |
|---|---|---|
| pyproject.toml 包路径 | `packages = ["src/taolib"]` | `packages = ["/Users/xinzo/chaos/src/taolib"]` |
| world.toml registry | `registry = "./registry.toml"` | `registry = "D:\\spaces\\AgentForge\\apps\\.agents\\registry.toml"` |
| CI yml working-directory | `working-directory: ./apps/chaos` | `working-directory: D:/spaces/AgentForge/apps/chaos` |
| Sphinx conf.py | `html_static_path = ["_static"]` | `html_static_path = ["/home/docs/_static"]` |

### 3.4 CI/CD workflow 路径

| 场景 | 正例 | 反例 |
|---|---|---|
| checkout 后进入目录 | `working-directory: ./apps/chaos` | `working-directory: /home/runner/work/AgentForge/AgentForge/apps/chaos` |
| 脚本文件引用 | `run: bash .github/scripts/check.sh` | `run: bash /home/xinzo/scripts/check.sh` |
| 产物路径 | `path: apps/chaos/dist/*.whl` | `path: /d/spaces/AgentForge/apps/chaos/dist/*.whl` |

### 3.5 Shell / 终端命令

| 场景 | 正例 | 反例 |
|---|---|---|
| uv 运行测试 | `uv run pytest tests/` | `uv run pytest /Users/xinzo/AgentForge/apps/chaos/tests/` |
| cd 进入目录 | `cd apps/chaos` | `cd D:/spaces/AgentForge/apps/chaos` |
| 执行脚本 | `python .agents/scripts/validate.py` | `python C:/Users/xinzo/.agents/scripts/validate.py` |
| 读取文件 | `cat pyproject.toml` | `cat /home/xinzo/AgentForge/pyproject.toml` |

## 4. 可执行性与验证

### 4.1 自动化扫描规则

以下模式应在 CI 和本地 pre-commit 中作为检查项执行：

| 检查项 | 正则/grep 模式 | 说明 |
|---|---|---|
| Unix 绝对路径 | `grep -rPn "(?<!/)/(home\|Users\|root)/[a-z]" --include="*.py" --include="*.md" --include="*.toml" --include="*.yml"` | 检测源代码/文档/配置中的绝对路径 |
| Windows 绝对路径 | `grep -rPn "[A-Z]:\\\\(Users\|Documents\|spaces)" --include="*.py" --include="*.md" --include="*.toml" --include="*.yml"` | 检测 Windows 盘符绝对路径 |
| `sys.path` 注入 | `grep -rPn "sys\.path\.(insert\|append).*[\"']/" --include="*.py"` | 检测运行时路径注入 |
| `file://` URL | `grep -rPn "file:///[A-Za-z]:" --include="*.md" --include="*.rst"` | 检测文档中的 file:// 绝对链接 |
| Python 绝对导入 | `grep -rPn "^from apps\.|^import apps\." --include="*.py" apps/chaos/src/` | 检测以项目根为起点的绝对导入 |

> **例外白名单**：以下路径允许包含绝对路径——(a) `.gitignore` 中的排除规则；(b) `.gitmodules` 中的子模块 URL；(c) Python `__pycache__/` 等自动生成的忽略文件。

### 4.2 人工审查清单

| 检查项 | 通过标准 |
|---|---|
| `git grep` 无绝对路径 | `git grep "/Users/\|/home/\|C:\\\\Users" -- "*.py" "*.md" "*.toml" "*.yml"` 无结果（排除白名单） |
| 配置文件路径相对化 | `world.toml`、`pyproject.toml`、CI yml 中所有路径字段均为相对路径 |
| 文档链接可解析 | 所有 `[text](path)` 中的 path 为相对路径且指向存在的文件 |
| 无 `sys.path` 硬编码 | Python 代码中无通过绝对路径操作 `sys.path` 的语句 |
| 新成员可克隆即运行 | `git clone && uv sync && uv run pytest` 在干净环境中通过 |

### 4.3 CI 集成建议

在 `.github/workflows/ci.yml` 中新增 `path-independence-check` job：

1. **绝对路径扫描**：执行上述 grep 模式，命中即失败。
2. **链接有效性检查**：使用 `markdown-link-check` 或等价工具检查所有 Markdown 内部链接指向的文件存在且路径为相对路径。
3. **克隆可运行性检查**：在独立 Docker 容器中执行 `git clone` → `uv sync` → `uv run pytest`，验证零依赖本地环境。

### 4.4 违规修复指引

| 违规类型 | 修复方式 |
|---|---|
| Python 文件绝对路径 | 改用 `pathlib.Path(__file__).parent / "..."` 或相对导入 |
| 文档绝对链接 | 改为相对路径链接 `[text](../path/to/file.md)` |
| 配置绝对路径 | 改为相对路径，以配置文件所在目录为基准 |
| CI 绝对路径 | 改用 `$GITHUB_WORKSPACE` 或 `working-directory` 相对路径 |
| Shell 命令绝对路径 | 改用 `cd` 到项目相对路径后再操作 |
