# 文档构建约定

本项目采用基于 [Invoke](https://www.pyinvoke.org/) 的文档构建系统，以实现跨平台一致性和更清晰的任务管理，彻底废弃了传统的 `Makefile` 和 `make.bat`。

## 环境准备

本项目的依赖管理由 `uv` 统一处理，确保已安装 `uv`，然后在项目根目录下运行以下命令安装包含文档构建工具的依赖：

```bash
uv sync --group docs
```

或者使用 `invoke` 或 `uv run invoke` 在 `docs` 目录下执行构建任务。

## 构建命令

所有文档构建任务统一收口在 `docs/tasks.py` 文件中，推荐在 `docs/` 目录下执行以下命令：

### 获取帮助信息

查看所有支持的文档构建目标和命令：

```bash
# 在 docs/ 目录下
uv run invoke help
```

### 构建 HTML 文档

构建本地 HTML 文档站点：

```bash
uv run invoke build html
```
或者
```bash
uv run invoke html
```
> **注意**：我们增加了针对常见目标的快捷任务，如 `html`, `clean`, `linkcheck`, `doctest`。

### 清理构建产物

清理之前构建生成的静态文件缓存（对应原 `make clean`）：

```bash
uv run invoke clean
```

### 检查链接有效性

检查文档中包含的所有外部链接是否可用：

```bash
uv run invoke linkcheck
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
