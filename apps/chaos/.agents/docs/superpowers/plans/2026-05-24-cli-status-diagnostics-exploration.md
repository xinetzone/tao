# CLI Status Diagnostics Exploration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 验证 AgentForge 当前 CLI 状态/诊断体验是否能支撑用户定位 GitHub App 配置、策略、缓存与错误路径问题，并沉淀后续开发动作。

**Architecture:** 本计划采用文档驱动、只读验证优先的探索方式。工作台位于 `.trae/specs/cli-status-diagnostics-exploration/`，执行时只补充 `.temp/` 临时验证记录、复盘文件，并更新工作台 checklist/tasks 的完成状态。本轮不修改产品代码，不访问外部服务，不处理真实凭据。

**Tech Stack:** Markdown, Python source reading, pytest test inventory, Git, PowerShell, `uv run pytest`, `uv run pre-commit run --all-files`

---

### Task 1: Confirm CLI diagnostics baseline

**Files:**
- Read: `src/taolib/cli/github_app.py`
- Read: `src/taolib/cli/_parsers.py`
- Read: `src/taolib/cli/_formatters.py`
- Read: `src/taolib/cli/_status.py`
- Read: `src/taolib/cli/_builders.py`
- Read: `src/taolib/github_app/config.py`
- Read: `src/taolib/github_app/token_manager.py`
- Read: `src/taolib/github_app/cache.py`
- Read: `src/taolib/github_app/errors.py`
- Read: `tests/github_app/test_cli.py`
- Read: `tests/github_app/test_cli_status.py`
- Read: `docs/github-app-token-override.md`
- Read: `.trae/specs/cli-status-diagnostics-exploration/spec.md`
- Read: `.trae/specs/cli-status-diagnostics-exploration/tasks.md`
- Read: `.trae/specs/cli-status-diagnostics-exploration/checklist.md`

- [ ] **Step 1: Confirm repository is clean before exploration**

Run:

```powershell
git status --short
```

Expected: no output. If output appears, stop and report the dirty files before continuing.

- [ ] **Step 2: Inspect CLI command routing**

Read `src/taolib/cli/github_app.py` and record which subcommands map to which output paths:

```text
profile -> _build_profile_payload(args) -> stdout JSON
token -> build_manager(args) + manager.get_token(build_request(args)) -> _build_token_payload(result) -> stdout JSON
status -> check_status(args) -> stdout JSON
GitHubAppConfigurationError -> stderr JSON + exit 1
GitHubAppClientError -> stderr JSON + exit 2
```

- [ ] **Step 3: Inspect CLI parser surface**

Read `src/taolib/cli/_parsers.py` and record the available user-facing knobs:

```text
profile: --api-url, --strategy
token: --installation-id, --strategy
status: --installation-id required, --strategy
strategy choices: auto, enabled, disabled
api url default: GITHUB_API_URL or https://api.github.com
```

- [ ] **Step 4: Inspect output payload semantics**

Read `src/taolib/cli/_formatters.py` and `src/taolib/cli/_status.py`, then record the current JSON fields:

```text
profile: api_url, default_strategy, environment
token: degraded, effective_strategy, expires_at, requested_strategy, token_kind, token_preview
status: cached, expired, expires_at, token_kind
```

- [ ] **Step 5: Inspect configuration and cache dependencies**

Read `src/taolib/cli/_builders.py`, `src/taolib/github_app/config.py`, `src/taolib/github_app/token_manager.py`, and `src/taolib/github_app/cache.py`, then record whether CLI diagnostics can explain these concerns:

```text
required env vars
api url and environment detection
requested vs effective token strategy
cache key construction
in-memory cache lifetime
configuration errors
client errors
```

### Task 2: Create manual validation record

**Files:**
- Create: `.temp/cli-status-diagnostics-exploration.md`

- [ ] **Step 1: Create validation record with evidence table**

Create `.temp/cli-status-diagnostics-exploration.md` with this content:

```md
# CLI Status Diagnostics Exploration

## Sample

- Sample topic: `cli-status-diagnostics-exploration`
- Scenario type: real development exploration
- Workbench path: `.trae/specs/cli-status-diagnostics-exploration/`
- Code area: `src/taolib/cli/` and `src/taolib/github_app/`

## Command Surface

| Command | Purpose | Current Output | Diagnostic Strength |
|---|---|---|---|
| `profile` | Report environment profile without requiring a valid private key | `api_url`, `default_strategy`, `environment` | TBD during validation |
| `token` | Fetch installation token and emit masked token metadata | `degraded`, `effective_strategy`, `expires_at`, `requested_strategy`, `token_kind`, `token_preview` | TBD during validation |
| `status` | Inspect current process in-memory cache state without network requests | `cached`, `expired`, `expires_at`, `token_kind` | TBD during validation |

## Check Results

| Check | Status | Evidence | Note |
|---|---|---|---|
| CLI exposes a no-secret environment profile path | PASS | `src/taolib/cli/github_app.py`, `src/taolib/cli/_formatters.py` | `profile` returns environment and strategy summary. |
| CLI exposes token metadata without leaking secrets | PASS | `src/taolib/cli/_formatters.py`, `tests/github_app/test_cli.py` | Token output uses `token_preview` and masks the full token. |
| CLI exposes a status path that avoids network requests | PASS | `src/taolib/cli/_status.py`, `tests/github_app/test_cli_status.py` | `status` checks cache only. |
| Status output explains cache lifetime limits | WARN | `src/taolib/cli/_status.py` | Implementation note says cache is current-process only, but JSON does not expose this caveat. |
| Configuration errors are machine-readable | PASS | `src/taolib/cli/github_app.py` | Configuration errors emit stderr JSON and exit 1. |
| Client errors are machine-readable | PASS | `src/taolib/cli/github_app.py` | Client errors emit stderr JSON and exit 2. |
| Tests cover profile/token/status basics | PASS | `tests/github_app/test_cli.py`, `tests/github_app/test_cli_status.py` | Basic output and masking paths are covered. |
| Tests cover diagnostic failure guidance | WARN | `tests/github_app/` | Existing tests check error codes less directly than success payload semantics. |
| Docs explain how users should interpret `status` | WARN | `docs/github-app-token-override.md` | Docs explain token strategy and observability but not the `status` command caveat. |

## Friction Points

- The CLI has useful JSON surfaces, but `status` may look more persistent than it is because the process-local cache caveat is not part of the output.
- `profile` is safe and low-friction, but it does not report whether required GitHub App environment variables are present.
- Error output is machine-readable, but user-facing next-step guidance is minimal.

## Initial Conclusion

- Current CLI diagnostics are suitable as a baseline.
- The most concrete follow-up is likely to improve `status`/`profile` explanatory output or documentation before adding new commands.
- `Expected Evidence` remains usable in a real development topic, but source evidence is more distributed than in mechanism self-check rounds.
```

- [ ] **Step 2: Review validation record against source evidence**

Read the record and verify that each `PASS` and `WARN` points to an existing file. If any evidence path is missing, change that row to `MISSING` and explain why.

### Task 3: Write retrospective and close workbench

**Files:**
- Create: `.agents/docs/superpowers/retrospectives/2026-05-24-cli-status-diagnostics-exploration.md`
- Modify: `.trae/specs/cli-status-diagnostics-exploration/tasks.md`
- Modify: `.trae/specs/cli-status-diagnostics-exploration/checklist.md`

- [ ] **Step 1: Create retrospective**

Create `.agents/docs/superpowers/retrospectives/2026-05-24-cli-status-diagnostics-exploration.md` with this content:

```md
# CLI Status Diagnostics Exploration Retrospective

## Outcome

- 本轮探索验证了知识驱动探索工作台可以用于真实开发议题，而不只适用于机制自检。
- 当前 `taolib-github-app` CLI 已具备基础状态/诊断面：`profile`、`token` 与 `status` 分别覆盖环境画像、令牌元信息与缓存状态。
- 真实开发议题中的证据分散在 CLI、GitHub App 模块、测试与文档之间，`Expected Evidence` 仍然有用，但需要配合更细的验证记录。

## Reused Foundation

- 复用了 `.agents/docs/templates/knowledge-driven-exploration-workbench-template.md` 的工作台结构。
- 复用了 `.trae/specs/cli-status-diagnostics-exploration/` 作为真实开发议题工作台。
- 复用了前三轮形成的 `PASS`、`WARN`、`MISSING` 状态语义。

## Findings

- `profile` 是低风险诊断入口，可以在不需要有效私钥的情况下输出 `api_url`、`default_strategy` 与 `environment`。
- `token` 输出包含策略降级、实际策略、令牌类型、过期时间和脱敏预览，适合作为令牌行为的机器可读诊断面。
- `status` 明确避免网络请求，但当前只检查新建进程内的内存缓存，因此对用户的实际排障价值有限。
- CLI 错误输出是 JSON 格式并区分配置错误与客户端错误，但缺少可直接指导用户下一步的字段。
- 测试覆盖了 `profile`、`token` 脱敏和 `status` 空缓存，但对错误指导、配置完整性摘要和 status 语义边界覆盖不足。

## Friction Points

- `status` 的进程内缓存限制只存在于源码说明中，用户从 JSON 输出中不容易理解为什么通常看到 `cached=false`。
- `profile` 可以判断环境类型和策略，但不能告诉用户关键环境变量是否已配置。
- 文档解释了 GitHub App token 策略与降级，但没有把 CLI 诊断命令作为排障路径串起来。

## Validation Result

- 真实议题适配：成立。探索工作台能承载真实 CLI 诊断问题。
- 证据闭环：成立。证据可指向工作台、源码、测试、文档和复盘。
- 模板泛化：成立。`Expected Evidence` 在真实开发议题中仍然能降低收尾遗漏。
- 开发可行动性：成立。本轮能导出明确后续动作。

## Upgrade Recommendations

- 后续可考虑让 `status` 输出增加 `cache_scope` 或等价字段，明确当前结果只代表进程内缓存。
- 后续可考虑让 `profile` 输出关键配置项的存在性摘要，但继续避免输出真实 secret。
- 后续可补充 CLI 诊断文档，把 `profile`、`token`、`status` 串成排障路径。
- 暂不新增自动化探索脚本，因为本轮结构性证据仍可人工维护。

## Best Fit

- 本轮探索属于真实开发议题探索。
- 它验证的是探索机制对代码、测试、文档交叉问题的承载能力，而不是直接交付代码变更。

## Next Action

- 下一步优先规划一个小型开发任务：增强 CLI 诊断输出的解释性，候选范围为 `profile` 配置存在性摘要、`status` 缓存作用域字段或对应文档补充。
- 自动化延后条件保持不变：当后续至少两个真实议题样本出现重复的结构性 `WARN` 或 `MISSING` 时，再考虑新增只读检查脚本。
```

- [ ] **Step 2: Mark tasks complete**

Replace `.trae/specs/cli-status-diagnostics-exploration/tasks.md` with:

```md
# Tasks
- [x] Task 1: 创建第四轮真实开发议题工作台。
- [x] Task 2: 完成 CLI 状态/诊断体验的只读验证记录。
- [x] Task 3: 输出真实开发议题探索复盘。
- [x] Task 4: 确认至少一个后续开发动作或延后条件。

# Task Dependencies
- [Task 2] depends on [Task 1]
- [Task 3] depends on [Task 2]
- [Task 4] depends on [Task 3]
```

- [ ] **Step 3: Mark checklist complete**

Replace `.trae/specs/cli-status-diagnostics-exploration/checklist.md` with:

```md
- [x] 场景卡或场景来源已明确
- [x] spec 已完成并边界清晰
- [x] plan 已完成并可执行
- [x] 至少完成一次最小验证
- [x] 已输出复盘并指定回流动作
- [x] 预期证据已完整指向协议、场景、工作台、复盘与回流动作
```

### Task 4: Validate and review

**Files:**
- Review: `.trae/specs/cli-status-diagnostics-exploration/spec.md`
- Review: `.trae/specs/cli-status-diagnostics-exploration/tasks.md`
- Review: `.trae/specs/cli-status-diagnostics-exploration/checklist.md`
- Review: `.temp/cli-status-diagnostics-exploration.md`
- Review: `.agents/docs/superpowers/retrospectives/2026-05-24-cli-status-diagnostics-exploration.md`

- [ ] **Step 1: Run tests**

Run:

```powershell
uv run pytest
```

Expected: all tests pass. Existing unrelated warnings may appear, but no test should fail.

- [ ] **Step 2: Run pre-commit**

Run:

```powershell
uv run pre-commit run --all-files
```

Expected: all hooks pass.

- [ ] **Step 3: Review git diff**

Run:

```powershell
git diff -- .trae/specs/cli-status-diagnostics-exploration .agents/docs/superpowers/plans/2026-05-24-cli-status-diagnostics-exploration.md .agents/docs/superpowers/retrospectives/2026-05-24-cli-status-diagnostics-exploration.md
```

Expected: only fourth-round exploration workbench, plan, and retrospective files are changed.

- [ ] **Step 4: Report execution result and ask before commit**

Report:

```text
第四轮 CLI 状态/诊断体验探索已完成。
验证结果：uv run pytest 通过；uv run pre-commit run --all-files 通过。
主要发现：当前 CLI 有 profile/token/status 三个诊断面；status 的进程内缓存语义和 profile 的配置存在性摘要是最明确的后续开发候选。
是否提交本轮计划与执行结果？
```

Do not commit unless the user explicitly asks for a commit.

---

## Self-Review

- Spec coverage: plan covers workbench creation, CLI source review, test/doc review, manual validation, retrospective, checklist closure, tests, pre-commit, and commit gate.
- Placeholder scan: no `TBD` remains in final expected artifacts except the temporary table fields that Task 2 immediately resolves in validation prose.
- Scope check: this remains a single read-only exploration and does not implement code changes.
- Ambiguity check: external service access and real secret handling are explicitly excluded.
