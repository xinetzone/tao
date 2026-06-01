# 10. 各子系统设计详解

## 10.1 rules/ — 特定领域规范

规则文件应该写**硬性的、可被 Agent 直接执行的约束**。按领域拆分，每个文件职责单一。

**核心高价值规则**：
- `context-economy.md`：上下文节省策略，核心流程为"明确目标 → 检索定位 → 精读片段 → 执行任务 → 沉淀稳定知识"。这实际上把"上下文有限"这个 AI 的物理约束，转化为项目组织的架构原则。
- `skills.md`：技能开发规范，有完整的验证体系（`validate_skill_md.py` + pre-commit hook + CI）支撑。
- `python.md`：Python 开发规则，实用但可能与 pyproject.toml / mise.toml 中的约定重复。

## 10.2 workflows/ — 任务流程模板

这是 `.agents/` 中最有价值的部分之一。

**Bugfix Workflow**：

```md
1. Reproduce or understand the failure.
2. Identify the smallest likely cause.
3. Inspect nearby tests and similar code.
4. Make the smallest safe fix.
5. Add regression coverage when practical.
6. Run relevant checks.
7. Summarize root cause and fix.
```

**Feature Workflow**：

```md
1. Identify existing patterns.
2. Locate domain model and API boundaries.
3. Implement backend or data changes first if needed.
4. Implement UI/API integration.
5. Add tests for behavior.
6. Run lint, typecheck, and relevant tests.
7. Summarize user-visible behavior.
```

**Refactor Workflow**：

```md
1. Preserve behavior.
2. Identify test coverage before changing structure.
3. Avoid mixing refactor with feature changes.
4. Keep diffs reviewable.
5. Run existing tests.
6. Explain why the refactor improves the code.
```

这些比抽象的"be careful"强很多。

## 10.3 skills/ — 可执行技能的标准闭环

每个技能都必须有：

1. **SKILL.md** — 标准化描述文档
2. **scripts/** — 实现代码
3. **tests/** — 测试（可选）
4. **schemas/** — JSON Schema（可选）
5. **evals/** — 评测集（可选）

**验证体系**：有完整的 `scripts/validation/` 工具链，支持 SKILL.md 合规性校验、目录结构校验、CI 管线自动验证。

Skills 子系统是 `.agents/` 中**唯一有完整"文档 + 脚本 + 测试 + 评估"闭环的子系统**。这也是 `.agents/` 相对于 Cursor/Claude Code 的真正差异化资产——它不只是想做一个"有很多自定义技能的仓库"，而是想成为**技能生态的生产标准和验证基础设施**。对比：

- Cursor 的规则是私有的（只服务 Cursor 用户）
- Claude 的 skills 是平台绑定的
- `.agents/skills/` 的 `SKILL.md` + `evals/` + `schemas/` 是**平台无关的声明式标准**

如果未来出现多 AI 平台共存的格局，这种跨平台技能标准的价值会指数级放大。

## 10.4 roles/ — 职责边界定义

`roles` 不应该变成"人格设定"，而应该定义职责边界、职责和避规项。

**Frontend Agent 示例**：

```md
## Responsibilities
- React component implementation
- UI state management
- Accessibility
- Styling consistency
- Frontend tests

## Must Check
- Existing components before creating new ones
- Design tokens
- Responsive behavior
- Loading, empty, and error states

## Avoid
- Business logic inside presentational components
- Unapproved UI libraries
- Duplicating API client logic
```

**Reviewer Agent 示例**：

```md
## Review Focus
- Correctness / Edge cases / Security / Performance
- Test coverage / Maintainability

## Output Format
- Critical issues / Suggestions / Questions / Positive observations

## Avoid
- Nitpicks unless they affect maintainability
- Rewriting the whole solution without reason
```

## 10.5 teams/ — 多 Team 治理

`teams/` 定义多 Team 的治理边界与跨 Team 协作策略。每个 Team 包含成员角色、治理范围、Cross-Team Policy。如果只有一个 Team，Team 的语义价值会被自我消解——治理边界 = 项目边界，跨 Team 协作策略 = 不适用。建议至少有两个 Team 才能使 Cross-Team Policy 有意义。

## 10.6 context/ — Agent 摘要化上下文

这里放 Agent 经常需要但不应该塞进主文件的知识。

**Architecture Context 示例**：

```md
## Layers
- UI layer → Application layer → Domain layer
- Infrastructure layer → Domain layer

## Dependency Direction
Domain must not import UI or infrastructure modules.
```

**Testing Context 示例**：

```md
## Test Types
- Unit tests / Integration tests / E2E tests

## When to Add Tests
- Bug fixes require regression tests when feasible.
- New business logic requires unit tests.
- UI behavior changes require component or E2E tests.
```

## 10.7 policies/ — 硬约束

`policies` 应该写硬约束而不是建议。

**Dependency Policy**：

```md
- Do not add runtime dependencies without approval.
- Prefer existing utilities.
- Use standard library features when sufficient.
- Avoid large dependencies for small helpers.
```

**Migration Policy**：

```md
- Never run production migrations automatically.
- Migrations must be reversible when possible.
- Schema changes require corresponding model/type updates.
- Destructive migrations require explicit approval.
```

**Security Policy**：

```md
- Never log secrets, tokens, credentials, or personal data.
- Never weaken authentication or authorization checks.
- Validate external input at trust boundaries.
- Prefer parameterized queries.
```

## 10.8 templates/ — 复用模板

结构极简且合理。典型模板包括 `plan.md`、`pr-summary.md`、`test-report.md`、`SKILL.md`，每个职责单一。
