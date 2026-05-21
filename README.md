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

**AgentForge** 致力于解决在大型复杂项目中“人类开发者”与“AI 智能体”之间的协作摩擦问题。本项目不仅是一个包含标准代码结构的脚手架，更是一个**“人机协同双向契约”**的载体。
通过物理隔离人类阅读文档（`docs/`）与 AI 阅读文档（`.agents/`），以及内置丰富的自定义 AI 技能（Skills），AgentForge 实现了代码编写、文档生成、架构评审和经验复盘的全流程 AI 赋能。

## ✨ 功能特性

- **🤖 智能体全局契约**：内置 `AGENTS.md` 规范，实现基于上下文的智能路由（Context Router）。
- **📦 模块化技能管理**：提供基于自然语言的自定义 AI 技能链（如 `skill-creator`、`task-execution-summary`）。
- **隔离式文档架构**：彻底分离人类专属文档（`docs/`）与 AI 专属资产库（`.agents/docs/`），防止 LLM 产生上下文幻觉。
- **🔄 自动化评测循环**：集成了针对 AI 技能的测试驱动开发（TDD）及兼容性修复验证体系。
- **📚 Sphinx/MyST 深度集成**：开箱即用的现代化文档构建流，支持多层级模块化日志追踪。

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

# 安装项目依赖 (根据 docs/requirements.txt)
uv pip install -r docs/requirements.txt
```

### 3. 构建本地文档 (可选)
```bash
cd docs
make html
# 构建完成后可通过浏览器访问 docs/_build/html/index.html
```

## 🎮 使用指南

1. **查阅全局契约**：在指派 AI 执行任务前，请先让 AI 阅读根目录下的 [`AGENTS.md`](AGENTS.md)。
2. **触发特定工作流**：
   - 当需要开发前端功能时，AI 会自动路由并读取 `.agents/rules/frontend.md`。
   - 当需要进行复盘总结时，直接对 AI 助手说：“帮我复盘一下刚才的任务”，即可触发内置总结技能。
3. **查阅人类文档**：访问 [`docs/index.md`](docs/index.md) 获取更详细的 API 说明与部署指南。

## 🛠️ 技能管理

本项目将 AI 技能 (Skills) 纳入版本管理，实现技能的集中维护、评测和优化。所有技能统一存放在 [`.agents/skills/`](.agents/skills/) 目录下：

| 技能 | 核心用途 | 文档路径 |
|------|----------|---------|
| **skill-creator** | 技能开发工具链：创建技能、编写触发评测集 (evals)、自动优化触发词 | [.agents/skills/skill-creator/](.agents/skills/skill-creator/) |
| **task-execution-summary** | 任务执行总结：从对话历史提取信息，生成标准化、结构化的 10 章复盘报告 | [.agents/skills/task-execution-summary/](.agents/skills/task-execution-summary/) |

> 💡 **提示**：技能的触发描述优化、Windows 兼容性修复等历史迭代记录，均归档于 [`.agents/docs/superpowers/`](.agents/docs/superpowers/) 下的专属目录中。

## � 版本更新日志

本项目已建立基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 的分层变更日志系统。

- **最新版本**：请查阅 [项目级更新日志 (2026-05)](tests/project_changelogs/CHANGELOG_2026-05.md)。
- **核心迭代**：近期重点优化了 `skill-creator` 的 Windows 跨平台兼容性，并发布了 `task-execution-summary` v2.4 核心契约。
- **全量日志**：请访问根目录下的 [CHANGELOG.md](CHANGELOG.md) 获取全局索引。

## 🤝 贡献规范

我们欢迎任何旨在提升人机协同效率的贡献！参与贡献前请注意：

1. **遵循 TDD 流程**：提交新的 AI 自动化脚本前，必须包含类似 `test_windows_compat.py` 的跨平台验证用例。
2. **遵守文件隔离**：技术方案设计文档 (Spec) 与复盘报告 (Retrospective) 必须放入 `.agents/docs/superpowers/`，严禁污染 `docs/` 目录。
3. **提交 PR**：请参考 `.agents/workflows/pr-review.md` 中的代码审查规范。

详细的贡献指南请参考：[📖 贡献文档](docs/contributing.md)

## 📫 联系方式

- **Issue 追踪**：[GitHub Issues](https://github.com/xinetzone/tao/issues)
- **文档站点**：[AgentForge 官方文档](https://taolib.readthedocs.io)

---
<div align="center">
  <i>基于 AgentForge 引擎构建，让人与 AI 的协作如丝般顺滑。</i>
</div>
