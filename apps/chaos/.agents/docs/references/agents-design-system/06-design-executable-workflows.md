# 6. 设计方向三：可执行工作流而非纯描述

对 Agent 帮助很小的写法：

```md
Please write good code.
Please test your changes.
Follow best practices.
```

对 Agent 帮助很大的写法：

```md
## Before Editing
- Identify the smallest relevant file set.
- Check existing patterns before adding new abstractions.
- Prefer editing existing files over creating new ones.

## After Editing
Run the following when relevant:
- pnpm typecheck
- pnpm lint
- pnpm test

If any command fails, fix the issue or explain why it is unrelated.
```

更好的 `AGENTS.md` 应该像一个 checklist，而不是价值观宣言。
