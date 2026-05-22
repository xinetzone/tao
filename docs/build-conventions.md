# 文档构建约定

本项目采用基于 [Invoke](https://www.pyinvoke.org/) 的文档构建系统，以实现跨平台一致性和更清晰的任务管理，彻底废弃了传统的 `Makefile` 和 `make.bat`。

## 环境准备

文档构建前，推荐先用 `mise` 收敛工具版本，再用 `uv` 同步 Python 依赖：

```bash
# 首次使用先信任项目配置
mise trust

# 仓库根目录 `mise.toml` 已声明工具链，直接安装即可
mise install

# 同步文档依赖
mise run install-docs-deps
```

如果你需要额外的外部工具或一键完成环境初始化，请回到仓库根目录运行：

```bash
mise run init
```

完成后再进入 `docs/` 目录执行构建命令。

## 构建命令

所有文档构建任务统一收口在 `docs/tasks.py` 文件中，推荐在 `docs/` 目录下执行以下命令：

### 获取帮助信息

查看所有支持的文档构建目标和命令：

```bash
# 在仓库根目录
mise run docs-html
```

### 构建 HTML 文档

构建本地 HTML 文档站点：

```bash
mise run docs-html
```
或者在 `docs/` 目录下手动执行：
```bash
uv run invoke build --target html
```
> **注意**：`mise` 负责编排环境与入口，实际构建仍复用 `docs/tasks.py` 中的 `invoke` 任务。

### 清理构建产物

清理之前构建生成的静态文件缓存（对应原 `make clean`）：

```bash
uv run invoke clean
```

### 检查链接有效性

检查文档中包含的所有外部链接是否可用：

```bash
mise run docs-linkcheck
```

### 运行文档测试

执行文档中包含的代码片段测试：

```bash
uv run invoke doctest
```

## 目录与配置

- **`docs/tasks.py`**：定义了所有的 `invoke` 任务，基于 `sphinx-build -M` 模式封装。
- **`docs/conf.py`**：Sphinx 核心配置，动态读取项目版本号等元信息。
- **`docs/_config.toml`**：提供与 Jupyter Book 或 MyST 兼容的额外配置。

通过这些统一的配置与命令，无论是本地开发还是 GitHub Actions 的 CI/CD 流水线，都共享完全相同的构建链路。

## 升级建议

当文档构建依赖、Python 版本或 `mise` 本体发生升级时，建议按以下顺序处理：

```bash
mise self-update
mise install --force
mise run install-docs-deps
```

如果升级涉及 Sphinx 或主题版本，请补跑一次以下命令验证：

```bash
uv run invoke html
uv run invoke linkcheck
```

## 常见排障

- **`invoke` 或 `sphinx-build` 找不到**：通常是 `mise run install-docs-deps` 尚未执行，或当前 Shell 未使用 `mise` 激活后的 Python/uv。
- **进入仓库后工具版本不对**：先运行 `mise trust`，再用 `mise doctor` 和 `mise current` 检查当前生效版本。
- **文档依赖升级后构建异常**：执行 `mise install --force` 与 `mise run install-docs-deps`，必要时清理 `_build/` 后重试。
- **Windows 下 PowerShell 命令无法识别**：确认 `$PROFILE` 中已配置 `(& mise activate pwsh) | Out-String | Invoke-Expression`，然后重开终端。
