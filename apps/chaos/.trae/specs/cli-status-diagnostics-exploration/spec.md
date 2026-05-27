# Spec

## Goal

- 验证 AgentForge 当前 CLI 状态/诊断体验是否能支撑用户定位 GitHub App 配置、策略、缓存与错误路径问题，并检验 `Expected Evidence` 在真实开发议题中的可用性。

## Scope

- 使用当前探索工作台模板创建 `cli-status-diagnostics-exploration` 工作台。
- 只读梳理 `taolib-github-app` CLI 的 `profile`、`status`、`token` 入口与输出语义。
- 只读检查 GitHub App 配置、token 管理、缓存和错误处理与 CLI 输出之间的关系。
- 对照现有测试与文档，记录状态/诊断体验的覆盖点、缺口与后续开发候选动作。
- 输出临时验证记录、复盘与至少一个 `Next Action`。

## Non-Goals

- 本轮不修改产品代码。
- 本轮不新增 CLI 命令或参数。
- 本轮不重构 GitHub App 错误模型。
- 本轮不新增自动化诊断脚本。
- 本轮不访问外部 GitHub 服务。
- 本轮不处理真实 GitHub 凭据、私钥或 token。

## Deliverables

- `.trae/specs/cli-status-diagnostics-exploration/spec.md`
- `.trae/specs/cli-status-diagnostics-exploration/tasks.md`
- `.trae/specs/cli-status-diagnostics-exploration/checklist.md`
- `.agents/docs/superpowers/plans/2026-05-24-cli-status-diagnostics-exploration.md`
- `.temp/cli-status-diagnostics-exploration.md`
- `.agents/docs/superpowers/retrospectives/2026-05-24-cli-status-diagnostics-exploration.md`

## Risks

- CLI 状态/诊断能力可能分散在 parser、formatter、builder、status 与 GitHub App 模块之间，证据链比模板自检更复杂。
- 现有 `status` 命令只检查进程内缓存，真实用户对跨进程缓存的预期可能与实现不一致。
- 如果发现真实缺口，本轮只能形成后续开发动作，不应直接扩大为代码修改。
- 如果文档与测试覆盖较少，结论需要标记为探索发现，而不是完整产品评审。
