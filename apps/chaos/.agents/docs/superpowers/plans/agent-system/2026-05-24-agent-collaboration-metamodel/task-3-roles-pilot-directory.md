### Task 3: 引入 `.agents/roles/` 首批试点目录

**Files:**
- Create: `.agents/roles/README.md`
- Create: `.agents/roles/collaboration-architect.md`

- [ ] **Step 1: 创建 `roles` 目录说明页**

在 `.agents/roles/README.md` 中说明目录目标、边界和文件约定。起始内容应包含：

```md
# Roles

本目录承载协作元模型中的 `Role` 实例，用于定义职责模板、默认规则绑定、权限边界和协作期望。

## 目录边界
- 不存放执行日志
- 不存放临时上下文
- 不直接复制 `skills/` 内容
```

- [ ] **Step 2: 创建首个试点角色文件**

在 `.agents/roles/collaboration-architect.md` 中定义一个最小可用角色实例，至少包含以下字段：

```md
# Collaboration Architect

## Role Identity
- Name: `collaboration-architect`
- Domain: `Governance + Knowledge`

## Responsibilities
- 维护协作元模型语义边界
- 设计目录映射与治理约束

## Default Bindings
- Rules: `documentation.md`, `context-economy.md`
- References: `agent-collaboration-metamodel.md`

## Non-Goals
- 不直接承担运行时任务调度实现
```

- [ ] **Step 3: 确保角色文件不退化为提示词仓库**

检查角色文件是否同时满足：

```text
有职责
有默认绑定
有边界
没有长篇自由提示词堆叠
```

- [ ] **Step 4: 运行目录检查**

Run:

```bash
git diff -- .agents/roles/README.md .agents/roles/collaboration-architect.md
```

Expected: 目录仅包含说明页和一个角色实例；没有额外引入 `teams/`、`agents/` 或 `policies/` 目录。

- [ ] **Step 5: Commit**

```bash
git add .agents/roles/README.md .agents/roles/collaboration-architect.md
git commit -m "docs(agent): add roles pilot directory"
```
