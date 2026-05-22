# 🤝贡献规范

## 贡献与扩展

欢迎提交代码、文档、规则与技能资产相关的改进。在开始贡献前，请先完成 `mise` 优先的开发环境准备。

## 开发环境

本项目推荐使用 "`mise` 管理工具层，`uv` 管理 Python 依赖层" 的方式完成本地接入：

```bash
mise trust
mise install
mise run sync
```

如需安装额外 CLI 或一键初始化，请运行：

```bash
mise run init
```

## 提交前检查

建议在提交前至少完成以下检查：

```bash
mise run test
uv run ruff check .
mise run fmt
```

如果本次修改涉及文档，还应在 `docs/` 目录下执行：

```bash
mise run docs-html
```

## 环境与版本升级约定

如果你的改动涉及 Python、`uv` 或其他开发工具版本，请遵循以下原则：

1. 优先更新 `mise` 侧的工具声明，确保本地与 CI 共用同一套版本基线。
2. 再同步 `pyproject.toml`、脚本、README 与 `docs/` 中的人类文档说明。
3. 升级后执行 `mise install --force` 与 `mise run sync`。
4. 至少补跑测试、Lint 与文档构建，确认没有环境漂移。

## 常见排障

- **命令与文档不一致**：先检查当前分支是否已更新到最新的 `mise` 方案，再执行 `mise doctor`。
- **工具版本漂移**：运行 `mise current`、`mise install --force`，然后重新执行 `mise run sync`。
- **新同事无法复现环境**：优先检查是否漏掉了 Shell 激活、`mise trust` 或 `mise run init`。
- **只想改文档或规则**：也建议先完成最小环境准备，至少确保 `python`、`uv` 与文档构建链路可用。

## 扩展建议

您可以根据团队的需要，在 `.agents/` 目录下添加更多的自定义规范，并在 `AGENTS.md` 中注册路由。例如：
- 添加 `database.md` 规范数据库设计。
- 添加 `testing.md` 规范测试用例编写。
