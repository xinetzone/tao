# 第 6 章 · 资源使用

### 6.1 人力投入

| 角色 | 投入 |
|---|---|
| 用户（决策者） | 约 14 次关键选择 + 若干次"认可/继续"确认 |
| AI（设计+执行者） | 4 轮 brainstorming 设计 + 4 次审批方案呈现 + 全部实施操作 |

### 6.2 工具链

| 工具 | 用途 |
|---|---|
| Mermaid | 所有流程图、关系图（元模型关系图、工作流门禁图、路由图） |
| Git | 13 次提交，conventional commits 格式 |
| Subagent (Task tool) | Phase 3 的并行实施 |
| rg (ripgrep) | 验收校验（占位词搜索） |

### 6.3 产物分布

```
.agents/
├── roles/                           # 4 角色 + 1 README
├── teams/                           # 1 Team + 1 README
├── workflows/
│   ├── role-review.md               # 工作流主文档
│   └── role-review/
│       ├── templates/
│       │   ├── proposal.md          # 角色提案模板
│       │   └── team-proposal.md     # Team 提案模板
│       └── verification/            # 4 份试运行记录
└── docs/
    ├── references/
    │   └── agent-collaboration-metamodel.md  # 稳定参考页
    └── superpowers/
        ├── specs/                   # 2 份设计 spec
        └── plans/                   # 2 份实现 plan
```
