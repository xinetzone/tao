# 🤖 AgentForge

<div align="center">

![repo size](https://img.shields.io/github/repo-size/xinetzone/tao.svg)
[![PyPI][pypi-badge]][pypi-link]
[![GitHub issues][issue-badge]][issue-link]
[![GitHub forks][fork-badge]][fork-link]
![atom star](https://gitcode.com/flexloop/flexloop/star/badge.svg)
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
[license-link]: https://github.com/xinetzone/tao/LICENSE
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
它提供了清晰的目录约定、文档分层、技能资产组织方式，以及开箱即用的开发与复盘工作流，适合构建需要长期演进的工程化项目。

## ✨ 功能特性

- **🤖 智能体全局契约**：内置 `AGENTS.md`，统一 AI 助手的执行入口与协作规则。
- **🧩 清晰的目录分层**：区分人类文档、AI 规则、任务工作台与长期知识资产。
- **📦 模块化技能管理**：提供可复用的 AI 技能体系与规范化资产目录。
- **隔离式文档架构**：彻底分离人类专属文档（`docs/`）与 AI 专属资产库（`.agents/docs/`），防止 LLM 产生上下文幻觉。
- **🔄 自动化评测循环**：集成了针对 AI 技能的测试驱动开发（TDD）及兼容性修复验证体系。
- **📚 Sphinx/MyST 深度集成**：开箱即用的现代化文档构建流，支持多层级模块化日志追踪。

## 🗂️ 阅读与目录导航

如果你是第一次进入项目，建议优先按下面的入口阅读：

| 入口 | 面向对象 | 说明 |
|------|----------|------|
| `README.md` | 人类开发者 | 当前首页，提供项目简介、环境要求、安装方式与使用入口。 |
| `AGENTS.md` | AI 助手 / 需要协作的开发者 | AI 执行契约、任务路由、文档边界与协作规则。 |
| `.agents/README.md` | 想理解 AI 目录结构的读者 | `.agents/` 目录说明与子目录导航。 |
| `.trae/` | 当前任务执行者 | 存放任务规划、草稿和执行中的临时产物。 |
| `.agents/docs/superpowers/` | 需要查历史沉淀的读者 | 归档 Spec、复盘和长期知识资产。 |

**推荐路径**：
- **快速上手**：先看当前首页，再按需进入 `docs/`。
- **需要 AI 协作**：阅读 `AGENTS.md`，让 AI 按契约执行。
- **需要了解 AI 资产布局**：阅读 `.agents/README.md`。
- **需要历史方案或复盘**：阅读 `.agents/docs/superpowers/` 与 `CHANGELOG.md`。

## 💻 环境依赖

本项目遵循严格的开发环境标准，请确保您的本地环境满足以下要求：

- **操作系统**：跨平台支持（Windows / macOS / Linux），推荐在 Windows 环境下使用 `PowerShell 7+`。
- **Python 版本**：`>= 3.13`
- **依赖管理工具**：统一使用 [uv](https://github.com/astral-sh/uv)（禁止直接使用 `pip` 或 `conda` 安装核心依赖）。
- **文档构建**：依赖 Sphinx, MyST Parser, Jupyter Book 等工具。

## 🚀 安装部署

### 1. 克隆项目
```bash
git clone https://github.com/xinetzone/tao.git
cd tao
```

### 2. 环境初始化
请使用 `uv` 创建虚拟环境并同步依赖：
```bash
# 创建虚拟环境
uv venv

# 激活虚拟环境 (Windows PowerShell)
.venv\Scripts\activate

# 安装项目核心依赖与文档依赖
uv sync --group docs
```

### 3. 构建本地文档 (可选)
```bash
cd docs
make html
# 构建完成后可通过浏览器访问 docs/_build/html/index.html
```

## 🎮 使用指南

1. **人类开发入口**：访问 [`docs/index.md`](docs/index.md) 获取更详细的使用说明、API 文档与部署指南。
2. **AI 协作入口**：在让 AI 参与任务前，先阅读 [`AGENTS.md`](AGENTS.md) 以确认执行契约、文档边界与任务路由。
3. **AI 目录说明**：如需了解 `.agents/` 的结构与资产分布，请阅读 [`.agents/README.md`](.agents/README.md)。

## 🛠️ 技能管理

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

- **贡献总入口**：阅读 [docs/contributing.md](docs/contributing.md)。
- **AI 协作约束**：阅读 [AGENTS.md](AGENTS.md)。
- **PR 审查流程**：阅读 [`.agents/workflows/pr-review.md`](.agents/workflows/pr-review.md)。

## 📫 联系方式

- **Issue 追踪**：[GitHub Issues](https://github.com/xinetzone/tao/issues)
- **文档站点**：[AgentForge 官方文档](https://taolib.readthedocs.io)

---
<div align="center">
  <i>基于 AgentForge 引擎构建，让人与 AI 的协作如丝般顺滑。</i>
</div>
