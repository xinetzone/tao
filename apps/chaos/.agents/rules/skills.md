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

本规范采用 **双模式校验**，以兼顾项目自有 Skills 的文档完备性与外部生态 Skills 的导入友好性：

- **strict 模式（默认）**：项目自有 Skills 保持全部 7 章节强制，确保文档完备性，是 PR/CI 的默认行为。
- **relaxed 模式**：外部导入或从 [agentskills.io](https://agentskills.io/home) 发布生态获取的 Skills 仅要求最小集（**Skill ID/Name + Description**），与官方标准对齐，避免对第三方 Skills 形成过度约束。

模式可通过校验脚本 `--mode strict|relaxed` 参数切换，或在 `.validate-config.toml` 的 `[mode]` 段配置默认值。

### 3.1 必填章节（强制，两种模式均必填）

每个技能的 `SKILL.md` 必须包含以下章节，无论 strict 还是 relaxed 模式：

1. **技能唯一标识 (Skill ID / Name)**：全局唯一的标识符，通常与技能目录名一致。
2. **功能描述 (Description)**：清晰说明该技能的用途、使用场景及核心能力。

> 上述两项是与 agentskills.io 标准对齐的最小集，确保任何 SKILL.md 均可被识别和路由。

### 3.2 推荐章节（strict 模式必填，relaxed 模式仅推荐）

以下章节在 **strict 模式下与必填章节同等强制**；在 **relaxed 模式下仅作推荐**，缺失只产生 WARN，不阻断校验：

1. **输入输出参数定义 (I/O Parameters)**：
   - **输入 (Input)**：参数名称、类型、是否必填、默认值及说明。
   - **输出 (Output)**：返回结果的数据结构和预期格式。
2. **依赖项说明 (Dependencies)**：该技能运行所需要的系统库、第三方包、环境变量或其他前置条件。
3. **部署要求 (Deployment)**：技能的安装、配置或初始化步骤。
4. **错误处理规范 (Error Handling)**：常见错误码、异常场景及应对策略。
5. **版本记录 (Changelog)**：记录技能的版本变更历史及更新内容。

### 3.3 建议章节（推荐，两种模式均不强制）

以下章节虽非强制，但强烈建议补充以提升文档质量：

1. **快速开始 (Quick Start)**：入门指南和最常用调用方式示例。
2. **执行流程 (Execution Flow)**：技能执行的详细流程说明。
3. **最佳实践 (Best Practices)**：使用建议、注意事项和常见问题解答（FAQ）。

### 3.4 Markdown 格式规范

- **中文标题锚点**：所有中文标题必须使用显式 MyST 锚点，例如 `(my-anchor)=`
- **链接格式**：项目内引用使用相对路径，外部链接使用完整 URL
- **标题层级**：建议只有一个 H1 标题，使用 H2-H4 组织内容

## 4. 技能目录结构

```
skills/<skill-name>/
├── SKILL.md           # 技能文档（必需）
├── scripts/           # 技能实现脚本（推荐）
│   └── *.py
├── tests/             # 测试文件（推荐，等同于 agentskills.io 的 evals/）
│   └── *.py
├── evals/             # 评测集（推荐，与 tests/ 等价，侧重端到端评估）
│   └── *.json
├── schemas/           # JSON Schema 定义（可选）
├── references/        # 参考文档（可选）
└── assets/            # 静态资源（可选，如模板、图标）
```

> **命名说明**：`tests/` 与 `evals/` 均为有效目录名称。`tests/` 侧重单元测试与脚本正确性验证；`evals/` 遵循 agentskills.io 标准命名，侧重端到端评估与基准测试。项目内两者均可使用，校验工具同等识别。

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

#### 双模式适用场景

| 场景 | 推荐模式 | 说明 |
|------|----------|------|
| 项目自有 Skills（位于 `.agents/skills/` 内的本地 Skills） | `strict` | 保持 7 章节完整性，确保文档可维护、可移交 |
| Pre-commit Hook / 默认 CI | `strict` | 阻止低质量文档进入主仓 |
| 从 agentskills.io 拉取/导入的外部 Skills | `relaxed` | 仅校验最小集（Name + Description），避免与上游标准冲突 |
| Skills 注册表（registry-index）抓取入库 | `relaxed` | 跨生态互通时容忍上游章节差异 |
| 临时探索/试验型 Skills | `relaxed` | 降低快速迭代时的文档负担 |

切换方式：`uv run python .agents/scripts/validation/validate_skill_md.py --mode relaxed`。

### 5.3 校验配置

校验规则可通过 `.agents/skills/.validate-config.toml` 自定义：

```toml
# 校验模式: strict = 全部必填, relaxed = 仅 Name + Description
[mode]
default = "strict"

[required_sections]
# 两种模式下均强制
"Skill ID/Name" = "(?:Skill\\s*(?:ID|Name|唯一标识)|Name)"
"Description" = "(?:Description|功能描述|功能|用途|Summary)"

[recommended_sections]
# strict 模式下视为必填，relaxed 模式下仅产生 WARN
"I/O Parameters" = "(?:I/?O\\s*Parameters?|Input|Output|输入|输出|Parameters?)"
"Dependencies" = "(?:Dependencies?|依赖|依赖项|Requirements?)"
"Deployment" = "(?:Deployment|部署|Install|安装|Setup|配置)"
"Error Handling" = "(?:Error\\s*Handling|错误|异常|handling)"
"Changelog" = "(?:Changelog|版本|Version|History|变更|更新记录)"
```

### 5.4 跳过机制

如需临时跳过某个技能的校验，可在 `.agents/skills/.validate-skip` 文件中添加技能名称（每行一个）。

## 6. 模板复用
为方便开发者快速接入，官方提供了一份标准的模板文件。请在创建新技能时，直接复制并填写：
👉 **[SKILL.md 模板](../templates/SKILL.md)**
