# 第 4 章 · 关键决策

### 4.1 双层结构 vs 单层定义

**选项**：
- A. 单层"实体定义"（只定义有什么实体和关系）
- B. MetaModel Layer + Governance Layer 双层并存

**决策**：B

**依据**：单层只回答"是什么"，缺少"怎么做"的约束层。协作的核心问题不是"有哪些实体"，而是"实体之间应该如何交互"。Governance Layer 承载强约束（如 Agent 必须通过 Role 进入协作），是这个体系的核心价值。

**事后评估**：✅ 正确。Role Review 工作流的四道门禁直接引用 Governance Layer 的强约束，证明了双层结构的实践价值。

### 4.2 角色数量：4 个覆盖 5 领域

**选项**：
- A. 5 个角色（每个领域一个）
- B. 3 个角色（合并相近领域）
- C. 4 个角色（一个角色双域覆盖）

**决策**：C（collaboration-architect 同时覆盖 Governance + Knowledge）

**依据**：Governance 域已有 governance-auditor 负责 Policy/Permission，但元模型语义维护（目录映射、字段规范）需要一个独立角色，且该角色天然需要 Knowledge 域的知识引用能力。

**事后评估**：✅ 合理。Phase 4 的 Team 审查扩展验证了 collaboration-architect 的双域定位在审查"字段完整性"和"引用有效性"时具有独特价值。

### 4.3 自指验证：用已有角色审查自身

**选项**：
- A. 创建独立审查工作流，不与现有资产关联
- B. 让 4 个已有角色按顺序互相审查

**决策**：B

**依据**：如果设计出来的角色和约束自己用不上，就证明设计有问题。让 Organization Steward 审查角色的组织归属、Execution Orchestrator 审查执行边界是"吃自己的狗粮"（dogfooding），能发现设计缺陷。

**事后评估**：✅ 成功。4 Gate 全部通过，无驳回，且审查记录本身也遵循了 Handoff 协议。验证了元模型的闭环一致性。

### 4.4 渐进式目录演进：roles/ → teams/ 而非一次性铺开

**选项**：
- A. 一次性创建 roles/ + teams/ + agents/ + policies/
- B. 先试点 roles/，稳定后再 teams/，最后 agents/

**决策**：B

**依据**：目录演进属于实例承载层而非元模型定义，不需要为了"完整"而一次性创建。每次试点都验证了上一层的稳定语义，降低设计返工成本。

**事后评估**：✅ 成功。Phase 4 的 Team 六字段模板建立在 Phase 2 的 Role 四字段模式之上，Cross-Team Policy 和 Member Roles 的语义只有 Role 稳定后才能定义清楚。

### 4.5 审查机制复用：Team 复用 Role Review 而非另建

**选项**：
- A. 为 Team 单独创建审查工作流
- B. 复用 Role Review 的四道门禁，做 Gate 检查标准适配
- C. 仅自审清单，不走正式门禁

**决策**：B

**依据**：Team 和 Role 同属 Organization 域，且 Team 的审查维度（组织归属/执行影响/语义一致性/合规）与 Role 高度重叠。复用门禁框架 + 适配检查标准是 DRY 原则在治理层的体现。

**事后评估**：✅ 合理。四道 Gate 的 Team 适配只需调整检查项用词（如"Domain 归属"→"Domain 固定为 Organization"），框架结构完全不变。
