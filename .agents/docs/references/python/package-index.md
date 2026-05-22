# Python Package Index

## Goal

记录 AgentForge 中值得为 agent 建立专门参考页的 Python 包与主题。

## Relevance In AgentForge

- 关联模块：`src/taolib/`、`tests/`、`pyproject.toml`
- 常见触发场景：依赖升级、测试失败、类型问题、网络请求行为变化
- 优先检查文件：`pyproject.toml`、`src/taolib/github_app/`、`tests/github_app/`

## Current Candidates

- `pytest`：测试组织、夹具、异步测试。
- `httpx`：GitHub App HTTP 客户端相关请求行为。
- `PyJWT`：GitHub App JWT 签发与认证链路。
- `PyGithub`：对象化 GitHub API 访问适配层。

## Next Suggested Pages

- `pytest.md`
- `httpx.md`
- `pyjwt.md`
- `pygithub.md`

## Sources

- 官方文档：待补充
- 版本：按仓库依赖锁定版本补充
- 抓取时间：待补充
