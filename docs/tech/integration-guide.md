# 🔗 外部项目集成指南

本文面向希望在其他项目中复用 AgentForge / `taolib` 的开发者，说明如何直接使用本项目的 Python 能力、命令行工具，以及如何在项目之外集成本项目的 AI 协作体系。

## 1. 集成边界

AgentForge 同时具备两种身份：

```{mermaid}
flowchart TD
    A["AgentForge / tao 仓库"] --> B["Python 包：taolib"]
    A --> C["AI 协作工程模板"]
    B --> D["GitHub App Token 管理能力"]
    B --> E["CLI：taolib-github-app"]
    C --> F["AGENTS.md 全局契约"]
    C --> G[".agents 规则/技能/知识资产"]
    C --> H["mise + uv 跨平台工程环境"]
```

因此，外部项目接入时应先判断目标：

| 目标 | 推荐方式 | 引入内容 |
|---|---|---|
| 只想使用 GitHub App token 管理 | 依赖 `taolib[github-app]` | Python API |
| 想在 CI 或脚本中获取 token | 安装后调用 CLI | `taolib-github-app` |
| 想让 AI 更好理解项目 | 迁移 AI 契约 | `AGENTS.md` 与必要 `.agents/rules/` |
| 想系统沉淀 AI 协作规则 | 引入 `.agents/` 体系 | rules / workflows / docs / scripts |
| 想创建 AI 原生项目 | 以本仓库为模板 | 全套工程结构 |

## 2. 作为 Python 包使用

### 2.1 从 PyPI 安装

如果外部项目只需要运行时代码，推荐把本项目作为依赖安装：

```bash
uv add taolib
```

如果需要 GitHub App 相关能力，安装可选依赖：

```bash
uv add "taolib[github-app]"
```

### 2.2 从 Git 仓库安装

如果需要使用尚未发布到 PyPI 的最新能力，可以直接依赖 Git 仓库：

```bash
uv add "taolib[github-app] @ git+https://github.com/xinetzone/tao.git"
```

也可以锁定分支或标签：

```bash
uv add "taolib[github-app] @ git+https://github.com/xinetzone/tao.git@main"
```

```bash
uv add "taolib[github-app] @ git+https://github.com/xinetzone/tao.git@v0.6.0"
```

### 2.3 本地路径联调

如果另一个项目和 AgentForge 在同一台机器上开发，可以使用本地路径依赖：

```bash
uv add "taolib[github-app] @ file:///path/to/AgentForge"
```

适用场景包括：

- 同时修改 AgentForge 和外部业务项目。
- 先在外部项目验证本项目的新能力。
- 暂时不发布 PyPI 版本。

## 3. 在 Python 代码中集成 GitHub App 能力

### 3.1 环境变量

外部项目需要准备以下环境变量：

```bash
GITHUB_APP_ID=你的 GitHub App ID
GITHUB_APP_INSTALLATION_ID=安装实例 ID
GITHUB_APP_PRIVATE_KEY_FILE=私钥文件路径
```

也可以直接传入私钥内容：

```bash
GITHUB_APP_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----..."
```

可选变量：

```bash
GITHUB_API_URL=https://api.github.com
GITHUB_APP_TOKEN_STRATEGY=auto
GITHUB_APP_TOKEN_EAGER_REFRESH_SECONDS=90
GITHUB_APP_ALLOW_HEADER_FALLBACK=true
```

建议优先使用 `GITHUB_APP_PRIVATE_KEY_FILE`，不要把私钥明文写入代码、日志或配置仓库。

### 3.2 Python API 示例

```python
import asyncio

from taolib.github_app import (
    GitHubAppClient,
    GitHubAppSettings,
    GitHubInstallationTokenManager,
    InMemoryInstallationTokenCache,
    InstallationTokenRequest,
)


async def main():
    settings = GitHubAppSettings.from_env()
    client = GitHubAppClient(
        app_id=settings.app_id,
        private_key=settings.private_key,
        api_url=settings.api_url,
    )
    manager = GitHubInstallationTokenManager(
        client=client,
        cache=InMemoryInstallationTokenCache(),
        settings=settings,
    )

    result = await manager.get_token(
        InstallationTokenRequest(
            installation_id=settings.installation_id,
            permissions={},
            repositories=[],
            strategy=settings.default_strategy,
        )
    )

    print(result.token)


asyncio.run(main())
```

令牌管理器内部负责：

- token 缓存；
- 提前刷新窗口；
- Singleflight 并发去重；
- GitHub Cloud / GHES 环境差异；
- stateful / stateless token 策略降级。

### 3.3 PyGithub 适配

如果外部项目已经使用 PyGithub，可以优先复用 `taolib.github_app` 暴露的适配器：

```python
from taolib.github_app import build_pygithub_client
```

这种方式适合在保留现有 PyGithub 调用逻辑的同时，把 GitHub App token 的签发、刷新、缓存和降级逻辑交给 `taolib`。

## 4. 作为命令行工具使用

安装 `taolib[github-app]` 后，可以直接使用命令行入口：

```bash
taolib-github-app profile
```

获取安装令牌：

```bash
taolib-github-app token
```

指定 installation id：

```bash
taolib-github-app token --installation-id 123456
```

检查状态：

```bash
taolib-github-app status --installation-id 123456
```

CLI 适合：

- CI/CD 中动态获取 GitHub App token。
- shell 脚本中接入。
- 非 Python 项目临时调用。
- 作为 GitHub API 自动化任务的前置凭据获取器。

## 5. 集成 AI 协作体系

如果目标不是调用 `taolib` 代码，而是把 AgentForge 的 AI 协作体系集成到另一个项目，可以按以下层级迁移。

### 5.1 轻量集成

适合已有项目，不想大规模调整目录结构。

建议迁移：

```text
AGENTS.md
.agents/rules/
.agents/workflows/
.agents/README.md
```

外部项目的 `AGENTS.md` 应保留核心路由思想：

```{mermaid}
flowchart TD
    A["外部项目 AGENTS.md"] --> B["全局协作规则"]
    A --> C["按任务类型路由"]
    C --> D["前端规则"]
    C --> E["后端规则"]
    C --> F["Python 规则"]
    C --> G["文档治理规则"]
```

该方式适合：

- 让 AI 助手进入项目后知道先读什么。
- 统一文档边界。
- 统一开发约定。
- 减少每次和 AI 重复解释项目规则的成本。

### 5.2 标准集成

适合希望长期维护 AI 协作资产的项目。

建议迁移结构：

```text
.agents/
  README.md
  rules/
  workflows/
  scripts/
  docs/
    references/
    integrations/
    issue-patterns/
    superpowers/
```

迁移后，外部项目可以形成：

- `.agents/rules/`：高频执行规则。
- `.agents/workflows/`：代码审查、发布、调试等工作流。
- `.agents/scripts/`：AI 可调用的项目自动化脚本。
- `.agents/docs/references/`：稳定技术知识。
- `.agents/docs/integrations/`：外部知识和项目实现之间的映射。
- `.agents/docs/superpowers/`：长期方案、设计、复盘沉淀。

### 5.3 完整模板化集成

适合新项目或准备重构工程治理的项目。

可以以本项目为模板，保留：

```text
AGENTS.md
.agents/
.trae/
docs/
mise.toml
pyproject.toml
tasks.py
.pre-commit-config.yaml
.github/workflows/
```

然后替换：

- 包名。
- 项目描述。
- Python 版本。
- README。
- 业务代码目录。
- CI 发布配置。
- 文档站配置。

## 6. 推荐落地路径

对已有外部项目，推荐分三步接入：

```{mermaid}
flowchart TD
    A["第一步：运行时接入"] --> B["安装 taolib[github-app]"]
    B --> C["用 Python API 或 CLI 验证 token 获取"]
    C --> D["第二步：AI 协作接入"]
    D --> E["复制 AGENTS.md 与必要 .agents/rules"]
    E --> F["第三步：工程治理接入"]
    F --> G["迁移 mise.toml / tasks.py / CI / 文档结构"]
```

### 6.1 先验证代码能力

```bash
uv add "taolib[github-app]"
```

配置 GitHub App 环境变量后运行：

```bash
taolib-github-app profile
taolib-github-app token
```

### 6.2 再接入 AI 协作规则

复制：

```text
AGENTS.md
.agents/rules/context-economy.md
.agents/rules/documentation.md
.agents/rules/python.md
```

然后根据外部项目实际情况删改。

### 6.3 最后统一工程工具链

如果外部项目愿意采用本项目的工程管理方式，再引入：

```text
mise.toml
tasks.py
.pre-commit-config.yaml
```

并在外部项目中统一使用：

```bash
mise run init
mise run check-env
mise run test
mise run lint
```

## 7. 注意事项

1. 不要跨项目复制密钥。
   - GitHub App 私钥应使用环境变量或密钥管理系统。
   - 推荐使用 `GITHUB_APP_PRIVATE_KEY_FILE`。
   - 不要提交 `.pem`、`.env`、token 到仓库。
2. 不要依赖内部模块。
   - 外部项目应优先从 `taolib.github_app` 导入公共接口。
   - 不建议直接依赖 `_builders.py`、`_parsers.py` 等 CLI 内部模块。
3. 区分 GitHub Cloud 与 GHES。
   - `GITHUB_API_URL=https://api.github.com` 会被识别为 GitHub Cloud。
   - GHES 通常是 `https://your-ghes-host/api/v3`。
   - GHES 下 stateless token 覆盖头会自动降级。
4. CLI 输出面向诊断和脚本集成。
   - 如果业务代码需要真实 token，建议直接用 Python API。
5. 外部项目若只想复用模板，不一定需要安装 `taolib`。
   - AI 协作体系和 Python 包能力是两条线。
   - 只集成 `AGENTS.md` / `.agents` 不要求引入运行时代码。

## 8. 总结

其他项目可以按四种方式复用本项目：

- 作为库：安装 `taolib[github-app]`，在 Python 中调用 `taolib.github_app`。
- 作为工具：安装后调用 `taolib-github-app profile/token/status`。
- 作为模板：迁移 `AGENTS.md`、`.agents/`、`mise.toml`、`tasks.py` 等工程治理资产。
- 作为 AI 协作规范：把“全局契约 + 按需路由 + 文档边界 + 工具链统一”迁移到外部项目。
