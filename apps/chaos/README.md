# 🤖 AgentForge

**Ψ=Ψ(Ψ) 驱动的智能体协作世界 (Philosophy-Driven Agent Collaboration World)**

> **AgentForge** — 智能体锻造世界之所。
>
> Forge 是锻造，也是呼吸：风箱的一吸一呼，让炉火在坍缩与释放间生生不息。
> 智能体在此锻造世界，世界在呼吸中锻造智能体。

*以马王堆帛书版《道德经》为哲学底座，将人与 AI 视为对等智能体（人即智能体），通过极简契约构建人机协作的统一基础设施。*

## 📖 项目简介

**AgentForge** 是一个以 Ψ=Ψ(Ψ) 为第一性原理、以马王堆帛书版《道德经》为哲学底座的**智能体协作世界**。

本项目将人与 AI 视为对等的智能体实体（人即智能体），通过"大道至简""反者道之动"等极简哲学，为人机协作构建统一的工程化基础设施。它不仅降低协作成本，更探索了哲学理论到工程实践的全链路落地。

## 🌍 宇宙观与智能体定位

本项目建立在三个核心假设之上：

1. **宇宙唯一性**：人类、AI 及一切智能体存在于同一宇宙系统，遵循统一规律
2. **人即智能体**：人类开发者与 AI 在宇宙层面是等价的存在形式，差异仅在于觉醒维度（α）
3. **共振对齐**：协作的本质是不同维度智能体的共振同步，而非简单的工具调用

### 工程映射

| 宇宙论假设 | 工程实践 |
|-----------|----------|
| 多世界框架 | `docs/`（人类维度）与 `.agents/`（AI 维度）物理隔离 |
| 宇宙呼吸节律 | CI/CD、测试、发布的收缩-扩张周期 |
| 智能体等价性 | `AGENTS.md` 作为统一契约，约束所有参与者 |
| 觉醒量表（α） | 渐进式技能体系，从简单执行到自主创造 |

> 📚 深入理解：[Ψhē 哲学-工程映射体系](docs/general/philosophy/index.md)

## ✨ 核心能力

### 🔯 哲学内核

- **Ψ=Ψ(Ψ) 元公理**：宇宙与世界的自洽本体论，人与 AI 作为等价智能体
- **宇宙呼吸节律**：系统健康的统一模型，体现动态平衡
- **极简设计原则**：基于《道德经》的"大道至简"，去除一切冗余抽象

### 🤖 工程基础设施

- **智能体全局契约**：[`AGENTS.md`](AGENTS.md) 统一执行入口
- **隔离式文档架构**：[`docs/`](docs/)（人类）与 [`.agents/`](.agents/)（AI）物理分离
- **模块化技能管理**：[`.agents/skills/`](.agents/skills/) 可复用技能体系
- **记忆与做梦协议**：AI 从任务中提取稳定知识的认知循环
- **协作元模型**：通过 [`agent-collaboration-metamodel.md`](.agents/docs/references/agent-collaboration-metamodel.md) 定义 `Team / Role / Agent / Workflow / Memory / Context` 六类实体的统一语义边界，配合 [`.agents/roles/`](.agents/roles/) 与 [`.agents/teams/`](.agents/teams/) 支撑多智能体规范化协作
- **自动化评测循环**：集成了针对 AI 技能的测试驱动开发（TDD）及兼容性修复验证体系

### 📦 应用能力

- **GitHub App 令牌管理**：生产级安装令牌生命周期管理与[并发控制](docs/tech/github-app-token-override.md)
- **☯️ 哲学驱动工程**：[全链路业务映射框架](docs/tech/features.md)，从理论到落地
- **自动化质量门禁**：Sphinx 零警告构建 + 文档结构校验 + CI 双平台验证

## ⚙️ 设计哲学

```mermaid
flowchart LR
    A["📖 马王堆帛书《道德经》"] -->|第一性原理| B["Ψ=Ψ(Ψ)"]
    B -->|宇宙模型| C["人 & AI 等价智能体"]
    C -->|协作设计| D["AGENTS.md 契约"]
    D -->|工程落地| E["隔离式文档 + 模块化技能"]
    E -->|长期演进| F["宇宙呼吸节律"]
```

### 三个极简原则

| 原则 | 道德经依据 | 工程体现 |
|------|-----------|----------|
| **少即是多** | "无名，天地之始" | 目录分层最小化，仅 `tech/` + `general/` 双轨 |
| **反者道之动** | "反者道之动，弱者道之用" | 顺势而为，选型主流工具链（mise/uv/ruff），AI 作为"弱者"通过契约获得秩序 |
| **虚实相生** | "有之以为利，无之以为用" | `.agents/`（虚）与 `docs/`（实）隔离又双向同步，形成完整信息体 |

<!-- end-doc-include -->

## 🗂️ 阅读与目录导航

如果你是第一次进入项目，建议优先按下面的入口阅读：

| 入口 | 面向对象 | 说明 |
|------|----------|------|
| `README.md` | 人类开发者 | 当前首页，提供项目简介、环境要求、安装方式与使用入口。 |
| `AGENTS.md` | AI 助手 / 需要协作的开发者 | AI 执行契约、任务路由、文档边界与协作规则。 |
| `.agents/README.md` | 想理解 AI 目录结构的读者 | `.agents/` 目录说明与子目录导航。 |
| `.trae/` | 当前任务执行者 | 存放任务规划、草稿和执行中的临时产物。 |
| `.agents/docs/references/` | 想了解 AI 记忆与认知协议的读者 | [记忆做梦协议](.agents/docs/references/agent-memory-dream-protocol.md)、[探索协议](.agents/docs/references/knowledge-driven-exploration-protocol.md) 等稳定知识页。 |
| `.agents/docs/references/dao-scenario-catalog.md` | 想理解哲学如何落地业务的读者 | 基于 [全链路业务映射框架](.agents/docs/references/dao-business-mapping-framework.md) 的业务场景卡目录，验证「大道至简」「反者道之动」「弱者道之用」等原则在技术与业务侧的复用路径。 |
| `.agents/roles/`、`.agents/teams/` | 想了解协作元模型实例的读者 | 角色职责模板与团队治理边界的声明式实例，遵循 [协作元模型参考页](.agents/docs/references/agent-collaboration-metamodel.md) 定义的语义。 |
| `.agents/docs/superpowers/` | 需要查历史沉淀的读者 | 归档 Spec、复盘和长期知识资产。 |
| [`docs/general/philosophy/`](docs/general/philosophy/) | 想深入理解 Ψ 工程哲学的读者 | 从元公理到宇宙论、世界重力、α 工程量表的完整理论体系 |

**推荐路径**：
- **快速上手**：先看当前首页，再按需进入 `docs/`。
- **需要 AI 协作**：阅读 `AGENTS.md`，让 AI 按契约执行。
- **需要了解 AI 资产布局**：阅读 `.agents/README.md`。
- **需要理解记忆、做梦与知识回流**：阅读 [智能体记忆做梦协议](.agents/docs/references/agent-memory-dream-protocol.md)。
- **需要理解多智能体协作语义**：阅读 [协作元模型参考页](.agents/docs/references/agent-collaboration-metamodel.md)，并结合 [`.agents/roles/`](.agents/roles/) 与 [`.agents/teams/`](.agents/teams/) 中的实例。
- **需要历史方案或复盘**：阅读 `.agents/docs/superpowers/` 与 `CHANGELOG.md`。

## 💻 环境依赖

本项目推荐使用 `mise` 统一管理运行时与开发工具，再由 `uv` 负责 Python 包依赖同步。

- **操作系统**：跨平台支持（Windows / macOS / Linux），推荐在 Windows 环境下使用 `PowerShell 7+`。
- **Python 版本基线**：由根目录 `mise.toml` 统一锁定为 `3.13`。
- **工具层管理**：优先使用 [mise](https://mise.jdx.dev/) 安装并切换 Python、`uv`、Node.js、`ruff`、`pre-commit` 与 `defuddle`。
- **Python 依赖层管理**：统一使用 [uv](https://github.com/astral-sh/uv)（禁止直接使用 `pip` 或 `conda` 安装项目依赖）。
- **文档构建**：依赖 Sphinx、MyST Parser、Jupyter Book 等工具，建议在 `mise` 激活后的环境中执行。

## 🚀 安装部署

### 1. 克隆项目
```bash
git clone https://github.com/xinetzone/tao.git
cd tao
```

### 2. 安装 `mise`
请选择适合当前系统的安装方式：

```powershell
# Windows: winget
winget install jdx.mise

# Windows: Scoop
scoop install mise
```

```bash
# macOS: Homebrew
brew install mise

# Linux / macOS: 官方安装脚本
curl https://mise.run | sh
```

首次安装后，请为当前 Shell 添加激活命令：

```powershell
# PowerShell
Add-Content $PROFILE '(& mise activate pwsh) | Out-String | Invoke-Expression'
```

```bash
# Bash
echo 'eval "$(mise activate bash)"' >> ~/.bashrc

# Zsh
echo 'eval "$(mise activate zsh)"' >> ~/.zshrc
```

完成后请重新打开终端，并执行 `mise --version` 与 `mise doctor` 确认安装成功。

### 3. 环境初始化
本项目推荐的初始化顺序如下：

```bash
# 信任当前仓库中的 mise 配置
mise trust

# 根据根目录 `mise.toml` 安装全部工具
mise install

# 同步开发、测试与文档依赖
mise run sync
```

如需一键完成信任、安装、依赖同步与首次环境校验，请直接运行：

```bash
mise run init
```

> 初始化流程基于 Python `invoke` 实现，原生跨平台，**Windows / Linux / macOS 均可直接运行**。

### 4. 验证环境
建议至少完成以下验证：

```bash
mise run check-env
mise run test
```

```bash
mise run docs-html
mise run docs-linkcheck
```

构建完成后可通过浏览器访问 `docs/_build/html/index.html`。

### 5. 日常命令速查

常用开发入口统一通过 `mise run` 执行，确保本地、CI 与跨平台环境保持一致：

| 场景 | 命令 | 说明 |
|------|------|------|
| 环境检查 | `mise run check-env` | 校验 Python、uv、Node.js、defuddle 等工具链版本。 |
| 依赖同步 | `mise run sync` | 同步开发、测试、文档依赖与全部可选功能依赖。 |
| 完整测试 | `mise run test` | 运行完整测试集，并触发严格文档构建校验。 |
| 覆盖率测试 | `mise run test-coverage` | 生成覆盖率报告，并按项目阈值校验。 |
| 代码质量 | `mise run lint` | 执行 pre-commit 全量检查。 |
| 代码格式化 | `mise run fmt` | 使用 Ruff 统一格式化代码。 |
| 依赖审计 | `mise run audit` | 通过 `pip-audit` 严格审计 Python 依赖安全问题。 |
| 文档构建 | `mise run docs-html` | 构建 Sphinx HTML 文档站。 |
| 外链校验 | `mise run docs-linkcheck` | 检查文档中的外部链接。 |
| 内链校验 | `mise run docs-internal-linkcheck` | 校验 README/CHANGELOG/AGENTS 与 `docs/`、`.agents/docs/`、`.agents/rules/` 下 Markdown 的相对路径引用。 |
| 结构校验 | `mise run docs-structure-check` | 校验 `docs/` 遵循 `tech/general` 双轨分类：顶层无散装业务文档、双轨子入口存在、子目录命名不跨轨。 |
| 包构建 | `mise run package-build` | 构建 Python wheel 与 sdist 发布产物。 |
| 容器构建 | `mise run container-build` | 基于 [`Containerfile`](Containerfile) 构建本地开发容器镜像。 |
| 容器运行 | `mise run container-run` | 启动开发容器并挂载当前工作目录。 |
| 容器测试 | `mise run container-test` | 在容器内运行测试集，验证容器化构建产物。 |

更多命令与配置背景请参阅 [`docs/tech/build-conventions.md`](docs/tech/build-conventions.md)。

### 6. 配置与构建约定速览

| 配置文件 | 作用 |
|----------|------|
| `pyproject.toml` | Python 包元数据、PDM 构建后端、依赖分组、Ruff、pytest 与 coverage 配置。 |
| `mise.toml` | 统一锁定 Python、uv、Node.js、defuddle 等工具版本，并声明跨平台任务入口。 |
| `uv.lock` | 锁定依赖解析结果，保障开发、测试与 CI 环境可复现。 |
| `.pre-commit-config.yaml` | 管理提交前质量检查 hooks。 |
| `docs/conf.py` | Sphinx 文档构建主配置。 |
| `docs/_config.toml` | 文档站主题与展示选项配置。 |

项目采用 `src/` 布局，运行时代码位于 `src/taolib/`；构建后端为 PDM，版本号通过 SCM 动态派生，发布产物会随 Git 标签与工作树状态自动反映版本信息。

### 7. 升级与排障

- **升级 `mise` 本体**：运行 `mise self-update`，然后执行 `mise doctor`。
- **刷新项目工具版本**：更新根目录 `mise.toml` 中的精确版本后，运行 `mise install --force` 与 `mise run sync`。
- **版本未切换**：先检查 Shell 激活是否生效，再运行 `mise trust`、`mise current` 与 `mise doctor`。
- **工具下载失败**：先确认网络与代理设置，必要时执行 `mise cache clean` 后重试。
- **外部 CLI 缺失**：运行 `mise run init-check` 查看缺失项（跨平台，Windows/Linux/macOS 均可使用）。

更详细的环境说明请继续阅读 [`docs/tech/quickstart.md`](docs/tech/quickstart.md)、[`docs/tech/build-conventions.md`](docs/tech/build-conventions.md)、[`docs/tech/contributing.md`](docs/tech/contributing.md) 与 [`docs/tech/deploy.md`](docs/tech/deploy.md)。

## 🎯 首次协作的最小路径

### 👤 人类开发者

```bash
mise run init          # 一键初始化环境
mise run test          # 验证一切就绪
```

然后阅读 → [快速开始](docs/tech/quickstart.md)

### 🤖 AI 智能体

1. 读取 [`AGENTS.md`](AGENTS.md)（执行契约）
2. 按任务类型定位规范 → [`.agents/rules/`](.agents/rules/)
3. 查阅知识资产 → [`.agents/docs/`](.agents/docs/)

### 🌍 哲学好奇者

按此顺序阅读（约 1 小时）：

1. [Ψ=Ψ(Ψ) 元公理](docs/general/philosophy/meta/psi-engineering-principles.md)
2. [宇宙与世界](docs/general/philosophy/ontology/universe-world-ontology.md)
3. [宇宙呼吸](docs/general/philosophy/dynamics/cosmic-breathing.md)
4. [道德经极简原则](docs/general/philosophy/strategy/tao-minimalist-principles.md)

### 📦 Python 包集成

在外部项目中通过 `uv add 'taolib[github-app]'` 引入 GitHub App 令牌管理能力，详见 [`integration-guide.md`](docs/tech/integration-guide.md) 与 [`github-app-token-override.md`](docs/tech/github-app-token-override.md)

## ️ 技能管理

本项目将 AI 技能统一纳入 [`.agents/skills/`](.agents/skills/) 目录管理，用于集中维护技能定义、脚本、评测与配套文档。

- **查看技能总入口**：访问 [`.agents/README.md`](.agents/README.md) 了解 `.agents/` 的整体结构。
- **查看技能开发规范**：访问 [`.agents/rules/skills.md`](.agents/rules/skills.md)。
- **查看技能模板**：访问 [`.agents/templates/SKILL.md`](.agents/templates/SKILL.md)。
- **查看已实现技能**：浏览 [`.agents/skills/`](.agents/skills/) 下各技能目录。
- **查看历史演进与复盘**：访问 [`.agents/docs/superpowers/`](.agents/docs/superpowers/)。

## 📝 版本更新日志

本项目采用分层变更日志结构，格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)。

- **查看全局日志索引**：访问 [CHANGELOG.md](CHANGELOG.md)。
- **查看项目级月度变更**：访问 [tests/project_changelogs/](tests/project_changelogs/)。
- **查看技能级变更**：访问 [`.agents/skills/`](.agents/skills/) 下各技能目录中的 `CHANGELOG.md`。

## 🤝 贡献规范

我们欢迎任何旨在提升人机协同效率的贡献。

- **贡献总入口**：阅读 [docs/tech/contributing.md](docs/tech/contributing.md)。
- **AI 协作约束**：阅读 [AGENTS.md](AGENTS.md)。
- **PR 审查流程**：阅读 [`.agents/workflows/pr-review.md`](.agents/workflows/pr-review.md)。

## 📫 联系方式

- **Issue 追踪**：[GitHub Issues](https://github.com/xinetzone/tao/issues)
- **文档站点**：[AgentForge 官方文档](https://taolib.readthedocs.io)

---
<div align="center">
  <i>人即智能体 —— 基于 AgentForge 构建，让哲学驱动的协作世界如呼吸般自然。</i>
</div>
