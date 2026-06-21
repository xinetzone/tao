# AgentForge 竞品标准引用表（许可证 / 商业化 / 自托管 / 锁定风险）

> **用途**：为 AgentForge 相关的竞品分析、实施路线图、管理汇报、定价说明提供统一引用口径。  
> **适用范围**：内部技术文档 + 对外报告草稿。  
> **最后校准**：2026-06-22

---

## 1. 使用原则

引用本表时，默认遵循以下四条规则：

1. **许可证看仓库实际授权**，以官方 `LICENSE` / 包元数据 / 官方文档为准。
2. **自托管不等于零商业限制**，必须区分“代码可部署”与“商业化分发是否受限”。
3. **锁定风险不只看许可证**，还要看云服务依赖、生态绑定、迁移成本、平台能力耦合。
4. **AgentForge 属于治理协议层**，不要用运行时框架的收费/锁定逻辑直接套用。

---

## 2. 标准引用总表

| 项目 | 协议 / 授权口径 | 商业化口径 | 自托管口径 | 锁定风险口径 | 标准短句 |
|------|------------------|------------|------------|--------------|----------|
| **AgentForge** | Apache 2.0 | 完全开源，零许可费 | 是，且核心形态为 Git 文件 | 极低 / 近零 | AgentForge 是 Apache 2.0 的治理协议层标准，零许可费、零运行时依赖、锁定风险近零。 |
| **LangChain** | MIT | 核心框架免费，LangSmith 付费 | 框架可自用，生产观测常借助 LangSmith | 中 | LangChain 框架本身是 MIT，但生产观测与工作流习惯常向 LangSmith 收敛，存在中度生态锁定。 |
| **CrewAI** | MIT | 核心框架免费，AMP/云平台付费 | 可选自托管 | 中 | CrewAI 是 MIT，但企业能力往往通过 AMP 承接，因此存在中度平台绑定。 |
| **AutoGen** | MIT（代码） / CC BY 4.0（文档） | 核心免费，企业承接常转向 Microsoft 路线 | 是 | 中 | AutoGen 代码是 MIT、文档是 CC BY 4.0；由于维护模式与 Microsoft 迁移路径，存在中度迁移依赖。 |
| **Dify** | Apache 2.0 + 附加商业限制条款 | 核心可用，但商业化分发 / 白标化需谨慎评估 | 是 | 低-中 | Dify 以 Apache 2.0 为基础且支持自托管，但存在附加商业限制条款，因此“可自托管”不等于“零商业限制”。 |
| **OpenAI Agents SDK** | MIT | SDK 免费，API 用量计费 | 是 | 中 | OpenAI Agents SDK 是 MIT，但在模型能力、Tracing 和平台体验上仍与 OpenAI 生态深度耦合。 |
| **Inkog** | Apache 2.0 | 开源基础 + 扫描额度 / 企业版 | 是 / 可选 | 低 | Inkog 是 Apache 2.0 的校验层工具，可替换性较高，锁定风险低。 |

---

## 3. 推荐固定表述

### 3.1 AgentForge

**推荐表述**

> AgentForge 的仓库根协议为 Apache 2.0。作为治理协议层标准，它不提供运行时，因此没有运行时许可费，也不存在典型框架级供应商锁定。

**不要写成**

- AgentForge 是 MIT
- AgentForge 需要 SaaS 才能使用
- AgentForge 与 LangChain/CrewAI 属于同类收费逻辑

---

### 3.2 Dify

**推荐表述**

> Dify 支持自托管，基础代码口径可归入 Apache 2.0，但在商业化分发与白标化场景下存在附加限制条款，因此不能简单等同于“标准 Apache 2.0 且零商业限制”。

**不要写成**

- Dify 是纯 Apache 2.0，完全没有额外商业限制
- Dify 可自托管，所以没有锁定风险

---

### 3.3 AutoGen

**推荐表述**

> AutoGen 需要区分代码与文档授权：代码侧为 MIT，文档侧为 CC BY 4.0。讨论许可证时不宜简单缩写为“纯 MIT”。

**不要写成**

- AutoGen 全部都是 MIT

---

### 3.4 OpenAI Agents SDK

**推荐表述**

> OpenAI Agents SDK 当前仓库授权为 MIT；其成本与锁定更多来自 API 使用和平台耦合，而不是许可证本身。

**不要写成**

- OpenAI Agents SDK 是 Apache 2.0

---

## 4. 文档写作时的统一分层

在任何分析文档里，建议把“许可证”“商业限制”“自托管”“锁定风险”拆开写，不要混成一句话。

| 维度 | 关注问题 | 示例 |
|------|----------|------|
| **许可证** | 法律授权是什么？ | Apache 2.0 / MIT / CC BY 4.0 |
| **商业限制** | 是否允许白标、SaaS 分发、商用再包装？ | Dify 需单独评估附加条款 |
| **自托管** | 能不能自己部署运行？ | Dify、LangChain、CrewAI 都可以在一定程度上自托管 |
| **锁定风险** | 迁移出去难不难？是否依赖生态/平台能力？ | LangSmith、AMP、OpenAI 平台体验依赖 |

---

## 5. 可直接复用的话术模板

### 模板 A：路线图 / 技术方案

> AgentForge 采用 Apache 2.0 协议，作为治理协议层标准可零许可费引入。需要注意，协议宽松并不自动等于所有竞品都同样宽松：例如 Dify 虽支持自托管，但商业化分发仍需结合附加限制条款评估。

### 模板 B：竞品分析

> 在许可证层面，AgentForge（Apache 2.0）、LangChain（MIT）、CrewAI（MIT）都属于宽松开源；但在商业限制与锁定风险层面差异明显。尤其 Dify 不能仅按“Apache 2.0”理解，而应补充其附加商业限制条款与白标化边界。

### 模板 C：管理汇报

> 从治理投入视角看，AgentForge 的优势不只是“免费”，而是以 Apache 2.0 协议提供零运行时依赖的治理层能力；相比之下，其他框架即便核心代码免费，也常在云观测、平台能力或商业化限制上引入额外约束。

---

## 6. 当前仓内已对齐文档

以下文档已按本表口径完成校准：

- [agentforge-competitive-analysis-2026.md](file:///d:/spaces/AgentForge/apps/chaos/docs/tech/agentforge-competitive-analysis-2026.md)
- [agents-md-implementation-roadmap.md](file:///d:/spaces/AgentForge/apps/chaos/docs/tech/agents-md-implementation-roadmap.md)
- [LICENSE](file:///d:/spaces/AgentForge/LICENSE)

---

## 7. 维护建议

后续若继续扩展竞品矩阵，新增项目时建议按以下顺序校准：

1. 先看官方 `LICENSE` / PyPI 元数据 / 官方文档
2. 再判断是否有附加商业限制条款
3. 再判断是否支持自托管
4. 最后单独评估锁定风险

如果四步没有分别确认，不要直接写总结性判断。
