# 执行流程文档 (Execution Flow)

本文档详细描述"任务执行总结报告生成器"技能的完整执行流程，包括各阶段的处理逻辑、数据流转、异常处理机制及性能特征。本文档面向开发者和技术维护人员，旨在提供深入理解技能内部工作原理的技术参考。

---

## 目录

- [1. 流程概述](#1-流程概述)
  - [1.1 设计原则](#11-设计原则)
  - [1.2 整体架构](#12-整体架构)
  - [1.3 关键性能指标](#13-关键性能指标)
- [2. 主执行流程](#2-主执行流程)
  - [Step 1: 参数解析与验证](#step-1-参数解析与验证)
  - [Step 2: 触发模式识别](#step-2-触发模式识别)
  - [Step 3: 信息收集阶段](#step-3-信息收集阶段)
  - [Step 4: 分析处理阶段](#step-4-分析处理阶段)
  - [Step 5: 报告生成阶段](#step-5-报告生成阶段)
  - [Step 6: 智能推荐生成](#step-6-智能推荐生成)
  - [Step 7: 质量检查与输出](#step-7-质量检查与输出)
- [3. 异常路径汇总](#3-异常路径汇总)
- [4. 性能基线](#4-性能基线)
- [5. 状态机说明](#5-状态机说明)
- [附录：错误码索引](#附录错误码索引)

---

## 1. 流程概述

### 1.1 设计原则

本技能的执行流程围绕三大核心设计原则构建：

#### 确定性 (Determinism)

```
┌─────────────────────────────────────────────────────┐
│                    确定性原则                         │
│                                                     │
│  • 相同输入 → 可复现的输出结构                       │
│  • 每个步骤有明确的输入/输出契约                      │
│  • 决策逻辑基于可量化的规则而非随机性                 │
│  • 默认值体系确保边界情况下的稳定行为                │
│                                                     │
│  实现方式：                                          │
│  - InternalConfig 统一配置对象                       │
│  - 类型化的数据模型（CollectedData, AnalysisReport） │
│  - 基于阈值的决策分支                                │
│  - 幂等的质量检查步骤                                │
└─────────────────────────────────────────────────────┘
```

确定性确保技能在相同条件下产生一致的结果。通过引入 `InternalConfig` 作为统一的内部配置对象，所有后续步骤都基于经过验证的标准化输入进行操作，消除了原始请求格式差异带来的不确定性。

#### 可观测性 (Observability)

```
┌─────────────────────────────────────────────────────┐
│                   可观测性原则                        │
│                                                     │
│  • 每个步骤产出可审查的中间结果                      │
│  • 关键决策点记录决策依据                            │
│  • 异常情况携带完整的上下文信息                      │
│  • 支持逐步调试和问题定位                            │
│                                                     │
│  实现方式：                                          │
│  - 结构化日志记录每个步骤的进入/退出                 │
│  - 中间数据对象的序列化能力                          │
│  - QualityMetrics 质量指标追踪                      │
│  - Warning/Error 层级的分级报告                     │
└─────────────────────────────────────────────────────┘
```

可观测性使得整个执行过程透明化。每个步骤的输入、处理过程、输出都被记录，便于在出现问题时快速定位原因，也支持对生成质量的持续监控。

#### 容错性 (Fault Tolerance)

```
┌─────────────────────────────────────────────────────┐
│                    容错性原则                         │
│                                                     │
│  • 非致命错误不阻断主流程                            │
│  • 支持降级运行（部分功能缺失时仍可产出）             │
│  • 清晰的错误分类和处理策略                          │
│  • 自动恢复和重试机制（适用场景）                    │
│                                                     │
│  实现方式：                                          │
│  - Error vs Warning 分级处理                        │
│  - Graceful Degradation 降级策略                    │
│  - 每步骤独立的错误捕获                              │
│  - 带警告的成功响应                                 │
└─────────────────────────────────────────────────────┘
```

容错性保证技能在面对不完美输入或局部故障时仍能交付有价值的结果。通过区分致命错误（Error）和非致命异常（Warning），系统可以在信息不完整的情况下降级运行，而不是完全失败。

### 1.2 整体架构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        任务执行总结报告生成器架构                         │
│                                                                         │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌───────┐ │
│  │  Step 1  │ → │  Step 2  │ → │  Step 3  │ → │  Step 4  │ → │Step 5 │ │
│  │ 参数解析 │   │ 模式识别 │   │ 信息收集 │   │ 分析处理 │   │ 报告生│ │
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘   └───┬───┘ │
│       │              │              │              │              │     │
│       ↓              ↓              ↓              ↓              ↓     │
│  InternalConfig  CollectionScope CollectedData  AnalysisReport DraftRpt│
│                                                                         │
│                                              ┌──────────┐   ┌───────┐  │
│                                              │  Step 6  │ → │Step 7 │  │
│                                              │ 推荐生成 │   │质检输│  │
│                                              └──────────┘   └───┬───┘  │
│                                                    │              │      │
│                                                    ↓              ↓      │
│                                              Recommendations  FinalResp │
│                                                                         │
│  ══════════════════════════════════════════════════════════════════    │
│                           数据流层 (Data Flow)                          │
│  ══════════════════════════════════════════════════════════════════    │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                      异常处理层 (Exception Layer)                │   │
│  │                                                                  │   │
│  │  E001-E005: 参数验证错误  → ❌ 直接返回 ErrorResponse            │   │
│  │  E010-E012: 数据质量问题  → ⚠️ 降级继续 / 用户选择               │   │
│  │  E021-E022: 分析引擎错误  → ⚠️ 部分跳过 / 降级输出              │   │
│  │  E031-E032: 报告生成错误  → ❌ 回退到简化模板                   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

**架构分层说明**：

| 层次 | 职责 | 包含组件 |
|------|------|---------|
| **执行流水线** | 按顺序执行7个处理步骤 | Step 1 ~ Step 7 |
| **数据流层** | 定义步骤间的数据传递格式 | InternalConfig, CollectionScope, CollectedData, AnalysisReport, DraftReport, Recommendations, FinalResponse |
| **异常处理层** | 统一管理各类错误的检测、分类和处理策略 | 错误码体系 (E001-E032) |

### 1.3 关键性能指标

以下是各阶段在典型任务场景下的预估耗时分布：

```
总耗时分布概览（标准版报告，中等复杂度任务）

Step 3 ████████████████████████████████░░░░░░░░  40-50%  (核心瓶颈)
Step 4 ██████████████████████████░░░░░░░░░░░░░░  35-40%
Step 5 ████████████████░░░░░░░░░░░░░░░░░░░░░░░  15-20%
Step 6 ████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   5-10%
Step 7 █░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   < 2%
Step 2 ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   < 2%
Step 1 ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   < 1%

总计：2-8 分钟（取决于对话长度和详细程度要求）
```

**主要性能影响因素**：

| 影响因素 | 对 Step 3 影响 | 对 Step 4 影响 | 对 Step 5 影响 |
|---------|---------------|---------------|---------------|
| 对话轮数 (< 20轮) | 低 (~30s) | 低 (~60s) | 低 (~30s) |
| 对话轮数 (20-50轮) | 中 (~60s) | 中 (~120s) | 中 (~60s) |
| 对话轮数 (> 50轮) | 高 (~120s) | 高 (~180s) | 高 (~120s) |
| 详细程度: 摘要版 | -30% | -40% | -50% |
| 详细程度: 标准版 | 基准 | 基准 | 基准 |
| 详细程度: 详细版 | +50% | +60% | +80% |

---

## 2. 主执行流程

### Step 1: 参数解析与验证

```
┌─────────────┐
│  接收请求    │ ──→ 解析 JSON/YAML 参数
└─────────────┘        │
                       ↓
              ┌──────────────────┐
              │  参数完整性检查   │
              │  • 必填参数存在?   │──→ ❌ → 返回 E001-E005
              │  • 类型正确?      │──→ ❌ → 返回 E002
              │  • 值在范围内?     │──→ ⚠️ → 返回 E003 或修正
              │  • 无参数冲突?     │──→ ❌ → 返回 E004
              └────────┬─────────┘
                       ↓ ✅
              ┌──────────────────┐
              │  应用默认值       │
              │  构建内部配置对象  │
              └────────┬─────────┘
                       ↓
              [进入 Step 2]
```

#### 输入

**原始请求**：可以是以下任一形式

| 输入类型 | 格式示例 | 处理方式 |
|---------|---------|---------|
| 结构化 JSON | `{"task_context": {"task_name": "xxx"}, "generation_options": {"detail_level": "standard"}}` | 直接解析 |
| 自然语言 | "帮我做个任务总结" | NLP 提取参数 |
| 快捷命令 | `/summary` 或 `/report` | 映射为默认配置 |
| 混合形式 | "生成详细版的总结，重点关注时间分析" | 组合解析 |

#### 处理逻辑

**1. 请求解析**

```python
# 伪代码示意
def parse_request(raw_input):
    # 尝试 JSON/YAML 解析
    if is_structured(raw_input):
        return parse_structured(raw_input)

    # NLP 提取自然语言中的参数
    extracted = nlp_extract_params(raw_input)

    # 命令映射
    if is_command(raw_input):
        return map_command_to_config(raw_input)

    return extract_from_natural_language(raw_input)
```

**2. 必填参数校验**

| 参数名 | 类型 | 是否必填 | 默认值 | 校验规则 |
|-------|------|---------|--------|---------|
| `task_name` | string | 是 | - | 非空，长度 2-200 |
| `detail_level` | enum | 否 | `"standard"` | `summary` / `standard` / `detailed` |
| `include_sections` | list | 否 | 全部10章 | 有效章节名列表 |
| `output_format` | enum | 否 | `"markdown"` | `markdown` / 当前支持格式 |
| `language` | enum | 否 | `"zh-CN"` | 支持的语言代码 |
| `time_range` | object | 否 | 全量 | `{start?, end?}` |

**3. 类型与范围校验**

```
校验优先级：
  ① 存在性检查 → 缺少必填参数 → E001 (缺少必填参数)
  ② 类型匹配 → 类型不符 → E002 (参数类型错误)
  ③ 值域范围 → 超出允许范围 → E003 (参数值越界) 或自动修正
  ④ 逻辑一致性 → 参数间冲突 → E004 (参数冲突)
  ⑤ 安全性检查 → 含非法内容 → E005 (安全策略违规)
```

**4. 默认值应用与配置构建**

当可选参数缺失时，按以下规则应用默认值：

```yaml
default_configuration:
  detail_level: standard          # 标准详细程度
  include_sections:               # 包含全部章节
    - executive_summary
    - background_objectives
    - execution_process
    - key_decisions
    - issues_solutions
    - resource_usage
    - team_collaboration          # 条件包含
    - multi_dimensional_analysis
    - lessons_methodologies
    - improvement_plan
  output_format: markdown        # Markdown 格式
  language: zh-CN                # 中文（简体）
  time_range: full               # 全量时间范围
  generation_options:
    with_recommendations: true    # 包含智能推荐
    with_risk_warning: true      # 包含风险预警
    quality_check: true          # 启用质量检查
```

#### 输出

| 输出类型 | 条件 | 说明 |
|---------|------|------|
| `InternalConfig` | 所有校验通过 | 标准化的内部配置对象 |
| `ErrorResponse` | 校验失败 | 包含错误码、错误描述、修复建议 |

**InternalConfig 结构**：

```typescript
interface InternalConfig {
  taskScope: string;
  detailLevel: 'summary' | 'standard' | 'detailed';
  includeSections: ChapterName[];
  outputFormat: OutputFormat;
  language: string;
  timeRange: TimeRange;
  generationOptions: GenerationOptions;
  rawRequest: string;           // 保留原始请求用于追溯
  parsedAt: Date;               // 解析时间戳
  validationWarnings?: string[]; // 非致命警告
}
```

#### 耗时预估

< 1 秒

#### 失败概率

低（< 5%，主要来自用户输入不规范）

---

### Step 2: 触发模式识别

```
┌──────────────────┐
│  识别触发模式     │
│                  │
│  • 自动触发       │ ← 检测到完成信号词
│  • 手动触发       │ ← 显式命令 (/summary)
│  • 命令行触发     │ ← 配置化参数
└────────┬─────────┘
         ↓
┌──────────────────┐
│  确认/调整范围   │
│  • 信息收集范围   │
│  • 时间窗口确认   │
│  • 用户意图澄清   │（如有歧义）
└────────┬─────────┘
         ↓
    [进入 Step 3]
```

#### 输入

`InternalConfig` （来自 Step 1 的标准化配置）

#### 处理逻辑

**1. 触发来源判定**

| 触发模式 | 判定条件 | 置信度要求 | 典型场景 |
|---------|---------|-----------|---------|
| **自动触发** | 检测到完成信号词 + 任务复杂度 > 中等 | > 70% | 用户说"好了"、"完成了"、"可以了" |
| **手动触发** | 显式命令关键词 | 100% | "请生成总结"、"/summary"、"做个复盘" |
| **命令行触发** | 配置化参数调用 | 100% | API 调用、脚本触发 |

**信号词检测库**：

```yaml
completion_signals:
  explicit:                  # 明确完成信号
    - "完成了"
    - "好了"
    - "成功了"
    - "可以了"
    - "搞定了"
    - "搞定"
    - "OK"
    - "没问题"

  implicit:                  # 隐含完成意图
    - "帮我总结一下"
    - "回顾一下"
    - "复盘"
    - "做得怎么样"
    - "有什么收获"
    - "记录一下"

  context_indicators:        # 上下文暗示
    - 连续多个操作后出现停顿
    - 用户切换话题前的过渡语
    - 询问保存或导出
```

**2. 收集范围确定**

```python
def determine_collection_scope(config: InternalConfig, context: ConversationContext) -> CollectionScope:
    # 时间窗口确定
    time_window = resolve_time_window(
        config.timeRange,
        context.taskStartTime,
        context.lastActivityTime
    )

    # 信息类别筛选
    categories = determine_info_categories(
        config.includeSections,
        context.taskType,
        context.participantCount
    )

    # 数据源选择
    data_sources = select_data_sources(
        available_sources=['conversation_history', 'file_changes', 'command_log'],
        required_by_categories=categories
    )

    return CollectionScope(
        timeWindow=time_window,
        infoCategories=categories,
        dataSources=data_sources,
        confidence=calculate_trigger_confidence(context)
    )
```

**3. 歧义处理策略**

| 歧义类型 | 检测条件 | 处理方式 | 默认假设 |
|---------|---------|---------|---------|
| 时间范围不明 | 未明确开始/结束点 | 使用全量范围 | 从首次需求到最后操作 |
| 任务边界模糊 | 多个任务交织 | 询问或使用最近的主任务 | 最近一个完整任务周期 |
| 协作信息存疑 | 不确定是否涉及多人 | 检测参与者数量 | 单人模式（如无多人迹象） |

#### 输出

**CollectionScope（收集范围定义）**：

```typescript
interface CollectionScope {
  timeWindow: {
    start: Date;
    end: Date;
    estimatedDuration: number;  // 分钟
  };
  infoCategories: InfoCategory[];  // 需要收集的信息类别
  dataSources: DataSource[];       // 启用的数据源
  triggerMode: 'auto' | 'manual' | 'command';
  confidence: number;              // 0-1, 触发置信度
  clarificationsApplied: string[]; // 应用的歧义消除措施
}
```

#### 耗时预估

< 2 秒

---

### Step 3: 信息收集阶段

> **注意**：这是整个流程的核心阶段，也是最复杂的步骤，通常占总耗时的 40-50%。

```
                    ┌──────────────────────┐
                    │   Step 3: 信息收集    │
                    │                      │
   ┌────────────────┤  3.1 数据源适配      ├────────┐
   │                │  • 对话历史解析器     │        │
   │  数据源层      │  • 操作记录提取器     │        │
   │                │  • 文件变更追踪器     │        │
   └────────────────┤                      ├────────┤
                    │  3.2 信息抽取         │        │
                    │  • 实体识别           │        │
   ┌────────────────┤  • 关系抽取           ├────────┤
   │                │  • 事件检测           │        │
   │  抽取层        │                      │        │
   └────────────────┤  3.3 数据整合         ├────────┤
                    │  • 清洗去重           │        │
   ┌────────────────┤  • 缺失值处理         │        │
   │                │  • 一致性校验         │        │
   │  整合层        │                      │        │
   └────────────────┤  3.4 质量检查         ├────────┘
                    │  • 完整性检查         │
                    │  • 准确性验证         │
                    │  • 缺口检测           │
                    └──────────┬───────────┘
                               ↓
                   ┌────────────────────┐
                   │  CollectedData      │
                   │  (结构化数据集)      │
                   └────────────────────┘
```

#### 输入

`CollectionScope` （来自 Step 2）

#### 子步骤详解

##### 3.1 数据源适配

**对话历史解析器 (ConversationHistoryParser)**

职责：扫描消息列表，提取任务相关的关键信息。

```python
class ConversationHistoryParser:
    """对话历史解析器"""

    def parse(self, messages: Message[], scope: CollectionScope) -> RawTaskData:
        # 1. 按时间戳排序
        sorted_messages = sort_by_timestamp(messages)

        # 2. 过滤时间范围内的消息
        filtered = filter_by_time_range(sorted_messages, scope.timeWindow)

        # 3. 识别消息角色和类型
        annotated = annotate_message_roles(filtered)

        # 4. 提取任务相关内容
        task_related = extract_task_content(annotated)

        return task_related
```

**提取重点**：
- 任务启动时的初始需求和目标定义
- 执行过程中的关键决策点和转折点
- 遇到的问题及解决方案描述
- 最终成果确认和用户反馈

**操作记录提取器 (OperationRecordExtractor)**

职责：识别并提取具体的操作行为记录。

| 操作类型 | 识别模式 | 提取字段 |
|---------|---------|---------|
| 文件读写 | 文件路径 + 操作动词 | path, action, content_preview |
| 命令执行 | Shell 命令模式 | command, output, exit_code |
| 代码修改 | diff/patch 格式 | file, changes, lines_affected |
| 工具调用 | 工具名 + 参数 | tool_name, params, result |

**文件变更追踪器 (FileChangeTracker)**

职责：获取文件系统的变更记录。

```yaml
tracking_capabilities:
  - git_diff:              # Git 差异对比
      source: "git diff HEAD~1"
      fields: [changed_files, insertions, deletions, modifications]

  - file_system_events:    # 文件系统事件
      source: "FS watcher log"
      fields: [created, modified, deleted, moved]

  - dependency_changes:    # 依赖变更
      source: "package manager lock files"
      fields: [added_deps, removed_deps, version_changes]
```

##### 3.2 信息抽取

从原始数据中抽取出6大类别结构化信息：

| 类别 | 抽取目标 | 关键信号词/模式 | 输出结构 |
|------|---------|----------------|---------|
| **任务目标实体** | 目标关键词、成功标准 | "目标是"、"需要实现"、"期望" | ObjectiveEntity[] |
| **时间节点实体** | 时间表达、阶段划分 | "T+Xmin"、"第一阶段"、"当时" | TimelineEntity[] |
| **决策实体** | 选择行为、依据 | "决定用"、"选择了"、"改为"、"采用" | DecisionEntity[] |
| **问题实体** | 错误、异常、困难 | "报错"、"出错"、"不行"、"为什么" | IssueEntity[] |
| **资源实体** | 工具、框架、服务 | 工具名、库名、框架名 | ResourceEntity[] |
| **协作实体** | 团队角色、分工 | 人名、角色词、"你/我/我们" | CollaborationEntity[] |

**实体识别示例**：

```
原文："我决定用 React 而不是 Vue，因为团队更熟悉 React 的生态"

抽取结果：
  - 决策实体:
      type: DECISION
      content: "选择 React 而非 Vue"
      chosen_option: "React"
      rejected_options: ["Vue"]
      rationale: "团队更熟悉 React 的生态"
      timestamp: T+Xmin
  - 资源实体:
      type: RESOURCE
      category: FRAMEWORK
      name: "React"
      usage_reason: "技术选型结果"
```

##### 3.3 数据整合

**去重处理**：同一事件可能出现在多个数据源中

```python
def deduplicate_entities(entities: Entity[], sources: DataSource[]) -> Entity[]:
    """
    去重策略：
    1. 基于内容相似度聚类（> 90% 视为重复）
    2. 保留信息最完整的版本
    3. 合并不同源的补充信息
    4. 记录去重元数据
    """
    clustered = cluster_by_similarity(entities, threshold=0.9)
    deduplicated = merge_clusters(clustered, strategy='keep_richest')
    return deduplicated
```

**时序对齐**：统一不同数据源的时间基准

```
时间基准统一规则：
  - 对话消息：使用消息时间戳
  - 文件变更：使用 git commit 时间或文件修改时间
  - 命令执行：使用命令执行完成时间
  - 统一格式：ISO 8601 (YYYY-MM-DDTHH:mm:ssZ)
  - 相对时间：转换为绝对时间（以任务开始时间为基准）
```

**关联建立**：将相关实体建立关联关系

```yaml
association_rules:
  decision_to_issue:           # 决策引发的问题
    pattern: "决策后出现的问题"
    link: decision.issue_caused

  issue_to_solution:           # 问题及其解决方案
    pattern: "问题-解决对"
    link: issue.solution_for

  resource_to_decision:        # 资源支撑的决策
    pattern: "决策使用的资源"
    link: decision.resources_used

  timeline_to_event:           # 时间节点对应的事件
    pattern: "时刻发生的事件"
    link: timeline.events_at
```

##### 3.4 质量检查

**完整性评分**：

| 信息类别 | 权重 | 覆盖率计算方式 | 评级阈值 |
|---------|------|---------------|---------|
| 任务目标 | 25% | (已提取目标数 / 应有目标数) × 100% | >90% 优, 70-90% 良, <70% 差 |
| 时间节点 | 20% | (已标记节点数 / 总阶段数) × 100% | 同上 |
| 决策记录 | 20% | (已记录决策数 / 检测到的决策信号数) × 100% | 同上 |
| 问题记录 | 20% | (已记录问题数 / 检测到的问题信号数) × 100% | 同上 |
| 资源使用 | 10% | (已统计资源数 / 检测到的资源引用数) × 100% | 同上 |
| 协作信息 | 5% | (如有协作则计算覆盖率，否则豁免) | 同上 |

**阈值判断与处理**：

```
综合覆盖率 ≥ 90%:  ✅ 优秀 — 直接进入下一步
综合覆盖率 70-90%: ⚠️ 良好 — 发出 E010 警告，标注缺失项，继续
综合覆盖率 < 70%:  ❌ 差   — 发出 E011 错误，提示用户选择：
                                  A. 降级继续（接受信息不全）
                                  B. 补充信息后重新生成
                                  C. 终止本次生成
```

#### 输出

| 输出类型 | 条件 | 说明 |
|---------|------|------|
| `CollectedData` | 质量检查通过或用户选择降级 | 结构化的完整数据集 |
| `E010` (Warning) | 覆盖率 70-90% | 带警告的数据集 |
| `E011` (Error) | 覆盖率 < 70% 且未选择降级 | 数据不足错误 |
| `E012` (Error) | 数据源不可用 | 数据获取失败 |

**CollectedData 结构**：

```typescript
interface CollectedData {
  metadata: {
    collectionTime: Date;
    dataSourceStats: Record<DataSource, number>;  // 各源提取条数
    qualityScore: number;                          // 0-100 综合质量分
    coverageByCategory: Record<InfoCategory, number>;
    warnings?: string[];
  };

  taskInfo: {
    objectives: ObjectiveEntity[];
    timeline: TimelineEntity[];
  };

  executionInfo: {
    decisions: DecisionEntity[];
    issues: IssueEntity[];
    operations: OperationRecord[];
  };

  resourceInfo: {
    resources: ResourceEntity[];
    dependencies: DependencyInfo[];
  };

  collaborationInfo?: {           // 条件字段
    participants: Participant[];
    communications: CommunicationEvent[];
  };
}
```

#### 耗时预估

30-120 秒（取决于对话长度和数据量）

---

### Step 4: 分析处理阶段

```
┌─────────────────────────────────────────────┐
│            Step 4: 五维分析引擎               │
│                                             │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐      │
│  │ 4.1 目标  │→│ 4.2 时间 │→│ 4.3 资源 │      │
│  │ 达成度   │ │ 效能    │ │ 利用率  │      │
│  └─────────┘ └─────────┘ └─────────┘      │
│         ↓                                   │
│  ┌─────────┐ ┌─────────┐                   │
│  │ 4.4 问题 │→│ 4.5 协作 │(条件)          │
│  │ 模式    │ │ 效果    │                   │
│  └─────────┘ └─────────┘                   │
│         ↓                                   │
│  ┌─────────────────────────┐              │
│  │   AnalysisReport        │              │
│  │   (五维分析结果)        │              │
│  └─────────────────────────┘              │
└─────────────────────────────────────────────┘
```

#### 输入

`CollectedData` （来自 Step 3）

#### 分析维度详解

##### 4.1 目标达成度分析 (Objective Achievement Analysis)

**分析方法**：对比法 + 量化评估

```
分析流程：
  目标分解 → 基线建立 → 逐项测量 → 偏差计算 → 综合评定
```

| 子步骤 | 操作 | 输出 |
|-------|------|------|
| 目标分解 | 将总目标拆解为子目标和关键指标 | SubGoal[] |
| 基线建立 | 记录初始期望值和验收标准 | Baseline |
| 逐项测量 | 对照最终成果逐项评估 | Measurement[] |
| 偏差计算 | 达成率 = 实际值/期望值 × 100% | Deviation[] |
| 综合评定 | 加权计算总体达成度 | AchievementResult |

**评判标准**：

| 达成等级 | 达成率范围 | 评定说明 |
|---------|-----------|---------|
| 优秀 (Excellent) | ≥ 95% | 超额或完美达成预期目标 |
| 良好 (Good) | 85% - 94% | 基本达成，有小幅超出或轻微不足 |
| 合格 (Acceptable) | 70% - 84% | 核心目标达成，次要目标有差距 |
| 待改进 (Needs Improvement) | < 70% | 未达预期，需深入分析原因 |

##### 4.2 时间效能分析 (Time Efficiency Analysis)

**分析方法**：偏差计算 + 瓶颈识别

**核心效能指标**：

| 指标名称 | 计算公式 | 说明 |
|---------|---------|------|
| 总体时效比 | 总预估时间 / 总实际时间 | >1表示超时，<1表示提前 |
| 阶段均衡度 | max(各阶段占比) / avg(各阶段占比) | 越接近1越均衡 |
| 瓶颈集中度 | 最长阶段时长 / 总时长 | 反映瓶颈严重程度 |
| 响应延迟 | 问题发现到解决的时间间隔 | 反应急反应速度 |
| 有效工作率 | 净工作时间 / 总工作时间 | 反映时间利用效率 |

**常见时间浪费模式识别**：

| 模式 | 特征表现 | 典型原因 | 改进方向 |
|------|---------|---------|---------|
| 前期拖沓 | 准备阶段过长 | 需求不清、环境问题 | 提前准备、明确需求 |
| 中段膨胀 | 核心执行阶段超预期 | 复杂度低估、反复修改 | 更准确的估算、MVP思维 |
| 尾部拖延 | 收尾阶段迟迟不完 | 完美主义、疲劳 | 设定截止时间、降低收尾标准 |
| 等待黑洞 | 大量等待时间 | 依赖阻塞、审批慢 | 异步并行、预先协调 |
| 反复返工 | 同一阶段多次重来 | 方案不当、理解偏差 | 加强前期设计、及时确认 |

##### 4.3 资源利用率分析 (Resource Utilization Analysis)

**分析方法**：利用率计算 + 浪费识别

**资源效用评估维度**：

| 评估维度 | 评估问题 | 评分标准(1-5) |
|---------|---------|--------------|
| 必要性 | 这项资源是否真的必要？ | 5=不可或缺, 1=完全可以不用 |
| 充分性 | 这项资源的能力是否被充分利用？ | 5=物尽其用, 1=大材小用 |
| 适配性 | 这项资源是否适合当前任务？ | 5=完美匹配, 1=严重错配 |
| 性价比 | 获得这项资源的成本是否值得？ | 5=超高性价比, 1=得不偿失 |

**浪费类型检测**：

```yaml
waste_patterns:
  tool_waste:           # 工具浪费
    indicators: ["引入但未使用", "过度复杂工具做简单事"]
  time_waste:           # 时间浪费
    indicators: ["低优先级任务过多", "重复手动操作"]
  cognitive_waste:      # 认知浪费
    indicators: ["重复解决已知问题", "过度追求完美"]
  collaboration_waste:  # 协作浪费（条件）
    indicators: ["沟通成本过高", "重复劳动"]
```

##### 4.4 问题模式分析 (Issue Pattern Analysis)

**分析方法**：分类统计 + 有效性评估

**问题分类体系**：

```yaml
issue_taxonomy:
  technical:            # 技术层面
    - code_defect       # 代码缺陷
    - architecture_issue # 架构设计问题
    - performance_bottleneck # 性能瓶颈
    - compatibility_issue # 兼容性问题
    - security_vulnerability # 安全漏洞

  environmental:        # 环境层面
    - config_error      # 配置错误
    - dependency_conflict # 依赖冲突
    - resource_shortage # 资源不足
    - network_issue     # 网络问题

  process:              # 流程层面
    - unclear_requirements # 需求不明确
    - poor_communication # 沟通不畅
    - insufficient_testing # 缺乏测试
    - missing_documentation # 文档缺失

  cognitive:            # 知识层面
    - knowledge_gap     # 技术盲区
    - inexperience      # 经验不足
    - misunderstanding  # 理解偏差
```

**解决有效性评估矩阵**：

| 解决方案 | 彻底性 | 副作用 | 可复用性 | 综合评价 |
|---------|--------|--------|---------|---------|
| 彻底解决 | ✅ 无残留 | 无 | 高 | ⭐⭐⭐⭐⭐ |
| 临时规避 | ⚠️ 可能复发 | 小 | 中 | ⭐⭐⭐☆☆ |
| 引入新问题 | ❌ 有遗留 | 有 | 低 | ⭐⭐☆☆☆ |

##### 4.5 协作效果分析 (Collaboration Effectiveness Analysis)

> **条件启用**：仅当检测到多人协同时执行此维度分析

**评估维度**：

| 维度 | 评分(1-5) | 优秀(5) | 良好(4) | 一般(3) | 待改进(2) | 差(1) |
|------|----------|---------|---------|---------|----------|-------|
| 沟通效率 | ⬜⬜⬜⬜⬜ | 即时精准 | 及时准确 | 基本通畅 | 有延误误解 | 频繁障碍 |
| 分工合理 | ⬜⬜⬜⬜⬜ | 完美匹配 | 基本合理 | 大致合适 | 局部不合理 | 严重失衡 |
| 协同效果 | ⬜⬜⬜⬜⬜ | 无缝配合 | 高效协同 | 正常协作 | 有摩擦阻力 | 严重内耗 |

#### 输出

| 输出类型 | 条件 | 说明 |
|---------|------|------|
| `AnalysisReport` | 分析成功完成 | 包含五维分析结果的完整报告 |
| `E021` (Warning) | 部分维度数据不足 | 带警告的部分分析结果 |
| `E022` (Error) | 核心分析失败 | 分析引擎错误 |

**AnalysisReport 结构**：

```typescript
interface AnalysisReport {
  objectiveAchievement: {
    overallRate: number;           // 0-100
    grade: 'excellent' | 'good' | 'acceptable' | 'needs_improvement';
    subGoals: SubGoalAnalysis[];
    deviations: DeviationAnalysis[];
  };

  timeEfficiency: {
    totalTime: number;             // 分钟
    phases: PhaseAnalysis[];
    metrics: EfficiencyMetrics;
    bottlenecks: BottleneckIdentification[];
    wastePatterns: WastePattern[];
  };

  resourceUtilization: {
    resources: ResourceAssessment[];
    wasteSummary: WasteSummary;
    optimizationOpportunities: OptimizationSuggestion[];
  };

  issuePatterns: {
    totalIssues: number;
    distribution: IssueDistribution;
    topPatterns: PatternIdentification[];
    solutionEffectiveness: SolutionEffectivenessMatrix;
  };

  collaborationEffectiveness?: {   // 条件字段
    overallScore: number;           // 0-15
    dimensions: DimensionScore[];
    highlights: string[];
    improvements: ImprovementArea[];
  };

  summary: {
    keyFindings: string[];
    overallAssessment: string;
    dataQualityNote: string;
  };
}
```

#### 耗时预估

60-180 秒（取决于数据量和分析深度）

---

### Step 5: 报告生成阶段

```
┌──────────────────────────────────────────┐
│          Step 5: 报告生成引擎             │
│                                          │
│  AnalysisReport                          │
│       ↓                                  │
│  ┌─────────┐                             │
│  │ 5.1 选择  │ ← 根据 generation_options  │
│  │   模板   │   选择模板变体              │
│  └────┬────┘                             │
│       ↓                                  │
│  ┌─────────┐                             │
│  │ 5.2 映射  │ ← 分析结果 → 模板字段     │
│  │   数据   │                             │
│  └────┬────┘                             │
│       ↓                                  │
│  ┌─────────┐                             │
│  │ 5.3 填充  │ ← 动态内容生成            │
│  │   内容   │   （文本、表格、列表）      │
│  └────┬────┘                             │
│       ↓                                  │
│  ┌─────────┐                             │
│  │ 5.4 优化  │ ← 格式化、排版            │
│  │   格式   │                             │
│  └────┬────┘                             │
│       ↓                                  │
│  ┌─────────┐                             │
│  │ 5.5 润色  │ ← 语言专业性检查          │
│  │   语言   │                             │
│  └────┬────┘                             │
│       ↓                                  │
│  DraftReport (草稿报告)                   │
└──────────────────────────────────────────┘
```

#### 输入

- `AnalysisReport` （来自 Step 4）
- `InternalConfig` （来自 Step 1，用于确定模板和格式选项）
- `CollectedData` （来自 Step 3，用于填充具体细节）

#### 子步骤详解

##### 5.1 模板选择

根据 `InternalConfig.detailLevel` 选择对应的模板变体：

| 详细程度 | 模板变体 | 包含章节 | 预计篇幅 |
|---------|---------|---------|---------|
| `summary` | 摘要版模板 | 第1章(完整) + 第10章(摘要) + 其他(标题+要点) | 500-800字 |
| `standard` | 标准版模板 | 全部10章（标准详细度） | 3000-5000字 |
| `detailed` | 详细版模板 | 全部10章（深度展开）+ 完整附录 | 8000-15000字 |

**章节定制处理**：

```python
def apply_section_customization(base_template, config: InternalConfig):
    """
    根据 config.includeSections 进行章节裁剪：
    - 基础章节（第1,2,3,5,9,10章）：建议始终保留
    - 可选章节（第4,6,7,8章）：按需包含
    - 附录：按需包含
    """
    template = base_template.copy()

    for chapter in ALL_CHAPTERS:
        if chapter not in config.includeSections:
            if chapter in ESSENTIAL_CHAPTERS:
                template[chapter].mode = 'condensed'  # 浓缩而非删除
            else:
                template[chapter].mode = 'omitted'    # 完全省略

    return template
```

##### 5.2 数据映射

将 `AnalysisReport` 的分析结果映射到模板的各个字段：

```yaml
mapping_rules:
  第一章_执行概览:
    基本信息: ← taskInfo.objectives + taskInfo.metadata
    核心成果: ← objectiveAchievement.overallAssessment
    关键数据速览: ← [objectiveAchievement, timeEfficiency, issuePatterns] 的聚合
    Top3亮点: ← objectiveAchievement.exceedingItems
    Top3挑战: ← issuePatterns.criticalIssues
    一句话总结: ← summary.overallAssessment

  第二章_背景与目标:
    任务背景: ← taskInfo.context
    初始目标: ← taskInfo.objectives.initial
    目标演进: ← taskInfo.objectives.adjustments
    约束条件: ← taskInfo.constraints

  第三章_执行过程:
    阶段划分: ← timeEfficiency.phases
    详细记录: ← executionInfo.operations
    决策索引: ← executionInfo.decisions (简要)

  第四章_关键决策:
    决策清单: ← executionInfo.decisions
    决策详情: ← executionInfo.decisions (展开)

  第五章_问题与方案:
    问题总览: ← issuePatterns.distribution
    问题详情: ← executionInfo.issues (展开)
    模式分析: ← issuePatterns.topPatterns

  第六章_资源使用:
    人力资源: ← collaborationInfo?.participants
    技术栈: ← resourceInfo.resources.techStack
    工具与服务: ← resourceInfo.resources.tools
    效率评估: ← resourceUtilization.wasteSummary

  第七章_协作分析: (条件)
    协作概况: ← collaborationInfo.overview
    效能评估: ← collaborationEffectiveness.dimensions
    亮点与问题: ← [collaborationEffectiveness.highlights, .improvements]

  第八章_多维分析:
    目标达成: ← objectiveAchievement (详细)
    时间效能: ← timeEfficiency (详细)
    资源效率: ← resourceUtilization (详细)
    问题模式: ← issuePatterns (详细)
    雷达图: ← 五维得分聚合

  第九章_经验与方法论:
    方法论提炼: ← (待Step 6填充)
    最佳实践: ← analysisReport.successPatterns
    知识图谱: ← resourceInfo.knowledgeGained
    成长记录: ← (待Step 6填充)

  第十章_改进建议:
    建议: ← (待Step 6填充)
    行动计划: ← (待Step 6填充)
    风险预警: ← (待Step 6填充)
```

##### 5.3 内容填充

针对每个章节字段，动态生成具体内容：

**文本段落生成**：
- 基于分析数据的叙述性文字
- 保持专业客观的书面语风格
- 适当使用数据支撑论点

**表格生成**：
- 统一表格格式规范
- 数字右对齐，文本左对齐
- 重要单元格加粗强调

**列表生成**：
- 有序列表用于有序步骤
- 无序列表用于并列项目
- 嵌套层级不超过3层

##### 5.4 格式优化

```python
def optimize_format(draft_content: str) -> str:
    """
    格式优化规则：
    1. Markdown 语法规范化
    2. 表格列宽自适应
    3. 标题层级连续性检查
    4. 代码块语言标注补全
    5. 列表缩进统一
    6. 空行规范性调整
    """
    optimized = normalize_markdown(draft_content)
    optimized = fix_table_formatting(optimized)
    optimized = ensure_heading_hierarchy(optimized)
    optimized = complete_code_block_lang(optimized)
    return optimized
```

##### 5.5 语言润色

```python
def polish_language(content: str, language: str) -> str:
    """
    语言润色检查项：
    1. 专业性：使用规范的书面语，避免口语化和网络用语
    2. 清晰性：逻辑层次分明，段落长度适中
    3. 一致性：人称、时态保持一致
    4. 准确性：技术术语使用准确，数值精确
    5. 完整性：自成一体的表达，必要的解释充分
    """
    polished = check_professionalism(content)
    polished = ensure_clarity(polished)
    polished = normalize_consistency(polished, language)
    polished = verify_accuracy(polished)
    return polished
```

#### 输出

| 输出类型 | 条件 | 说明 |
|---------|------|------|
| `DraftReport` | 生成成功 | 完整的草稿报告（Markdown 格式） |
| `E031` (Error) | 模板渲染失败 | 模板引擎错误 |
| `E032` (Error) | 内容生成失败 | 内容生成器错误 |

**DraftReport 结构**：

```typescript
interface DraftReport {
  content: string;                    // Markdown 格式的报告正文
  metadata: {
    generatedAt: Date;
    templateUsed: TemplateVariant;
    chapterCount: number;
    wordCount: number;
    sectionsIncluded: ChapterName[];
  };
  qualityIndicators: {
    structureCompleteness: number;     // 0-100
    dataMappingCoverage: number;      // 0-100
    formatCompliance: number;         // 0-100
  };
}
```

#### 耗时预估

30-120 秒（取决于详细程度和内容量）

---

### Step 6: 智能推荐生成

```
┌──────────────────────────────────┐
│    Step 6: 智能推荐引擎           │
│                                  │
│  DraftReport + AnalysisReport    │
│       ↓                         │
│  ┌──────────┬──────────┐        │
│  │ 6.1 方法论│ 6.2 改进  │        │
│  │   提取   │   建议   │        │
│  └────┬─────┴────┬─────┘        │
│       ↓          ↓              │
│  ┌──────────┐                   │
│  │ 6.3 风险  │                   │
│  │   预警   │                   │
│  └────┬─────┘                   │
│       ↓                         │
│  Recommendations                 │
│  (嵌入报告第9-10章)             │
└──────────────────────────────────┘
```

#### 输入

- `DraftReport` （来自 Step 5）
- `AnalysisReport` （来自 Step 4）
- `CollectedData` （来自 Step 3）

#### 子步骤详解

##### 6.1 方法论提取

从成功实践中抽象出可复用的方法论：

**识别标准**：

| 标准 | 说明 | 示例 |
|------|------|------|
| 有效性证明 | 该做法在本次任务中被证明有效 | 通过了测试验证 |
| 普适性 | 不局限于特定情境 | 可应用于类似任务 |
| 可描述性 | 可以被清晰地描述和复制 | 能形成步骤化流程 |
| 优势明显 | 相比常规做法有明显优势 | 效率提升 > 20% |

**提取流程**：

```
成功实践识别 → 抽象化（去除特定情境） → 步骤化（形成SOP） → 命名（赋予方法论名称） → 验证（检查普适性） → 输出
```

**输出格式**：

每个方法论包含：
- 名称：简洁有力的方法名称
- 核心理念：一句话概括核心思想
- 适用场景：何时可以使用此方法
- 操作步骤：分阶段的 Action → Output → Checkpoint
- 关键成功要素：必须做到的点
- 常见陷阱：容易犯的错误
- 实战案例：来自本次任务的真实案例
- 变体与扩展：简化和增强版本

##### 6.2 改进建议生成

**建议生成原则**：

| 原则 | 要求 | 不合格示例 | 合格示例 |
|------|------|-----------|---------|
| 基于证据 | 必须有分析数据支撑 | "我觉得应该..." | "由于第5章显示XX问题出现了3次，建议..." |
| 具体可行 | 可以直接执行 | "提高效率" | "引入自动化测试，预计减少50%的手动验证时间" |
| 优先级明确 | 区分紧急重要和不紧急不重要 | （无优先级） | "🔴高优先级：立即实施" |
| 量化预期 | 能预估效果或收益 | "这样做比较好" | "预计可将部署时间从30分钟缩短至5分钟" |
| 责任明确 | 清楚说明谁应该做什么 | （无责任人） | "责任人：开发组长" |

**优先级排序算法**：

```python
def calculate_priority(suggestion: Suggestion) -> PriorityScore:
    factors = {
        'impact_weight': 0.35,       # 影响程度权重
        'urgency_weight': 0.25,      # 紧迫程度权重
        'effort_weight': 0.20,       # 实施难度权重（反向）
        'confidence_weight': 0.20    # 确信度权重
    }

    scores = {
        'impact': rate_impact(suggestion),         # 1-10分
        'urgency': rate_urgency(suggestion),       # 1-10分
        'effort': 11 - rate_effort(suggestion),    # 1-10分（易=高分）
        'confidence': rate_confidence(suggestion)  # 1-10分
    }

    priority_score = sum(
        scores[key] * factors[f'{key}_weight']
        for key in scores
    )

    return PriorityScore(
        score=priority_score,
        level=map_to_level(priority_score)  # P0-P4
    )
```

**优先级分级**：

| 等级 | 分数区间 | 标记 | 含义 | 响应要求 |
|------|---------|------|------|---------|
| P0-紧急 | 8.0-10.0 | 🔴 | 必须立即处理 | 本周内启动 |
| P1-高 | 6.5-7.9 | 🟠 | 尽快安排 | 两周内启动 |
| P2-中 | 5.0-6.4 | 🟡 | 正常排期 | 月内规划 |
| P3-低 | 3.0-4.9 | 🟢 | 有空再做 | 季度规划 |
| P4-可选 | <3.0 | ⚪ | 可做可不做 | 长期储备 |

##### 6.3 风险预警生成

**风险识别维度**：

```yaml
risk_dimensions:
  technical_risks:
    - technical_debt_accumulation  # 技术债务积累
    - technology_eol_risk          # 技术End-of-Life风险
    - performance_bottleneck_risk  # 性能瓶颈隐患
    - security_vulnerability_risk  # 安全性隐患

  process_risks:
    - sustainability_risk         # 流程可持续性风险
    - knowledge_loss_risk         # 知识流失风险
    - monitoring_gap_risk         # 监控缺失风险

  dependency_risks:
    - sla_compliance_risk         # SLA保障风险
    - single_point_of_failure     # 单点故障风险
    - external_service_stability  # 外部服务稳定性

  personnel_risks:
    - knowledge_concentration_risk # 知识集中风险
    - turnover_impact_risk        # 人员流动影响
```

**风险呈现格式**：

每个风险预警包含：
- 风险标题：醒目的风险名称
- 风险描述：清晰描述内容和可能后果
- 可能触发条件：什么情况下会发生
- 可能性评估：高(>70%) / 中(30-70%) / 低(<30%)
- 影响程度：严重 / 中等 / 轻微
- 预防措施：事前如何预防
- 应急预案：发生后如何应对

#### 输出

**Recommendations 对象**：

```typescript
interface Recommendations {
  methodologies: Methodology[];           // 提炼的方法论列表
  improvementSuggestions: Suggestion[];   // 改进建议列表（已排序）
  riskWarnings: RiskWarning[];            // 风险预警列表

  summary: {
    methodologyCount: number;             // 方法论数量
    suggestionCount: number;              // 建议总数
    highPriorityCount: number;            // 高优先级建议数
    riskCount: number;                    // 风险数量
    criticalRiskCount: number;            // 重大风险数
  };

  embeddingTarget: {
    chapter9: Chapter9Content;            // 第九章嵌入内容
    chapter10: Chapter10Content;          // 第十章嵌入内容
  };
}
```

#### 耗时预估

30-60 秒

---

### Step 7: 质量检查与输出

```
┌──────────────────────────────────┐
│   Step 7: 质量检查与组装          │
│                                  │
│  DraftReport + Recommendations    │
│       ↓                         │
│  ┌──────────────────────────┐    │
│  │ 7.1 结构完整性验证        │    │
│  │ • 10章齐全?              │    │
│  │ • 必填字段存在?           │    │
│  │ • 表格格式正确?           │    │
│  └────────────┬─────────────┘    │
│               ↓                  │
│  ┌──────────────────────────┐    │
│  │ 7.2 内容准确性抽检        │    │
│  │ • 数字一致性              │    │
│  │ • 逻辑自洽性              │    │
│  │ • 引用有效性              │    │
│  └────────────┬─────────────┘    │
│               ↓                  │
│  ┌──────────────────────────┐    │
│  │ 7.3 组装最终响应          │    │
│  │ • 构建 success 响应       │    │
│  │ • 附加质量指标            │    │
│  │ • 保存文件（如配置）      │    │
│  └────────────┬─────────────┘    │
│               ↓                  │
│       [Final Response]           │
└──────────────────────────────────┘
```

#### 输入

- `DraftReport` （来自 Step 5）
- `Recommendations` （来自 Step 6）
- `InternalConfig` （来自 Step 1）

#### 子步骤详解

##### 7.1 结构完整性验证

**检查清单**：

| 检查项 | 检查方式 | 通过标准 | 失败处理 |
|-------|---------|---------|---------|
| YAML Frontmatter 完整 | 正则匹配 | 包含所有必需元数据字段 | 自动补全缺失字段 |
| 10章齐全（或按定制） | 章节计数 | 与 config.includeSections 匹配 | 标记缺失章节 |
| 每章包含规定小节 | 小节存在性检查 | 符合模板规范 | 补充空小节占位 |
| 表格格式正确 | Markdown 表格语法解析 | 表头+行数匹配 | 修复格式错误 |
| 代码块有语言标注 | 代码块正则 | 三反引号后有语言标识 | 补充语言标注 |
| 标题层级正确 | 层级连续性检查 | 无跳跃（如 h1→h3） | 调整层级 |
| 附录完整（如有） | 附录存在性检查 | 按配置要求包含 | 补充或移除 |

##### 7.2 内容准确性抽检

**抽检策略**（非全量检查，抽样验证）：

| 抽检维度 | 抽检方法 | 样本量 | 验证规则 |
|---------|---------|-------|---------|
| 数字一致性 | 跨章节数字比对 | 100% 关键数字 | 各处引用同一数字应一致 |
| 逻辑自洽性 | 因果关系检查 | 抽样 20% | 结论应有前置数据支撑 |
| 引用有效性 | 来源可追溯性 | 抽样 30% | 引用的数据应在 CollectedData 中存在 |
| 时间线连贯性 | 时间顺序验证 | 100% 时间节点 | 后续时间不应早于前序时间 |
| 建议可操作性 | 建议质量检查 | 100% 建议 | 符合 SMART 原则 |

##### 7.3 组装最终响应

**响应构建**：

```typescript
interface SuccessResponse {
  status: 'success';
  report: {
    content: string;                    // 最终报告内容（Markdown）
    fileName: string;                   // 建议的文件名
    metadata: ReportMetadata;
  };
  qualityMetrics: {
    overallScore: number;                // 0-100 综合质量分
    informationCoverage: number;         // 信息覆盖率
    factualAccuracy: number;             // 事实准确性
    structuralIntegrity: number;         // 结构完整性
    suggestionQuality: number;           // 建议质量
  };
  processingInfo: {
    totalDuration: number;               // 总处理时间（毫秒）
    stepDurations: Record<StepName, number>;
    warningsIssued: ErrorCode[];         // 过程中发出的警告
    degradationsApplied: string[];      // 应用的降级措施
  };
  recommendations: Recommendations;     // 完整的推荐对象
}
```

**文件保存（如配置要求）**：

```python
def save_report_if_configured(response: SuccessResponse, config: InternalConfig):
    if config.generationOptions.saveToFile:
        filename = generate_filename(config)
        filepath = os.path.join(config.outputDir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(response.report.content)

        response.report.savedPath = filepath
        response.report.fileSize = os.path.getsize(filepath)
```

**文件命名规范**：

```
task-summary-[任务名称简写]-YYYYMMDD.md

示例：
task-summary-payment-refactor-20260409.md
task-summary-crawler-development-20260409.md
task-summary-bugfix-auth-error-20260409.md
```

#### 输出

**Final Response (SuccessResponse)**

这是整个技能执行的最终产物，包含完整的报告内容和质量元数据。

#### 耗时预估

< 10 秒

---

## 3. 异常路径汇总

### 完整异常路径图

```
                    正常路径
Step1 → Step2 → Step3 → Step4 → Step5 → Step6 → Step7 → ✅ Success
  │        │       │       │       │       │
  ↓E001   ↓       ↓E010   ↓E021   ↓E031   │
  ❌Error  │       ⚠️Warn  ⚠️Warn  ❌Error  │
          │       ↓       ↓       ↓       │
          │   [降级继续] [跳过] [回退]    │
          │       │       │       │       │
          └───────→──────→──────→───────→┘
                        (带警告的成功)
```

### 错误码详细说明

#### 第一类：参数验证错误 (E001-E005)

| 错误码 | 错误名称 | 触发条件 | 严重级别 | 处理方式 | 恢复可能 |
|-------|---------|---------|---------|---------|---------|
| E001 | 缺少必填参数 | 必填参数未提供 | 🔴 致命 | 返回错误响应，提示补充 | 需用户修正输入 |
| E002 | 参数类型错误 | 参数值类型不符合要求 | 🔴 致命 | 返回错误响应，给出正确格式示例 | 需用户修正输入 |
| E003 | 参数值越界 | 参数值超出允许范围 | 🟡 警告 | 尝试修正到最近合法值，发出警告 | 自动恢复 |
| E004 | 参数冲突 | 参数之间存在逻辑矛盾 | 🔴 致命 | 返回错误响应，指出冲突的参数对 | 需用户选择 |
| E005 | 安全策略违规 | 参数包含非法内容 | 🔴 致命 | 返回错误响应，拒绝处理 | 需用户修正输入 |

**影响范围**：仅在 Step 1 发生，阻断后续所有步骤

**典型场景**：
```
用户输入: {"detail_level": "ultra"}  # 不支持的值
→ E003: 参数值越界
→ 自动修正为 "detailed"，发出警告

用户输入: {}  # 空对象
→ E001: 缺少必填参数 task_name
→ 返回错误，提示必须提供任务名称
```

#### 第二类：数据质量错误 (E010-E012)

| 错误码 | 错误名称 | 触发条件 | 严重级别 | 处理方式 | 恢复可能 |
|-------|---------|---------|---------|---------|---------|
| E010 | 信息覆盖不足 | 综合覆盖率 70-90% | 🟡 警告 | 标注缺失项，降级继续 | 可降级运行 |
| E011 | 信息严重缺失 | 综合覆盖率 < 70% | 🔴 错误 | 提供三选一：降级/补充/终止 | 用户选择决定 |
| E012 | 数据源不可用 | 关键数据源无法访问 | 🔴 错误 | 尝试备用源，全部不可用时终止 | 部分可恢复 |

**影响范围**：发生在 Step 3，影响 Step 4-7 的数据质量

**降级策略**：

```
E010 降级后果：
  - 缺失的信息类别在报告中标注 "[信息不足]"
  - 相关分析维度降低可信度标注
  - 最终响应的 qualityMetrics 降低相应分数
  - 在 processingInfo.warningsIssued 中记录

E011 用户选择：
  A. 降级继续 → 同 E010 处理，但质量分数更低
  B. 补充信息 → 暂停执行，等待用户提供额外信息后重新进入 Step 3
  C. 终止 → 返回错误响应，说明信息缺口
```

#### 第三类：分析引擎错误 (E021-E022)

| 错误码 | 错误名称 | 触发条件 | 严重级别 | 处理方式 | 恢复可能 |
|-------|---------|---------|---------|---------|---------|
| E021 | 部分分析失败 | 某一维度的分析数据不足 | 🟡 警告 | 跳过该维度，其他维度正常输出 | 自动恢复 |
| E022 | 核心分析引擎错误 | 分析引擎本身异常 | 🔴 错误 | 回退到简化分析模式 | 部分可恢复 |

**影响范围**：发生在 Step 4，影响报告的分析深度

**回退策略**：

```
E021 处理：
  - 跳过数据不足的维度（如"协作效果"因无协作数据而跳过）
  - 在报告中该章节显示 "[数据不足以进行分析]"
  - AnalysisReport 中对应字段设为 null 并标注原因
  - qualityMetrics.analysisCompleteness 降低

E022 处理：
  - 激活简化分析模式（仅做基础统计，不做深度洞察）
  - 生成基础版的 AnalysisReport
  - 在报告第八章标注 "因分析引擎异常，本次分析为简化版本"
  - 强烈建议用户稍后重试
```

#### 第四类：报告生成错误 (E031-E032)

| 错误码 | 错误名称 | 触发条件 | 严重级别 | 处理方式 | 恢复可能 |
|-------|---------|---------|---------|---------|---------|
| E031 | 模板渲染失败 | 模板引擎异常 | 🔴 错误 | 回退到备用模板 | 通常可恢复 |
| E032 | 内容生成失败 | 内容生成器异常 | 🔴 错误 | 使用已有数据直接组装 | 部分可恢复 |

**影响范围**：发生在 Step 5，直接影响最终报告质量

**回退策略**：

```
E031 处理：
  - 尝试备用模板（简化版模板）
  - 如备用模板也失败，使用纯文本模板（最小可用模板）
  - 记录模板错误详情到日志

E032 处理：
  - 跳过动态内容生成步骤
  - 将 AnalysisReport 的数据以结构化方式直接嵌入
  - 格式化为基本的 Markdown（表格+列表）
  - 报告可读性降低但信息完整性保持
```

### 错误传播链

```
Step 1 错误 (E001-E005)
  └→ 直接返回 ErrorResponse
     └→ 不进入后续步骤

Step 2 错误（极少，通常不会独立出错）
  └→ 使用默认 CollectionScope 继续

Step 3 错误 (E010-E012)
  ├→ E010: 带 warning 标记的 CollectedData → 进入 Step 4
  ├→ E011: 用户选择降级 → 进入 Step 4（低质量数据）
  └→ E011: 用户选择终止 → 返回 ErrorResponse

Step 4 错误 (E021-E022)
  ├→ E021: 带 warning 标记的 AnalysisReport → 进入 Step 5
  └→ E022: 简化版 AnalysisReport → 进入 Step 5

Step 5 错误 (E031-E032)
  ├→ E031: 回退模板 → 重新尝试 → 成功则进入 Step 6
  └→ E032: 简化内容 → 进入 Step 6

Step 6 错误（极少，通常不会完全失败）
  └→ 空 Recommendations → 进入 Step 7

Step 7 错误（极少，主要是格式问题）
  └→ 修复后重试 → 返回 SuccessResponse
```

---

## 4. 性能基线

### 各阶段性能明细

| 步骤 | 预估耗时 | 占总时长% | 主要瓶颈 | 优化空间 |
|------|---------|----------|---------|---------|
| Step 1: 参数解析与验证 | < 1s | < 1% | 无 | 已最优 |
| Step 2: 触发模式识别 | < 2s | < 2% | 无 | 已最优 |
| Step 3: 信息收集阶段 | 30-120s | 40-50% | 对话历史解析 | 可并行化数据源处理 |
| Step 4: 分析处理阶段 | 60-180s | 35-40% | 五维分析计算 | 可缓存常用分析模式 |
| Step 5: 报告生成阶段 | 30-120s | 15-20% | 内容生成 | 可预编译模板 |
| Step 6: 智能推荐生成 | 30-60s | 5-10% | 推荐算法 | 可增量更新 |
| Step 7: 质量检查与输出 | < 10s | < 2% | 无 | 已最优 |
| **总计** | **2-8 min** | **100%** | Step 3 + Step 4 | **约 30-40%** |

### 场景化性能参考

| 任务场景 | 对话轮数 | 详细程度 | 预估总耗时 | Step 3 占比 | Step 4 占比 |
|---------|---------|---------|-----------|------------|------------|
| 简单任务总结 | < 20轮 | 摘要版 | 1-2 min | ~30% | ~35% |
| 标准任务复盘 | 20-50轮 | 标准版 | 3-5 min | ~42% | ~38% |
| 复杂项目总结 | > 50轮 | 详细版 | 6-10 min | ~48% | ~40% |
| 大规模协作回顾 | > 100轮 | 详细版 | 8-15 min | ~50% | ~38% |

### 性能优化建议

**短期优化（立即可实施）**：

1. **Step 3 并行化**：多数据源的处理可以并行执行
   - 预期提升：减少 30-40% 的 Step 3 耗时

2. **Step 5 模板预编译**：将常用模板预编译为高效渲染格式
   - 预期提升：减少 20-30% 的 Step 5 耗时

3. **增量处理**：对于长对话，支持分段处理并合并结果
   - 预期提升：大幅降低内存占用，线性扩展处理能力

**中期优化（需要架构调整）**：

4. **分析结果缓存**：相似任务类型的分析模式可缓存复用
   - 适用场景：同类任务的批量总结

5. **异步流水线**：Step 3-6 可设计为异步流水线，支持流式输出
   - 用户体验：边生成边展示，无需等待全部完成

---

## 5. 状态机说明

### 执行状态定义

```
IDLE → PARSING → COLLECTING → ANALYZING → GENERATING → RECOMMENDING → FINALIZING → COMPLETE
  ↑         ↓           ↓           ↓            ↓              ↓              ↓
  └─────────┴───────────┴───────────┴────────────┴──────────────┴──────────────┘
                           (任何错误状态均可回到 IDLE 或 ERROR)
```

### 状态详解

| 状态 | 英文名称 | 触发条件 | 退出条件 | 允许的下一状态 |
|------|---------|---------|---------|-------------|
| 空闲 | IDLE | 技能初始化 / 上次执行完成 | 接收到新的请求 | PARSING |
| 解析中 | PARSING | 开始 Step 1 | Step 1 完成 | COLLECTING / ERROR |
| 收集中 | COLLECTING | 开始 Step 3 | Step 3 完成 | ANALYZING / ERROR |
| 分析中 | ANALYZING | 开始 Step 4 | Step 4 完成 | GENERATING / ERROR |
| 生成中 | GENERATING | 开始 Step 5 | Step 5 完成 | RECOMMENDING / ERROR |
| 推荐中 | RECOMMENDING | 开始 Step 6 | Step 6 完成 | FINALIZING / ERROR |
| 完善中 | FINALIZING | 开始 Step 7 | Step 7 完成 | COMPLETE / ERROR |
| 完成 | COMPLETE | 所有步骤成功 | 新请求到达 | IDLE |
| 错误 | ERROR | 任何步骤遇到致命错误 | 用户重试 / 放弃 | IDLE |

### 状态转换规则

```
合法转换：
  IDLE ──→ PARSING          (新请求到达)
  PARSING ──→ COLLECTING    (参数验证通过)
  PARSING ──→ ERROR         (参数验证失败)
  COLLECTING ──→ ANALYZING  (信息收集完成且质量达标)
  COLLECTING ──→ ERROR      (数据严重缺失且用户选择终止)
  ANALYZING ──→ GENERATING  (分析完成)
  ANALYZING ──→ ERROR       (分析引擎严重故障)
  GENERATING ──→ RECOMMENDING (报告草稿生成完成)
  GENERATING ──→ ERROR      (报告生成完全失败)
  RECOMMENDING ──→ FINALIZING (推荐生成完成)
  FINALIZING ──→ COMPLETE   (质量检查通过)
  FINALIZING ──→ ERROR      (质量检查发现致命问题)
  COMPLETE ──→ IDLE         (准备接收新请求)
  ERROR ──→ IDLE            (错误处理后重置)

非法转换（不允许）：
  ✗ 任意状态 ──→ COMPLETE   (必须走完所有步骤)
  ✗ ERROR ──→ PARSING       (必须先回到 IDLE)
  ✗ COLLECTING ──→ GENERATING (不能跳过分析步骤)
  ✗ 任意状态 ──→ IDLE       (除 COMPLETE 和 ERROR 外)
```

### 状态持久化

```typescript
interface ExecutionState {
  currentState: StateName;
  previousState: StateName | null;
  enteredAt: Date;
  currentStep: StepName | null;

  progress: {
    completedSteps: StepName[];
    currentStepProgress: number;  // 0-100 当前进度百分比
    estimatedRemaining: number;   // 预估剩余毫秒数
  };

  context: {
    internalConfig: InternalConfig | null;
    collectedData: CollectedData | null;
    analysisReport: AnalysisReport | null;
    draftReport: DraftReport | null;
    recommendations: Recommendations | null;
  };

  errorInfo: {
    lastError: AppError | null;
    errorHistory: AppError[];
    retryCount: number;
  } | null;
}
```

### 超时与中断处理

| 状态 | 超时阈值 | 超时处理 | 中断处理 |
|------|---------|---------|---------|
| PARSING | 5s | 返回 E001 超时错误 | 丢弃当前请求 |
| COLLECTING | 180s | 保存已收集数据，返回 E012 | 保留进度，支持断点续传 |
| ANALYZING | 300s | 返回 E022 分析超时，返回部分结果 | 保留分析中间结果 |
| GENERATING | 120s | 返回 E031 生成超时，返回已生成部分 | 保留草稿 |
| RECOMMENDING | 90s | 跳过推荐，使用空 Recommendations | 继续后续步骤 |
| FINALIZING | 30s | 返回已完成部分的报告 | 直接输出当前版本 |

---

## 附录：错误码索引

| 错误码 | 所属类别 | 错误名称 | 严重级别 | 发生步骤 | 可恢复性 |
|-------|---------|---------|---------|---------|---------|
| E001 | 参数验证 | 缺少必填参数 | 🔴 致命 | Step 1 | 需用户修正 |
| E002 | 参数验证 | 参数类型错误 | 🔴 致命 | Step 1 | 需用户修正 |
| E003 | 参数验证 | 参数值越界 | 🟡 警告 | Step 1 | 自动修正 |
| E004 | 参数验证 | 参数冲突 | 🔴 致命 | Step 1 | 需用户选择 |
| E005 | 参数验证 | 安全策略违规 | 🔴 致命 | Step 1 | 需用户修正 |
| E010 | 数据质量 | 信息覆盖不足 | 🟡 警告 | Step 3 | 可降级运行 |
| E011 | 数据质量 | 信息严重缺失 | 🔴 错误 | Step 3 | 用户选择 |
| E012 | 数据质量 | 数据源不可用 | 🔴 错误 | Step 3 | 部分可恢复 |
| E021 | 分析引擎 | 部分分析失败 | 🟡 警告 | Step 4 | 自动跳过 |
| E022 | 分析引擎 | 核心分析引擎错误 | 🔴 错误 | Step 4 | 可降级运行 |
| E031 | 报告生成 | 模板渲染失败 | 🔴 错误 | Step 5 | 可回退模板 |
| E032 | 报告生成 | 内容生成失败 | 🔴 错误 | Step 5 | 部分可恢复 |

---

*文档版本：v1.0*
*最后更新：2026-04-09*
*适用于 Task Execution Summary Generator v1.0*
*关联文档：[SKILL.md](./SKILL.md) | [terminology.md](./terminology.md) | [templates.md](./templates.md)*
