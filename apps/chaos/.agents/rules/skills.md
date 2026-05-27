# 🛠️ 技能开发规范 (Skills Development Rules)

本文档定义了项目中所有智能体技能（Skills）的标准化约束。任何新增技能必须严格遵循此规范才能纳入技能管理体系。

## 1. 生效范围与目录结构
- **生效范围**：本规范适用于所有位于 `skills/` 目录下的子技能（例如 `skills/xxx/`，其中 `xxx` 为具体技能标识）。
- **目录约束**：在每一个技能专属目录内，**强制**要求包含一个 `SKILL.md` 文件。

## 2. 官方标准遵循 (Official Standards Compliance)
在开发任何 skill 功能时，**必须**严格遵循 [Agent Skills 官方规范](https://agentskills.io/home) 中规定的全部要求。
1. **开发前准备**：必须首先访问 `https://agentskills.io/home` 获取完整的开发标准、接口定义、设计规范及功能约束。
2. **实现要求**：确保 skill 的所有实现逻辑、交互流程、视觉呈现都与官方网页要求保持绝对一致。
3. **验收测试**：完成开发后，必须对照网页内的验收标准，逐项进行功能测试与兼容性验证，确保最终交付的 skill 完美符合所有预设要求。

## 3. SKILL.md 文件结构要求

### 3.1 必填章节（强制）

每个技能的 `SKILL.md` 必须包含以下必填章节：

1. **技能唯一标识 (Skill ID)**：全局唯一的标识符，通常与技能目录名一致。
2. **功能描述 (Description)**：清晰说明该技能的用途、使用场景及核心能力。
3. **输入输出参数定义 (I/O Parameters)**：
   - **输入 (Input)**：参数名称、类型、是否必填、默认值及说明。
   - **输出 (Output)**：返回结果的数据结构和预期格式。
4. **依赖项说明 (Dependencies)**：该技能运行所需要的系统库、第三方包、环境变量或其他前置条件。
5. **部署要求 (Deployment)**：技能的安装、配置或初始化步骤。
6. **错误处理规范 (Error Handling)**：常见错误码、异常场景及应对策略。
7. **版本记录 (Changelog)**：记录技能的版本变更历史及更新内容。

### 3.2 建议章节（推荐）

以下章节虽非强制，但强烈建议补充以提升文档质量：

1. **快速开始 (Quick Start)**：入门指南和最常用调用方式示例。
2. **执行流程 (Execution Flow)**：技能执行的详细流程说明。
3. **最佳实践 (Best Practices)**：使用建议、注意事项和常见问题解答（FAQ）。

### 3.3 Markdown 格式规范

- **中文标题锚点**：所有中文标题必须使用显式 MyST 锚点，例如 `(my-anchor)=`
- **链接格式**：项目内引用使用相对路径，外部链接使用完整 URL
- **标题层级**：建议只有一个 H1 标题，使用 H2-H4 组织内容

## 4. 技能目录结构

```
skills/<skill-name>/
├── SKILL.md           # 技能文档（必需）
├── scripts/           # 技能实现脚本（推荐）
│   └── *.py
├── tests/             # 测试文件（推荐）
│   └── *.py
├── schemas/           # JSON Schema 定义（可选）
├── references/        # 参考文档（可选）
└── evals/             # 评测集（可选）
```

## 5. 技能验证体系

### 5.1 验证脚本列表

项目提供完整的验证工具链，位于 `.agents/scripts/validation/`：

| 脚本 | 功能 | 校验内容 |
|------|------|----------|
| `validate_skill_md.py` | SKILL.md 合规性校验 | 必填章节、建议章节、Markdown 质量、目录结构 |
| `validate_workbench.py` | 探索工作台完整性校验 | spec.md、tasks.md、checklist.md 完整性 |
| `validate_retro_feedback.py` | 复盘回流动作校验 | Next Action 章节存在性与可执行性 |
| `validate_references.py` | 引用完整性校验 | 协议页与场景目录交叉引用 |
| `validate_all.py` | 综合校验入口 | 运行所有验证并生成汇总报告 |

### 5.2 执行检查机制

为了确保规范被严格执行，系统引入以下检查机制：

- **本地预提交校验**：运行 `uv run python .agents/scripts/validation/validate_all.py` 进行综合检查。
- **Pre-commit Hook**：在代码提交阶段自动触发 `validate-skills` hook，检查 SKILL.md 合规性。
- **CI 管线校验**：PR 阶段自动执行完整验证套件，确保代码质量。
- **AI 智能体检查**：智能体在调用或初始化新技能前，必须主动检查对应的 `SKILL.md` 是否合规。若不合规，则拒绝执行相关操作并提醒开发者补充文档。
- **人工审查**：在 PR Review 阶段，架构师或审查者需确保技能文档的完整性与准确性。

### 5.3 校验配置

校验规则可通过 `.agents/skills/.validate-config.toml` 自定义：

```toml
[required_sections]
"Skill ID/Name" = "(?:Skill\\s*(?:ID|Name|唯一标识)|Name)"
"Description" = "(?:Description|功能描述|功能|用途|Summary)"
# ... 更多配置
```

### 5.4 跳过机制

如需临时跳过某个技能的校验，可在 `.agents/skills/.validate-skip` 文件中添加技能名称（每行一个）。

## 6. 模板复用
为方便开发者快速接入，官方提供了一份标准的模板文件。请在创建新技能时，直接复制并填写：
👉 **[SKILL.md 模板](../templates/SKILL.md)**
