# 5. 设计方向二：分层指令与优先级规则

很多项目现在倾向于在 monorepo 中分层：

```
AGENTS.md
packages/
  web/
    AGENTS.md
  api/
    AGENTS.md
  worker/
    AGENTS.md
```

根目录 `AGENTS.md` 写全局规则（包管理器、共享类型、受影响包测试），子项目 `AGENTS.md` 写局部规则（框架选择、组件目录、渲染策略）。

当多个 `AGENTS.md` 发生冲突时，推荐优先级规则：

```
用户当前指令 > 子目录 AGENTS.md > 根目录 AGENTS.md > 默认工具规则
```

这样 Agent 在处理局部任务时可以获得更精确的上下文，越靠近代码目录，规则越具体。
