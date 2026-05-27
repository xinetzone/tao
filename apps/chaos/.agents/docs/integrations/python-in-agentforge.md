# Python In AgentForge

## Goal

说明 Python 相关外部知识在 AgentForge 仓库中的主要落点，帮助 agent 快速从问题跳到代码和配置。

## Primary Files

- `pyproject.toml`：依赖组、Python 版本范围和工具配置入口。
- `src/taolib/`：核心 Python 代码。
- `tests/`：行为验证与回归测试。
- `.agents/docs/version-tracking.md`：Python 版本适配知识沉淀。

## Common Navigation Paths

- 依赖问题：先看 `pyproject.toml` 与 `uv.lock`
- GitHub App 认证问题：先看 `src/taolib/github_app/`
- 测试失败：先看 `tests/github_app/` 和对应模块
- 版本兼容问题：先看 `.agents/docs/version-tracking.md` 与 `.agents/scripts/`

## Related References

- `../issue-patterns/python-errors.md`
- `../references/python/package-index.md`
