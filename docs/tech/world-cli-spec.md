# World CLI 工具规格

> **Draft v0.1** · `evolve()` 原语的工程实现——Fragment 与 Capability 的安装、发布与生命周期管理

## 概述

World CLI（命令行接口）是 AgentForge 世界七大操作原语中 **`evolve()`** 的工程实现。它以命令行工具的形式将抽象的"世界进化"语义转化为可执行的技术操作，使世界能够动态获取新的规则、技能、脚本与文档组合（Fragment），以及独立的技能单元（Capability）。

**定位**：

- 面向**世界操作者**（world operator）提供统一的 Fragment / Capability 管理接口
- 将 [Fragment Manifest 规格](./fragment-manifest-spec.md) 与 [Registry 分发协议](./world-registry-protocol.md) 串联为可执行的用户界面
- 不管理 Kernel 层（Kernel 通过 GitHub Template fork 实现，无需 CLI 介入）

**范围**：

| 层级 | CLI 是否管理 | 说明 |
|------|------------|------|
| Kernel | **否** | GitHub Template fork 即创世，物理隔离 |
| Fragment | **是** | `world install` / `world publish` / `world upgrade` / `world remove` |
| Capability | **是** | 同 Fragment，通过相同命令体系管理 |

```{mermaid}
flowchart LR
    A["world.toml<br/>（依赖声明）"] --> B["World CLI"]
    C["registry.toml<br/>（Registry 源）"] --> B
    B --> D["兼容性校验引擎"]
    D --> E[".agents/<br/>（文件放置）"]
    B --> F["world.lock<br/>（锁定文件）"]
```

---

## 命令总览

| 子命令 | 简述 | 对应原语 |
|--------|------|---------|
| `world install <source> [options]` | 安装 Fragment 或 Capability | `evolve()` — 注入新能力 |
| `world publish <path> [options]` | 将本地组件发布到 Registry | `evolve()` — 对外共享 |
| `world resolve [options]` | 解析依赖图并生成/更新 `world.lock` | `evolve()` — 前置推导 |
| `world status` | 查看当前世界已安装组件状态 | `observe()` — 状态快照 |
| `world upgrade <name> [options]` | 升级已安装组件到最新或指定版本 | `evolve()` — 版本跃迁 |
| `world remove <name>` | 卸载组件并清理 world.toml 注册 | `evolve()` — 能力回收 |
| `world search <query>` | 在 Registry 中搜索可用组件 | `observe()` — 探索可选项 |

---

(world-install)=
## world install 详细规格

### 语法

```text
world install <source>
             [--registry <name>]
             [--version <constraint>]
             [--dry-run]
             [--force]
             [--no-hooks]
             [--optional]
             [--allow-yanked]
```

### 参数说明

| 参数 | 类型 | 说明 |
|------|------|------|
| `<source>` | 位置参数 | 组件来源（见 [source 解析规则](#source-解析规则)） |
| `--registry <name>` | string | 指定从哪个 registry 查询（默认按 `registry.toml` priority 顺序） |
| `--version <constraint>` | string | 版本约束字符串，覆盖 registry 中的 `latest.stable`（如 `^1.2.0`） |
| `--dry-run` | flag | 模拟执行，输出将发生的变更但不实际修改文件 |
| `--force` | flag | 跳过文件冲突检查（L4），强制覆盖已有文件 |
| `--no-hooks` | flag | 跳过安装后的生命周期钩子执行 |
| `--optional` | flag | 在 `world.toml` 中将该组件标记为 `optional = true`（默认） |
| `--allow-yanked` | flag | 允许安装已被 yank 的版本 |

(source-解析规则)=
### source 解析规则

CLI 按以下顺序尝试解析 `<source>` 参数：

```{mermaid}
flowchart TD
    A["<source> 输入"] --> B{"格式识别"}
    B -->|"含 @，无 //"| C["registry name@version<br/>如 python-engineering@1.2.0"]
    B -->|"http:// 或 https://"| D["Git URL<br/>如 https://github.com/org/repo"]
    B -->|"git@"| E["SSH Git URL<br/>如 git@github.com:org/repo"]
    B -->|"./ 或 ../"| F["本地路径<br/>如 ./fragments/my-fragment"]
    B -->|"仅名称"| G["Registry 默认查询<br/>如 python-engineering"]
```

**解析细则**：

| source 格式 | 示例 | 版本来源 |
|-------------|------|---------|
| `<name>` | `python-engineering` | Registry `latest.stable`（或 `--version` 覆盖） |
| `<name>@<version>` | `python-engineering@1.2.0` | 精确版本（不可与 `--version` 同时使用） |
| `<name>@<constraint>` | `python-engineering@^1.2` | 约束字符串 |
| `https://github.com/...` | `https://github.com/org/repo` | 默认分支 HEAD（`--version` 可指定 tag/branch） |
| `git@github.com:...` | `git@github.com:org/repo` | 同上 |
| `./path/to/fragment` | `./fragments/my-fragment` | 本地文件系统，版本取自 manifest |

(安装流程)=
### 安装流程

安装分五个串行步骤执行，任意步骤失败均阻断后续执行：

```{mermaid}
flowchart LR
    A["resolve<br/>依赖图解析"] --> B["validate<br/>兼容性校验"]
    B --> C["fetch<br/>内容获取"]
    C --> D["place<br/>文件放置"]
    D --> E["verify<br/>安装后校验"]
```

**Step 1 — resolve（依赖图解析）**

读取目标组件的 `manifest.toml`，递归收集 `[fragment.dependencies]` 中声明的所有传递依赖，构建完整依赖图。若存在依赖解析无解（SAT 不可满足），立即阻断并输出冲突报告。

**Step 2 — validate（兼容性校验）**

调用[兼容性校验引擎](#compat-engine)，依次执行 L1 ~ L4 层校验（L5 在 Step 4 后执行）。校验失败直接阻断，用户须根据错误信息修复后重试。

**Step 3 — fetch（内容获取）**

根据 source 类型选择获取策略：

| source 类型 | 获取方式 | 完整性校验 |
|------------|---------|-----------|
| registry (git) | `git archive --remote <url> <ref>` | 重算 sha256 与 index 中 `checksum` 比对 |
| registry (http) | HTTP GET + tarball 下载 | 同上 |
| Git URL | `git clone --depth 1 --branch <ref>` | 重算 sha256（无 registry checksum 时跳过） |
| 本地路径 | 直接读取文件系统 | 跳过 checksum 校验（本地开发场景） |

**Step 4 — place（文件放置）**

根据 `manifest.toml` 的 `[fragment.contents]` 将文件映射到 `.agents/` 对应目录：

| contents 字段 | 目标目录 |
|--------------|---------|
| `rules` | `.agents/rules/` |
| `skills` | `.agents/skills/` |
| `scripts` | `.agents/scripts/` |
| `docs` | `.agents/docs/fragments/<name>/` |
| `templates` | `.agents/templates/` |

放置完成后，向 `world.toml` 的 `[fragments.<name>]` 或 `[capabilities.*.<name>]` 写入注册摘要。

**Step 5 — verify（安装后校验）**

1. **完整性检查**：按 `manifest.toml` 中 `[fragment.contents]` 声明的所有路径，验证文件是否已实际写入 `.agents/`。
2. **hooks 执行**（除非 `--no-hooks`）：执行 `[fragment.hooks].post-install` 钩子命令。
3. **L5 语义冲突检测**：扫描 `.agents/rules/` 下的规则文件，检测覆盖问题并输出警告。

### 输出格式示例

**成功**：

```text
✓ Resolving  python-engineering@^1.2.0 → 1.2.0
✓ Resolving  citations@^1.0 → 1.0.3 (dependency)
✓ Validating L1 Kernel compatibility ... OK
✓ Validating L2 Fragment conflicts  ... OK
✓ Validating L3 Dependency graph    ... OK
✓ Validating L4 File conflicts      ... OK
↓ Fetching   python-engineering 1.2.0 [sha256:abc123]
↓ Fetching   citations 1.0.3         [sha256:def456]
📁 Placing   .agents/rules/python.md
📁 Placing   .agents/scripts/check_python_compat.py
📁 Placing   .agents/scripts/check_python_deprecations.py
📁 Placing   .agents/docs/fragments/python-engineering/version-tracking.md
✓ Verifying  integrity check ... OK
✓ Running    post-install hook ... OK
⚠ L5 Warning: rules/python.md overrides existing rules/python-legacy.md style
              (non-blocking; review `.agents/rules/` for conflicts)

Installed 2 components:
  python-engineering 1.2.0 (fragment)
  citations 1.0.3 (fragment, dependency)
```

**冲突（L2）**：

```text
✓ Resolving  legacy-python-lint@1.0.0 → 1.0.0
✗ Validating L2 Fragment conflicts:

  ERROR: Fragment 'legacy-python-lint' conflicts with installed 'python-engineering'
  Reason: 与本 Fragment 的 ruff 配置冲突

  Fix options:
    1. Remove python-engineering first:  world remove python-engineering
    2. Use --force to skip conflict check (not recommended)

Exit code: 2
```

**校验失败（L1）**：

```text
✗ Validating L1 Kernel compatibility:

  ERROR: Fragment 'advanced-ai-toolchain' requires Kernel >= 4.0.0
  Current world Kernel version: 3.1.0 (from world.toml [world].version)

  Fix options:
    1. Upgrade your world Kernel to >= 4.0.0
    2. Use an older version: world install advanced-ai-toolchain@<=2.x

Exit code: 2
```

### Fragment vs Capability 安装的行为差异

| 行为 | Fragment | Capability |
|------|---------|-----------|
| manifest 文件名 | `manifest.toml`（`[fragment]` section） | `SKILL.md` 或 `manifest.toml`（`[capability]` section） |
| 依赖解析 | 递归解析 `[fragment.dependencies]` | 一般无传递依赖（叶节点） |
| 文件放置目标 | `.agents/rules/`、`.agents/skills/` 等 | `.agents/skills/` 或 `.agents/scripts/` |
| world.toml 注册段 | `[fragments.<name>]` | `[capabilities.skills.<name>]` 或 `[capabilities.scripts.<name>]` |
| L5 语义冲突检测 | 检查 rules/ 覆盖 | 检查 skills/ 同名覆盖 |

---

(world-publish)=
## world publish 详细规格

### 语法

```text
world publish [<path>]
              [--registry <name>]
              [--tag <tag>]
              [--dry-run]
              [--access public|private]
              [--sign]
```

### 参数说明

| 参数 | 类型 | 说明 |
|------|------|------|
| `<path>` | 位置参数（可选） | 组件目录路径，默认为当前目录 `.` |
| `--registry <name>` | string | 发布目标 registry，默认使用 `registry.toml` 中 priority 最高的可写 registry |
| `--tag <tag>` | string | 指定 Git tag 名称，默认使用 `manifest.toml` 中的 `version` 生成（如 `v1.2.0`） |
| `--dry-run` | flag | 模拟发布流程，输出将执行的操作但不实际提交 |
| `--access` | `public\|private` | 发布可见性，默认 `public` |
| `--sign` | flag | 对打包内容进行 GPG/SSH 签名 |

### 发布前校验清单

发布流程启动前，CLI 自动执行以下校验。任意项失败均阻断发布：

- [ ] **manifest 完整性**：`manifest.toml` 存在，且满足 {ref}`Fragment 校验规则 <fragment-validation>` 中的所有必填字段与格式要求
- [ ] **版本递增**：新版本号必须严格大于 registry index 中该组件的所有已有版本（SemVer 排序）
- [ ] **contents 文件存在性**：`[fragment.contents]` 声明的所有路径在组件目录内实际存在
- [ ] **SKILL.md 合规**（仅 Capability）：若为 skill 类型，`SKILL.md` 必须包含 `## Usage` 与 `## Parameters` 章节
- [ ] **无 yanked 版本重复**：即使目标版本已被 yank，也不得重新发布相同版本号
- [ ] **git_ref 可达**：`--tag` 指定的 Git tag 在当前仓库中存在且已推送到远端

### 发布流程（五步）

```{mermaid}
flowchart LR
    A["validate<br/>发布前校验"] --> B["pack<br/>打包压缩"]
    B --> C["sign<br/>签名（可选）"]
    C --> D["push<br/>推送 Git tag"]
    D --> E["index<br/>更新 Registry 索引"]
```

**Step 1 — validate**：执行发布前校验清单（见上）。

**Step 2 — pack**：将组件目录（排除 `.git/`、`.temp/`、`*.pyc` 等）压缩为 tarball，计算 `sha256` 校验和。

**Step 3 — sign**（需 `--sign` flag）：使用本地 GPG/SSH key 对 tarball 签名，生成 `.sig` 文件。

**Step 4 — push**：在组件源码仓库创建并推送语义化 Git tag（如 `v1.2.0`），作为 `git_ref` 的物理锚点。

**Step 5 — index**：向目标 registry index 仓库提交更新：
- 在 `fragments/{category}/{name}.toml` 中追加新的 `[[versions]]` 条目
- 更新 `[latest].stable` 指向新版本（若新版本为 stable release）
- 若 registry 为 HTTP 类型，调用 `POST /v1/fragments`（见 [Registry 协议](./world-registry-protocol.md)）

### 输出格式示例

```text
✓ Validating manifest.toml ... OK
✓ Validating version increment: 1.1.0 → 1.2.0 ... OK
✓ Validating contents files exist ... OK (5 files)
📦 Packing   python-engineering-1.2.0.tar.gz
   sha256: abc123def456...
✓ Pushing   tag v1.2.0 to origin
✓ Indexing  fragments/py/python-engineering.toml
   Added [[versions]] entry for 1.2.0
   Updated [latest].stable → 1.2.0

Published: python-engineering 1.2.0
Registry:  agentforge-official (https://github.com/agentforge/registry-index)
```

---

(world-resolve)=
## world resolve 详细规格

### 语法

```text
world resolve
             [--update]
             [--locked]
             [--allow-yanked]
             [--allow-prerelease]
```

### 参数说明

| 参数 | 类型 | 说明 |
|------|------|------|
| `--update` | flag | 忽略现有 `world.lock`，重新解析所有依赖并生成新的锁定文件 |
| `--locked` | flag | 严格模式：要求 `world.lock` 已存在且与 `world.toml` 完全一致，不执行网络请求 |
| `--allow-yanked` | flag | 允许将 yanked 版本纳入解析候选集 |
| `--allow-prerelease` | flag | 允许将预发布版本（如 `1.0.0-beta.1`）纳入候选集 |

### 依赖图构建算法

```text
FUNCTION resolve_dependencies(world_toml, registry_sources):
    pending_queue  ← world.toml 中所有直接依赖
    resolved_set   ← {}
    conflict_set   ← {}

    WHILE pending_queue 非空:
        dep ← pending_queue.pop()

        IF dep.name 已在 resolved_set:
            existing ← resolved_set[dep.name]
            merged ← intersect_constraints(existing.constraint, dep.constraint)
            IF merged 为空集:
                conflict_set.add({dep.name, existing, dep})  // 不可满足
            ELSE:
                resolved_set[dep.name].constraint ← merged
            CONTINUE

        candidates ← query_registry(dep.name, dep.constraint, registry_sources)
        IF candidates 为空:
            RAISE UnresolvableError(dep.name, dep.constraint)

        selected ← select_version(candidates)  // 见版本选择算法
        resolved_set[dep.name] ← selected

        // 递归收集传递依赖
        transitive ← fetch_manifest(selected).dependencies
        pending_queue.extend(transitive)

    IF conflict_set 非空:
        RAISE ConflictError(conflict_set)

    RETURN resolved_set
```

### world.lock 文件格式定义

`world.lock` 文件位于世界根目录（与 `world.toml` 同级），格式为 TOML：

```toml
# world.lock — 自动生成，请勿手动修改
# 由 world resolve 生成，记录精确的依赖版本与来源

[lock]
generated = "2026-05-26T10:00:00Z"   # ISO 8601 生成时间
resolver-version = "1"                # 解析器算法版本
world-toml-hash = "sha256:..."        # 生成时 world.toml 的内容哈希

[[packages]]
name = "python-engineering"
version = "1.2.0"
type = "fragment"
source = "registry+default"           # 格式: registry+<registry_name> 或 git+<url> 或 local+<path>
git_url = "https://github.com/agentforge/fragment-python-engineering"
git_ref = "v1.2.0"
checksum = "sha256:abc123..."
dependencies = ["citations@>=1.0.0, <2.0.0"]

[[packages]]
name = "citations"
version = "1.0.3"
type = "fragment"
source = "registry+default"
git_url = "https://github.com/agentforge/fragment-citations"
git_ref = "v1.0.3"
checksum = "sha256:ghi789..."
dependencies = []
```

**字段说明**：

| 字段 | 说明 |
|------|------|
| `[lock].generated` | 锁定文件生成的 UTC 时间戳 |
| `[lock].resolver-version` | 解析算法版本（用于兼容性判断） |
| `[lock].world-toml-hash` | 生成时 `world.toml` 的内容哈希，用于检测配置漂移 |
| `packages[].source` | 来源标识：`registry+<name>`、`git+<url>`、`local+<path>` |
| `packages[].dependencies` | 传递依赖的精确版本约束（已从 manifest 解析） |

---

## 其他命令简要规格

### world status

列出当前世界所有已安装的组件及其状态。

```text
world status [--json] [--outdated]
```

| 参数 | 说明 |
|------|------|
| `--json` | 以 JSON 格式输出，适合脚本解析 |
| `--outdated` | 仅列出有可用更新版本的组件 |

**输出示例**：

```text
World: my-agentforge-world (Kernel 3.1.0)
Installed: 3 fragments, 1 capability

FRAGMENTS
  python-engineering   1.2.0    ✓ up-to-date   (registry+default)
  citations            1.0.3    ✓ up-to-date   (registry+default)
  docs-governance      2.1.0    ↑ 2.2.0 available

CAPABILITIES
  task-execution-summary  1.0.0  ✓ up-to-date   (registry+default)
```

---

### world upgrade

升级已安装的组件到最新版本或指定版本。

```text
world upgrade <name>
              [--version <constraint>]
              [--all]
              [--dry-run]
              [--no-hooks]
```

| 参数 | 说明 |
|------|------|
| `<name>` | 要升级的组件名（与 `--all` 互斥） |
| `--version <constraint>` | 指定目标版本约束，默认取 `latest.stable` |
| `--all` | 升级所有有可用更新的组件 |
| `--dry-run` | 模拟执行，输出将升级的版本但不实际操作 |
| `--no-hooks` | 跳过 `post-upgrade` 钩子执行 |

升级操作先执行完整的兼容性校验（L1 ~ L4），通过后再替换文件并更新 `world.toml` 中的版本记录。

---

### world remove

卸载已安装的组件，清理 `.agents/` 下对应文件并移除 `world.toml` 中的注册条目。

```text
world remove <name> [--force] [--keep-files]
```

| 参数 | 说明 |
|------|------|
| `<name>` | 要卸载的组件名 |
| `--force` | 跳过依赖者检查（若其他组件依赖此组件，默认阻断） |
| `--keep-files` | 仅移除 `world.toml` 注册，保留 `.agents/` 下的实际文件 |

**依赖者检查**：卸载前检查已安装的其他 Fragment 的 `[fragment.dependencies]` 中是否存在对 `<name>` 的引用。若存在，默认阻断并提示：

```text
✗ Cannot remove 'citations': required by installed fragments:
    python-engineering ^1.0

  Fix options:
    1. Remove dependents first: world remove python-engineering
    2. Force removal: world remove citations --force
```

---

### world search

在配置的 Registry 中搜索可用组件。

```text
world search <query>
             [--type fragment|skill|script|template]
             [--registry <name>]
             [--limit <n>]
             [--json]
```

| 参数 | 说明 |
|------|------|
| `<query>` | 搜索关键词（匹配 name / description / keywords） |
| `--type` | 过滤组件类型 |
| `--registry <name>` | 仅在指定 registry 中搜索 |
| `--limit <n>` | 返回结果上限，默认 20，最大 100 |
| `--json` | JSON 格式输出 |

**输出示例**：

```text
Search results for "python" (3 matches)

  python-engineering   fragment  1.2.0  Python 工程规范与兼容性检查
  python-type-hints    fragment  0.8.1  Python 类型注解规范与工具集成
  python-test-suite    fragment  1.0.0  Python 测试策略规范

  [registry: agentforge-official]
```

---

(compat-engine)=
## 兼容性校验引擎

兼容性校验引擎是 `world install` 与 `world upgrade` 的核心安全机制，确保组件在安装前后不破坏世界的一致性。引擎采用**五层渐进校验模型**，层次越低越优先执行，失败则立即阻断。

### 五层校验模型总览

| 层次 | 名称 | 校验内容 | 执行时机 | 失败行为 |
|------|------|---------|---------|---------|
| **L1** | Kernel 兼容性 | fragment `kernel-compat` vs `world.toml [world].version` | install/upgrade 前 | 阻断（exit 2） |
| **L2** | Fragment 互斥 | fragment `conflicts` vs 已安装 fragments | install/upgrade 前 | 阻断（exit 2） |
| **L3** | 依赖完整性 | 依赖图可满足性（SAT） | resolve 时 | 阻断（exit 10） |
| **L4** | 文件冲突 | `fragment.contents` 路径 vs 已有文件 | install 时（place 前） | 阻断（exit 2），`--force` 可跳过 |
| **L5** | 语义冲突 | `rules/` 下规则覆盖检测 | install 后（verify 时） | 警告（exit 0） |

---

### L1 — Kernel 兼容性校验

**输入数据来源**：
- 目标 Fragment 的 `manifest.toml` → `[fragment.kernel-compat]`（`min-version`、`max-version`）
- 当前世界的 `world.toml` → `[world].version`（世界 Kernel 版本）

**校验逻辑**：

```text
FUNCTION check_L1(fragment_manifest, world_toml):
    kernel_ver ← world_toml["world"]["version"]  // 当前 Kernel 版本
    compat     ← fragment_manifest["fragment"]["kernel-compat"]

    IF compat.min-version 存在:
        IF semver_compare(kernel_ver, compat.min-version) < 0:
            FAIL "Fragment requires Kernel >= {compat.min-version}, current: {kernel_ver}"

    IF compat.max-version 存在:
        IF semver_compare(kernel_ver, compat.max-version) >= 0:
            FAIL "Fragment incompatible with Kernel >= {compat.max-version}, current: {kernel_ver}"

    PASS
```

**错误信息格式**：

```text
ERROR [L1 Kernel Compatibility]:
  Fragment '{name}' requires Kernel version {constraint}
  Current world Kernel version: {actual_version} (from world.toml)

  To fix:
    - Upgrade your world Kernel, OR
    - Use a compatible fragment version: world install {name}@<older_constraint>
```

**修复动作**：升级世界 Kernel（fork 新版本 Template）；或降级 Fragment 版本约束。

---

### L2 — Fragment 互斥校验

**输入数据来源**：
- 目标 Fragment 的 `manifest.toml` → `[fragment.conflicts]`
- 当前世界的 `world.toml` → `[fragments.*]`（已安装 Fragment 名称列表）

**校验逻辑**：

```text
FUNCTION check_L2(fragment_manifest, world_toml):
    conflicts         ← fragment_manifest["fragment"]["conflicts"]  // {name: reason}
    installed_names   ← keys(world_toml["fragments"])

    FOR conflict_name, reason IN conflicts:
        IF conflict_name IN installed_names:
            FAIL "Conflict with installed '{conflict_name}': {reason}"

    // 反向检查：已安装的 Fragment 是否声明与目标冲突
    FOR installed_name IN installed_names:
        installed_manifest ← load_manifest(installed_name)
        IF fragment_manifest["fragment"]["name"] IN installed_manifest["fragment"]["conflicts"]:
            reverse_reason ← installed_manifest["fragment"]["conflicts"][target_name]
            FAIL "Installed '{installed_name}' conflicts with '{target_name}': {reverse_reason}"

    PASS
```

**错误信息格式**：

```text
ERROR [L2 Fragment Conflict]:
  Fragment '{target}' conflicts with installed fragment '{conflicting}'
  Conflict reason: {reason}

  To fix:
    - Remove the conflicting fragment: world remove {conflicting}
    - Choose a different fragment that doesn't conflict
```

**修复动作**：先卸载冲突的已安装 Fragment，然后重试安装。

---

### L3 — 依赖完整性校验（SAT）

**输入数据来源**：
- 目标 Fragment 及其所有传递依赖的 `manifest.toml` → `[fragment.dependencies]`
- Registry index 中各依赖组件的可用版本列表

**校验逻辑**（基于约束传播）：

```text
FUNCTION check_L3(dep_graph):
    // dep_graph: {name → [VersionConstraint]}（收集所有对同一组件的约束）

    FOR name, constraints IN dep_graph:
        candidates ← registry.get_versions(name)
        candidates ← filter(candidates, lambda v: NOT v.yanked)

        FOR constraint IN constraints:
            candidates ← filter(candidates, lambda v: satisfies(v, constraint))

        IF candidates 为空:
            FAIL "No satisfying version for '{name}' given constraints: {constraints}"

    // 检测循环依赖
    IF has_cycle(dep_graph):
        cycle_path ← find_cycle(dep_graph)
        FAIL "Circular dependency detected: {cycle_path}"

    PASS
```

**错误信息格式**：

```text
ERROR [L3 Dependency Resolution]:
  Cannot resolve dependency '{name}':
    Required by: {requirer_a} (>={ver_a}), {requirer_b} (^{ver_b})
    Available versions satisfying all constraints: none

  Dependency tree:
    python-engineering@1.2.0
      └── citations@^1.0        ← requires >=1.0.0, <2.0.0
      └── citations@>=1.5.0     ← from docs-governance-tools@2.0.0 (incompatible)

  To fix:
    - Check if a newer version of any dependent fragment relaxes its constraints
    - Use world search {name} to see available versions
```

**退出码**：依赖解析无解时返回 `10`（与一般校验失败的 `2` 区分）。

**修复动作**：调整 `world.toml` 中的版本约束；或使用 `world search` 查找兼容版本组合。

---

### L4 — 文件冲突校验

**输入数据来源**：
- 目标 Fragment 的 `manifest.toml` → `[fragment.contents]`（展开后的目标文件路径列表）
- 当前世界 `.agents/` 目录的实际文件系统状态
- `world.toml` → 已安装 Fragment 的 `includes` 字段

**校验逻辑**：

```text
FUNCTION check_L4(fragment_manifest, agents_dir, world_toml):
    target_files ← expand_contents(fragment_manifest["fragment"]["contents"])

    FOR target_path IN target_files:
        abs_path ← agents_dir / target_path

        IF file_exists(abs_path):
            owner ← find_owner(abs_path, world_toml)
            IF owner 不存在:
                // 文件存在但无 Fragment 记录（可能是手动创建的）
                WARN "File '{target_path}' exists but is not owned by any fragment"
                FAIL (unless --force)
            ELSE IF owner != fragment_manifest["fragment"]["name"]:
                FAIL "File '{target_path}' already owned by fragment '{owner}'"

    PASS
```

**错误信息格式**：

```text
ERROR [L4 File Conflict]:
  The following files already exist and would be overwritten:
    .agents/rules/python.md  (owned by: python-engineering-legacy 0.9.0)
    .agents/scripts/lint.sh  (unowned, manually created)

  To fix:
    - Remove conflicting fragment: world remove python-engineering-legacy
    - Use --force to overwrite (data loss risk!)
    - Rename conflicting files manually
```

**`--force` 行为**：跳过 L4 阻断，继续安装并覆盖文件。覆盖操作会在输出中以 `⚠ OVERWRITE` 明确标注每个被覆盖的文件。

**修复动作**：卸载占用文件的 Fragment；或手动备份冲突文件后使用 `--force`。

---

### L5 — 语义冲突检测（警告级）

**输入数据来源**：
- 安装完成后 `.agents/rules/` 下所有规则文件的内容
- `.agents/skills/` 下所有技能文件的名称

**校验逻辑**（启发式扫描）：

```text
FUNCTION check_L5(agents_dir):
    rule_files ← list_files(agents_dir / "rules/")
    warnings   ← []

    // 检测规则覆盖：同名规则文件来自不同 Fragment
    FOR each (file_a, file_b) IN pairs(rule_files):
        IF same_basename(file_a, file_b) AND different_owner(file_a, file_b):
            warnings.append("Rule '{basename}' defined by both '{owner_a}' and '{owner_b}'")

    // 检测技能同名冲突
    skill_names ← {skill.name: skill.owner for skill IN list_skills(agents_dir / "skills/")}
    duplicates  ← find_duplicates(skill_names)
    FOR dup IN duplicates:
        warnings.append("Skill '{dup.name}' provided by multiple fragments")

    RETURN warnings  // 仅警告，不阻断
```

**警告信息格式**：

```text
⚠ WARNING [L5 Semantic Conflict]:
  Rule file 'code-style.md' is provided by both:
    - python-engineering 1.2.0 (.agents/rules/python.md)
    - code-style-global 2.0.0 (.agents/rules/python.md)

  This may cause ambiguous behavior. Review and align the conflicting rules manually.
  (This is a warning only; installation completed successfully)
```

**修复动作**：人工审查冲突规则，决定保留哪个版本；或通过 `world remove` 移除冗余 Fragment。

---

## 版本选择算法

### 策略：最大兼容版本（Max Compatible）

World CLI 默认采用**最大兼容版本**策略（而非最小版本），即在满足所有约束的候选集中选择**版本号最大**的稳定版：

```text
FUNCTION select_version(candidates, constraints):
    filtered ← [v for v in candidates
                   if satisfies_all(v, constraints)
                   and NOT v.yanked]

    IF --allow-prerelease 未设置:
        filtered ← [v for v in filtered if NOT is_prerelease(v)]

    IF filtered 为空:
        RAISE UnresolvableError

    RETURN max(filtered, key=semver_key)  // 取最大 SemVer
```

**选择最大兼容版本的理由**：

- Fragment 通常包含规则与最佳实践，新版本通常更准确；
- 与 `^` 约束语义一致（用户表达"我希望用最新的兼容版本"）；
- 减少因"最小版本"导致长期停留在旧版的技术债。

### 冲突检测与报告

当同一组件被多个来源约束，且约束交集为空时，触发冲突报告：

```text
Dependency conflict for 'citations':
  python-engineering@1.2.0 requires: ^1.0   (>=1.0.0, <2.0.0)
  docs-governance@2.0.0  requires: >=2.0.0

  Intersection: empty — no version satisfies both constraints

  Resolution options:
    1. Upgrade python-engineering to a version compatible with citations >=2.0.0
    2. Downgrade docs-governance to a version requiring citations ^1.x
    3. Use world search to explore compatible version combinations
```

### 循环依赖处理

依赖图构建过程中使用**深度优先搜索**检测环路。发现循环时：

1. 输出完整的循环路径（如 `A → B → C → A`）
2. 阻断安装并以 exit code `10` 退出
3. 提示用户检查相关 Fragment 的 `manifest.toml` 并修正依赖声明

循环依赖被视为 Fragment 开发者的设计错误（而非安装者错误），通常需向上游 Fragment 维护者报告。

---

## 错误码与退出状态

| 退出码 | 符号常量 | 含义 | 触发场景 |
|--------|---------|------|---------|
| `0` | `EXIT_OK` | 成功 | 所有操作正常完成 |
| `1` | `EXIT_GENERAL_ERROR` | 一般错误 | 参数解析失败、文件读写错误、未预期异常 |
| `2` | `EXIT_VALIDATION_FAILED` | 校验失败（L1~L4） | Kernel 不兼容、Fragment 冲突、文件冲突 |
| `3` | `EXIT_NETWORK_ERROR` | 网络错误 | Registry 不可达、Git clone 超时、HTTP 4xx/5xx |
| `4` | `EXIT_AUTH_FAILED` | 认证失败 | Token 无效、SSH key 错误、Registry 权限不足 |
| `10` | `EXIT_UNRESOLVABLE` | 依赖解析无解（L3） | 约束交集为空、循环依赖 |

**退出码设计原则**：

- `0` 永远表示成功（包括 L5 警告出现时，因为 L5 非阻断）
- `2` vs `10`：将依赖解析失败单独编码，便于 CI 脚本区分"配置错误"与"解析算法失败"
- `3` 与 `4` 分离：网络错误可重试，认证失败需人工介入

---

## 配置与环境

### world.toml 中的 CLI 相关配置

在 `world.toml` 中可通过 `[cli]` section 定制 CLI 行为（可选）：

```toml
[cli]
default-registry = "private"     # 覆盖安装/发布时的默认 registry
cache-ttl = 3600                  # Registry index 缓存有效期（秒），默认 3600
hooks-timeout = 30                # 生命周期钩子执行超时（秒），默认 30
auto-lock = true                  # install/upgrade 后自动执行 world resolve，默认 true
```

### 环境变量

CLI 支持通过环境变量覆盖配置，优先级高于 `world.toml`：

| 环境变量 | 类型 | 说明 | 默认值 |
|---------|------|------|-------|
| `WORLD_REGISTRY` | string | 默认 registry 名称（覆盖 `[cli].default-registry`） | `"default"` |
| `WORLD_CACHE_DIR` | path | Registry index 本地缓存目录 | `~/.cache/agentforge/registry` |
| `WORLD_TOKEN` | string | 认证 Token，用于私有 registry 访问 | — |
| `WORLD_NO_HOOKS` | bool | 全局禁用生命周期钩子（`true`/`1`） | `false` |
| `WORLD_OFFLINE` | bool | 强制离线模式，禁止所有网络请求 | `false` |
| `WORLD_LOG_LEVEL` | string | 日志级别：`debug`/`info`/`warn`/`error` | `"info"` |

### 缓存策略

Registry index（Git 类型）在本地以 `git clone` 形式缓存于 `$WORLD_CACHE_DIR/<registry_name>/`：

| 操作 | 缓存行为 |
|------|---------|
| 首次查询 | `git clone --depth 1 <registry_url>` |
| 后续查询（缓存未过期） | 直接读取本地缓存，不执行网络请求 |
| 后续查询（缓存已过期，TTL 由 `cache-ttl` 控制） | `git fetch --depth 1` 增量更新 |
| `--update` 或 `world resolve --update` | 强制 `git fetch`，无论缓存是否过期 |
| `WORLD_OFFLINE=true` | 始终使用本地缓存，不执行任何网络请求 |

HTTP 类型 registry 的响应使用内存缓存（进程级别），不持久化到磁盘。

---

## 与现有文档的关系

本文档是 AgentForge 三层组件分发规格体系的第三篇，与前两篇规格文档形成完整闭环：

```{mermaid}
flowchart TD
    A["Fragment Manifest 规格<br/>fragment-manifest-spec.md<br/>（定义组件的自描述格式）"]
    B["World Registry Protocol<br/>world-registry-protocol.md<br/>（定义组件的分发与发现协议）"]
    C["World CLI 工具规格<br/>world-cli-spec.md（本文档）<br/>（将上述两者串联为可执行界面）"]

    A --> C
    B --> C
```

### 与 Fragment Manifest 规格的关系

[Fragment Manifest 规格](./fragment-manifest-spec.md) 定义了组件的自描述格式（`manifest.toml`）。本文档的 CLI 在以下环节直接消费该规格：

- **[发布前校验清单](#world-publish)**：依据 `manifest.toml` 完整性校验规则执行本地校验
- **[兼容性校验引擎 L1~L4](#compat-engine)**：读取 `[fragment.kernel-compat]`、`[fragment.conflicts]`、`[fragment.contents]` 进行各层校验
- **[文件放置（Step 4）](#安装流程)**：根据 `[fragment.contents]` 映射规则将文件写入 `.agents/`
- **生命周期钩子**：执行 `[fragment.hooks].post-install`、`post-upgrade`、`pre-remove`

### 与 World Registry Protocol 的关系

[World Registry Protocol](./world-registry-protocol.md) 定义了组件的发现与分发协议。本文档的 CLI 在以下环节直接消费该协议：

- **`world install` fetch 步骤**：依据 registry index 条目中的 `git_url`、`git_ref`、`checksum` 获取组件
- **`world publish` index 步骤**：向 registry index 追加新的 `[[versions]]` 条目（或调用 HTTP `POST /v1/fragments`）
- **`world resolve`**：调用 `POST /v1/resolve`（HTTP registry）或扫描本地 Git 缓存（Git registry）构建依赖图
- **`world search`**：调用 `GET /v1/search`（HTTP registry）或本地 index 全文扫描

### 与 world-operations.md（evolve() 原语）的关系

本文档实现了 `docs/general/philosophy/engineering/world-operations.md` 中定义的 **`evolve()` 原语**：

> `evolve()` — 进化：向世界注入新的 skills、workflows、rules 等能力单元，使世界能够承载更复杂的智能体任务。

具体映射关系：

| evolve() 语义 | CLI 命令 |
|--------------|---------|
| 注入新能力 | `world install` |
| 共享进化成果 | `world publish` |
| 推演进化路径 | `world resolve` |
| 能力版本跃迁 | `world upgrade` |
| 能力回收 | `world remove` |
