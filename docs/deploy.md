# 📦部署指南

当前模板尚未包含具体业务服务的发布脚本，但环境准备、构建验证与发布前检查仍建议统一采用 `mise` 优先方案。

## 部署前环境准备

无论是本地演练还是 CI/CD，建议先完成以下步骤：

```bash
mise trust
mise install
mise run sync
```

如需额外外部工具，请在仓库根目录执行：

```powershell
pwsh -File scripts/init.ps1
```

## 本地发布前验证

在缺少正式部署流水线之前，建议把以下命令视为最小发布前检查：

```bash
mise run test
uv run ruff check .
```

```bash
mise run docs-html
mise run docs-linkcheck
```

这些检查至少可以确保：

- Python 运行时与 `uv` 版本符合项目基线。
- 测试、Lint 与文档构建链路在当前环境中可执行。
- 人类文档与发布前说明没有明显断链。

## 升级策略

如果部署相关任务需要升级 Python、`uv` 或其他工具，推荐按以下顺序操作：

```bash
mise self-update
mise install --force
mise run sync
```

升级后应重新执行上方的发布前验证命令，避免出现“本地能跑、CI 失败”或“CI 能跑、本地漂移”的情况。

## 常见排障

- **CI 与本地版本不一致**：先确认双方都以 `mise` 作为工具版本入口，不要混用独立安装的 Python/uv。
- **部署前构建失败**：优先执行 `mise doctor`、`mise install --force` 与 `mise run sync`。
- **文档构建或链接检查失败**：先在 `docs/` 目录重新执行 `invoke html` 和 `invoke linkcheck`，确认是否为依赖缺失或外链波动。
- **额外 CLI 缺失**：运行 `pwsh -File scripts/init.ps1 -CheckOnly` 检查本地缺失项。

后续如果仓库补充正式的发布脚本、容器镜像构建或云端部署步骤，应继续沿用同一套 `mise` 工具声明，避免再次回到多处硬编码版本的状态。
