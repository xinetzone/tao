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

## Docstring 风格规范（AutoAPI 友好）

本项目使用 [sphinx-autoapi](https://sphinx-autoapi.readthedocs.io/) 静态扫描 `src/taolib/` 自动生成 API 文档，构建在 CI 中以 `-W --keep-going` 严格模式执行。为保持 0-warning 基线，请遵守以下三条规则：

1. **属性说明使用 PEP 257 内联 docstring**，不要使用 `Attributes:` 段或 `:ivar:` 字段。AutoAPI 会从源码静态生成 `.. py:attribute::`，与 Napoleon 处理的 `Attributes:` 段叠加会触发 `duplicate object description` 警告。

   ✅ 正确写法：

   ```python
   @dataclass(slots=True)
   class GitHubAppSettings:
       """GitHub App 的全局配置聚合。"""

       app_id: str
       """GitHub App 的 App ID。"""

       installation_id: str
       """默认的安装实例 ID。"""
   ```

   ❌ 错误写法（会触发重复声明警告）：

   ```python
   @dataclass(slots=True)
   class GitHubAppSettings:
       """GitHub App 的全局配置聚合。

       Attributes:
           app_id: GitHub App 的 App ID。
           installation_id: 默认的安装实例 ID。
       """
       app_id: str
       installation_id: str
   ```

2. **inline literal 不能紧贴中文标点**。docutils 仅识别 ASCII 空格与英文标点为 `` ``...`` `` 的合法 end-string，紧贴中文 `：`、`、`、`。` 会触发 `Inline literal start-string without end-string`。

   ✅ 正确：`` ``GITHUB_APP_ID`` 必填，App ID。``（字面量后接 ASCII 空格）

   ❌ 错误：`` ``GITHUB_APP_ID`` (默认 ``auto``)：必填。``（嵌套字面量后紧贴中文冒号）

3. **不要启用 `imported-members`**。`taolib.github_app/__init__.py` 已对子模块对象做 re-export，启用后 AutoAPI 会在包级页面再次声明，造成大面积重复。

详细规范、典型反例与 lint 落地建议详见仓库内的 `.agents/docs/references/autoapi-docstring-style.md`（仅向 AI 智能体开放，不纳入 Sphinx 文档站点）。

## 扩展建议

您可以根据团队的需要，在 `.agents/` 目录下添加更多的自定义规范，并在 `AGENTS.md` 中注册路由。例如：
- 添加 `database.md` 规范数据库设计。
- 添加 `testing.md` 规范测试用例编写。
