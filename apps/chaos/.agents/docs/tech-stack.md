# 技术栈速览

本文档列出 AgentForge 项目使用的主要技术组件与工具链。

| 组件 | 技术 | 说明 |
|------|------|------|
| Python 包管理 | `uv` | 统一虚拟环境与依赖管理 |
| 构建后端 | `pdm-backend` + SCM 动态版本 | `pyproject.toml` 中配置 |
| 版本管理 | `mise` | 工具链版本统一管理（Python、uv、ruff 等） |
| Lint / Format | `ruff` | 统一替代 flake8/isort/black |
| 文档构建 | Sphinx | 零警告策略 |
| CI/CD | GitHub Actions + GitCode | 双平台流水线 |
| 容器化 | Podman / Docker | 评估环境与部署 |
| 子模块管理 | Git Submodule | rebirth/ 下三个 WorldSprout 仓库均跟踪 main 分支 |
