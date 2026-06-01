# 12. 与现有工具配置的关系

现在很多工具有自己的规则文件：

```
.claude/
.cursor/rules/
.github/copilot-instructions.md
.continue/
.aider.conf.yml
```

问题是每个工具各搞一套，容易分裂。比较好的策略是：

```
AGENTS.md                      # canonical source（中立、通用、稳定的源头）
.github/copilot-instructions.md # thin wrapper / pointer
.cursor/rules/...              # tool-specific adaptation
.claude/...                    # tool-specific adaptation
```

也就是说：**`AGENTS.md` 做中立、通用、稳定的源头；其他工具配置引用或同步它。** 不要把同一套规则复制五份，否则很快会不一致。
