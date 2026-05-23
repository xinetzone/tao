# 📦部署指南

当前模板尚未包含具体业务服务的发布脚本，但环境准备、构建验证与发布前检查仍建议统一采用 `mise` 优先方案。

## 部署前环境准备

无论是本地演练还是 CI/CD，建议先完成以下步骤：

```bash
mise trust
mise install
mise run sync
```

如需额外外部工具或一键初始化，请在仓库根目录执行：

```bash
mise run init
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
- **额外 CLI 缺失**：运行 `mise run init-check` 检查本地缺失项（跨平台，Windows/Linux/macOS 均可使用）。

后续如果仓库补充正式的发布脚本、容器镜像构建或云端部署步骤，应继续沿用同一套 `mise` 工具声明，避免再次回到多处硬编码版本的状态。

## AtomGit 平台使用

本项目同时支持 AtomGit 代码托管平台。使用方式如下：

1. 在 [AtomGit](https://atomgit.com) 创建项目仓库
2. 将本地仓库关联到 AtomGit 远程地址：

   ```bash
   git remote add atomgit https://atomgit.com/<your-namespace>/<repo-name>.git
   ```

3. 推送代码：

   ```bash
   git push atomgit main
   ```

4. 日常协作（拉取、推送、分支管理）使用标准 Git 命令即可，与 GitHub 流程一致

## GitCode CI/CD

项目已集成 GitCode Pipeline CI/CD 能力，配置文件位于 `.gitcode/workflows/ci.yml`。

**触发规则**：
- 推送到 `main` 分支时自动触发
- 创建/更新 Pull Request 到 `main` 时自动触发
- 支持在 GitCode 控制台手动触发（workflow_dispatch）

**流水线阶段**：
1. **lint**（静态代码扫描）：通过 `ruff check` 检查代码规范
2. **test**（单元测试）：运行 `pytest` 全量测试并生成覆盖率报告（要求 >= 80%）
3. **build**（构建编译）：使用 `uv build` 构建 Python 包

**维护说明**：
- 修改 CI 流程请编辑 `.gitcode/workflows/ci.yml`
- CI 使用 GitCode EulerOS runner（`euleros-2.10.1`）
- 依赖管理通过 `uv` 工具，Python 版本要求 3.14+
- 如有新增测试目录或修改覆盖率阈值，需同步更新 CI 配置
