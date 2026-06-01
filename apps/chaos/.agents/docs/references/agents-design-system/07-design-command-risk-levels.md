# 7. 设计方向四：命令白名单与风险分级

现在越来越重要的是把命令分级。例如：

```md
## Safe Commands（无需确认）
- pnpm test / pnpm lint / pnpm typecheck / pnpm build
- git diff / git status

## Confirmation Required（需确认）
- database migrations
- dependency upgrades
- deployment commands
- destructive filesystem operations
- commands that access production services

## Forbidden（禁止）
- rm -rf /
- commands that expose secrets
- production deploys without explicit user approval
```

对 agentic workflow 来说，这比"请小心"有效得多。
