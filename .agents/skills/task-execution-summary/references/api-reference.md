# 任务执行总结报告生成器 - 参数参考文档

> **文档版本**: v2.0
>
> **最后更新**: 2026-05-20
>
> **适用技能版本**: task-execution-summary v2.2
>
> **维护者**: Task Execution Summary Generator Team

---

## 目录

- [1. 文档定位](#1-文档定位)
- [2. 输入方式](#2-输入方式)
- [3. 输入参数定义](#3-输入参数定义)
- [4. 输出格式定义](#4-输出格式定义)
- [5. 参数校验规则](#5-参数校验规则)
- [6. 调用示例](#6-调用示例)
- [7. 版本记录](#7-版本记录)

---

## 1. 文档定位

本文档描述的是 `task-execution-summary` 技能在对话内可理解的参数模型，用于帮助模型或集成工作流生成一致的任务执行总结。

它不是远程 REST API 规范，不包含公网地址、认证流程、速率限制或服务端 SLA。若宿主系统需要将这些参数映射到自己的命令、表单或自动化工作流，应由宿主系统自行负责实现。

---

## 2. 输入方式

本技能支持两类输入：

### 2.1 自然语言输入

适合直接在对话中触发技能，例如：

```text
帮我总结一下这个任务
Sprint 结束了，做个回顾
请生成详细版任务总结，重点分析关键决策和问题解决
```

### 2.2 结构化输入

适合希望明确控制输出字段或在自动化工作流中复用同一套参数语义的场景，例如：

```json
{
  "task_context": {
    "task_name": "用户认证模块开发",
    "task_type": "development"
  },
  "generation_options": {
    "detail_level": "standard",
    "include_sections": ["overview", "execution", "decisions", "issues", "actions"],
    "language": "zh-CN",
    "tone": "professional"
  },
  "output_config": {
    "format": "markdown",
    "save_to": "./reports/task-summary-auth-module.md"
  }
}
```

---

## 3. 输入参数定义

### 3.1 `task_context` 对象

`task_context` 是总结对象的核心信息容器。

#### `task_name`

- **类型**: string
- **必填**: 是
- **默认值**: 无
- **说明**: 任务名称或任务主题，用于标识本次总结对象
- **约束**:
  - 长度 2-200 字符
  - 不允许纯空格
  - 支持中文、英文、数字及常见标点

#### `task_type`

- **类型**: enum
- **必填**: 否
- **默认值**: `auto-detect`
- **可选值**:
  - `development`
  - `management`
  - `operations`
  - `research`
  - `learning`
  - `auto-detect`
- **说明**: 用于帮助技能调整分析权重和模板措辞

#### `time_range`

- **类型**: object
- **必填**: 否
- **默认值**: 自动从对话中推断
- **字段**:
  - `start_time`: ISO 8601 时间
  - `end_time`: ISO 8601 时间
- **说明**: 用于限制总结范围

### 3.2 `generation_options` 对象

#### `detail_level`

- **类型**: enum
- **必填**: 否
- **默认值**: `standard`
- **可选值**: `summary` / `standard` / `detailed`
- **说明**: 控制报告篇幅和分析深度

#### `include_sections`

- **类型**: array<string>
- **必填**: 否
- **默认值**: 全部标准章节
- **说明**: 指定需要输出的章节范围

#### `language`

- **类型**: enum
- **必填**: 否
- **默认值**: `zh-CN`
- **说明**: 输出语言

#### `tone`

- **类型**: enum
- **必填**: 否
- **默认值**: `professional`
- **可选值**: `professional` / `casual`
- **说明**: 控制整体文风

### 3.3 `output_config` 对象

#### `format`

- **类型**: enum
- **必填**: 否
- **默认值**: `markdown`
- **说明**: 当前主输出格式为 Markdown

#### `save_to`

- **类型**: string
- **必填**: 否
- **默认值**: 由宿主工作区决定
- **说明**: 若宿主环境支持保存文件，可用该字段表达期望输出路径

---

## 4. 输出格式定义

### 4.1 主输出

技能返回一份 Markdown 格式的结构化报告，通常包含以下内容：

- 执行概览
- 目标背景
- 执行过程
- 关键决策
- 问题解决
- 资源使用
- 团队协作（如适用）
- 多维分析
- 经验方法
- 改进行动

### 4.2 辅助输出

根据上下文与宿主能力，可能附带以下信息：

- 低置信度或信息不足提示
- 保存路径
- 章节裁剪结果
- 风险预警与改进优先级

---

## 5. 参数校验规则

### 5.1 必填约束

- 缺少 `task_context.task_name` 时，返回 `E001`
- `task_name` 为空、全空格或明显非法时，返回 `E002`

### 5.2 枚举约束

- `detail_level` 仅允许 `summary` / `standard` / `detailed`
- `task_type` 仅允许文档列出的枚举值
- `tone` 仅允许 `professional` / `casual`

### 5.3 降级策略

- 对话历史不足时，允许返回带 `E010` 警告的降级报告
- 协作信息缺失时，可省略团队协作章节而非整体失败
- 时间戳不完整时，可使用“约耗时”或“阶段性推断”替代精确统计

---

## 6. 调用示例

### 6.1 最小调用

```text
请生成任务总结：用户认证模块开发
```

### 6.2 常规调用

```text
请生成标准版任务总结：Sprint 24 回顾，重点关注团队协作和进度偏差
```

### 6.3 结构化调用

```json
{
  "task_context": {
    "task_name": "Docker 容器化学习",
    "task_type": "learning"
  },
  "generation_options": {
    "detail_level": "summary",
    "language": "zh-CN",
    "tone": "professional"
  }
}
```

---

## 7. 版本记录

| 版本 | 日期 | 变更 |
|------|------|------|
| v2.0 | 2026-05-20 | 从虚构远程 API 规范调整为技能内参数参考，移除公网地址、认证与速率限制描述 |
| v1.0 | 2026-04-09 | 初版参数说明文档 |
