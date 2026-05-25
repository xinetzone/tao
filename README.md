# 🤖 AgentForge

<div align="center">

![repo size](https://img.shields.io/github/repo-size/xinetzone/tao.svg)
[![PyPI][pypi-badge]][pypi-link]
[![GitHub issues][issue-badge]][issue-link]
[![GitHub forks][fork-badge]][fork-link]
[![GitHub stars][star-badge]][star-link]
[![GitHub license][license-badge]][license-link]
[![contributors][contributor-badge]][contributor-link]
[![watcher][watcher-badge]][watcher-link]
[![Binder][binder-badge]][binder-link]
[![Downloads][download-badge]][download-link]
[![Documentation Status][status-badge]][status-link]
[![PyPI - Downloads][install-badge]][install-link]

[pypi-badge]: https://img.shields.io/pypi/v/taolib.svg
[pypi-link]: https://pypi.org/project/taolib/
[issue-badge]: https://img.shields.io/github/issues/xinetzone/tao
[issue-link]: https://github.com/xinetzone/tao/issues
[fork-badge]: https://img.shields.io/github/forks/xinetzone/tao
[fork-link]: https://github.com/xinetzone/tao/network
[star-badge]: https://img.shields.io/github/stars/xinetzone/tao
[star-link]: https://github.com/xinetzone/tao/stargazers
[license-badge]: https://img.shields.io/github/license/xinetzone/tao
[license-link]: https://github.com/xinetzone/tao/blob/main/LICENSE
[contributor-badge]: https://img.shields.io/github/contributors/xinetzone/tao
[contributor-link]: https://github.com/xinetzone/tao/contributors
[watcher-badge]: https://img.shields.io/github/watchers/xinetzone/tao
[watcher-link]: https://github.com/xinetzone/tao/watchers
[binder-badge]: https://mybinder.org/badge_logo.svg
[binder-link]: https://mybinder.org/v2/gh/xinetzone/tao/main
[install-badge]: https://img.shields.io/pypi/dw/taolib?label=pypi%20installs
[install-link]: https://pypistats.org/packages/taolib
[status-badge]: https://readthedocs.org/projects/taolib/badge/?version=latest
[status-link]: https://taolib.readthedocs.io/zh-cn/latest/?badge=latest
[download-badge]: https://pepy.tech/badge/taolib
[download-link]: https://pepy.tech/project/taolib

**AI 驱动开发模板 (AI-Driven Development Template)**

*这是一个面向未来的、为 AI 智能体高度优化的项目脚手架与开发模板。通过内置的“契约”系统，它可以确保 AI 助手在辅助开发时遵循统一的规范和最佳实践。*

</div>

<!-- end-doc-include -->

---

## 📖 项目简介

**AgentForge** 是一个面向 AI 辅助开发场景的项目模板，目标是降低人类开发者与 AI 智能体协作时的沟通和维护成本。
本项目以马王堆帛书版《道德经》为哲学底座，追求极致简约与学以致用。它不仅提供了清晰的目录约定与智能体协作规范，更探索了将“大道至简”、“反者道之动”等理论哲学转化为可落地的工程实施方案，适合构建需要长期演进的工程化项目。

## ✨ 功能特性

- **☯️ 哲学驱动工程**：基于《道德经》底层逻辑，通过 [全链路业务映射框架](.agents/docs/references/dao-business-mapping-framework.md) 实现从哲学理论到业务场景的融会贯通。
- **🤖 智能体全局契约**：内置 `AGENTS.md`，统一 AI 助手的执行入口与协作规则。
- **🧩 清晰的目录分层**：区分人类文档、AI 规则、任务工作台与长期知识资产。
- **📦 模块化技能管理**：提供可复用的 AI 技能体系与规范化资产目录。
- **🛡️ 隔离式文档架构**：彻底分离人类专属文档（`docs/`）与 AI 专属资产库（`.agents/docs/`），防止 LLM 产生上下文幻觉。
- **🔄 自动化评测循环**：集成了针对 AI 技能的测试驱动开发（TDD）及兼容性修复验证体系。
- **🧠 智能体记忆与做梦协议**：定义了 [记忆、做梦、洞见回流与遗忘](.agents/docs/references/agent-memory-dream-protocol.md) 的认知循环，使智能体能够从任务中提取稳定知识，通过做梦式重组发现隐藏模式，并回流到规则与模板。
- **🧬 协作元模型**：通过 [`agent-collaboration-metamodel.md`](.agents/docs/references/agent-collaboration-metamodel.md) 定义 `Team / Role / Agent / Workflow / Memory / Context` 六类实体的统一语义边界，配合 [`.agents/roles/`](.agents/roles/) 与 [`.agents/teams/`](.agents/teams/) 提供职责模板与治理边界的声明式实例，支撑多智能体规范化协作。
- **🔐 GitHub App 令牌管理**：内置 [`taolib.github_app`](src/taolib/github_app/) Python 模块与 [`taolib-github-app`](src/taolib/cli/github_app.py) CLI，提供 GitHub App 安装令牌的策略解析、缓存、Singleflight 并发控制、事件钩子与 [PyGithub 适配器](src/taolib/github_app/pygithub_adapter.py)，可作为 Python 包独立集成到外部项目。
- **📚 Sphinx/MyST 深度集成**：开箱即用的现代化文档构建流，支持多层级模块化日志追踪。

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
- **Python 版本基线**：由根目录 `mise.toml` 统一锁定为 `3.14.5`。
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

## 🎮 使用指南

1. **人类开发入口**：访问 [`docs/index.md`](docs/index.md) 获取更详细的使用说明、API 文档与部署指南。
2. **AI 协作入口**：在让 AI 参与任务前，先阅读 [`AGENTS.md`](AGENTS.md) 以确认执行契约、文档边界与任务路由。
3. **AI 目录说明**：如需了解 `.agents/` 的结构与资产分布，请阅读 [`.agents/README.md`](.agents/README.md)。
4. **作为 Python 包集成**：在外部项目中通过 `uv add 'taolib[github-app]'` 引入 GitHub App 令牌管理能力，详见 [`docs/tech/integration-guide.md`](docs/tech/integration-guide.md) 与 [`docs/tech/github-app-token-override.md`](docs/tech/github-app-token-override.md)。

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
  <i>基于 AgentForge 引擎构建，让人与 AI 的协作如丝般顺滑。</i>
</div>
