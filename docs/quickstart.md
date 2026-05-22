# 🚀 快速开始

## 适用对象

本文面向第一次接入 AgentForge 的人类开发者，默认采用 "`mise` 管理工具层 + `uv` 管理 Python 依赖层" 的方式准备环境。

## 1. 克隆仓库

```bash
git clone https://github.com/xinetzone/tao.git
cd tao
```

## 2. 安装 `mise`

推荐按操作系统选择以下命令：

```powershell
# Windows
winget install jdx.mise

# 或
scoop install mise
```

```bash
# macOS
brew install mise

# Linux / macOS 通用
curl https://mise.run | sh
```

安装完成后，请为当前 Shell 添加激活命令。

```powershell
# PowerShell
Add-Content $PROFILE '(& mise activate pwsh) | Out-String | Invoke-Expression'
```

```bash
# Bash
echo 'eval "$(mise activate bash)"' >> ~/.bashrc

# Zsh
echo 'eval "$(mise activate zsh)"' >> ~/.zshrc
```

重新打开终端后，先验证本体状态：

```bash
mise --version
mise doctor
```

## 3. 初始化项目环境

进入仓库后，推荐按以下顺序完成初始化：

```bash
# 首次使用前信任项目配置
mise trust

# 根据根目录 `mise.toml` 安装声明的全部工具
mise install
```

然后同步项目依赖：

```bash
mise run sync
```

如需安装仓库依赖的额外外部工具或一键完成环境初始化，请执行：

```bash
mise run init
```

> 初始化流程基于 Python `invoke` 实现，原生跨平台，**Windows / Linux / macOS 均可直接运行**。

## 4. 验证接入结果

建议至少执行以下命令：

```bash
mise run check-env
mise run test
```

如果需要构建文档站，再执行：

```bash
mise run docs-html
mise run docs-linkcheck
```

## 5. 日常开发入口

完成环境准备后，可以按以下路径开始使用本模板：

1. 阅读 `README.md` 了解项目入口、目录导航与环境要求。
2. 打开 `AGENTS.md` 查看 AI 协作契约与任务路由。
3. 按需完善 `.agents/rules/` 下的规范文档。
4. 在支持 Workspace Rules / Instructions 的 AI IDE 中开始协作开发。

## 6. 升级流程

当你需要刷新本地工具链或跟进团队升级时，建议按以下顺序执行：

```bash
# 升级 mise 本体
mise self-update

# 重新安装项目声明的工具
mise install --force

# 刷新 Python 依赖
mise run sync
```

如果项目升级了 Python、`uv`、Node.js 或其他工具版本，请先更新根目录 `mise.toml` 中的精确版本，再执行 `mise install --force`，最后补跑 `mise run check-env`、`mise run test` 与 `mise run docs-html` 做回归验证。

## 7. 常见排障

- **`mise` 命令不可用**：确认已重开终端，并检查 Shell 配置文件中是否存在 `mise activate`。
- **进入仓库后版本未切换**：优先执行 `mise trust`，然后运行 `mise doctor`。
- **`uv` 或 `python` 版本不符合预期**：执行 `mise current`、`mise ls`，必要时重新运行 `mise install --force`。
- **外部工具缺失**：运行 `mise run init-check` 查看缺失项（跨平台，Windows/Linux/macOS 均可使用）。
- **文档构建失败**：先执行 `mise run install-docs-deps`，再运行 `mise run docs-html` 或进入 `docs/` 目录手动调用 `uv run invoke`。

如果问题仍未解决，请继续阅读 `docs/build-conventions.md`、`docs/contributing.md` 与 `docs/deploy.md` 中的环境说明。
