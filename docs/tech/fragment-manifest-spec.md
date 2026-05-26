# Fragment Manifest 规格

> **Draft v0.1** · 定义 Fragment `manifest.toml` 的完整格式规格

## 概述

Fragment 是 AgentForge 世界可移植性三层模型中的中间层——介于不可分割的 Kernel 与即插即用的 Capability 之间。每个 Fragment 代表一组**领域内聚**的规则、技能、脚本与文档的组合，可独立版本化、可选安装、可自由组合。

本文档定义 Fragment 自身的声明式描述文件 `manifest.toml` 的完整格式，使 Fragment 能够：

- 在不同世界之间**可移植、可复用**
- 声明对 Kernel 版本的**兼容性约束**
- 声明对其他 Fragment 的**依赖与冲突**
- 支持**生命周期钩子**与**扩展元数据**

(fragment-design-principles)=
## 设计原则

| 原则 | 含义 |
|------|------|
| **语言无关** | manifest.toml 使用 TOML 格式，任何语言/工具均可解析，不绑定特定运行时 |
| **声明式** | 只描述"是什么"，不规定"怎么做"；状态由消费者自行推导 |
| **可组合** | 多个 Fragment 可自由组合安装，通过 `dependencies` 和 `conflicts` 表达组合语义 |
| **极简必需** | 仅 `name`、`version`、`description` 为必填字段，其余均可选——遵循"少即是多" |

(fragment-fields)=
## manifest.toml 完整字段定义

Fragment 的 `manifest.toml` 放置于 Fragment 根目录，包含以下 section：

```{mermaid}
flowchart TD
    A["manifest.toml"] --> B["[fragment]"]
    A --> C["[fragment.kernel-compat]"]
    A --> D["[fragment.dependencies]"]
    A --> E["[fragment.conflicts]"]
    A --> F["[fragment.contents]"]
    A --> G["[fragment.hooks]"]
    A --> H["[fragment.metadata]"]
```

### `[fragment]` — 基础元数据

| 字段 | 类型 | 必填 | 默认值 | 语义 |
|------|------|------|--------|------|
| `name` | string | **是** | — | Fragment 标识符，使用 kebab-case（如 `python-engineering`），全局唯一 |
| `version` | string | **是** | — | 语义化版本号，遵循 [SemVer 2.0](https://semver.org/) |
| `description` | string | **是** | — | 一句话功能描述，面向人类阅读 |
| `authors` | string[] | 否 | `[]` | 作者列表，建议格式 `"Name <email>"` 或 `"@handle"` |
| `license` | string | 否 | `"MIT"` | SPDX 许可证标识符 |
| `keywords` | string[] | 否 | `[]` | 分类标签，用于搜索与过滤 |
| `repository` | string | 否 | — | Fragment 源码仓库 URL |

### `[fragment.kernel-compat]` — Kernel 版本兼容性

声明本 Fragment 对世界 Kernel 最低版本的要求，以及已知不兼容的最高版本。

| 字段 | 类型 | 必填 | 默认值 | 语义 |
|------|------|------|--------|------|
| `min-version` | string | 否 | `"0.1.0"` | Kernel 最低兼容版本（含） |
| `max-version` | string | 否 | — | Kernel 不兼容版本（**排他**，即 `< max-version`） |

:::{note}
`max-version` 遵循 SemVer 排他语义：`max-version = "4.0.0"` 表示兼容 `< 4.0.0` 的所有 Kernel 版本。这与 Cargo 的 `semver` 约定一致。
:::

### `[fragment.dependencies]` — Fragment 间依赖

声明本 Fragment 对其他 Fragment 的版本约束。Key 为 Fragment `name`，Value 为版本约束字符串。

| 字段 | 类型 | 必填 | 默认值 | 语义 |
|------|------|------|--------|------|
| `{name}` | string | 否 | — | 依赖的 Fragment 名称 → 版本约束字符串 |

版本约束语法详见 [](#version-constraints)。

示例：

```toml
[fragment.dependencies]
"docs-governance-tools" = ">=2.0"
"citations" = "^1.0"
```

### `[fragment.conflicts]` — 不兼容声明

声明与哪些 Fragment 不兼容。Key 为冲突 Fragment 的 `name`，Value 为冲突原因说明。

| 字段 | 类型 | 必填 | 默认值 | 语义 |
|------|------|------|--------|------|
| `{name}` | string | 否 | — | 冲突 Fragment 名称 → 冲突原因描述 |

示例：

```toml
[fragment.conflicts]
"legacy-python-lint" = "与本 Fragment 的 ruff 配置冲突"
```

### `[fragment.contents]` — 内容清单

声明 Fragment 包含的资源，按类型分组。所有路径均为相对于 Fragment 根目录的相对路径。

| 字段 | 类型 | 必填 | 默认值 | 语义 |
|------|------|------|--------|------|
| `rules` | string[] | 否 | `[]` | 规则文件列表 |
| `skills` | string[] | 否 | `[]` | 技能目录/文件列表 |
| `scripts` | string[] | 否 | `[]` | 脚本文件列表 |
| `docs` | string[] | 否 | `[]` | 参考文档列表 |
| `templates` | string[] | 否 | `[]` | 模板文件列表 |

路径约定：

- 以 `/` 结尾的路径表示**目录**（包含其下所有文件）
- 不以 `/` 结尾的路径表示**具体文件**
- 路径不允许包含 `..`（禁止上溯到 Fragment 根之外）

### `[fragment.hooks]` — 生命周期钩子

声明 Fragment 安装/卸载/升级时需执行的操作。Value 为可执行命令字符串。

| 字段 | 类型 | 必填 | 默认值 | 语义 |
|------|------|------|--------|------|
| `post-install` | string | 否 | — | Fragment 安装完成后执行的命令 |
| `pre-remove` | string | 否 | — | Fragment 卸载前执行的命令 |
| `post-upgrade` | string | 否 | — | Fragment 升级完成后执行的命令 |

:::{warning}
钩子命令在世界的宿主环境中执行，应尽量保持简单与幂等。推荐仅用于校验或轻量初始化，避免破坏性操作。
:::

### `[fragment.metadata]` — 扩展元数据

自由格式的 key-value 对，用于存放项目特定的扩展信息，不影响 Fragment 的解析与校验。

| 字段 | 类型 | 必填 | 默认值 | 语义 |
|------|------|------|--------|------|
| *(任意)* | string / number / boolean | 否 | — | 自定义键值对，消费者按需读取 |

```toml
[fragment.metadata]
domain = "engineering"
maturity = "stable"
internal-id = "PE-001"
```

(version-constraints)=
## 版本约束语法

Fragment 的版本约束对齐 SemVer 2.0，采用 Cargo 风格的表达式：

| 语法 | 含义 | 示例 |
|------|------|------|
| `">=X.Y.Z"` | 大于等于指定版本 | `">=1.2.0"` — 1.2.0 及以上 |
| `"^X.Y"` / `"^X.Y.Z"` | 兼容范围：同 major 版本 | `"^1.2"` — `>=1.2.0, <2.0.0` |
| `"~X.Y"` / `"~X.Y.Z"` | 补丁范围：同 minor 版本 | `"~1.2"` — `>=1.2.0, <1.3.0` |
| `">=X, <Y"` | 区间组合 | `">=1.0, <3.0"` — 1.0（含）至 3.0（不含） |
| `"*"` | 任意版本 | `"*"` — 无版本约束 |
| `"=X.Y.Z"` | 精确版本 | `"=1.2.3"` — 仅匹配 1.2.3 |

### 约束解析规则

1. **`^` 插值规则**（Caret）：
   - `^1.2.3` → `>=1.2.3, <2.0.0`（major ≥ 1 时，锁定 major）
   - `^0.2.3` → `>=0.2.3, <0.3.0`（major = 0 时，锁定 minor）
   - `^0.0.3` → `>=0.0.3, <0.0.4`（major.minor = 0.0 时，锁定 patch）

2. **`~` 插值规则**（Tilde）：
   - `~1.2.3` → `>=1.2.3, <1.3.0`（锁定 major.minor）
   - `~1.2` → `>=1.2.0, <1.3.0`

3. **区间组合**：用逗号分隔多个约束，取交集；逗号两侧允许空格。

4. **缺省版本号**：`"1.2"` 等价于 `">=1.2.0, <2.0.0"`（即 `^1.2`）。

(fragment-example)=
## 完整示例

以 `python-engineering` Fragment 为例：

```toml
# manifest.toml — python-engineering Fragment
# 位于 .agents/kernel/python-engineering/manifest.toml

[fragment]
name = "python-engineering"
version = "1.2.0"
description = "Python 工程规范与兼容性检查"
authors = ["@agentforge-team"]
license = "MIT"
keywords = ["python", "engineering", "lint", "compatibility"]
repository = "https://github.com/example/agentforge"

[fragment.kernel-compat]
min-version = "3.0.0"
max-version = "4.0.0"  # 兼容 < 4.0.0

[fragment.dependencies]
"citations" = "^1.0"

[fragment.conflicts]
# 当前无冲突

[fragment.contents]
rules = ["rules/python.md"]
scripts = [
    "scripts/check_python_compat.py",
    "scripts/check_python_deprecations.py",
]
docs = ["docs/version-tracking.md"]

[fragment.hooks]
post-install = "python -c 'print(\"python-engineering fragment installed\")'"

[fragment.metadata]
domain = "engineering"
maturity = "stable"
```

(fragment-world-relationship)=
## 与 world.toml 的关系

Fragment 的 `manifest.toml` 是 Fragment **自身的完整规格**，而 `world.toml` 中的 `[fragments.*]` 是世界对已安装 Fragment 的**注册表摘要**。两者关系如下：

```{mermaid}
flowchart LR
    A["manifest.toml<br/>（Fragment 自身规格）"] -->|"安装时注册"| B["world.toml [fragments.*]<br/>（世界级注册表摘要）"]
    B -->|"卸载时移除"| C["删除对应 [fragments.*] 条目"]
```

### 映射规则

| manifest.toml 字段 | world.toml `[fragments.{name}]` 字段 | 映射说明 |
|---|---|---|
| `fragment.name` | section key（`[fragments.{name}]`） | name 成为 section key |
| `fragment.version` | `version` | 直接映射 |
| `fragment.description` | `description` | 直接映射 |
| `fragment.contents.*` | `includes` | 所有 contents 子字段合并为 `includes` 数组 |
| *(无对应字段)* | `optional` | Fragment 安装时由安装者指定，默认 `true` |

### 安装后的 world.toml 示例

安装 `python-engineering` Fragment 后，`world.toml` 中新增：

```toml
[fragments.python-engineering]
version = "1.2.0"
includes = [
    "rules/python.md",
    "scripts/check_python_compat.py",
    "scripts/check_python_deprecations.py",
    "docs/version-tracking.md",
]
optional = true
description = "Python 工程规范与兼容性检查"
```

### 一致性约束

1. **单一权威源**：`manifest.toml` 是 Fragment 元数据的权威源；`world.toml` 仅为注册摘要，不得脱离 manifest 独立修改版本号或描述。
2. **版本同步**：Fragment 升级后，必须同步更新 `world.toml` 中对应条目的 `version` 和 `includes`。
3. **卸载清理**：Fragment 卸载时，`world.toml` 中对应 `[fragments.*]` 条目必须一并移除。

(fragment-validation)=
## 校验规则

`manifest.toml` 的合法性校验清单如下：

### 必填字段校验

- [ ] `[fragment]` section 存在
- [ ] `fragment.name` 非空且符合 kebab-case（`^[a-z][a-z0-9-]*[a-z0-9]$`）
- [ ] `fragment.version` 非空且符合 SemVer 格式（`^(\d+)\.(\d+)\.(\d+)(-[a-zA-Z0-9.]+)?$`）
- [ ] `fragment.description` 非空

### 版本约束校验

- [ ] `kernel-compat.min-version` 若存在，符合 SemVer 格式
- [ ] `kernel-compat.max-version` 若存在，符合 SemVer 格式
- [ ] `kernel-compat.min-version` < `kernel-compat.max-version`（当两者均存在时）
- [ ] `dependencies` 中所有版本约束字符串可被解析
- [ ] `conflicts` 中的 Fragment name 不出现在 `dependencies` 中（自相矛盾）

### 内容路径校验

- [ ] `contents` 中所有路径以 `rules/`、`skills/`、`scripts/`、`docs/`、`templates/` 之一为前缀
- [ ] 无路径包含 `..`（禁止上溯）
- [ ] 以 `/` 结尾的路径表示目录，不以 `/` 结尾的表示文件
- [ ] 所声明的文件/目录在 Fragment 包内实际存在

### 语义校验

- [ ] `fragment.name` 不与 Kernel 或其他已安装 Fragment 重名
- [ ] `dependencies` 中引用的 Fragment 在当前世界或 Fragment 仓库中存在
- [ ] `hooks` 中的命令为合法可执行字符串（非空、无 shell 注入风险）
- [ ] `metadata` 的 key 不与任何已定义 section 字段重名

### 格式校验

- [ ] 文件为合法 TOML 格式
- [ ] 无重复 key
- [ ] 字符串值无前后空白（除非有意为之）
