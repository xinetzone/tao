# Podman In AgentForge

## Goal

说明 Podman 相关知识在 AgentForge 中的当前和潜在落点，帮助 agent 判断何时需要参考容器文档。

## Current Assessment

- 当前仓库中尚未形成明显的 Podman 专用脚本或完整容器工作流。
- Podman 相关知识目前更适合作为通用运行环境与排障能力储备。

## Suggested Future Mapping

- 若后续引入本地容器开发脚本，优先记录到 `scripts/`
- 若后续引入 CI 容器构建流程，优先记录到 `.github/workflows/`
- 若后续引入开发文档，再同步到面向人类的 `docs/`

## Related References

- `../issue-patterns/podman-errors.md`
- `../references/podman/command-cheatsheet.md`
- `../references/podman/windows-setup.md`
- `../references/podman/podman-py-sdk.md`
- `../rules/containerization.md`
