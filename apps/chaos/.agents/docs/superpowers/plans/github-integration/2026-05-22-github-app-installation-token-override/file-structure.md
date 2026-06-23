# File Structure

- Create: `src/taolib/github_app/__init__.py`
- Create: `src/taolib/github_app/config.py`
- Create: `src/taolib/github_app/models.py`
- Create: `src/taolib/github_app/errors.py`
- Create: `src/taolib/github_app/cache.py`
- Create: `src/taolib/github_app/client.py`
- Create: `src/taolib/cli/__init__.py`
- Create: `src/taolib/cli/github_app.py`
- Create: `tests/github_app/test_config.py`
- Create: `tests/github_app/test_client.py`
- Create: `tests/github_app/test_token_manager.py`
- Create: `tests/github_app/test_concurrency.py`
- Create: `tests/github_app/test_stress.py`
- Create: `docs/github-app-token-override.md`
- Modify: `docs/index.md`
- Modify: `README.md`
- Modify: `pyproject.toml`
- Modify: `.github/workflows/ci.yml`
- Modify: `tests/project_changelogs/CHANGELOG_2026-05.md`
- Create: `.agents/docs/superpowers/retrospectives/2026-05-22-github-app-installation-token-override-testing.md`

## Responsibility Map

- `config.py`：解析环境变量、私钥与默认策略
- `models.py`：定义请求、结果、环境画像与枚举
- `client.py`：签发 App JWT、发送 access token 请求、识别令牌类型
- `cache.py`：保存进程内缓存与过期窗口判断
- `token_manager.py`：计算有效策略、处理缓存、执行单飞刷新与降级
- `cli/github_app.py`：暴露 `token` 与 `profile` 子命令
- `docs/github-app-token-override.md`：承载学习笔记、接入说明与指标摘要
- `retrospectives/*.md`：记录测试结果、压测数据与残余风险

## Shared Conventions

- 令牌策略枚举使用 `auto`, `enabled`, `disabled`
- 令牌类型枚举使用 `stateful`, `stateless`, `unknown`
- 运行环境枚举使用 `cloud`, `ghes`, `unknown`
- 所有日志与 CLI 输出都不打印完整 token 或私钥
- 测试中的 HTTP 模拟统一使用 `httpx.MockTransport`
