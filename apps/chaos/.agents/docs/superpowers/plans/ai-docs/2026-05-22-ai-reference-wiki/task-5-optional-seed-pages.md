# Task 5: Optional Follow-Up Seed Pages

**Files:**
- Create: `.agents/docs/references/python/pytest.md`
- Create: `.agents/docs/references/python/httpx.md`
- Create: `.agents/docs/references/podman/rootless.md`

- [ ] **Step 1: Decide whether to keep the first iteration minimal**

If the goal is only to land the approved skeleton, skip this task.

If adding seed pages now, continue with the next steps.

- [ ] **Step 2: Write `pytest.md`**

Create `.agents/docs/references/python/pytest.md`:
```md
# pytest

## Goal

沉淀 AgentForge 中与测试失败排查最相关的 `pytest` 使用知识。

## Relevance In AgentForge

- 关联模块：`tests/`
- 常见触发场景：单元测试失败、夹具行为异常、异步测试问题
- 优先检查文件：`tests/github_app/`

## Key Concepts

- 夹具用于共享测试准备逻辑
- `pytest.mark.asyncio` 用于异步测试

## Sources

- 官方文档：待补充
- 版本：待补充
- 抓取时间：待补充
```

- [ ] **Step 3: Write `httpx.md`**

Create `.agents/docs/references/python/httpx.md`:
```md
# httpx

## Goal

沉淀 AgentForge 中与 HTTP 请求行为和客户端交互最相关的 `httpx` 使用知识。

## Relevance In AgentForge

- 关联模块：`src/taolib/github_app/client.py`
- 常见触发场景：请求头异常、超时、响应解析失败
- 优先检查文件：`src/taolib/github_app/client.py`

## Key Concepts

- 请求头注入
- 异步请求与响应对象

## Sources

- 官方文档：待补充
- 版本：待补充
- 抓取时间：待补充
```

- [ ] **Step 4: Write `rootless.md`**

Create `.agents/docs/references/podman/rootless.md`:
```md
# Podman Rootless

## Goal

沉淀 rootless 模式下最常见的 Podman 使用限制与排障要点。

## Relevance In AgentForge

- 关联模块：本地开发环境与潜在容器运行脚本
- 常见触发场景：权限不足、挂载异常、网络行为差异
- 优先检查文件：后续容器脚本与集成说明页

## Key Concepts

- rootless 依赖当前用户权限
- 挂载与网络行为可能与 rootful 模式不同

## Sources

- 官方文档：待补充
- 版本：待补充
- 抓取时间：待补充
```

- [ ] **Step 5: Commit**

```bash
git add .agents/docs/references/python/pytest.md .agents/docs/references/python/httpx.md .agents/docs/references/podman/rootless.md
git commit -m "docs: add optional seed reference pages for AI wiki"
```
