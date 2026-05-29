# 🤖 AgentForge

> **AI Agent 协作基础设施** — 以 Ψ=Ψ(Ψ) 为第一性原理的智能体协作世界，遵循混沌→萃取→脱胎的双态孵化模型。

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

## 这是什么

AgentForge 是一个 **AI Agent 项目约定的开放标准制定与示范实现仓库**。它的独特之处在于采用 **双态架构**：

```
混沌态 (Chaos)                    脱胎态 (Rebirth)
apps/chaos/         持续萃取      rebirth/
  原始孵化器        ──────────▶    社区标准
  自由探索、试错                   精炼、去个人化
  哲学内核、实验代码               WorldSprout 开放协议
```

- **`apps/chaos/`** — 一切未精炼的原始探索：哲学内核（Ψ=Ψ(Ψ)、道德经）、实验性代码、个人知识库、技能生态。信息在此自由生长。
- **`rebirth/`** — 从 chaos 持续萃取、去个人化后的精炼产出，以 git submodule 链接到 [WorldSprout](https://github.com/worldsprout) 组织，作为可独立发布的社区开放标准。

## AGENTS.md 开放标准

`AGENTS.md` 是一个独立的社区开放标准——只需在项目根目录放一个 `AGENTS.md` 文件，AI 工具就能自动读取项目指令。OpenAI Codex、Google Jules、GitHub Copilot、Cursor 等 30+ 工具原生支持，**零依赖**。

AgentForge 在此基础上提供渐进可选扩展（`.agents/` 目录、`world.toml`、SKILL.md、constraints.toml）。二者关系类比：AGENTS.md ≈ Markdown，AgentForge ≈ CommonMark + GFM 扩展。

详见根目录 [`AGENTS.md`](AGENTS.md)（本项目的 AI 智能体全局契约）。

## 快速开始

### 面向开发者

```bash
cd apps/chaos

# 安装依赖
uv sync --extra docs

# 运行测试
uv run pytest

# 构建文档
uv run invoke docs
```

### 面向 AI 协作者

直接读取根目录 [`AGENTS.md`](AGENTS.md)，它会按任务类型路由到正确的子项目规范。

### 面向 WorldSprout 贡献者

```bash
cd rebirth

# 拉取所有子模块最新代码
git submodule update --remote

# 进入参考实现独立开发
cd worldsprout
```

## 仓库结构

```
AgentForge/
├── AGENTS.md              ← AI 智能体全局契约（最高优先级入口）
├── README.md              ← 本文件：人类开发者入口
├── LICENSE                ← Apache 2.0
│
├── apps/chaos/            ← 混沌态：原始孵化器
│   ├── AGENTS.md          ← chaos 子项目路由
│   ├── .agents/           ← 规则/技能/工作流/角色
│   ├── specs/             ← AgentForge Spec v0.2
│   └── src/taolib/        ← world CLI + 参考实现
│
├── docs/                  ← 人类文档（tech/ + general/ 双轨）
├── .github/workflows/     ← CI/CD 流水线
│
└── rebirth/               ← 脱胎态：WorldSprout 标准（git submodule）
    ├── worldsprout/       → github.com/worldsprout/worldsprout
    ├── spec/              → github.com/worldsprout/spec
    └── .github/           → github.com/worldsprout/.github
```

## 核心特性

- **三层分离架构** (AgentForge Spec v0.2)：Layer 1 项目协议（零前提采用）→ Layer 2 协作协议（多智能体语义）→ Layer 3 世界运行时（示范实现）
- **哲学驱动工程**：Ψ=Ψ(Ψ) 元公理 + 马王堆帛书《道德经》→ 极简设计原则 → 技术实施方案
- **约束即代码**：`constraints.toml` 声明式协议 + CI 自动校验
- **World CLI 工具链**：`world init` 脚手架 / `world guide` 诊断推荐 / `world fragment` 打包分发
- **GitHub App 令牌服务**：自动化 Token 管理与事件处理
- **双平台 CI**：GitHub Actions + GitCode 流水线，Sphinx 文档零警告

## 技术栈

| 组件 | 技术 |
|------|------|
| 语言 | Python 3.14+ |
| 包管理 | uv |
| 构建 | pdm-backend + SCM 动态版本 |
| Lint | ruff |
| 文档 | Sphinx |
| CI/CD | GitHub Actions + GitCode |
| 容器化 | Podman / Docker |

## 相关链接

- [WorldSprout 组织](https://github.com/worldsprout) — 脱胎后的社区开放标准
- [taolib PyPI](https://pypi.org/project/taolib/) — Python 参考实现包
- [文档](https://taolib.readthedocs.io/) — 完整技术文档与哲学体系
- [AGENTS.md 开放标准](https://agents.md/) — 社区驱动的 AI 指令标准

## 许可证

Apache License 2.0 © [LICENSE](LICENSE)

