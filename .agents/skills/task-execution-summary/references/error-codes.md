# 错误码定义文档 (Error Codes Reference)

本文档定义了"任务执行总结报告生成器"技能的完整错误码体系，包括错误分类、详细定义、处理策略和降级机制。

---

## 目录

- [1. 概述](#1-概述)
  - [1.1 错误处理设计理念](#11-错误处理设计理念)
  - [1.2 错误码命名规则](#12-错误码命名规则)
  - [1.3 错误响应通用结构](#13-错误响应通用结构)
- [2. 错误分类体系总览](#2-错误分类体系总览)
- [3. 详细错误码定义](#3-详细错误码定义)
  - [E001: MissingRequiredParameter](#e001-missingrequiredparameter)
  - [E002: InvalidParameterType](#e002-invalidparametertype)
  - [E003: ParameterValueOutOfRange](#e003-parametervalueoutofrange)
  - [E004: ConflictingParameters](#e004-conflictingparameters)
  - [E005: InvalidChapterCombination](#e005-invalidchaptercombination)
  - [E010: InsufficientDataWarning](#e010-insufficientdatawarning)
  - [E011: ConversationHistoryUnavailable](#e011-conversationhistoryunavailable)
  - [E012: FileAccessDenied](#e012-fileaccessdenied)
  - [E021: GoalAnalysisFailed](#e021-goalanalysisfailed)
  - [E022: TimelineReconstructionFailed](#e022-timelinereconstructionfailed)
  - [E031: TemplateNotFound](#e031-templatenotfound)
  - [E032: ReportGenerationTimeout](#e032-reportgenerationtimeout)
  - [E041: InsufficientMemory](#e041-insufficientmemory)
  - [E051: ExecutionTimeout](#e051-executiontimeout)
- [4. 错误处理策略矩阵](#4-错误处理策略矩阵)
- [5. 降级策略详解](#5-降级策略详解)
- [6. 错误码快速查询表](#6-错误码快速查询表)

---

## 1. 概述

### 1.1 错误处理设计理念

本技能的错误处理体系遵循以下核心原则：

**分层防御 (Defense in Depth)**
- 输入层：参数验证，拦截非法请求
- 数据层：数据源可用性检查，确保信息可获取
- 分析层：分析引擎异常捕获，保证计算稳定性
- 生成层：报告生成容错，支持部分成功输出

**优雅降级 (Graceful Degradation)**
- 非致命错误不中断执行流程
- Warning 级别错误允许继续运行并标注影响
- 最终报告质量评分反映降级程度
- 用户始终获得有价值的输出（即使不完美）

**透明告知 (Transparent Communication)**
- 所有错误都有明确的错误码和消息
- 响应中包含恢复建议和预防措施
- 日志记录完整上下文便于排查
- 降级信息在报告中清晰标注

**可观测性 (Observability)**
- 错误发生时自动记录完整堆栈和上下文
- 支持错误统计和趋势分析
- 提供质量评分量化报告可信度
- 关键节点有明确的健康检查指标

### 1.2 错误码命名规则

```
格式: E + 类别编号(1位) + 序号(2位)

示例: E001, E010, E041
```

**命名规则详解**：

| 组成部分 | 说明 | 取值范围 |
|---------|------|---------|
| **前缀 E** | 固定前缀，表示 Error | E |
| **类别编号** | 错误所属大类 | 0-5 |
| **序号** | 同类错误的顺序号 | 01-99 |

**类别编号分配**：

| 编号 | 类别 | 说明 |
|------|------|------|
| 0 | 参数验证 | 输入参数相关错误 |
| 1 | 数据源 | 数据获取相关错误 |
| 2 | 分析引擎 | 分析过程相关错误 |
| 3 | 报告生成 | 生成输出相关错误 |
| 4 | 系统资源 | 运行环境资源错误 |
| 5 | 超时 | 执行时间超限错误 |

**错误码保留规则**：
- 每个类别预留 5 个错误码空间
- 新增错误码需在对应类别范围内顺延
- 已废弃的错误码标记为 `DEPRECATED` 并保留文档
- 跨类别的通用错误归入最相关的类别

### 1.3 错误响应通用结构

所有错误响应遵循统一的 JSON 结构：

```json
{
  "success": false,
  "error": {
    "code": "E001",
    "name": "MissingRequiredParameter",
    "message": "缺少必填参数: task_name",
    "category": "parameter_validation",
    "severity": "Error",
    "http_status": 400,
    "timestamp": "2026-04-09T14:30:00Z",
    "request_id": "req_abc123xyz",
    "context": {
      "missing_parameter": "task_name",
      "available_parameters": ["detail_level", "output_format"]
    },
    "recovery": {
      "mode": "terminate",
      "suggestions": [
        "请提供 task_name 参数",
        "参考文档: /docs/api#parameters"
      ],
      "documentation_url": "/errors/E001"
    }
  },
  "metadata": {
    "version": "1.0.0",
    "service": "task-execution-summary"
  }
}
```

**字段说明**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| success | boolean | ✅ | 是否成功，错误时为 false |
| error.code | string | ✅ | 错误码，如 "E001" |
| error.name | string | ✅ | 错误名称，PascalCase |
| error.message | string | ✅ | 人类可读的错误描述 |
| error.category | string | ✅ | 错误分类标识 |
| error.severity | string | ✅ | 严重级别: Critical/Error/Warning |
| error.http_status | integer | ✅ | 对应的 HTTP 状态码 |
| error.timestamp | string | ✅ | ISO 8601 格式的时间戳 |
| error.request_id | string | ✅ | 请求唯一标识，用于追踪 |
| error.context | object | ⚠️ | 错误发生的上下文信息 |
| error.recovery | object | ✅ | 恢复建议和模式 |

---

## 2. 错误分类体系总览

| 类别编码 | 类别名称 | 错误码范围 | 严重级别 | 处理策略 | 触发阶段 |
|---------|---------|-----------|---------|---------|---------|
| **E0xx** | 参数验证错误 | E001-E010 | Error/Warning | 验证失败时立即返回或降级 | 触发检测 → 信息收集 |
| **E1xx** | 数据源错误 | E011-E015 | Error/Warning | 数据获取异常时重试或降级 | 信息收集阶段 |
| **E2xx** | 分析引擎错误 | E021-E025 | Error/Warning | 分析失败时使用默认值或跳过 | 分析处理阶段 |
| **E3xx** | 报告生成错误 | E031-E035 | Error | 生成失败时返回错误或部分结果 | 报告生成阶段 |
| **E4xx** | 系统资源错误 | E041-E045 | Critical | 资源不足时终止并告警 | 任意阶段 |
| **E5xx** | 超时错误 | E051 | Error | 超时时终止或返回部分结果 | 任意阶段 |

**严重级别说明**：

| 级别 | 图标 | 定义 | 对执行的影响 |
|------|------|------|-------------|
| **Critical** | 🔴 | 系统级故障，无法继续运行 | 立即终止，不生成任何输出 |
| **Error** | 🟠 | 功能性错误，当前操作无法完成 | 终止当前步骤，可能返回部分结果 |
| **Warning** | 🟡 | 非致命问题，可以继续但质量受损 | 标记警告，继续执行，最终报告标注 |

---

## 3. 详细错误码定义

---

### E001: MissingRequiredParameter

| 属性 | 值 |
|------|---|
| **错误码** | E001 |
| **名称** | MissingRequiredParameter |
| **类别** | parameter_validation |
| **严重程度** | 🟠 Error |
| **HTTP 状态码** | 400 Bad Request |
| **恢复模式** | terminate |

**触发条件**:
当调用技能时缺少一个或多个必填参数时触发。必填参数包括但不限于：
- `task_name` 或等效的任务标识
- 对话历史引用（隐式或显式）
- 输出路径（如果需要保存文件）

**错误消息模板**:
```
缺少必填参数: {parameter_name}

必需参数列表:
- {required_param_1}: {description_1}
- {required_param_2}: {description_2}

当前已提供参数: {provided_params_list}

请补充缺失的必填参数后重试。
```

**示例场景**:
> 用户直接发送 `/summary` 命令但没有指定要总结的任务，且当前对话中没有足够的任务执行上下文。
>
> **请求**: `{ "action": "generate_summary" }`
>
> **响应**:
> ```json
> {
>   "success": false,
>   "error": {
>     "code": "E001",
>     "name": "MissingRequiredParameter",
>     "message": "缺少必填参数: task_context",
>     "context": {
>       "missing_parameter": "task_context",
>       "reason": "无法从当前对话中识别出待总结的任务"
>     },
>     "recovery": {
>       "mode": "terminate",
>       "suggestions": [
>         "请明确描述要总结的任务内容",
>         "提供任务的开始和结束时间范围",
>         "或者先执行一个任务，然后再请求总结"
>       ]
>     }
>   }
> }
> ```

**恢复建议**:
1. 检查 API 文档确认所有必填参数
2. 在请求中补充缺失的参数值
3. 如果是交互式场景，引导用户提供必要信息

**预防措施**:
- 在 SDK 和 CLI 工具中实现参数校验
- 提供清晰的参数文档和示例
- 实现智能推断：尝试从对话上下文中自动提取缺失信息
- 对于可选但有默认值的参数，在文档中明确标注默认行为

---

### E002: InvalidParameterType

| 属性 | 值 |
|------|---|
| **错误码** | E002 |
| **名称** | InvalidParameterType |
| **类别** | parameter_validation |
| **严重程度** | 🟠 Error |
| **HTTP 状态码** | 400 Bad Request |
| **恢复模式** | terminate |

**触发条件**:
当提供的参数类型与预期不符时触发，常见情况包括：
- `detail_level` 应为字符串 ("summary"/"standard"/"detailed") 但传入了数字
- `chapters` 应为数组但传入了字符串
- `output_format` 应为特定枚举值但传入了自定义字符串
- 时间参数格式错误（非 ISO 8601 格式）

**错误消息模板**:
```
参数类型错误: {parameter_name}

期望类型: {expected_type}
实际类型: {actual_type}
实际值: {actual_value}

有效的值示例: {valid_examples}

请修正参数类型后重试。
```

**示例场景**:
> 用户在请求中将 `detail_level` 设置为数字 `2` 而不是字符串 `"detailed"`。
>
> **请求**: `{ "detail_level": 2 }`
>
> **响应**:
> ```json
> {
>   "success": false,
>   "error": {
>     "code": "E002",
>     "name": "InvalidParameterType",
>     "message": "参数类型错误: detail_level",
>     "context": {
>       "parameter": "detail_level",
>       "expected": "string (enum: 'summary', 'standard', 'detailed')",
>       "actual": "integer",
>       "actual_value": 2
>     },
>     "recovery": {
>       "mode": "terminate",
>       "suggestions": [
>         "使用字符串值: \"summary\", \"standard\", 或 \"detailed\"",
>         "参考: /docs/api#detail-level"
>       ]
>     }
>   }
> }
> ```

**恢复建议**:
1. 对照文档检查参数的预期类型
2. 使用正确的数据类型重新提交请求
3. 利用 SDK 的类型提示功能避免此类错误

**预防措施**:
- 使用强类型的请求模型（如 TypeScript interface、Pydantic model）
- 提供 OpenAPI/Swagger 文档供自动校验
- 在客户端 SDK 中内置类型检查
- 对边界情况进行清晰的错误提示

---

### E003: ParameterValueOutOfRange

| 属性 | 值 |
|------|---|
| **错误码** | E003 |
| **名称** | ParameterValueOutOfRange |
| **类别** | parameter_validation |
| **严重程度** | 🟠 Error |
| **HTTP 状态码** | 400 Bad Request |
| **恢复模式** | terminate |

**触发条件**:
当参数值超出允许的范围时触发，包括：
- 数值型参数超过最大/最小限制（如 `max_issues` > 100）
- 字符串长度超出限制（如 `task_name` > 200 字符）
- 枚举值不在允许集合中
- 日期范围不合理（结束时间早于开始时间）
- 章节选择包含无效的章节编号

**错误消息模板**:
```
参数值超出范围: {parameter_name}

当前值: {current_value}
有效范围: {valid_range}
约束说明: {constraint_description}

请将参数调整到有效范围内后重试。
```

**示例场景**:
> 用户请求生成报告时指定了无效的章节组合，包含了不存在的第11章。
>
> **请求**: `{ "chapters": [1, 2, 3, 11] }`
>
> **响应**:
> ```json
> {
>   "success": false,
>   "error": {
>     "code": "E003",
>     "name": "ParameterValueOutOfRange",
>     "message": "参数值超出范围: chapters",
>     "context": {
>       "parameter": "chapters",
>       "invalid_values": [11],
>       "valid_range": "1-10",
>       "available_chapters": [
>         "1: 执行概览",
>         "2: 任务背景与目标",
>         "...",
>         "10: 改进建议与行动计划"
>       ]
>     },
>     "recovery": {
>       "mode": "terminate",
>       "suggestions": [
>         "有效章节范围为 1-10",
>         "使用 chapter_names 参数按名称选择"
>       ]
>     }
>   }
> }
> ```

**恢复建议**:
1. 查看文档了解参数的有效取值范围
2. 将参数值调整到合法范围内
3. 如需扩展范围，联系系统管理员评估可行性

**预防措施**:
- 在文档中明确标注每个参数的取值范围和约束
- 使用 enum 类型限制枚举值的选择
- 实现客户端预校验，在提交前拦截无效值
- 对复杂约束提供在线验证工具

---

### E004: ConflictingParameters

| 属性 | 值 |
|------|---|
| **错误码** | E004 |
| **名称** | ConflictingParameters |
| **类别** | parameter_validation |
| **严重程度** | 🟠 Error |
| **HTTP 状态码** | 400 Bad Request |
| **恢复模式** | terminate |

**触发条件**:
当多个参数之间存在逻辑冲突时触发，典型场景包括：
- 同时指定了 `detail_level="summary"` 和 `chapters=[1,2,3,4,5,6,7,8,9,10]`（摘要版不应包含全部章节）
- 同时指定了 `include_chapters` 和 `exclude_chapters` 且存在重叠
- `output_path` 指定了 `.pdf` 但 `output_format` 为 `"markdown"`
- `time_range` 与具体的时间点参数冲突

**错误消息模板**:
```
参数冲突: {parameter_1} 与 {parameter_2} 存在矛盾

{parameter_1} = {value_1}: {meaning_1}
{parameter_2} = {value_2}: {meaning_2}

冲突原因: {conflict_explanation}

请移除或修改其中一个参数以消除冲突。
```

**示例场景**:
> 用户同时要求摘要版输出但又指定了包含所有10个章节。
>
> **请求**: `{ "detail_level": "summary", "chapters": [1,2,3,4,5,6,7,8,9,10] }`
>
> **响应**:
> ```json
> {
>   "success": false,
>   "error": {
>     "code": "E004",
>     "name": "ConflictingParameters",
>     "message": "参数冲突: detail_level 与 chapters 存在矛盾",
>     "context": {
>       "param_1": "detail_level = 'summary' (仅包含第1章和第10章摘要)",
>       "param_2": "chapters = [1..10] (包含全部10章)",
>       "resolution_options": [
>         "移除 chapters 参数，使用 summary 默认章节",
>         "将 detail_level 改为 'standard' 或 'detailed'",
>         "将 chapters 改为 [1, 10]"
>       ]
>     },
>     "recovery": {
>       "mode": "terminate",
>       "suggestions": [
>         "选择方案A: 移除 chapters，使用 summary 默认配置",
>         "选择方案B: 将 detail_level 改为 'detailed'"
>       ]
>     }
>   }
> }
> ```

**恢复建议**:
1. 理解每个参数的含义和它们之间的相互关系
2. 选择一组一致的非冲突参数组合
3. 参考文档中的参数兼容性矩阵

**预防措施**:
- 提供参数兼容性表格，明确哪些参数不能同时使用
- 在 SDK 中实现参数冲突检测
- 当检测到冲突时，提供具体的解决方案选项
- 使用 builder 模式或 fluent API 引导用户正确配置

---

### E005: InvalidChapterCombination

| 属性 | 值 |
|------|---|
| **错误码** | E005 |
| **名称** | InvalidChapterCombination |
| **类别** | parameter_validation |
| **严重程度** | 🟠 Error |
| **HTTP 状态码** | 400 Bad Request |
| **恢复模式** | terminate |

**触发条件**:
当选择的章节组合违反依赖关系或完整性约束时触发：
- 缺少基础章节（如只有第9章经验总结却没有第3章执行过程）
- 章节间存在前置依赖未满足（如选了第8章多维度分析却没选第2章目标）
- 仅选择了附录而没有正文章节
- 选择的章节数量为0（空数组）

**错误消息模板**:
```
无效的章节组合: {chapter_list}

问题: {dependency_issue_description}

依赖关系说明:
- {dependent_chapter} 依赖于 {prerequisite_chapter}
- 原因: {reason}

建议的完整组合:
- 方案A: {recommended_set_a}
- 方案B: {recommended_set_b}
```

**示例场景**:
> 用户只选择了第8章（多维度分析）和第9章（经验总结），缺少了提供原始数据的第2-7章。
>
> **请求**: `{ "chapters": [8, 9] }`
>
> **响应**:
> ```json
> {
>   "success": false,
>   "error": {
>     "code": "E005",
>     "name": "InvalidChapterCombination",
>     "message": "无效的章节组合: 第8章、第9章",
>     "context": {
>       "selected_chapters": [8, 9],
>       "issue": "第8章(多维度分析)需要第2-7章的数据作为输入",
>       "chapter_dependencies": [
>         {"chapter": 8, "requires": [2, 3, 4, 5, 6], "reason": "需要原始执行数据"},
>         {"chapter": 9, "requires": [3, 5], "reason": "需要问题和决策记录"}
>       ],
>       "recommendations": [
>         {"set": [2, 3, 4, 5, 6, 8, 9], "label": "最小可行集"},
>         {"set": [1, 2, 3, 4, 5, 6, 8, 9], "label": "推荐集（含概览）"},
>         {"set": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], "label": "完整集"}
>       ]
>     },
>     "recovery": {
>       "mode": "terminate",
>       "suggestions": [
>         "添加第2-6章作为数据分析的基础输入",
>         "或使用 detail_level='standard' 获取标准章节组合"
>       ]
>     }
>   }
> }
> ```

**恢复建议**:
1. 了解章节之间的依赖关系图
2. 补充被依赖的前置章节
3. 或使用预设的 `detail_level` 快速选择合理的章节组合

**预防措施**:
- 在文档中提供章节依赖关系图
- 实现 interactive 模式下的实时校验和提示
- 提供"智能推荐"功能，根据用户意图推荐最优章节组合
- 对常见组合提供快捷选项（如"仅复盘"、"仅方法论"等）

---

### E010: InsufficientDataWarning ⚠️ 重要

| 属性 | 值 |
|------|---|
| **错误码** | E010 |
| **名称** | InsufficientDataWarning |
| **类别** | data_source |
| **严重程度** | 🟡 Warning |
| **HTTP 状态码** | 206 Partial Content |
| **恢复模式** | degrade |

**触发条件**:
当任务执行过程中发现某些关键信息缺失或不充分，但不足以阻止报告生成时触发。这是**降级继续的核心机制**：

- 对话历史过短（< 5轮交互），信息密度不足
- 缺少关键阶段的信息（如有执行无决策记录）
- 时间戳信息不完整，无法精确重建时间线
- 问题解决过程描述模糊，缺乏细节
- 资源使用信息未被提及
- 团队协作信息完全缺失（对于多人任务）

**错误消息模板**:
```
⚠️ 数据不充分警告

缺失信息类型: {missing_data_types}
影响程度: {impact_level} (轻微/中等/显著)
受影响章节: {affected_chapters}

系统将以降级模式继续生成报告:
- 受影响的章节将使用推断数据或标注[数据不足]
- 报告质量评分将相应降低
- 建议在获得更完整数据后重新生成

缺失详情:
{missing_details_by_category}
```

**示例场景**:
> 用户的任务对话只有8轮，其中大部分是简短的指令确认，缺少详细的决策讨论和问题描述。
>
> **请求**: （正常发起总结请求）
>
> **响应** (带警告的成功响应):
> ```json
> {
>   "success": true,
>   "warning": {
>     "code": "E010",
>     "name": "InsufficientDataWarning",
>     "message": "数据不充分：决策记录和时间细节有限",
>     "severity": "Warning",
>     "impact": {
>       "quality_score_penalty": -15,
>       "affected_chapters": [4, 8],
>       "degraded_sections": {
>         "4": "关键决策分析 - 将基于有限信息推断",
>         "8": "时间效能分析 - 时间粒度较粗"
>       }
>     },
>     "details": {
       "conversation_rounds": 8,
       "minimum_recommended": 15,
       "missing_elements": [
         "决策 rationale 详细说明",
         "问题排查的中间步骤",
         "精确的时间消耗数据"
       ]
     },
     "recovery": {
       "mode": "degrade",
       "suggestions": [
         "报告已生成但第四章和第八章信息有限",
         "如需更详细的分析，请提供更多任务执行的背景信息",
         "可在报告中手动补充关键决策的详细说明"
       ]
     }
   },
   "result": {
     "report_path": "./task-summary-xxx.md",
     "quality_score": 78,
     "quality_grade": "B",
     "degradation_notice": "报告因数据不充分已降级生成，部分章节内容为推断或简化版本"
   }
 }
> ```

**恢复建议**:
1. **接受降级结果**：查看生成的报告，在 `[数据不足]` 标注处手动补充信息
2. **补充信息后重新生成**：提供更多关于任务执行的详细信息后再次请求
3. **切换到交互模式**：使用交互式生成方式，在过程中逐步补充缺失信息
4. **导入手动记录**：如果有外部笔记或文档，可以作为附加数据源导入

**预防措施**:
- 在任务执行过程中保持详细的对话记录（鼓励用户说明思考过程）
- 使用结构化的命令来标记关键事件（如 `/decision`, `/issue`, `/milestone`）
- 定期保存中间状态和重要结论
- 对于重要任务，建议在开始前明确告知需要记录哪些维度的信息

**对 quality_score 的影响**:

| 缺失信息类型 | 分数扣减 | 说明 |
|-------------|---------|------|
| 决策记录缺失 | -10 至 -20 | 第四章关键决策分析质量下降 |
| 时间信息不全 | -5 至 -15 | 第三章时间线和第八章时间分析精度降低 |
| 问题记录模糊 | -10 至 -20 | 第五章问题分析深度不足 |
| 资源信息缺失 | -5 至 -10 | 第六章资源分析简化 |
| 协作信息缺失 | -0 至 -10 | 第七章标注为"不适用"（单人任务时不扣分） |

---

### E011: ConversationHistoryUnavailable

| 属性 | 值 |
|------|---|
| **错误码** | E011 |
| **名称** | ConversationHistoryUnavailable |
| **类别** | data_source |
| **严重程度** | 🟠 Error |
| **HTTP 状态码** | 503 Service Unavailable |
| **恢复模式** | partial (支持手动输入替代) |

**触发条件**:
当无法访问对话历史时触发：
- 对话历史服务不可用或超时
- 权限不足无法读取对话记录
- 对话已被删除或过期
- 会话ID无效或不存在
- 网络连接问题导致数据拉取失败

**错误消息模板**:
```
对话历史不可用: {reason}

错误原因: {detailed_reason}
会话ID: {session_id} (如适用)

可选的恢复方案:
1. 手动提供任务执行的关键信息
2. 稍后重试（如果是临时性服务问题）
3. 从本地缓存或导出的记录中恢复

如选择手动输入，请提供以下信息:
- 任务目标和背景
- 主要执行步骤
- 遇到的问题和解决方案
- 关键决策及其理由
```

**示例场景**:
> 由于权限变更，系统无法访问用户指定的历史会话记录。
>
> **请求**: `{ "session_id": "sess_98765" }`
>
> **响应**:
> ```json
> {
>   "success": false,
>   "error": {
>     "code": "E011",
>     "name": "ConversationHistoryUnavailable",
>     "message": "对话历史不可用: 权限不足",
>     "context": {
>       "session_id": "sess_98765",
>       "reason": "ACCESS_DENIED",
>       "retryable": false
>     },
>     "recovery": {
>       "mode": "partial",
       "suggestions": [
         "检查会话访问权限是否正确配置",
         "使用 manual_input 模式手动提供任务信息",
         "联系管理员确认数据保留策略"
       ],
       "alternative_mode": {
         "type": "manual_input",
         "description": "切换到手动输入模式，通过表单或对话方式提供任务信息",
         "required_fields": [
           "task_name", "objectives", "timeline_summary",
           "key_decisions", "issues_encountered", "outcomes"
         ]
       }
     }
   }
 }
> ```

**恢复建议**:
1. **检查权限**：确认当前身份有权限访问目标会话
2. **使用手动模式**：切换到手动输入模式，自行填写任务信息
3. **等待重试**：如果是临时服务问题，等待几分钟后重试
4. **导出恢复**：如果之前有导出过对话记录，可以从本地文件恢复

**预防措施**:
- 定期备份重要的对话记录
- 使用持久化的存储方案而非纯内存
- 实现分级权限管理，避免意外丢失访问权
- 提供对话导出功能，让用户可以本地存档

---

### E012: FileAccessDenied

| 属性 | 值 |
|------|---|
| **错误码** | E012 |
| **名称** | FileAccessDenied |
| **类别** | data_source |
| **严重程度** | 🟠 Error |
| **HTTP 状态码** | 403 Forbidden |
| **恢复模式** | partial (更换路径或权限修复后重试) |

**触发条件**:
当无法读写指定的文件时触发：
- 输出目录没有写入权限
- 指定的文件路径不存在且无法创建（父目录无权限）
- 文件被其他进程锁定
- 磁盘配额已满
- 安全策略禁止访问该路径（如沙箱限制）

**错误消息模板**:
```
文件访问被拒绝: {file_path}

操作类型: {operation} (read/write/create/delete)
原因: {access_denied_reason}

当前用户: {current_user}
目标路径权限: {path_permissions}
磁盘状态: {disk_status}

建议:
1. 检查文件/目录权限设置
2. 更换输出路径到有权限的位置
3. 以更高权限运行（谨慎使用）
4. 检查磁盘空间是否充足
```

**示例场景**:
> 用户指定将报告输出到系统保护目录 `C:\Windows\` 下。
>
> **请求**: `{ "output_path": "C:\\Windows\\task-summary.md" }`
>
> **响应**:
> ```json
> {
>   "success": false,
>   "error": {
>     "code": "E012",
>     "name": "FileAccessDenied",
>     "message": "文件访问被拒绝: C:\\Windows\\task-summary.md",
>     "context": {
>       "operation": "create",
>       "path": "C:\\Windows\\task-summary.md",
>       "reason": "SYSTEM_PROTECTED_DIRECTORY",
>       "alternative_paths": [
>         ".\\reports\\task-summary.md",
>         "%USERPROFILE%\\Documents\\task-summary.md",
>         "%TEMP%\\task-summary.md"
       ]
     },
>     "recovery": {
>       "mode": "partial",
       "suggestions": [
         "使用备选路径: ./reports/task-summary.md",
         "或指定用户目录下的路径",
         "检查目标目录的写入权限"
       ]
     }
   }
 }
> ```

**恢复建议**:
1. **更换路径**：使用推荐的备选路径或用户目录下的位置
2. **修复权限**：对目标目录授予当前用户写入权限
3. **创建父目录**：确保输出路径的所有父目录都已存在
4. **检查空间**：确认磁盘有足够的空间（建议至少预留 10MB）

**预防措施**:
- 在保存前检查目标路径的可写性
- 默认使用相对路径或用户目录下的安全位置
- 提供路径建议和自动补全功能
- 实现临时文件机制，先写到临时位置再移动

---

### E021: GoalAnalysisFailed

| 属性 | 值 |
|------|---|
| **错误码** | E021 |
| **名称** | GoalAnalysisFailed |
| **类别** | analysis_engine |
| **严重程度** | 🟠 Error |
| **HTTP 状态码** | 500 Internal Server Error |
| **恢复模式** | estimate (使用估算值代替精确分析) |

**触发条件**:
当目标达成度分析过程出现异常时触发：
- 无法从对话中提取明确的目标定义
- 目标描述过于模糊无法量化
- 缺少验收标准无法判断达成情况
- 分析算法内部错误
- 目标在执行过程中发生了重大变更且未记录

**错误消息模板**:
```
目标达成度分析失败: {failure_reason}

原始目标描述: {goal_description}
问题: {analysis_problem}

影响范围:
- 第二章: 任务背景与目标 - 目标定义部分将使用原始文本
- 第八章: 多维度分析 - 目标达成度分析将被跳过或简化
- 第一章: 执行概览 - 达成率数据将为估算值

系统将继续生成报告，目标分析部分将标注[分析受限]。
```

**示例场景**:
> 用户的任务目标是"优化一下代码"，这个描述过于模糊，无法进行量化的达成度分析。
>
> **响应** (带警告):
> ```json
> {
>   "success": true,
>   "warning": {
>     "code": "E021",
>     "name": "GoalAnalysisFailed",
>     "message": "目标达成度分析受限: 目标描述过于定性化",
>     "severity": "Error",
>     "recovery": {
>       "mode": "estimate",
       "fallback_action": "使用定性描述代替定量分析"
     }
   },
   "result": {
     "report_generated": true,
     "affected_sections": ["2.2", "8.1"],
     "quality_impact": "目标达成度将以文字描述形式呈现，不含数值化指标"
   }
 }
> ```

**恢复建议**:
1. **接受估算结果**：报告将包含定性的目标分析而非定量指标
2. **补充目标信息**：如果可能，提供更具体的目标描述和验收标准
3. **事后编辑**：在生成的报告基础上手动补充目标分析的数值

**预防措施**:
- 在任务开始时引导用户设定 SMART 目标
- 使用结构化的目标定义模板
- 在执行过程中定期确认目标是否仍然适用
- 记录目标的任何变更及其原因

---

### E022: TimelineReconstructionFailed

| 属性 | 值 |
|------|---|
| **错误码** | E022 |
| **名称** | TimelineReconstructionFailed |
| **类别** | analysis_engine |
| **严重程度** | 🟡 Warning |
| **HTTP 状态码** | 206 Partial Content |
| **恢复模式** | degrade (使用粗粒度时间线) |

**触发条件**:
当无法精确重建任务执行时间线时触发：
- 对话消息缺少时间戳或时间戳不准确
- 存在大量的离线操作（未在对话中记录的工作）
- 时间跨度太大导致精度损失
- 并行任务交错导致时序混乱
- 中途切换了工作上下文

**错误消息模板**:
```
⚠️ 时间线重建精度受限: {limitation_reason}

可用时间信息: {available_time_info}
时间精度: {precision_level} (精确到{granularity})

影响:
- 第三章: 执行过程详解 - 时间数据为近似值
- 第八章: 时间效能分析 - 效能指标为估算值

时间线将以{granularity}粒度呈现，具体时刻可能存在偏差。
```

**示例场景**:
> 用户的任务跨越了3天，但对话中有大量时间段是没有消息的（用户在离线编码），导致只能根据消息间隔粗略估计耗时。
>
> **响应** (带警告):
> ```json
> {
>   "success": true,
>   "warning": {
>     "code": "E022",
>     "name": "TimelineReconstructionFailed",
>     "message": "时间线重建精度受限: 存在大量离线操作时段",
>     "severity": "Warning",
>     "context": {
       "total_duration_known": true,
       "phase_level_timing_available": true,
       "step_level_timing_available": false,
       "estimated_precision": "±30%"
     },
     "recovery": {
       "mode": "degrade",
       "fallback_action": "使用阶段级时间估算，步骤级时间为推测值"
     }
   }
 }
> ```

**恢复建议**:
1. **接受粗粒度时间线**：报告中的时间数据标注为"估算值"
2. **手动校正**：在报告生成后手动修正已知准确的时间数据
3. **补充时间记录**：如果有外部的工时记录系统，可以整合进去

**预防措施**:
- 鼓励用户在任务执行过程中使用 `/timer` 或类似工具记录时间
- 对于长周期任务，定期进行阶段性汇报
- 使用集成开发环境的活动日志作为辅助数据源
- 在对话中使用时间标记（如"[耗时约2小时]"）

---

### E031: TemplateNotFound

| 属性 | 值 |
|------|---|
| **错误码** | E031 |
| **名称** | TemplateNotFound |
| **类别** | report_generation |
| **严重程度** | 🟠 Error |
| **HTTP 状态码** | 404 Not Found |
| **恢复模式** | terminate (必须使用有效模板) |

**触发条件**:
当请求的报告模板不存在时触发：
- 模板名称拼写错误
- 模板版本不存在
- 自定义模板已被删除
- 模板 ID 无效或过期
- 模板文件损坏无法加载

**错误消息模板**:
```
报告模板不存在: {template_identifier}

查找位置: {search_locations}
已注册模板列表: {available_templates}

可能的纠正:
1. 检查模板名称拼写
2. 使用 --list-templates 查看可用模板
3. 使用默认模板 (default) 重试
4. 确认自定义模板是否仍存在
```

**示例场景**:
> 用户指定了一个不存在的自定义模板名称。
>
> **请求**: `{ "template": "quarterly-review-v2" }`
>
> **响应**:
> ```json
> {
>   "success": false,
>   "error": {
>     "code": "E031",
>     "name": "TemplateNotFound",
>     "message": "报告模板不存在: quarterly-review-v2",
>     "context": {
>       "requested_template": "quarterly-review-v2",
>       "available_templates": [
>         "default (标准10章模板)",
>         "minimal (精简版)",
>         "technical (技术导向版)"
       ],
>       "searched_locations": [
>         "./templates/",
>         "~/.config/task-summary/templates/",
>         "/usr/share/task-summary/templates/"
       ]
>     },
>     "recovery": {
>       "mode": "terminate",
>       "suggestions": [
>         "使用默认模板: 不指定 template 参数或使用 'default'",
>         "查看可用模板: GET /api/templates",
>         "创建自定义模板: POST /api/templates"
       ]
>     }
   }
 }
> ```

**恢复建议**:
1. **使用默认模板**：省略 template 参数或使用 `"default"`
2. **列出可用模板**：调用模板列表 API 查看正确的模板名称
3. **创建新模板**：如果需要特殊格式，可以先创建再使用

**预防措施**:
- 提供模板名称的自动补全功能
- 在文档中列出所有内置模板及其用途
- 实现模板版本管理，避免误删正在使用的模板
- 对自定义模板提供验证和测试机制

---

### E032: ReportGenerationTimeout

| 属性 | 值 |
|------|---|
| **错误码** | E032 |
| **名称** | ReportGenerationTimeout |
| **类别** | report_generation |
| **严重程度** | 🟠 Error |
| **HTTP 状态码** | 504 Gateway Timeout |
| **恢复模式** | partial (返回已生成的内容) |

**触发条件**:
当报告生成过程超过预设时间限制时触发：
- 任务过于复杂（如超长对话、大量代码变更）
- 系统负载过高导致处理缓慢
- 外部服务调用阻塞（如 LLM API 响应慢）
- 模板渲染涉及大量动态内容
- 输出文件过大（如包含大量代码清单）

**错误消息模板**:
```
报告生成超时: 已超过 {timeout_limit} 限制

当前进度: {progress_percentage}%
已完成章节: {completed_chapters}
正在生成: {current_chapter}

可选操作:
1. 接收已生成的部分报告 (partial output)
2. 降低详细程度后重试 (use summary mode)
3. 排除部分章节后重试 (reduce scope)
4. 稍后重试 (system may be under load)
```

**示例场景**:
> 用户的任务对话长达200轮，包含大量代码片段，报告生成超过了默认的5分钟超时限制。
>
> **响应**:
> ```json
> {
>   "success": false,
>   "error": {
>     "code": "E032",
>     "name": "ReportGenerationTimeout",
>     "message": "报告生成超时: 已超过300秒限制",
>     "context": {
>       "timeout_limit": "300s",
>       "elapsed_time": "305s",
>       "progress": {
>         "completed_chapters": [1, 2, 3, 4, 5],
>         "in_progress": "第六章: 资源使用情况",
>         "remaining_chapters": [6, 7, 8, 9, 10]
>       },
>       "partial_output_available": true
     },
     "recovery": {
       "mode": "partial",
       "suggestions": [
         "获取部分报告: 包含已完成的前5章",
         "使用摘要模式重试: 减少约70%的处理时间",
         "增加超时时间: 设置 timeout=600 (需管理员权限)"
       ],
       "partial_result": {
         "report_path": "./task-summary-partial.md",
         "included_chapters": [1, 2, 3, 4, 5],
         "note": "报告不完整，缺少第6-10章"
       }
     }
   }
 }
> ```

**恢复建议**:
1. **接收部分报告**：获取已经完成的章节内容，后续可单独生成剩余章节
2. **降低详细程度**：使用 `detail_level="summary"` 大幅减少处理时间
3. **缩小范围**：排除不需要的章节减少工作量
4. **增加超时**：如果确实需要完整报告，联系管理员调整超时设置

**预防措施**:
- 对于大型任务，提前预估生成时间并提示用户
- 实现增量生成机制，支持断点续传
- 提供进度显示，让用户了解当前状态
- 优化性能瓶颈（如 LLM 调用批处理、缓存机制）

---

### E041: InsufficientMemory

| 属性 | 值 |
|------|---|
| **错误码** | E041 |
| **名称** | InsufficientMemory |
| **类别** | system_resource |
| **严重程度** | 🔴 Critical |
| **HTTP 状态码** | 507 Insufficient Storage |
| **恢复模式** | terminate (无法恢复，需释放资源) |

**触发条件**:
当系统内存不足以继续执行时触发：
- 处理超大对话历史时内存溢出
- 同时处理多个大型报告生成任务
- 内存泄漏导致可用内存耗尽
- 系统级别的内存压力（其他进程占用过多）
- 虚拟内存交换频繁导致性能急剧下降

**错误消息模板**:
```
🔴 致命错误: 内存不足

当前内存状态:
- 已用内存: {used_memory} / {total_memory} ({usage_percent}%)
- 可用内存: {available_memory}
- 需求内存: {estimated_required_memory}
- 内存缺口: {memory_deficit}

此错误无法自动恢复。请采取以下措施:

1. 关闭不必要的应用程序释放内存
2. 减少并发任务数量
3. 增加系统物理内存
4. 使用更轻量的配置（如 summary 模式）

错误追踪ID: {error_trace_id}
请联系系统管理员获取支持。
```

**示例场景**:
> 系统正在同时处理3个大型报告生成任务，加上其他服务的内存占用，导致可用内存不足2GB，而当前任务预计需要4GB。
>
> **响应**:
> ```json
> {
>   "success": false,
>   "error": {
>     "code": "E041",
>     "name": "InsufficientMemory",
>     "message": "🔴 致命错误: 内存不足",
>     "severity": "Critical",
>     "context": {
>       "memory_status": {
>         "total_gb": 16.0,
>         "used_gb": 14.2,
>         "available_gb": 1.8,
>         "required_gb": 4.0,
>         "deficit_gb": 2.2
>       },
>       "concurrent_tasks": 3,
>       "system_load": "high"
     },
     "recovery": {
       "mode": "terminate",
       "suggestions": [
         "等待其他任务完成后再试",
         "关闭浏览器或其他内存密集应用",
         "联系管理员增加服务器内存配置"
       ],
       "trace_id": "err_mem_20260409_143000_abc123"
     }
   }
 }
> ```

**恢复建议**:
1. **释放内存**：关闭其他占用内存的应用程序
2. **等待空闲**：等待其他报告生成任务完成
3. **降低需求**：使用 summary 模式减少内存需求（约降低60%）
4. **升级硬件**：长期解决方案是增加物理内存

**预防措施**:
- 实现内存使用监控和预警机制
- 设置并发任务数上限
- 对超大输入进行分块处理
- 实现内存优化的数据处理流水线（流式处理而非全量加载）
- 定期进行内存泄漏检测和修复

---

### E051: ExecutionTimeout

| 属性 | 值 |
|------|---|
| **错误码** | E051 |
| **名称** | ExecutionTimeout |
| **类别** | timeout |
| **严重程度** | 🟠 Error |
| **HTTP 状态码** | 504 Gateway Timeout |
| **恢复模式** | partial (返回部分结果或允许延长) |

**触发条件**:
当整个任务执行流程（从信息收集到报告生成）超过全局超时限制时触发：
- 全局超时默认值为 10 分钟
- 复杂任务（如跨多天的项目）可能需要更长处理时间
- 系统处于高负载状态导致整体变慢
- 外部依赖服务响应缓慢

**错误消息模板**:
```
执行超时: 任务总耗时已超过 {global_timeout} 限制

已用时间: {elapsed_time}
超时限制: {timeout_limit}
当前阶段: {current_phase}
阶段进度: {phase_progress}%

此超时覆盖整个执行流程，不同于单阶段的超时(E032)。

恢复选项:
1. 获取已产生的中间结果
2. 使用更宽松的超时设置重试 (需权限)
3. 简化任务范围后重试
```

**示例场景**:
> 一个涉及50+轮对话、多个代码文件变更、复杂问题排查过程的任务，总体执行时间达到了12分钟，超过了10分钟的全局超时。
>
> **响应**:
> ```json
> {
>   "success": false,
>   "error": {
>     "code": "E051",
>     "name": "ExecutionTimeout",
>     "message": "执行超时: 任务总耗时已超过600秒限制",
>     "context": {
>       "elapsed_seconds": 720,
>       "timeout_seconds": 600,
>       "current_phase": "分析处理",
>       "phase_progress": "75%",
>       "completed_phases": ["触发检测", "信息收集"],
>       "intermediate_results": {
>         "collected_data": true,
>         "analysis_partial": true,
>         "report_not_started": true
       }
     },
     "recovery": {
       "mode": "partial",
       "suggestions": [
         "任务规模较大，建议拆分为子任务分别总结",
         "使用 summary 模式可缩短约60%执行时间",
         "联系管理员调整全局超时设置"
       ]
     }
   }
 }
> ```

**恢复建议**:
1. **拆分任务**：将大型任务拆分为多个小任务分别生成报告
2. **降低复杂度**：使用 summary 模式或减少包含的章节
3. **申请延长时间**：联系管理员为当前任务类型设置更长的超时
4. **错峰执行**：在系统负载较低时重试

**预防措施**:
- 在任务开始前进行复杂度评估并预警
- 实现任务拆分建议（自动检测是否应该拆分）
- 提供进度条和预计剩余时间
- 优化各阶段的性能瓶颈
- 对已知的大型任务类型使用专门的优化路径

---

## 4. 错误处理策略矩阵

| 严重级别 | 是否中断执行 | 用户通知方式 | 日志级别 | 默认行为 | 可配置？ | 典型错误码 |
|---------|-------------|-------------|---------|---------|---------|-----------|
| **🔴 Critical** | ✅ 立即终止 | 弹窗 + 日志 + 告警 | ERROR | 返回错误，不生成任何输出，释放资源 | ❌ 不可覆盖 | E041 |
| **🟠 Error** | ✅ 终止当前操作 | 提示 + 日志 + 建议 | WARN | 返回错误信息和恢复建议，不生成完整报告 | ⚠️ 部分可配置（可选择 partial 模式） | E001, E002, E003, E004, E005, E011, E012, E021, E031, E032, E051 |
| **🟡 Warning** | ❌ 继续执行 | 报告内标注 + 日志 | INFO | 降级继续，在最终报告中体现警告信息 | ✅ 完全可配置（可选择严格模式升级为 Error） | E010, E022 |

**配置项说明**:

```yaml
error_handling_config:
  # 严格模式：将 Warning 升级为 Error
  strict_mode: false
  
  # 允许部分输出（针对 Error 级别）
  allow_partial_output: true
  
  # 降级阈值：低于此分数视为不可接受
  min_acceptable_quality_score: 60
  
  # 自动重试配置
  retry_policy:
    max_retries: 2
    retryable_errors: [E011, E032, E051]
    backoff_strategy: exponential
  
  # 通知配置
  notification:
    on_critical: ["email_admin", "slack_alert"]
    on_error: ["log_warning"]
    on_warning: ["report_annotation"]
  
  # 质量门禁
  quality_gate:
    enabled: true
    fail_on_score_below: 50
    warn_on_score_below: 70
```

---

## 5. 降级策略详解

### 5.1 降级执行流程对比

```
正常流程:
  ┌──────┐   ┌──────┐   ┌──────┐   ┌──────┐   ┌────────┐
  │ 触发  │ → │ 收集  │ → │ 分析  │ → │ 生成  │ → │ 成功交付│
  │ 检测  │   │ 信息  │   │ 处理  │   │ 报告  │   │ (100%) │
  └──────┘   └──────┘   └──────┘   └──────┘   └────────┘


降级流程 (以 E010 为例):
  ┌──────┐   ┌──────┐   ┌───────────┐   ┌──────┐   ┌─────────────┐
  │ 触发  │ → │ 收集  │ → │ ⚠️ Warning │ → │ 生成  │ → │ 降级交付     │
  │ 检测  │   │ 信息  │   │ (E010)    │   │ 报告  │   │ (85%,带警告) │
  └──────┘   └──────┘   └───────────┘   └──────┘   └─────────────┘
                           │
                           ↓
                  ┌──────────────────┐
                  │ 降级处理动作:     │
                  │ • 标记受影响章节  │
                  │ • 使用推断/默认值 │
                  │ • 计算 penalty   │
                  │ • 生成降级说明   │
                  └──────────────────┘
```

### 5.2 降级时的内容影响

当触发 E010 (InsufficientDataWarning) 时，以下内容会受到影响：

| 受影响方面 | 正常模式 | 降级模式 | 影响程度 |
|-----------|---------|---------|---------|
| **目标达成度分析** | 量化评分 + 等级 | 定性描述 + 估算等级 | 🟡 中等 |
| **时间线精度** | 精确到分钟 | 精确到阶段（±30%） | 🟡 中等 |
| **决策记录完整性** | 含完整 rationale | 仅记录决策结论 | 🟠 较高 |
| **问题分析深度** | 含根因分析和排查过程 | 仅记录问题和解决方案 | 🟠 较高 |
| **资源使用统计** | 详细清单 | 高层级概述 | 🟢 轻微 |
| **团队协作分析** | 多维度评分 | 标注"数据不足"或跳过 | 🟢 轻微 |
| **改进建议质量** | 基于数据的精准建议 | 通用性建议 | 🟡 中等 |
| **报告质量评分** | 90-100 分 | 60-85 分（视缺失程度） | — |

### 5.3 降级信息的报告呈现

在最终生成的报告中，降级信息会在以下位置体现：

**(1) 报告头部 - 元信息区域**

```markdown
> **报告元信息**
>
> - **质量评分**: 78/100 (B级) ⚠️
> - **降级标记**: 是
> - **降级原因**: E010 - 数据不充分（决策记录和时间细节有限）
> - **受影响章节**: §4 关键决策分析, §8 多维度分析
```

**(2) 受影响章节内的内联标注**

```markdown
## 第四章：关键决策分析

> ⚠️ **本章说明**: 由于决策过程的详细讨论记录有限，以下决策记录基于可用信息整理，
> 部分 rationale 为推断内容。[详见降级说明]

### 决策D1：技术选型
...
**决策依据**:
1. 性能考量 ✅ (有明确记录)
2. 团队熟悉度 🔶 (基于推断)
3. 长期维护性 ⚪ (信息不足，未列入)
```

**(3) 报告末尾 - 降级说明附录**

```markdown
---
## 附录E：降级说明 (Degradation Notice)

### 降级概要
- **降级错误码**: E010 (InsufficientDataWarning)
- **降级时间**: 2026-04-09T14:30:00Z
- **原始质量预期**: 95分 (A级)
- **实际质量得分**: 78分 (B级)
- **分数差异**: -17分

### 数据缺失详情
| 信息类别 | 缺失程度 | 影响 | 建议 |
|---------|---------|------|------|
| 决策 rationale | 60% 缺失 | 第四章分析深度降低 | 手动补充关键决策理由 |
| 精确时间戳 | 40% 缺失 | 时间线精度降低 | 如有工时记录可后续整合 |
| 问题排查细节 | 30% 缺失 | 第五章部分案例简化 | 可在回顾会议时补充 |

### 如何提升报告质量
1. 本次报告可作为初稿，建议在团队复盘会议上补充完善
2. 后续如有更多信息，可使用相同参数重新生成以获得完整版本
3. 对于未来任务，建议在执行过程中保持更详细的沟通记录
```

### 5.4 quality_score 计算与降级影响

**基础分**: 100 分

**扣分规则**:

```python
def calculate_quality_score(warnings: List[Warning]) -> int:
    score = 100
    
    for warning in warnings:
        if warning.code == "E010":
            # 根据缺失信息类型和程度扣分
            for missing_item in warning.missing_items:
                if missing_item.type == "decision_records":
                    score -= 10 * missing_item.severity  # 最高 -20
                elif missing_item.type == "timeline_data":
                    score -= 5 * missing_item.severity    # 最高 -15
                elif missing_item.type == "issue_details":
                    score -= 10 * missing_item.severity   # 最高 -20
                elif missing_item.type == "resource_info":
                    score -= 5 * missing_item.severity     # 最高 -10
        
        elif warning.code == "E022":
            score -= 5  # 时间线精度问题固定扣分
    
    # 确保分数不低于 0
    return max(0, score)


def get_quality_grade(score: int) -> str:
    if score >= 90: return "A (优秀)"
    elif score >= 80: return "B (良好)"
    elif score >= 70: return "C (合格)"
    elif score >= 60: return "D (勉强可用)"
    else: return "F (不建议使用)"
```

**质量等级与使用建议**:

| 分数区间 | 等级 | 建议操作 |
|---------|------|---------|
| 90-100 | A (优秀) | 可直接使用，适合正式归档和分享 |
| 80-89 | B (良好) | 可用，建议快速审阅后使用 |
| 70-79 | C (合格) | 建议补充关键信息后使用 |
| 60-69 | D (勉强可用) | 建议大幅修订或重新生成 |
| <60 | F (不建议使用) | 建议补充数据后重新生成 |

---

## 6. 错误码快速查询表

| 错误码 | 名称 | 一句话说明 | 严重级别 | 用户该怎么做 |
|-------|------|-----------|---------|------------|
| **E001** | MissingRequiredParameter | 忘了填 xxx | 🟠 Error | 补上这个必填参数，查看文档了解需要什么 |
| **E002** | InvalidParameterType | 参数类型不对 | 🟠 Error | 检查参数应该是字符串还是数字，改正确后重试 |
| **E003** | ParameterValueOutOfRange | 参数值超范围 | 🟠 Error | 把参数调到允许的范围内（文档里有说明） |
| **E004** | ConflictingParameters | 参数互相打架 | 🟠 Error | 去掉矛盾的其中一个参数，或换一组兼容的组合 |
| **E005** | InvalidChapterCombination | 章节选得有问题 | 🟠 Error | 补充被依赖的前置章节，或用 detail_level 快捷选择 |
| **E010** | InsufficientDataWarning | 数据不够完整 | 🟡 Warning | 报告会照常生成但部分内容是估算的，看看能不能补充信息后重新生成 |
| **E011** | ConversationHistoryUnavailable | 对话记录拿不到 | 🟠 Error | 检查权限，或切换到手动输入模式自己填写任务信息 |
| **E012** | FileAccessDenied | 文件读写被拒 | 🟠 Error | 换个有权限的路径，或给目标文件夹加上写入权限 |
| **E021** | GoalAnalysisFailed | 目标分析做不了 | 🟠 Error | 报告还是会生成，但目标达成度那块会是文字描述而不是数字 |
| **E022** | TimelineReconstructionFailed | 时间线建不准 | 🟡 Warning | 时间数据会有误差（±30%），重要的时间点可以手动校正 |
| **E031** | TemplateNotFound | 找不到模板 | 🟠 Error | 检查模板名字拼对了没，或直接用默认模板 |
| **E032** | ReportGenerationTimeout | 生成报告太慢超时了 | 🟠 Error | 可以拿已经生成的那部分，或用摘要模式重试（快很多） |
| **E041** | InsufficientMemory | 内存不够用了 | 🔴 Critical | 关掉一些其他程序释放内存，这是致命错误没法自动恢复 |
| **E051** | ExecutionTimeout | 整个任务跑太久了 | 🟠 Error | 任务太大了，考虑拆分成几个小任务分别总结 |

---

## 附录A：错误码分布图

```
E0xx 参数验证 (5个)          E1xx 数据源 (3个)           E2xx 分析引擎 (2个)
┌─────────────────┐          ┌───────────────┐          ┌───────────────┐
│ E001 缺少参数    │          │ E010 数据不足⚠️ │          │ E021 目标分析   │
│ E002 类型错误    │    →     │ E011 历史不可用 │    →     │ E022 时间线不准⚠️│
│ E003 值超范围    │          │ E012 文件权限   │          │               │
│ E004 参数冲突    │          │               │          │               │
│ E005 章节无效    │          │               │          │               │
└─────────────────┘          └───────────────┘          └───────────────┘
                                                                    ↓
                                                        E3xx 报告生成 (2个)    E4xx 资源 (1个)    E5xx 超时 (1个)
                                                        ┌───────────────┐    ┌───────────┐    ┌───────────┐
                                                        │ E031 模板不存在 │    │ E041 内存不足🔴│   │ E051 执行超时│
                                                        │ E032 生成超时   │    │           │    │           │
                                                        └───────────────┘    └───────────┘    └───────────┘
```

## 附录B：HTTP 状态码映射

| HTTP 状态码 | 含义 | 对应的错误码 |
|------------|------|------------|
| 400 Bad Request | 请求参数有问题 | E001, E002, E003, E004, E005 |
| 403 Forbidden | 无权限访问 | E012 |
| 404 Not Found | 资源不存在 | E031 |
| 206 Partial Content | 部分成功（带警告） | E010, E022 |
| 500 Internal Server Error | 服务器内部错误 | E021 |
| 503 Service Unavailable | 服务暂不可用 | E011 |
| 504 Gateway Timeout | 网关超时 | E032, E051 |
| 507 Insufficient Storage | 存储空间不足 | E041 |

## 附录C：版本更新记录

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| v1.0.0 | 2026-04-09 | 初始版本，定义15个错误码及完整的分类体系 |

---

*文档版本: v1.0.0*
*最后更新: 2026-04-09*
*适用于 Task Execution Summary Generator v1.0*
*维护者: Task Execution Summary Generator Team*
