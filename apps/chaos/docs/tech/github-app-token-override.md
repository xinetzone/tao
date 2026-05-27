# 🛡️ GitHub App 安装令牌请求级覆盖头学习笔记

## 背景：GitHub App 安装令牌

GitHub App 通过 OAuth 2.0 风格的流程获取对组织或仓库的访问权限。其核心流程如下：

1. **应用注册**：开发者创建 GitHub App，获取 `App ID` 与 RSA 私钥
2. **JWT 签发**：使用私钥签发短期 JWT（通常 10 分钟有效），作为应用级身份凭证
3. **安装令牌请求**：携带 JWT 向 `/app/installations/{installation_id}/access_tokens` 发送 POST 请求
4. **安装令牌返回**：GitHub 返回一个安装令牌（installation token），后续 API 调用以该令牌作为 `Authorization: token {token}` 的凭证

安装令牌的默认行为由 GitHub 服务端控制，但在某些场景下，开发者需要**显式干预**令牌的生成策略，这就是请求级覆盖头的价值所在。

## S2S Token 策略：Stateful vs Stateless

GitHub 在安装令牌领域提供了两种底层策略：

| 维度 | Stateful Token | Stateless Token |
|------|----------------|-----------------|
| **服务端状态** | 需要持久化存储令牌元数据 | 无服务端状态，纯加密验证 |
| **撤销延迟** | 存在传播延迟（秒级到分钟级） | 即时生效，无需传播 |
| **令牌格式** | `ghs_` 前缀，三段式（含签名） | `ghs_` 前缀，三段式（含签名与额外元数据） |
| **适用场景** | 通用场景，兼容性最好 | 对撤销延迟敏感的高安全场景 |

> **如何区分**：taolib 中通过 `GitHubAppClient.classify_token_kind()` 实现。若令牌在 `ghs_` 前缀后包含恰好两个 `.` 分隔符，则判定为 `STATELESS`。

## `X-GitHub-Stateless-S2S-Token` 请求头

GitHub API 允许在请求安装令牌时，通过自定义 HTTP 头显式声明对 Stateless Token 的偏好：

```text
POST /app/installations/{installation_id}/access_tokens
Authorization: Bearer {jwt}
Accept: application/vnd.github+json
X-GitHub-Stateless-S2S-Token: enabled
```

### 取值语义

| 取值 | 含义 |
|------|------|
| `enabled` | 请求 GitHub 尽可能返回 Stateless Token |
| `disabled` | 显式请求 Stateful Token（覆盖默认策略） |
| 不携带 | 完全由 GitHub 服务端按默认策略决定 |

taolib 中通过 `GitHubAppClient._build_override_headers()` 根据 `EffectiveTokenStrategy` 构造该请求头：

```python
def _build_override_headers(self, strategy: EffectiveTokenStrategy) -> dict[str, str]:
    if strategy is EffectiveTokenStrategy.ENABLED:
        return {"X-GitHub-Stateless-S2S-Token": "enabled"}
    if strategy is EffectiveTokenStrategy.DISABLED:
        return {"X-GitHub-Stateless-S2S-Token": "disabled"}
    return {}
```

## 兼容性约束：GHES 不支持 S2S Token

GitHub Enterprise Server（GHES）作为私有化部署版本，其 API 能力通常落后于 GitHub Cloud。在 S2S Token 领域，核心约束如下：

- **GHES 不支持 `X-GitHub-Stateless-S2S-Token` 请求头**：携带该头不会报错，但会被静默忽略，服务端始终返回 Stateful Token
- **策略降级是必要行为**：若代码在 GHES 环境下仍强制要求 Stateless Token，可能导致安全假设被违背（以为令牌可即时撤销，实际并非如此）

### taolib 的环境检测与降级

`GitHubAppSettings.from_env()` 在初始化时自动检测运行环境：

```python
def _detect_environment(api_url: str) -> EnvironmentKind:
    normalized = api_url.rstrip("/")
    if normalized == "https://api.github.com":
        return EnvironmentKind.CLOUD
    if normalized.endswith("/api/v3"):
        return EnvironmentKind.GHES
    return EnvironmentKind.UNKNOWN
```

通过 `api_url` 的 URL 模式即可区分 Cloud 与 GHES，无需额外配置。

## 工程实现：RequestedTokenStrategy → EffectiveTokenStrategy

taolib 采用双层策略枚举设计，将"用户请求"与"实际生效"解耦：

```{mermaid}
flowchart LR
    A["RequestedTokenStrategy<br/>用户/调用方意图"] --> B{"resolve_effective_strategy"}
    B -->|GHES 环境| C["EffectiveTokenStrategy.NONE<br/>不发送覆盖头"]
    B -->|Cloud + ENABLED| D["EffectiveTokenStrategy.ENABLED"]
    B -->|Cloud + DISABLED| E["EffectiveTokenStrategy.DISABLED"]
    B -->|Cloud + AUTO| C
```

### 枚举定义

**`RequestedTokenStrategy`**（调用方意图）

| 成员 | 值 | 语义 |
|------|-----|------|
| `AUTO` | `"auto"` | 不干预，由环境与服务端共同决定 |
| `ENABLED` | `"enabled"` | 期望使用 Stateless Token |
| `DISABLED` | `"disabled"` | 期望使用 Stateful Token |

**`EffectiveTokenStrategy`**（实际生效）

| 成员 | 值 | 语义 |
|------|-----|------|
| `NONE` | `"none"` | 不发送覆盖头 |
| `ENABLED` | `"enabled"` | 发送 `X-GitHub-Stateless-S2S-Token: enabled` |
| `DISABLED` | `"disabled"` | 发送 `X-GitHub-Stateless-S2S-Token: disabled` |

### 转换核心逻辑

```python
def resolve_effective_strategy(self, requested: RequestedTokenStrategy) -> EffectiveTokenStrategy:
    if self.settings.runtime_profile.environment is EnvironmentKind.GHES:
        return EffectiveTokenStrategy.NONE
    if requested is RequestedTokenStrategy.ENABLED:
        return EffectiveTokenStrategy.ENABLED
    if requested is RequestedTokenStrategy.DISABLED:
        return EffectiveTokenStrategy.DISABLED
    return EffectiveTokenStrategy.NONE
```

### 降级标记

当调用方显式请求了 `ENABLED` 或 `DISABLED`，但因环境约束被降级为 `NONE` 时，`InstallationTokenResult.degraded` 字段会被置为 `True`：

```python
def _was_degraded(
    self,
    requested: RequestedTokenStrategy,
    effective: EffectiveTokenStrategy,
) -> bool:
    return (
        requested in {RequestedTokenStrategy.ENABLED, RequestedTokenStrategy.DISABLED}
        and effective is EffectiveTokenStrategy.NONE
    )
```

这一标记对上层业务至关重要：它允许调用方在拿到令牌后，根据 `degraded` 值调整自身的安全假设（如是否依赖即时撤销能力）。

## Singleflight 缓存去重的工程启发

在高并发场景下，多个并发请求可能同时发现缓存中的令牌即将过期，从而引发对 GitHub API 的重复请求。taolib 通过 **Singleflight 模式** 解决这一问题：

```{mermaid}
sequenceDiagram
    participant C1 as 并发请求 1
    participant C2 as 并发请求 2
    participant Cache as InMemoryCache
    participant Lock as asyncio.Lock
    participant GH as GitHub API

    C1->>Cache: get(cache_key)
    C2->>Cache: get(cache_key)
    Cache-->>C1: stale / missing
    Cache-->>C2: stale / missing
    C1->>Lock: acquire
    C2->>Lock: wait
    C1->>GH: POST access_tokens
    GH-->>C1: new token
    C1->>Cache: set(cache_key, token)
    C1->>Lock: release
    Lock-->>C2: acquired
    C2->>Cache: get(cache_key)
    Cache-->>C2: fresh token (just set)
    C2->>Lock: release
```

### 实现要点

1. **锁粒度**：以 `cache_key` 为维度，每个 key 对应独立的 `asyncio.Lock`，避免全局锁瓶颈
2. **二次检查**：获取锁后再次检查缓存，防止锁竞争期间其他协程已完成刷新
3. **缓存键设计**：包含 `installation_id`、`permissions`、`repositories`、`effective_strategy`，确保不同权限组合的令牌隔离存储

```python
def build_cache_key(self, request: InstallationTokenRequest, effective: EffectiveTokenStrategy | None = None) -> str:
    effective = effective or self.resolve_effective_strategy(request.strategy)
    return (
        f"{request.installation_id}|"
        f"{sorted(request.permissions.items())}|"
        f"{sorted(request.repositories)}|"
        f"{effective.value}"
    )
```

### 工程启发

- **防御性编程**：并发场景下的缓存失效（cache stampede）是常见问题，Singleflight 是一种轻量级且高效的解决方案
- **异步锁的生命周期**：`self._refresh_locks` 以字典形式惰性创建锁对象，避免无意义的内存分配
- **时间窗口控制**：`eager_refresh_seconds` 参数允许在令牌正式过期前提前刷新，为网络延迟与 GitHub API 响应时间预留缓冲

## 总结

taolib 的 GitHub App Token 管理模块展示了如何在工程实现中平衡"能力探索"与"兼容性兜底"：

1. **策略分层**：将"用户意图"（`RequestedTokenStrategy`）与"实际生效"（`EffectiveTokenStrategy`）分离，使降级逻辑透明化
2. **环境自适应**：通过 URL 模式自动识别 GHES，无需用户手动配置，降低使用门槛
3. **并发安全**：Singleflight 缓存机制在极简实现（纯内存、无外部依赖）下解决了高并发令牌刷新问题
4. **可观测性**：`degraded` 标记让上层业务能够感知策略降级，做出对应的安全调整
