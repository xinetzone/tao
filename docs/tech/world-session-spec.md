# World Session 规约

> **Draft v0.1** · 多端协同的统一上下文容器协议
>
> **协议标识**：`world-session-v1`
>
> **状态**：草案（Exploratory）—— 等待 PoC 验证后晋升为 v1.0

## 概述

World Session 是 AgentForge **`World 容器`** 的运行时层，定义了一个**任务态**如何在多个端（CLI / Web / Skill / API）之间挂起、续作、归档。它是对 [`world.toml`](../../apps/chaos/.agents/world.toml) 静态定义的**正交补充**，不修改任何现有 kernel/fragments/capabilities/memory 字段。

**定位**：

- World 之于多端，正如内核之于多进程：**一个收敛点，N 个消费者**。
- Session 是任务的"挂起点"——任意端起手，任意端续作，任意端嵌入。
- 与 [World CLI 规格](./world-cli-spec.md) 互补：CLI 负责"世界进化"（evolve），Session 负责"任务流转"（flow）。

**核心断言**：

> **端是"用"，世界是"体"。** N 个端的 N×N 集成成本，通过引入一个统一的 World Session 层，坍缩为 N×1 的"端-世界"注册关系。

```{mermaid}
flowchart LR
    Surfaces["CLI / Web / Skill / API"] -->|读写| Session["World Session"]
    Session -->|落盘| WorldState["world.state/"]
    WorldState -->|归档| Retro["superpowers/retrospectives/"]
    WorldDef["world.toml<br/>（体）"] -.规约.-> Session
```

---

## 哲学锚点

| 道家原则 | 工程映射 |
|---|---|
| 反者道之动 | 端是"用"的发散，World 是"体"的归一 |
| 弱者道之用 | 不强求多端同步语义，靠**追加事件 + 投影上下文**弱耦合 |
| 多则惑，少则得 | 用一个 Session 容器收敛 N 个端的混乱 |
| 抱一为天下式 | events.toml 是单一真相源 |

详见 [`.agents/docs/references/dao-tech-foundation.md`](../../apps/chaos/.agents/docs/references/dao-tech-foundation.md)。

---

## 三层架构

```{mermaid}
flowchart TB
    subgraph L3["L3 产物层"]
        P1["artifacts/"]
        P2["归档至 retrospectives/"]
    end
    subgraph L2["L2 运行时层（本规约定义）"]
        S1["sessions/"]
        S2["events.toml"]
        S3["context.md"]
        S4["locks/"]
    end
    subgraph L1["L1 定义层（现状）"]
        D1["world.toml"]
        D2["kernel/fragments/capabilities/memory"]
    end
    L1 --> L2 --> L3
```

| 层级 | 由谁定义 | 是否可变 | 由谁产生 |
|---|---|---|---|
| L1 定义层 | [`world.toml`](../../apps/chaos/.agents/world.toml) | 由人显式编辑 | 设计者 |
| L2 运行时层 | 本规约 | 由各端读写 | Session 操作 |
| L3 产物层 | [`documentation.md`](../../apps/chaos/.agents/rules/documentation.md) | 归档后不可变 | Session 收尾时迁移 |

---

## 核心概念

### Session（会话）
一次有边界的任务态。具有：
- 全局唯一 `session_id`（`<topic-slug>-<timestamp-base36>`，例：`laozi-boshu-l9k2x`）
- 一个或多个端的活跃读写
- 一条不可变的 `events.toml`
- 一份可重建的 `context.md` 投影
- 可选的产物目录 `artifacts/`

### Event（事件）
对 Session 的不可变变更记录。所有端的所有写入**必须**追加到 `events.toml`（使用 TOML `[[event]]` Array of Tables 语法），禁止原地修改已有条目。

### Context（上下文）
`events.toml` 的人类可读投影，由当前持有锁的端在每次重要事件后重写。任何端都可以**从 events 完整重建** context，因此 context 是**派生数据**，非真相源。

### Lock（互斥）
任意时刻，至多一个端持有 Session 的写锁。读不占锁。锁是**租约式**的，过期自动释放。

### Surface（端）
读写 Session 的执行体。当前定义四种：`cli` / `web` / `ide-skill` / `api`。Skill 必须在其 frontmatter 中声明 `runtimes` 与 `context-protocol: world-session-v1` 才能合法读写 Session。

---

## 目录与文件结构

Session 的物理布局位于 [`.agents/world.state/`](../../apps/chaos/.agents/) 下（默认 `.gitignore`，可通过 `world session export` 显式分享）：

```text
.agents/
├── world.toml                         # 不变
└── world.state/                       # 🆕 运行时层根目录
    ├── index.toml                     # 全部 session 索引
    ├── sessions/
    │   └── laozi-boshu-l9k2x/
    │       ├── manifest.toml          # 会话元数据
    │       ├── context.md             # 当前上下文投影（人可读）
    │       ├── events.toml            # WAL 追加事件流（真相源）
    │       ├── artifacts/             # 中间产物
    │       │   ├── notes.md
    │       │   └── data.csv
    │       └── lock.toml              # 当前持有端的租约
    └── tasks/
        └── <task-id>.toml             # 跨 session 的长任务元数据（可选）
```

### `manifest.toml` 格式

```
[session]
id = "laozi-boshu-l9k2x"
title = "为帛书《老子》做注疏"
created_by = "cli"
created_at = "2026-05-27T14:32:11+08:00"
schema_version = "world-session-v1"

[session.task]                # 可选：跨 session 的长任务关联
task_id = "laozi-annotation"
parent_session = null

[session.allowed_runtimes]    # 哪些端被允许接入
runtimes = ["cli", "web", "ide-skill", "api"]

[session.fragments]           # 该 session 允许调用的 fragments
required = ["python-engineering", "docs-governance-tools"]

[session.status]
state = "active"              # active | suspended | archived
last_event_seq = 47
last_writer = "cli"
last_touched_at = "2026-05-27T15:08:42+08:00"
```

### `events.toml` 格式

使用 TOML **Array of Tables**（`[[event]]`）语法，每条事件追加到文件末尾，**已有条目不可修改**：

```toml
[[event]]
seq = 1
ts = "2026-05-27T14:32:11+08:00"
surface = "cli"
actor = "user"
type = "session.created"

[event.payload]
title = "为帛书《老子》做注疏"

[[event]]
seq = 2
ts = "2026-05-27T14:33:05+08:00"
surface = "cli"
actor = "agent"
type = "context.appended"

[event.payload]
text = "已确认源文件位于 .temp/laozi.pdf"

[[event]]
seq = 3
ts = "2026-05-27T14:35:22+08:00"
surface = "cli"
actor = "agent"
type = "artifact.added"

[event.payload]
path = "artifacts/notes.md"
sha256 = "abc..."

[[event]]
seq = 4
ts = "2026-05-27T15:01:00+08:00"
surface = "web"
actor = "user"
type = "session.resumed"

[event.payload]
from_seq = 3
```

### `lock.toml` 格式

```toml
[holder]
surface = "web"
instance_id = "browser-7f3a"
actor = "user@local"

[lease]
acquired_at = "2026-05-27T15:01:00+08:00"
lease_until = "2026-05-27T15:11:00+08:00"
renew_count = 0
```

---

## Session 生命周期与状态机

```{mermaid}
stateDiagram-v2
    [*] --> active: world session new
    active --> suspended: 主动 snapshot 或 lease 过期
    suspended --> active: world session resume
    active --> archived: world session archive
    suspended --> archived: world session archive
    archived --> [*]: 迁入 retrospectives/
```

| 状态 | 含义 | 可写 | 可读 |
|---|---|---|---|
| `active` | 有端持锁，正在写入 | ✅ 持锁端 | ✅ 全部端 |
| `suspended` | 无端持锁，但未归档 | ❌ 需 resume 拿锁 | ✅ 全部端 |
| `archived` | 已迁移到 `retrospectives/` | ❌ 不可变 | ✅ 全部端 |

---

## 事件类型枚举

事件类型分为五大类：`session.*` / `context.*` / `artifact.*` / `lock.*` / `runtime.*`。

| 类型 | 触发场景 | payload 关键字段 |
|---|---|---|
| `session.created` | 新建 session | `title`, `task_id?` |
| `session.resumed` | 端 resume 已存在 session | `from_seq` |
| `session.suspended` | 主动挂起或锁过期 | `reason` |
| `session.archived` | 归档至 retrospectives | `target_path` |
| `context.appended` | 写入新上下文片段 | `text`, `tags?` |
| `context.rewritten` | 整段重写 context.md | `prev_seq`, `summary` |
| `artifact.added` | 新增产物文件 | `path`, `sha256` |
| `artifact.updated` | 更新产物 | `path`, `sha256_old`, `sha256_new` |
| `artifact.removed` | 删除产物 | `path` |
| `lock.acquired` | 拿锁 | `holder`, `lease_until` |
| `lock.renewed` | 续约 | `lease_until` |
| `lock.released` | 主动释放或过期回收 | `reason` |
| `runtime.error` | 端执行报错（不影响 session 完整性） | `surface`, `message` |
| `runtime.skill_invoked` | Skill 被调用 | `skill_name`, `runtime` |
| `runtime.skill_completed` | Skill 完成 | `skill_name`, `result_path?` |

**约束**：

- 自定义类型必须以 `x.` 前缀（如 `x.user.checkpoint`），避免污染保留命名空间。
- `seq` 必须**单调递增**，由当前持锁端在追加时分配（基于 `manifest.toml` 的 `last_event_seq + 1`）。
- 时间戳使用 ISO 8601 with offset，**绝不**作为排序依据，仅供人类阅读。

---

## CLI 子命令规格

在现有 [`taolib world ...`](./world-cli-spec.md) 之上扩展 `session` 子命令族。

### 命令总览

| 子命令 | 简述 |
|---|---|
| `world session new <title>` | 新建 session 并取锁 |
| `world session list [--state <s>]` | 列出全部 session |
| `world session show <id>` | 查看 session 详情（manifest + 最近事件） |
| `world session resume <id>` | 拿锁并加载到当前端 |
| `world session snapshot` | 主动落盘 context.md（不释放锁） |
| `world session release` | 主动释放锁，进入 suspended |
| `world session archive <id>` | 归档至 `superpowers/retrospectives/` |
| `world session export <id> [--out <path>]` | 导出为可分享 zip |
| `world session import <path>` | 导入外部 session 包 |
| `world session log <id> [--tail N]` | 查看 events.toml |
| `world session prune [--older-than <duration>]` | 清理过期 suspended |

### 关键命令详解

#### `world session new`
```text
world session new <title>
                  [--task <task-id>]
                  [--allow <surfaces>]   # 默认 cli,web,ide-skill,api
                  [--lease <duration>]   # 默认 10m
```
- 生成 `session_id`
- 创建目录骨架（manifest.toml / context.md / events.toml / lock.toml / artifacts/）
- 写入 `session.created` 与 `lock.acquired` 两条事件
- 返回 `session_id` 至 stdout

#### `world session resume`
```text
world session resume <id>
                     [--steal]            # 强制夺锁（仅当锁已过期）
                     [--lease <duration>]
```
- 校验目标 session 存在且非 archived
- 检查 lock：若锁有效且非本端持有，拒绝（除非 `--steal` 且锁已过期）
- 写入 `lock.acquired` + `session.resumed`
- 加载 `manifest.toml` 与 `context.md` 到当前端工作上下文

#### `world session archive`
```text
world session archive <id> [--retro-template <name>]
```
- 必须先 `release` 锁
- 调用 task-execution-summary 风格模板生成归档 markdown
- 移动整个 session 目录至 `superpowers/retrospectives/<date>-<title>/`
- 写入 `session.archived` 后冻结 events.toml

---

## 多端协同协议（context-protocol: world-session-v1）

任何端要合法读写 Session，**必须**满足以下契约：

### A. 写入约束
1. 写前必须持有 `lock`，`lease_until` 大于当前时间。
2. 每次写入必须**先**追加 `events.toml`，**再**更新派生数据（`manifest.toml.last_event_seq`、`context.md`）。
3. 顺序违反 = 视为腐坏，需要从 events.toml 完全重建。

### B. 读取约束
1. 读取无需持锁，但必须以 `events.toml` 为唯一真相源。
2. 若 `context.md` 与 events 不一致（通过 `last_event_seq` 校验），应**忽略 context.md** 并提示用户调用 `world session repair <id>`。

### C. 锁的获取与释放
```{mermaid}
sequenceDiagram
    participant Client as 端
    participant FS as world.state/
    Client->>FS: 读 lock.toml
    alt 锁不存在 or 已过期
        Client->>FS: 原子写入新 lock.toml（O_CREAT|O_EXCL）
        FS-->>Client: 写入成功 → 拿锁
    else 锁有效且非本端
        FS-->>Client: 拒绝
    else 锁是本端
        Client->>FS: 续约 lease_until
    end
```
**实现要点**：
- Windows 下使用 `CreateFile` + `CREATE_NEW` 实现原子性。
- POSIX 下使用 `open(..., O_CREAT|O_EXCL)`。
- 禁止使用 `flock`/`fcntl`，因为 Session 可能跨设备同步（见后续 server 演进）。

### D. 多端冲突解决
- **首期策略**：悲观锁 + 租约。冲突时直接拒绝，由用户决定 `--steal` 或等待。
- **不引入** CRDT、OT 等复杂合并算法，符合"少则得"原则。

### E. 端能力降级
若 Skill 在 frontmatter 中声明 `runtimes` 但当前宿主不支持，则：
1. Skill 必须在 `runtime.skill_invoked` 事件中标注 `degraded: true`
2. 缺失能力（如本地文件读写）应在 `payload.unavailable_capabilities` 列出
3. 用户可通过 `world session log` 检视降级历史

---

## Skill 端集成约束

### Frontmatter 要求

Skill `SKILL.md` 必须新增字段：

```yaml
---
name: pdf-to-markdown
runtimes:
  - cli
  - web
  - ide-skill
context-protocol: world-session-v1
session-access:
  read: true
  write: true
  artifacts: ["*.md", "*.json"]   # 允许写入的产物 glob
---
```

### 调用约定

Skill 在 active session 中被触发时：

1. 必须读取 `WORLD_SESSION_ID` 环境变量（CLI 注入）或 `?session=<id>` query 参数（Web 注入）
2. 写入产物必须经由 `world session artifact add` 子命令或同等 API
3. 完成后追加 `runtime.skill_completed` 事件

未声明 `context-protocol: world-session-v1` 的 Skill **禁止**直接读写 `world.state/`，仅可通过显式 CLI 子命令操作。

---

## 安全与隐私

### Git 处理
- `world.state/` 默认进入 `.gitignore`
- `world session export <id>` 产出可分享 zip（自动剥离 lock 与本地路径）
- `world session import <path>` 导入时强制重新生成 `session_id`，避免 ID 撞车

### 敏感信息
- events.toml 不应记录 token、密码、私钥
- Skill 在 payload 中检测到敏感模式（默认正则集）时必须替换为 `<redacted>`
- 用户可通过 `world session redact <id> --pattern <regex>` 事后脱敏（追加 `context.rewritten` 事件，原 events 仍保留但人类不再呈现）

### 跨设备同步（v0.2 演进）
首期不提供。用户可：
1. 单纯使用 git 管理 `world.state/`（手动 commit）
2. 使用云盘同步整个目录（自行解决冲突）
3. 等待 v0.2 引入可选的 server 模式（详见演进路线）

---

## 与现有契约的兼容性

| 现有契约 | 影响 | 处理 |
|---|---|---|
| `kernel.immutable_rules` | session 必须遵守 | 在 `manifest.toml` 中冷静校验 |
| `kernel.boundary-policy = "kernel/"` | session 不属于 kernel | 物理隔离在 `world.state/` |
| `[fragments]` | session 仅可调用已声明的 fragments | `manifest.session.fragments.required` 校验 |
| `[capabilities].skills` | Skill 调用需符合本规约的端集成约束 | frontmatter 新增字段 |
| `[memory] portable=false` | session 归档后进入 memory 层 | 自动迁移到 `superpowers/retrospectives/` |

**不修改 [`world.toml`](../../apps/chaos/.agents/world.toml) 的任何字段**。如需声明项目对 world-session 协议的支持，可选地新增一个 fragment：

```toml
[fragments.world-session]
version = "0.1.0"
includes = [
    "docs/tech/world-session-spec.md",
]
optional = true
description = "World Session 多端协同协议（v0.1 草案）"
```

---

## 错误码

| 代码 | 名称 | 处置 |
|---|---|---|
| `WS001` | session 不存在 | 列出近邻 ID |
| `WS002` | session 已归档 | 提示只读访问 |
| `WS101` | 锁被他端持有 | 显示 holder 与剩余 lease |
| `WS102` | 锁已过期需 `--steal` | 提示 steal 命令 |
| `WS103` | 续约失败（写竞争） | 退避重试 |
| `WS201` | events.toml 损坏 | 引导 `world session repair` |
| `WS202` | context.md 与 events seq 不一致 | 自动从 events 重建并提醒 |
| `WS301` | Skill 未声明 context-protocol | 拒绝调用并打印修正示例 |
| `WS302` | 当前 session 不允许该 runtime | 列出 allowed_runtimes |
| `WS401` | 归档目标已存在 | 提示重命名或覆盖标志 |

---

## 落地路径

```{mermaid}
flowchart LR
    P1["P1: 协议定稿<br/>本文档"] --> P2["P2: CLI session 子命令"]
    P2 --> P3["P3: Skill 协议绑定"]
    P3 --> P4["P4: Web 端原型"]
    P4 --> V1["v1.0 stable"]
```

| 阶段 | 关键产出 | 验收 |
|---|---|---|
| **P1** | 本规约 v0.1 落库 | 文档进入 `docs/tech/index.md` |
| **P2** | `taolib world session *` 全部子命令 | 单元测试 + E2E：CLI 起手 → suspend → resume |
| **P3** | 改造 1 个 Skill（推荐 `pdf-to-markdown`） | 同一 session 跨命令复用产物 |
| **P4** | `apps/web/` 最小 session 续作器 | E2E：CLI 新建 → Web 浏览 events → Web 续作 |
| **v0.2** | 可选 server 同步、redact、repair | 跨设备无 git 协同 |
| **v1.0** | 接口冻结、全端覆盖 | 至少 3 个 Skill + 1 个 Web 端实测 |

---

## 演进区域（明确不冻结的部分）

以下设计标记为**可演进**，v0.1 不强约束实现：

1. **冲突合并策略**：当前悲观锁是首选，但 v0.x 可探索"读写分离 + 异步合并"。
2. **跨设备同步**：v0.2 可能引入 server 模式（参考 [`world-registry-protocol.md`](./world-registry-protocol.md) 的分发模式）。
3. **events.toml 压缩**：超过 N 条后是否引入 snapshot + delta，待 PoC 数据后定。
4. **context.md 投影策略**：摘要 vs 全量 vs LLM 总结，留给端实现自行选择。

---

## 关键设计决策记录（ADR 形式）

### ADR-001：使用 TOML 而非 JSONL / SQLite
**取舍**：SQLite 性能好但 git 不友好；JSONL 可流式但风格不统一；TOML 的 `[[event]]` 人类可读性最强且与项目既有格式（`world.toml`、`manifest.toml`）风格一致。
**结论**：选 TOML Array of Tables，符合"大道至简"与项目风格统一原则。追加写入时在文件末尾追加 `[[event]]` 块即可。

### ADR-002：悲观锁而非 CRDT
**取舍**：CRDT 支持离线并发但实现复杂；悲观锁简单但限制并行。
**结论**：v0.1 选悲观锁，复杂度收益比最高。

### ADR-003：`world.state/` 默认 ignore
**取舍**：入 git 利于追溯但泄漏隐私；ignore 干净但难分享。
**结论**：默认 ignore + `export` 显式分享，平衡两端。

### ADR-004：以 `seq` 而非时间戳排序
**取舍**：wall clock 跨设备不可靠；逻辑序号简单可靠。
**结论**：seq 单调递增，时间戳仅供人类阅读。

---

## 关联资料

- [`world.toml`](../../apps/chaos/.agents/world.toml) — World 静态定义
- [World CLI 规格](./world-cli-spec.md) — `evolve()` 原语实现
- [Fragment Manifest 规格](./fragment-manifest-spec.md) — Fragment 声明格式
- [World Registry 协议](./world-registry-protocol.md) — 分发协议
- [协作元模型](../../apps/chaos/.agents/docs/references/agent-collaboration-metamodel.md) — Team/Role/Agent 语义
- [道-技术映射基础](../../apps/chaos/.agents/docs/references/dao-tech-foundation.md) — 哲学锚点
- [本规约设计复盘](../../apps/chaos/.agents/docs/superpowers/retrospectives/task-summary-world-multi-surface-exploration-20260527.md) — 设计过程归档

---

*版本：Draft v0.1 · 2026-05-27 · 等待 PoC 验证后晋升 v1.0*
