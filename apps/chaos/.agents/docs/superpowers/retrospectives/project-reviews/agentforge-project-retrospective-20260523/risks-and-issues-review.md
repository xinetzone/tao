# 三、风险与问题复盘

### 3.1 已识别风险清单

#### R1: Python 版本目标三态不一致

| 属性 | 值 |
|------|-----|
| **优先级** | **P1（高）** |
| **风险描述** | `pyproject.toml` 声明 `requires-python = ">=3.13"`、Ruff target `py313`、mise 实际运行 `3.14.5`、版本追踪目标 `3.15`。四个地方反映三种不同的 Python 版本"锚点"。 |
| **影响范围** | 代码规范（Ruff 规则）、CI 环境（mise install 的 Python 版本）、兼容性检测（check_python_compat.py 的检测面）、新成员上手（README 中声明的 Python 版本） |
| **当前应对** | `check_env.py` 验证 mise 实际安装的 Python 为 3.14.5；`check_python_compat.py` 独立扫描代码中的 Python 3.15 弃用项；`check_python_deprecations.py` 基于 AST 精确检测弃用 API。 |
| **残余风险** | Ruff target 未同步，导致 lint 阶段无法捕获 3.14+ 特有的语法问题。`requires-python >= 3.13` 过宽，允许用户在 Python 3.13 上安装但实际工具链要求 3.14.5。 |
| **优化建议** | 1. 将 Ruff target 更新为 `py314`；2. 考虑将 `requires-python` 收紧为 `>=3.14`；3. 在 check_env.py 中增加 Ruff target 与 mise Python 版本的一致性校验。 |

#### R2: frontend.md / backend.md 模板化导致路由空转

| 属性 | 值 |
|------|-----|
| **优先级** | **P2（中）** |
| **风险描述** | `AGENTS.md §2` 上下文路由指引 AI 在遇到前端/后端任务时读取 `frontend.md`/`backend.md`，但这两份文件当前为模板骨架，无法提供有效规范。 |
| **影响范围** | AI 智能体在处理前端/后端任务时的行为一致性、生成代码的质量 |
| **当前应对** | 两份文件均在顶部标注"注意：这是一份模板文件，请根据实际项目技术栈进行修改"。 |
| **残余风险** | 标注依赖于 AI 智能体主动读取并理解模板状态，实际执行中可能出现 AI 照搬模板内容的情况。 |
| **优化建议** | 1. 在 AGENTS.md 上下文路由中添加状态标注（如 "⚠️ 模板骨架，待填充"）；2. 制定填充计划，明确触发条件（如"当项目首个前端模块创建时"）；3. 考虑将模板文件移至 `.agents/templates/` 并创建实际文件时从模板复制。 |

#### R3: 技能 CHANGELOG 版本历史缺失

| 属性 | 值 |
|------|-----|
| **优先级** | **P2（中）** |
| **风险描述** | skill-creator 和 task-execution-summary 的 CHANGELOG 仅有 `[Unreleased]` 初始化记录，实际版本演进历史缺失。 |
| **影响范围** | 技能版本可追溯性、向后兼容性评估、新成员理解技能演进历程 |
| **当前应对** | 13 份复盘报告以非结构化方式记录了部分变更历史。 |
| **残余风险** | 复盘报告格式不统一，从复盘中提取版本变更信息需要人工阅读，成本高。 |
| **优化建议** | 1. 制定技能 CHANGELOG 回填计划，从现有复盘报告中提取关键变更节点；2. 将 CHANGELOG 更新纳入 spec 交付 checklist（当前 skills.md §3.7 已要求但未强制执行）；3. 在 check_env.py 或新增脚本中增加 CHANGELOG 完整性检查。 |

#### R4: Ruff target 与实际运行版本不一致

| 属性 | 值 |
|------|-----|
| **优先级** | **P1（高）** |
| **风险描述** | `tool.ruff.target-version = "py313"` 但 mise 实际安装 Python 3.14.5。详见 R1。 |
| **影响范围** | Lint 规则覆盖不完整，Python 3.14 新增语法特性不受 Ruff py313 规则约束 |
| **当前应对** | `check_python_deprecations.py` 提供独立于 Ruff 的弃用 API 检测。 |
| **残余风险** | 独立脚本仅检测弃用 API，不检测语法兼容性。 |
| **优化建议** | 立即将 `target-version` 更新为 `py314`，与 mise.toml 保持一致。 |

#### R5: defuddle 预装集成存在工具链复杂度

| 属性 | 值 |
|------|-----|
| **优先级** | **P3（低）** |
| **风险描述** | defuddle 通过 `npm:defuddle` 在 mise 中声明，依赖 Node.js 22.22.3。对于仅使用 Python 的开发者，Node.js 是一个额外依赖。 |
| **影响范围** | 环境初始化时间、工具链复杂度 |
| **当前应对** | `mise.toml` 中 defuddle 声明为 `depends = ["node"]`，`check_env.py` 中 defuddle 为最后一个校验项。 |
| **残余风险** | 如果 Node.js 安装失败，defuddle 不可用但 `mise install` 不会报错（取决于 depends 实现）。 |
| **优化建议** | 1. 在 `init-check` 中将 defuddle 标记为非关键依赖（仅在使用网页抓取功能时需要）；2. 考虑提供纯 Python 替代方案作为 fallback。 |

#### R6: Notion Mermaid 兼容性

| 属性 | 值 |
|------|-----|
| **优先级** | **P3（低）** |
| **风险描述** | AGENTS.md 中的 Mermaid 图表使用"主流 Markdown 环境兼容的基础语法子集"，但 Notion 等特定平台对 Mermaid 的渲染支持不完整。 |
| **影响范围** | 通过 Notion 或其他不支持完整 Mermaid 的平台查看 AGENTS.md 时的可读性 |
| **当前应对** | 图表下方保留文字说明兜底（如"该图用于表达...具体子目录边界仍以...为准"）。 |
| **残余风险** | 如果图表自身信息密度较高，纯文字兜底可能丢失部分信息。已在 `AGENTS.md` 中添加规则声明"避免私有扩展、实验性语法与可能导致整体渲染失败的复杂写法"。 |
| **优化建议** | 1. 在 `.agents/docs/` 中新增 Mermaid 兼容性说明，记录已知兼容/不兼容平台；2. 在 PR review checklist 中增加 Mermaid 可渲染性检查。 |

### 3.2 技术债务全景（来自 tech-debt-tracker.md）

| 类别 | 数量 | 紧迫度 | 说明 |
|------|------|--------|------|
| Python 3.15 已移除 | ~20 项 | 当前 | 项目代码需逐一排查是否使用了已移除 API |
| Python 3.16 计划移除 | ~12 项 | 高 | 下一版本将移除，需提前适配 |
| Python 3.17 计划移除 | ~8 项 | 中 | 有缓冲期 |
| Python 3.18+ 计划移除 | ~6 项 | 低 | 长期跟踪 |
| 未来移除（无具体日期） | ~35 项 | 低 | 持续监控 |
| C API 弃用 | ~20 项 | 视 C 扩展使用情况 | 本项目为纯 Python，影响较小 |

### 3.3 应对措施有效性评估

| 措施 | 覆盖风险 | 有效性 | 说明 |
|------|---------|--------|------|
| `check_env.py` 环境一致性校验 | R1, R4 | ⭐⭐⭐⭐ | 覆盖 7 个工具，输出清晰，但未检测 Ruff target 一致性 |
| `check_python_compat.py` 正则扫描 | R1, 技术债务 | ⭐⭐⭐ | 基于正则，可能在复杂语法下漏检 |
| `check_python_deprecations.py` AST 检测 | R1, 技术债务 | ⭐⭐⭐⭐⭐ | 基于 AST 精确定位，准确度高，覆盖 Ruff 盲区 |
| `citations.md` 引用策略 | 文档质量 | ⭐⭐⭐⭐⭐ | 三层优先级策略清晰，禁止绝对路径机制有效 |
| `version-tracking.md` 季度追踪 | R1, 技术债务 | ⭐⭐⭐⭐ | 机制完善，但依赖人工触发（下次检查 2026-08-21） |
| `skills.md` 三重检查机制 | R3 | ⭐⭐⭐ | 规范定义了自动化/AI/人工三层检查，但 CHANGELOG 检查未自动化 |
