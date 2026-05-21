# AgentForge

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

> AI 驱动开发模板 (AI-Driven Development Template)

这是一个面向未来的、为 AI 智能体高度优化的项目脚手架/模板。通过内置的“契约”系统，它可以确保 AI 助手在辅助开发时遵循统一的规范和最佳实践。

<!-- end-doc-include -->

## 🛠️ 技能管理

本项目将 AI 技能 (Skills) 纳入版本管理，实现技能的集中维护、评测和优化。所有技能统一存放在 [.agents/skills/](.agents/skills/) 目录下：

| 技能 | 用途 |
|------|------|
| [skill-creator](.agents/skills/skill-creator/) | 技能开发工具链：创建技能、编写触发评测集 (evals)、自动优化 description 触发词 |
| [task-execution-summary](.agents/skills/task-execution-summary/) | 任务执行总结报告生成器：从对话历史中提取关键信息，生成结构化复盘报告 |

技能的触发描述优化、Windows 兼容性修复等迭代记录见 `.agents/docs/superpowers/` 下的设计文档和复盘报告。

## 📚 文档导航

为了提供更清晰的指引，本项目文档已进行模块化拆分。请访问 [📖 文档目录](docs/index.md) 获取详细指引。

