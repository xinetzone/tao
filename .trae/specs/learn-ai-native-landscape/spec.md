# AI Native Landscape 学习 Spec

> 模板：learning-task | 变体：教程类（叙事型）
> 学习来源：https://landscape.jimmysong.io/zh/about/ （ supplemented by 主页与评分方法页）

## Why
AI 原生技术栈正快速演进，工具/Agent/运行时/基础设施层出不穷。AI Native Landscape 是 Jimmy Song 维护的策展式开源生态地图，提供结构化分类、双语描述与透明评分，是理解这一生态全貌的高质量入口。系统学习该站点内容，可建立 AI 原生技术栈的全景认知，辅助技术选型与生态定位。

## What Changes
- 新增结构化学习笔记，覆盖站点定位、收录边界、分类体系、评分方法与生态趋势
- 输出 8 大技术域与子类的分类地图（Mermaid）
- 输出评分模型（4 维度 + 5 等级 + 4 参考状态）的机制说明
- 输出自测问答集（5-10 题）用于检验学习效果
- 输出知识框架思维导图用于梳理知识体系

## Impact
- Affected specs: 无（纯学习任务）
- Affected code: 无
- 学习来源:
  - 主源：https://landscape.jimmysong.io/zh/about/ （关于页）
  - 补充源：https://landscape.jimmysong.io/zh/ （主页：8 分类 663 项目结构）
  - 补充源：https://landscape.jimmysong.io/zh/methodology/ （评分体系与收录标准）

## ADDED Requirements

### Requirement: 核心概念定义与解释
系统 SHALL 提取并定义学习内容中的核心概念，每个概念包含清晰的名称、定义和关键特征。

#### Scenario: 核心概念提取
- **WHEN** 阅读关于页、主页与评分方法页后
- **THEN** 输出每个核心概念的明确定义与解释，数量不少于 5 个（覆盖：AI Native Landscape、AI 原生技术栈、策展式收录、项目墓地、综合健康度评分、参考状态等）

### Requirement: 技术原理与工作机制
系统 SHALL 阐述学习内容中的关键技术原理、工作机制或底层逻辑，必要时使用流程图辅助说明。

#### Scenario: 技术原理分析
- **WHEN** 分析评分模型、收录流程、归档机制等环节
- **THEN** 输出原理说明，包含至少 1 张 Mermaid 流程图（如：评分计算流程 / 项目生命周期 / 收录与归档流转）

### Requirement: 实践案例分析与应用场景
系统 SHALL 总结学习内容中的实践案例、操作步骤或应用场景，以可复现的形式呈现。

#### Scenario: 实践案例归纳
- **WHEN** 梳理站点中的实操部分（提交项目、变更项目、归档项目、按域浏览、按评分筛选等）
- **THEN** 输出按场景分类的实践案例，每个案例包含步骤或模板（如：如何提交一个新项目、如何通过评分筛选选型）

### Requirement: 关键结论与个人理解
系统 SHALL 归纳学习后的关键结论（5-8 条），并结合个人理解形成可迁移的知识总结。

#### Scenario: 结论提炼
- **WHEN** 完成全部内容学习后
- **THEN** 输出关键结论列表 + 可迁移知识总结（含至少 1 个"可迁移模式"，如：策展式生态地图的治理方法论可迁移到其他技术生态整理）

### Requirement: 自测问答
系统 SHALL 基于学习内容设计 5-10 个关键问题并提供标准答案。

#### Scenario: 自测题设计
- **WHEN** 学习内容整理完成后
- **THEN** 输出 5-10 道覆盖核心知识点的 Q&A（覆盖：站点定位、收录边界、8 大分类、评分 4 维度、5 等级、4 参考状态、提交流程、归档条件等维度）

### Requirement: 知识框架梳理
系统 SHALL 构建 Mermaid 思维导图，以结构化方式总结全部学习内容。

#### Scenario: 知识框架构建
- **WHEN** 全部学习内容整理完成后
- **THEN** 输出 Mermaid mindmap，展示知识体系结构，覆盖全部学习模块（定位、收录边界、分类体系、评分模型、参考状态、提交流程、生态趋势）
