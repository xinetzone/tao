# httpx

## Search Keywords

- 主关键词：httpx
- 英文术语：HTTP Client, Async HTTP, Request Headers
- 常见别名：请求库, 异步请求
- 错误短语：httpx.HTTPError, Connection error, ConnectTimeout, ReadTimeout

## Goal

说明项目中 httpx (HTTP Client) 的异步使用模式、请求头配置规范以及网络异常处理机制。

## Relevance In AgentForge

- 关联模块：GitHub App 客户端 (`src/taolib/github_app/client.py`)，OAuth 认证，文件存储客户端。
- 常见触发场景：调用外部 API 失败、超时报错、或者需要自定义请求头（如 `X-GitHub-Stateless-S2S-Token`）。
- 优先检查文件：`src/taolib/github_app/client.py`

## Trigger Phrases

- httpx 请求怎么设置超时时间？
- httpx 请求头为什么没带上？
- 怎么在测试中 Mock httpx 的返回结果？
- httpx 报 Connection error 怎么排查？

## Key Concepts

- **AsyncClient**: `httpx.AsyncClient` 用于异步发送 HTTP 请求，通常建议使用 `async with` 上下文管理器来管理连接池。
- **MockTransport**: 在测试中用来模拟 HTTP 响应的机制，避免发起真实网络请求。
- **Timeout**: 防止网络请求无限挂起，通常在客户端实例化时全局设置（如 `timeout=10.0`）。

## Common Problems

### 问题：请求未携带期望的 Header

- 现象：服务端返回 401/403，或者行为不符合预期（如未触发 GitHub 无状态 token 机制）。
- 原因：实例化 Client 时未注入 Header，或者在具体的 `.get()` / `.post()` 方法中覆盖了 Header。
- 排查步骤：
  1. 检查 `httpx.AsyncClient` 实例化时的 `headers` 参数。
  2. 如果是针对特定请求动态设置，检查发送请求处的逻辑。比如 `GitHubAppClient` 中是否正确写入了 `X-GitHub-Stateless-S2S-Token`。
- 相关命令或代码位置：`src/taolib/github_app/client.py`

### 问题：HTTP 请求超时或连接错误

- 现象：抛出 `httpx.ConnectTimeout` 或 `httpx.HTTPError: Connection error`。
- 原因：目标服务器不可达，网络不通，或者响应时间超过了客户端设置的 `timeout`。
- 排查步骤：
  1. 确认目标 URL 正确且网络可达。
  2. 检查 `timeout` 设置是否过短，对于可能较慢的 API 可以适当增加超时时间。

## Commands Or Snippets

```python
# 推荐的异步调用模式
import httpx

async def fetch_data(url: str, token: str):
    headers = {"Authorization": f"Bearer {token}"}
    # 推荐使用上下文管理器，自动管理连接
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status() # 遇到 4xx/5xx 会抛出异常
        return response.json()
```

```python
# 测试中使用 MockTransport
import httpx
import pytest

@pytest.mark.asyncio
async def test_with_mock_transport():
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"status": "ok"})

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    response = await client.get("https://example.com")
    assert response.json()["status"] == "ok"
```

## Sources

- 官方文档：[HTTPX - A next generation HTTP client for Python](https://www.python-httpx.org/)
- 版本：基于项目中使用的当前版本
- 抓取时间：N/A
