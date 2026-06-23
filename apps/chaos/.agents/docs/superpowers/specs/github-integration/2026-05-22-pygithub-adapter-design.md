# PyGithub Adapter Layer Design

## Goal

在不破坏现有 GitHub App installation token 管理链路的前提下，为 `taolib.github_app` 增加一个可选的 `PyGithub` 适配层，使调用方可以在复用现有请求级覆盖头、环境降级、缓存和单飞刷新能力的同时，使用 `PyGithub` 提供的对象化 GitHub API 访问体验。

## Background

当前 `taolib.github_app` 已经具备以下能力：

- 使用 `PyJWT` 自行签发 App JWT
- 使用 `httpx` 调用 `POST /app/installations/{installation_id}/access_tokens`
- 按策略注入 `X-GitHub-Stateless-S2S-Token`
- 在 GHES 或未知环境中自动降级为无覆盖头模式
- 通过进程内缓存与 single-flight 避免并发刷新风暴

这些能力直接服务于本项目针对 GitHub 2026 请求级覆盖头能力所做的协议级控制需求。`PyGithub` 虽然提供了 GitHub App 与 installation authentication 能力，但其优势主要在于高层 API 对象访问，而不是对 installation token 请求头与异步刷新链路的精细控制。

因此，本次工作不尝试用 `PyGithub` 替换现有底层 HTTP 客户端，而是在其上方增加一层薄适配，使其成为“已有 installation token 的消费者”。

## Scope

- 将 `PyGithub` 加入 `project.optional-dependencies.github-app`
- 新增 `src/taolib/github_app/pygithub_adapter.py`
- 提供从 `GitHubInstallationTokenManager` 获取 installation token 并构造 `PyGithub` 客户端的统一入口
- 在 `src/taolib/github_app/__init__.py` 暴露适配层 API
- 新增聚焦单元测试，验证适配层不会绕过现有 manager 策略

## Non-Goals

- 不让 `PyGithub` 接管 installation token 的生成流程
- 不修改现有 `client.py` 与 `token_manager.py` 的职责边界
- 不新增文件缓存、分布式缓存或跨进程锁
- 不在本次增加新的 CLI 子命令
- 不实现 repo、issue、pull request 等更高层的业务封装

## Design Principles

1. 最小侵入：保留现有 token 管理链路，避免为了引入 SDK 而打散已验证的协议控制层。
2. 单一职责：`PyGithub` 只负责“拿到 token 之后的 GitHub 资源访问”，不负责 token 策略计算。
3. 显式依赖：适配层只依赖 `settings` 与 `manager`，不复制配置解析和缓存逻辑。
4. 可测试性：适配层通过 mock manager 进行单测，避免把真实 GitHub API 耦合进基础测试。
5. 可扩展性：后续若需要 repo / issue / PR 级封装，可在该层之上渐进增加，而不影响 token 核心层。

## Current Assessment

当前模块职责边界已经较为清晰：

- [client.py](file:///c:/Users/xinzo/OneDrive/Desktop/AI/Dao/spaces/AgentForge/src/taolib/github_app/client.py) 负责 JWT、HTTP 请求与响应解析
- [token_manager.py](file:///c:/Users/xinzo/OneDrive/Desktop/AI/Dao/spaces/AgentForge/src/taolib/github_app/token_manager.py) 负责策略分发、缓存、single-flight 与降级结果投影
- [config.py](file:///c:/Users/xinzo/OneDrive/Desktop/AI/Dao/spaces/AgentForge/src/taolib/github_app/config.py) 负责环境变量配置读取
- [test_client.py](file:///c:/Users/xinzo/OneDrive/Desktop/AI/Dao/spaces/AgentForge/tests/github_app/test_client.py) 和 [test_token_manager.py](file:///c:/Users/xinzo/OneDrive/Desktop/AI/Dao/spaces/AgentForge/tests/github_app/test_token_manager.py) 已覆盖关键行为

这意味着新增 `PyGithub` 支持的最佳位置不是替换 `client.py`，而是新增一个面向上层调用方的客户端工厂。

## Proposed Architecture

建议新增如下模块：

- `src/taolib/github_app/pygithub_adapter.py`

建议暴露如下接口：

- `PyGithubInstallationClientFactory`
- `build_pygithub_client()`

模块职责如下：

### `PyGithubInstallationClientFactory`

- 接收 `GitHubAppSettings` 与 `GitHubInstallationTokenManager`
- 对外提供异步方法，根据 `InstallationTokenRequest` 获取 installation token
- 使用返回的 token 构造 `PyGithub` 的 `Github` 客户端
- 保持为薄工厂，不承载额外缓存、重试或权限推导逻辑

### `build_pygithub_client()`

- 作为便捷函数，降低简单调用场景的接入成本
- 适用于仅需一次性创建客户端的场景
- 内部委托给工厂实现，避免出现两套逻辑

## API Sketch

建议接口形态如下：

```python
from github import Auth, Github

from taolib.github_app import (
    GitHubAppSettings,
    GitHubInstallationTokenManager,
    InstallationTokenRequest,
)


class PyGithubInstallationClientFactory:
    def __init__(
        self,
        settings: GitHubAppSettings,
        manager: GitHubInstallationTokenManager,
    ) -> None: ...

    async def create(self, request: InstallationTokenRequest) -> Github: ...


async def build_pygithub_client(
    settings: GitHubAppSettings,
    manager: GitHubInstallationTokenManager,
    request: InstallationTokenRequest,
) -> Github: ...
```

内部流程：

1. 适配层收到 `InstallationTokenRequest`
2. 调用 `manager.get_token(request)` 获取结构化 `InstallationTokenResult`
3. 使用 `result.token` 创建 `Auth.Token(result.token)`
4. 使用 `settings.api_url` 创建 `Github(auth=..., base_url=...)`
5. 返回可直接用于仓库、Issue、PR 等对象 API 的 `Github` 客户端

## Base URL Strategy

适配层必须沿用现有 `settings.api_url`，以保持云端与 GHES 行为一致：

- GitHub Cloud 使用 `https://api.github.com`
- GHES 使用类似 `https://github.example.com/api/v3`
- 未知环境保持调用方显式配置

这样做的目的是保证 `PyGithub` 客户端和 installation token 来源处于同一运行环境，避免出现“token 来自 GHES、客户端却请求 GitHub Cloud”的错配。

## Error Handling

适配层不新增复杂异常体系，但需保持错误来源清晰：

- 如果 `manager.get_token()` 失败，透传现有 `GitHubAppError` 子类
- 如果 `PyGithub` 构造参数不合法，直接抛出对应库异常
- 不在适配层吞掉 token 获取失败，也不做静默回退

这样可以保证调用方仍然通过现有 token 层获得完整的降级与诊断语义。

## Testing Strategy

新增测试文件：

- `tests/github_app/test_pygithub_adapter.py`

测试重点：

- 工厂会把传入的 `InstallationTokenRequest` 原样交给 `manager.get_token()`
- 工厂会使用 `settings.api_url` 创建 `Github` 客户端
- 工厂会消费 `manager` 返回的 token，而不是自行生成 token
- 便捷函数 `build_pygithub_client()` 与工厂行为一致

测试方法：

- 使用 `AsyncMock` 模拟 `manager.get_token()`
- 构造最小 `GitHubAppSettings`
- 断言返回对象为 `Github`
- 必要时检查内部 auth/base_url 是否符合预期

## Dependency Strategy

`PyGithub` 应并入现有 `github-app` 可选依赖组，而不是成为默认安装依赖：

```toml
[project.optional-dependencies]
github-app = [
  "httpx>=0.27,<1",
  "PyJWT[crypto]>=2.10,<3",
  "PyGithub>=2.5,<3",
]
```

这样安装 `taolib[github-app]` 即可同时获得现有 GitHub App token 管理能力与新的 `PyGithub` 适配层。

## Implementation Plan

建议按以下顺序实现：

1. 更新 `pyproject.toml`，将 `PyGithub` 纳入 `github-app` 可选依赖组
2. 新增 `src/taolib/github_app/pygithub_adapter.py`
3. 在 `src/taolib/github_app/__init__.py` 中导出新接口
4. 新增 `tests/github_app/test_pygithub_adapter.py`
5. 运行聚焦测试与诊断，确认未破坏现有 token 行为

## Risks

- `PyGithub` 内部实现可能对 `base_url`、认证对象或私有属性暴露方式有版本差异，因此测试应尽量基于公开行为而非深度依赖内部属性
- 如果未来希望让 `PyGithub` 深度参与 installation token 生命周期管理，可能与当前异步 manager 语义产生冲突
- 一旦后续扩展到 repo / issue / PR 业务封装，需避免把适配层演化成新的“大而全”服务对象

## Recommendation

本次采用“保留现有 token 管理链路 + 新增 `PyGithub` 薄适配层”的方案。

这是当前风险最低、收益最直接的接入路径：

- 不破坏已实现的请求级覆盖头与降级逻辑
- 让调用方能够立即使用 `PyGithub` 的对象化 API
- 为后续逐步增加更高层 GitHub 资源封装保留清晰演进路径
