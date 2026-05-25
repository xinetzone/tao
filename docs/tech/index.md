# 📦 技术文档

本目录集中承载 **AgentForge 本项目** 的技术相关文档。全部项目技术资产（包含 API 参考、集成指南、部署流程与变更日志）均位于本目录下，与同级 [通用知识](../general/index.md)（传统文化、数学等）完全隔离。

```{toctree}
:maxdepth: 2
:caption: 技术文档

intro
quickstart
features
github-app-token-override
integration-guide
api/taolib/index
deploy
build-conventions
contributing
changelog
jupyterlite
```

:::{note}
`api/taolib/` 目录由 sphinx-autoapi 在构建时从源码自动生成，不存在于版本库中。
:::

## 目录清单

| 路径 | 说明 |
|---|---|
| `intro.md` | 项目介绍与定位 |
| `quickstart.md` | 环境初始化与首次接入 |
| `features.md` | 核心功能与 `.agents/` 详解 |
| `github-app-token-override.md` | GitHub App Token 覆盖头学习笔记 |
| `integration-guide.md` | 外部项目集成指南 |
| `api/taolib/` | sphinx-autoapi 自动生成的 API 参考 |
| `deploy.md` | 文档托管、CI/CD 与发布流程 |
| `build-conventions.md` | PDM / uv / mise 构建约定 |
| `contributing.md` | PR 流程、代码审查与测试要求 |
| `changelog.md` + `changelogs/` | 项目级变更索引与月度/技能变更镜像页 |
| `jupyterlite.md` | JupyterLite 集成说明 |

## 边界

不放置：传统文化、数学、通用知识等与本项目源码/工程化无直接关系的内容，请见同级目录 [`../general/`](../general/index.md)。

## 接入约定

> 新增技术文档时：
>
> 1. 将文件放入本目录；
> 2. 在本 `index.md` 的 `toctree` 中追加对应文档名（无需 `tech/` 前缀）；
> 3. 如需反向链接到 `../general/` 中的文档，使用相对路径（如 `../general/philosophy/tao-minimalist-principles.md`）。
