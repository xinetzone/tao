# 14. 反模式：Prompt 垃圾场

坏的 `.agents/` 可能会变成这样：

```
.agents/
  prompt1.md
  old-prompt.md
  better-prompt-final.md
  reviewer-v2.md
  reviewer-v3-final.md
  random.md
  notes.md
```

这会让 Agent 更困惑。建议 `.agents/` 也要有治理：每个文件有清晰职责，用 README.md 作为目录入口，避免版本后缀堆积。
