# 🌍 World Registry Protocol (Draft v0.1)

本文档定义 AgentForge 世界的 **Registry 分发协议**——一套基于 Git 的去中心化世界组件（Fragment 与 Capability）发现、解析与分发规范。

AgentForge 采用分层混合分发策略：

| 层级 | 实体类型 | 分发方式 |
|------|----------|----------|
| Kernel | 世界内核 | GitHub Template（fork 即创世，禁止远程自动更新） |
| Fragment | 规则/技能/脚本组合 | Registry 协议驱动（本文档定义） |
| Capability | 独立技能与脚本 | Registry 协议驱动（本文档定义） |

本协议不解决 Kernel 层分发（Kernel 通过模板 fork 实现物理隔离），专注解决 Fragment 与 Capability 的可组合、可升级、可信赖分发问题。

## 设计原则

### 去中心化优先 (Decentralized-first)

Registry 的权威状态存储在 Git 仓库中，不依赖中心化的 package server。任何组织或个人均可运行独立的 registry index，通过 Git 的分布式特性实现天然的去中心化。

### Git-native

以 Git 仓库作为 index 的物理载体，利用 Git 的签名、历史追溯、分支与标签机制实现版本管理与溯源。协议层不引入额外的状态存储。

### 语言无关 (Language-agnostic)

世界组件（Fragment / Capability）本质是结构（规则、技能定义、脚本元数据），而非代码依赖。因此协议不绑定任何特定语言的包管理器（如 npm/pip/cargo），仅以 Git URL + manifest 驱动分发。

### 渐进增强 (Progressive enhancement)

- **v0.x**：纯 Git 方案，通过 `git clone`/`git archive` 获取组件，无需任何服务端。
- **v1.x**：可选 HTTP API 加速层，在 Git 之上提供查询、搜索、批量解析等高性能接口，但 Git 始终保留为可信源（source of truth）。

## Registry 配置格式

每个世界通过 `registry.toml` 声明其依赖的 registry 源。该文件位于世界根目录（与 `world.toml` 同级）。

```toml
# registry.toml — 世界级别的 Registry 源配置
# Draft v0.1

[registries.default]
url = "https://github.com/agentforge/registry-index"
type = "git"        # git | http
priority = 1

[registries.private]
url = "https://github.com/my-org/world-registry"
type = "git"
priority = 2
auth = "token"      # 可选：token | ssh | none（默认值）

[registries.community]
url = "https://registry.agentforge.community"
type = "http"
priority = 3
```

### 配置字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `url` | string | 是 | Registry index 地址。`type=git` 时为 Git 仓库 URL；`type=http` 时为 HTTP API 根地址 |
| `type` | string | 是 | Registry 类型：`git` 或 `http` |
| `priority` | integer | 是 | 解析优先级，数值越小优先级越高。冲突时高优先级 registry 的条目覆盖低优先级 |
| `auth` | string | 否 | 认证方式：`none`（默认）、`token`（HTTP Bearer Token 或 Git HTTPS token）、`ssh`（Git SSH key） |

### 解析优先级规则

当多个 registry 声明同名组件时，按以下规则裁决：

1. **priority 数值最小者优先**。
2. **同 priority 时，按 `registry.toml` 中声明顺序**，先声明者优先。
3. **本地覆盖**：世界根目录的 `.local/` 目录可放置同名组件，优先级最高（用于本地开发与调试）。

## Git-based Registry Index 仓库结构

一个标准的 registry index 是遵循本协议目录约定的 Git 仓库。

```text
registry-index/
├── fragments/                          # Fragment 索引目录
│   ├── py/
│   │   └── python-engineering.toml     # 条目文件（TOML 格式）
│   ├── do/
│   │   └── docs-governance-tools.toml
│   └── ...
├── capabilities/                       # Capability 索引目录
│   ├── skills/
│   │   └── task-execution-summary.toml
│   ├── scripts/
│   │   └── check-env.toml
│   └── ...
├── registry-meta.toml                  # Registry 自身元数据
└── README.md                           # 人类可读的 registry 说明
```

### 目录组织约定

| 目录 | 内容 |
|------|------|
| `fragments/{category}/` | Fragment 条目。`{category}` 为短分类标识（如 `py` = Python、`do` = docs、`fe` = frontend），不超过 4 个字符 |
| `capabilities/skills/` | Skill 类型 Capability 条目 |
| `capabilities/scripts/` | Script 类型 Capability 条目 |
| `capabilities/templates/` | Template 类型 Capability 条目 |

### registry-meta.toml

Registry 仓库自身的声明文件：

```toml
[registry]
name = "agentforge-official"
description = "AgentForge 官方世界组件 Registry"
version = "2025.1"
maintainers = ["agentforge-core"]
url = "https://github.com/agentforge/registry-index"

[registry.policy]
accept_submissions = true       # 是否接受外部提交
require_signed_commits = true   # 是否要求提交签名
review_required = true          # 合并前是否需人工审查

[registry.capabilities]
http_api = false                # 当前是否提供 HTTP API 加速层
search_enabled = false          # 是否支持全文搜索
checksum_algorithm = "sha256"   # 默认校验和算法
```

## Index 条目格式

每个 Fragment 或 Capability 对应一个 TOML 条目文件，文件名即组件名（不含版本号）。

### 条目文件示例

```toml
# fragments/py/python-engineering.toml

[metadata]
name = "python-engineering"
description = "Python 工程规范与兼容性检查"
authors = ["agentforge-core <core@agentforge.dev>"]
license = "MIT"
keywords = ["python", "lint", "compatibility", "engineering"]
category = "py"
type = "fragment"           # fragment | skill | script | template

[source]
repository = "https://github.com/agentforge/fragment-python-engineering"

[[versions]]
version = "1.2.0"
git_url = "https://github.com/agentforge/fragment-python-engineering"
git_ref = "v1.2.0"          # tag、branch 或 commit hash
checksum = "sha256:abc123..."
manifest_path = "fragment.toml"
yanked = false
published_at = "2025-03-15T08:00:00Z"

[[versions]]
version = "1.1.0"
git_url = "https://github.com/agentforge/fragment-python-engineering"
git_ref = "v1.1.0"
checksum = "sha256:def456..."
manifest_path = "fragment.toml"
yanked = false
published_at = "2025-01-20T08:00:00Z"

[latest]
stable = "1.2.0"
```

### 字段说明

#### metadata 段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | 是 | 组件唯一标识名，全局唯一（跨 registry 通过 `[registry]/[name]` 限定） |
| `description` | string | 是 | 一句话描述 |
| `authors` | [string] | 否 | 作者列表，格式 `Name <email>` |
| `license` | string | 否 | SPDX 许可证标识 |
| `keywords` | [string] | 否 | 搜索关键词 |
| `category` | string | 否 | 分类标识，与目录结构中的 `{category}` 一致 |
| `type` | string | 是 | `fragment` / `skill` / `script` / `template` |

#### source 段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `repository` | string | 是 | 组件源码主仓库地址 |

#### versions 数组

每个版本为一个数组元素：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `version` | string | 是 | 语义化版本号（SemVer） |
| `git_url` | string | 是 | 该版本源码的 Git URL |
| `git_ref` | string | 是 | Git 标签、分支名或 commit hash |
| `checksum` | string | 否 | 内容校验和，格式 `[algorithm]:[hexdigest]` |
| `manifest_path` | string | 否 | 组件内 manifest 文件相对路径（如 `fragment.toml`、`SKILL.md`） |
| `yanked` | boolean | 否 | 是否已被撤回（默认为 `false`） |
| `published_at` | string | 否 | ISO 8601 发布时间 |

#### latest 段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `stable` | string | 是 | 当前最新的稳定版本号 |

### yanking 机制

已发布的版本可通过将 `yanked` 标记为 `true` 实现**软撤回**：

- **yanked = true 的条目仍保留在 index 中**，供依赖解析时提供明确的弃用信号。
- CLI / 工具在解析依赖时，**默认跳过 yanked 版本**，但允许通过 `--allow-yanked` 显式选择。
- yanked 版本**不得作为 `latest.stable` 指向的目标**。

## HTTP API 接口（可选加速层）

当 registry 提供 `type = "http"` 的源时，协议定义以下 RESTful API。所有接口的基地址为 registry 配置中的 `url`。

### 接口概览

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/v1/fragments/{name}` | 获取指定 Fragment 的所有版本元数据 |
| `GET` | `/v1/fragments/{name}/{version}` | 获取指定 Fragment 特定版本的详情 |
| `POST` | `/v1/fragments` | 发布新的 Fragment 版本（需认证） |
| `GET` | `/v1/capabilities/{name}` | 获取指定 Capability 的所有版本元数据 |
| `GET` | `/v1/capabilities/{name}/{version}` | 获取指定 Capability 特定版本的详情 |
| `POST` | `/v1/capabilities` | 发布新的 Capability 版本（需认证） |
| `GET` | `/v1/search` | 搜索组件 |
| `POST` | `/v1/resolve` | 批量依赖解析 |

### GET /v1/fragments/{name}

获取 Fragment 条目内容，与 Git index 中的 TOML 文件语义等价。

**响应示例**：

```json
{
  "metadata": {
    "name": "python-engineering",
    "description": "Python 工程规范与兼容性检查",
    "authors": ["agentforge-core <core@agentforge.dev>"],
    "license": "MIT",
    "keywords": ["python", "lint", "compatibility"],
    "category": "py",
    "type": "fragment"
  },
  "source": {
    "repository": "https://github.com/agentforge/fragment-python-engineering"
  },
  "versions": [
    {
      "version": "1.2.0",
      "git_url": "https://github.com/agentforge/fragment-python-engineering",
      "git_ref": "v1.2.0",
      "checksum": "sha256:abc123...",
      "manifest_path": "fragment.toml",
      "yanked": false,
      "published_at": "2025-03-15T08:00:00Z"
    }
  ],
  "latest": {
    "stable": "1.2.0"
  }
}
```

### GET /v1/fragments/{name}/{version}

获取特定版本的详情。若版本不存在或已 yanked，返回 `404 Not Found`（`--allow-yanked` 查询参数可绕过 yanked 检查）。

### POST /v1/fragments

发布新的 Fragment 版本。请求体：

```json
{
  "name": "python-engineering",
  "version": "1.3.0",
  "git_url": "https://github.com/agentforge/fragment-python-engineering",
  "git_ref": "v1.3.0",
  "checksum": "sha256:xyz789...",
  "manifest_path": "fragment.toml"
}
```

**校验规则**：

- `version` 必须遵循 SemVer。
- 同 `name` 下 `version` 不得重复。
- `git_ref` 必须在 `git_url` 对应的仓库中可解析。
- `checksum` 算法必须与 `registry-meta.toml` 中的 `checksum_algorithm` 一致。

**认证**：使用 `Authorization: Bearer <token>` 头部。

### GET /v1/search

**查询参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `q` | string | 是 | 搜索关键词（匹配 name / description / keywords） |
| `type` | string | 否 | 过滤类型：`fragment` / `skill` / `script` / `template` |
| `category` | string | 否 | 过滤分类 |
| `limit` | integer | 否 | 返回结果上限（默认 20，最大 100） |

**响应示例**：

```json
{
  "query": "python",
  "total": 3,
  "results": [
    {
      "name": "python-engineering",
      "type": "fragment",
      "description": "Python 工程规范与兼容性检查",
      "latest_version": "1.2.0",
      "registry": "agentforge-official"
    }
  ]
}
```

### POST /v1/resolve

批量依赖解析，用于 CLI 在 `world.toml` 依赖声明变更时计算完整依赖树。

**请求体**：

```json
{
  "dependencies": [
    {"name": "python-engineering", "version_req": ">=1.1.0"},
    {"name": "docs-governance-tools", "version_req": "^2.0.0"}
  ],
  "allow_yanked": false,
  "allow_prerelease": false
}
```

**响应示例**：

```json
{
  "resolved": [
    {
      "name": "python-engineering",
      "version": "1.2.0",
      "git_url": "https://github.com/agentforge/fragment-python-engineering",
      "git_ref": "v1.2.0",
      "checksum": "sha256:abc123..."
    }
  ],
  "unresolved": [],
  "conflicts": []
}
```

**版本需求语法（Version Req）**：

| 写法 | 含义 |
|------|------|
| `1.2.0` | 精确版本 |
| `>=1.1.0` | 大于等于 |
| `^1.2.0` | 兼容版本（`>=1.2.0, <2.0.0`） |
| `~1.2.0` | 近似版本（`>=1.2.0, <1.3.0`） |
| `*` | 任意版本（取 latest stable） |

## 发布流程

组件从开发者本地到进入 Registry 的完整流程：

```{mermaid}
flowchart LR
    A["本地开发"] --> B["本地校验"]
    B --> C["打包签名"]
    C --> D["推送到 Registry Index"]
    D --> E["更新索引 TOML"]
    E --> F["CI 校验与合并"]
```

### 1. 本地校验

开发者在组件源码仓库执行：

```bash
# 校验 manifest 文件格式与必填字段
agentforge validate ./fragment.toml

# 校验版本号是否符合 SemVer
agentforge validate --semver ./fragment.toml

# 运行组件自带测试（如有）
agentforge test ./
```

### 2. 打包与签名

```bash
# 生成内容 tarball 并计算校验和
agentforge pack ./ --output ./python-engineering-1.3.0.tar.gz

# 可选：对 tarball 进行 GPG 签名
agentforge sign ./python-engineering-1.3.0.tar.gz --key ~/.gpg/agentforge.key
```

打包过程将组件目录（排除 `.git/`、`.temp/` 等）压缩为归档文件，用于生成 `checksum`。

### 3. 推送到 Registry Index

Registry index 本身是一个 Git 仓库。发布即向该仓库提交一个更新对应 TOML 条目的 PR：

```bash
# 1. Fork / clone registry-index 仓库
git clone https://github.com/agentforge/registry-index.git

# 2. 更新对应条目文件
# 在 fragments/py/python-engineering.toml 中追加新版本

# 3. 本地校验 index 格式
agentforge registry-check ./registry-index/

# 4. 提交并推送
git add fragments/py/python-engineering.toml
git commit -S -m "publish(fragment): python-engineering v1.3.0"
git push origin publish/python-engineering-1.3.0

# 5. 创建 Pull Request
```

### 4. 版本递增校验

Registry 维护方在合并 PR 前执行以下校验：

- **版本号递增**：新版本的 `version` 必须大于该条目下所有已有版本。
- **不重复**：`version` 在该条目下不得已存在。
- **git_ref 可达**：`git_ref` 必须在 `git_url` 仓库中可解析（CI 可自动 shallow clone 验证）。
- **checksum 匹配**：打包 tarball 的 checksum 与提交声明一致。

### 5. Yanking 流程

撤回已发布版本通过修改 index 条目实现：

```bash
# 将对应版本的 yanked 设为 true
git commit -S -m "yank(fragment): python-engineering v1.1.0"
```

Yanking 不删除历史记录，仅标记弃用状态，确保下游工具的确定性行为。

## 安全模型

### Git 签名验证

Registry index 仓库**必须启用 signed commits**（`require_signed_commits = true`）。所有修改 index 的提交须由维护者 GPG 或 SSH key 签名，确保索引完整性。

### Checksum 校验

每个版本声明 `checksum`，CLI 在安装组件时：

1. 通过 `git archive` 或 HTTP 获取组件内容。
2. 重新计算校验和。
3. 与 index 中声明值比对，不匹配则中止安装并告警。

### 权限控制

| 操作 | 权限要求 | 说明 |
|------|----------|------|
| 读取 / 搜索 index | 公开 | 无需认证 |
| 发布新版本 | Registry 维护者 / 已授权提交者 | 通过 GitHub/GitLab 的 branch protection + CODEOWNERS 控制 |
| Yank 版本 | 同发布权限，或更高的治理角色 | 建议通过团队审批流程 |
| 修改 registry-meta.toml | Registry 所有者 | 涉及全局策略变更 |

## 与 world.toml 的关系

`world.toml` 是世界的**声明式描述**，`registry.toml` 是世界的**Registry 源配置**。两者相互独立但协作：

```{mermaid}
flowchart TD
    A["world.toml"] -->|声明依赖哪些 Fragment/Capability| B["CLI / AgentForge 工具"]
    C["registry.toml"] -->|声明从哪些 Registry 解析| B
    B --> D["Registry Index<br/>Git 仓库"]
    D --> E["组件源码仓库"]
```

### world.toml 中的依赖声明

`world.toml` 的 `[fragments]` 与 `[capabilities]` 段可引用 Registry 中的组件：

```toml
# world.toml

[fragments.python-engineering]
version = "1.2.0"        # 精确版本
source = "registry"      # 从 Registry 解析（默认行为）
optional = true

[fragments.docs-governance-tools]
version = "^2.0.0"       # 兼容版本，解析时取满足条件的最新版
source = "registry"

[capabilities.skills.task-execution-summary]
version = "~1.0.0"
source = "registry"
```

### 解析顺序

1. CLI 读取 `world.toml`，收集所有 `source = "registry"` 的组件需求。
2. 读取 `registry.toml`，按 `priority` 排序 registry 源。
3. 依次查询各 registry，解析 `version_req` 为精确版本。
4. 将解析结果（Git URL + ref + checksum）写入锁定文件 `world.lock`（或 `.agents/world.lock`）。
5. 安装时依据锁定文件执行 `git archive` 或 `git clone --depth 1`，并将组件内容映射到 `.agents/` 对应位置。

### 离线模式

若 `registry.toml` 缺失或为空，CLI 退化为**纯本地模式**：

- 仅解析 `world.toml` 中已存在路径的组件（如本地相对路径的 fragments）。
- 不执行网络请求，不生成锁定文件。

## 渐进式演进路线

### v0.5 — 纯 Git 方案（当前目标）

- [x] `registry.toml` 配置格式定义
- [x] Git-based index 目录结构与条目格式
- [ ] CLI `agentforge install` 支持从 Git index 解析并安装 Fragment/Capability
- [ ] `agentforge validate` 支持校验 index 条目与 manifest 格式
- [ ] `world.lock` 锁定文件生成与消费

### v0.8 — 多 Registry 与冲突解决

- [ ] 支持多 registry 源并行查询与优先级裁决
- [ ] 同名组件跨 registry 冲突告警与交互式选择
- [ ] 本地 `.local/` 覆盖机制

### v1.0 — Git + HTTP 混合方案

- [ ] 标准 HTTP API 服务端参考实现
- [ ] Registry 缓存与镜像机制
- [ ] 批量解析 `/v1/resolve` 客户端优化
- [ ] 搜索接口与语义化推荐

### v1.x+ — 治理增强

- [ ] Registry 联邦（Registry 之间互相索引）
- [ ] 自动化安全审计（CVE 扫描、恶意脚本检测）
- [ ] 组件评分与信誉体系

## 附录

### A. 术语表

| 术语 | 说明 |
|------|------|
| **Registry** | 世界组件的索引与分发服务，物理载体为 Git 仓库或 HTTP API |
| **Index** | Registry 中的索引数据，即 TOML 条目文件的集合 |
| **Entry** | 单个组件的元数据描述文件（如 `python-engineering.toml`） |
| **Component** | 可分发单元，包括 Fragment 与 Capability |
| **Yank** | 软撤回已发布版本，保留记录但阻止默认安装 |
| **world.lock** | 精确版本锁定文件，记录解析后的 Git URL + ref + checksum |

### B. 相关文档

- `world.toml` 格式规范：``.agents/world.toml``（项目真实源）
- 世界分层架构：{doc}`features` 中 {ref}`.agents 目录详解 <agents-dir-details>` 章节
- 外部项目集成：{doc}`integration-guide`
