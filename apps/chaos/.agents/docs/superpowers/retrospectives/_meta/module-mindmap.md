# Retrospectives 模块化结构思维导图

> **生成日期**：2026-06-23
> **用途**：帮助团队快速理解 retrospectives 模块化重构后的目录划分与层级关系
> **配套文档**：[module-catalog.md](./module-catalog.md)、[dependency-graph.md](./dependency-graph.md)

## 可视化思维导图

```mermaid
mindmap
  root((retrospectives/))
    _meta[元数据治理]
      naming-convention[命名规范]
      module-catalog[模块目录清单]
      dependency-graph[依赖关系图谱]
      migration-log[迁移日志]
    project-reviews[项目级复盘<br/>4 份文件]
      agentforge-retro-20260523[原子化目录<br/>6 单元]
      project-retrospective-governance-20260609
      retrospective-agentforge-project-20260601
      taolib-project-review-2026-05
    audit-reports[质量审计<br/>2 份文件]
      memory-debt-20260611[原子化目录<br/>4 单元]
      mise-knowledge-base-quality-audit-20260518
    insights[技术洞察<br/>3 份文件]
      insights-containerrun-refactor-20260610
      insights-context-hub-20260622
      insights-cross-module-private-import-refactor-20260417
    session-reviews[会话复盘<br/>1 份文件]
      session-retrospective-doc-governance-full-cycle-20260611
    task-summaries[任务总结<br/>60 份文件 + 9 子模块]
      ci-cd[CI/CD<br/>5 份]
      documentation[文档治理<br/>16 份]
      python-environment[Python 环境<br/>7 份]
        lint-python313-20260609[原子化目录<br/>13 单元]
      skills[技能资产<br/>2 份]
      releases[版本发布<br/>5 份]
      exploration[探索任务<br/>8 份]
      world-cli[World CLI<br/>3 份]
      refactoring[代码重构<br/>3 份]
        containerrun-refactor-20260610[原子化目录<br/>12 单元]
      misc[其他任务<br/>11 份]
        agentforge-collaboration-20260524[原子化目录<br/>12 单元]
    misc[其他复盘<br/>2 份文件]
      wechat-archive-and-commits-summary-20260623
      zhihu-promotion-content-20260525
    README[总入口索引]
```

## 模块层级关系图

```mermaid
flowchart TD
    Root["retrospectives/"]

    subgraph L1["一级模块"]
        M1["project-reviews/<br/>项目级复盘"]
        M2["audit-reports/<br/>质量审计"]
        M3["insights/<br/>技术洞察"]
        M4["session-reviews/<br/>会话复盘"]
        M5["task-summaries/<br/>任务总结"]
        M6["misc/<br/>其他复盘"]
    end

    subgraph L2["task-summaries 二级子模块"]
        S1["ci-cd/"]
        S2["documentation/"]
        S3["python-environment/"]
        S4["skills/"]
        S5["releases/"]
        S6["exploration/"]
        S7["world-cli/"]
        S8["refactoring/"]
        S9["misc/"]
    end

    subgraph L3["原子化拆分目录"]
        A1["agentforge-project-retrospective-20260523/<br/>6 单元"]
        A2["audit-report-superpowers-memory-debt-20260611/<br/>4 单元"]
        A3["task-summary-lint-python313-20260609/<br/>13 单元"]
        A4["task-summary-agentforge-collaboration-system-20260524/<br/>12 单元"]
        A5["task-summary-containerrun-refactor-20260610/<br/>12 单元"]
    end

    Root --> M1
    Root --> M2
    Root --> M3
    Root --> M4
    Root --> M5
    Root --> M6

    M5 --> S1
    M5 --> S2
    M5 --> S3
    M5 --> S4
    M5 --> S5
    M5 --> S6
    M5 --> S7
    M5 --> S8
    M5 --> S9

    M1 --> A1
    M2 --> A2
    S3 --> A3
    S9 --> A4
    S8 --> A5

    style Root fill:#4a90e2,color:#fff,stroke:#2c5f8a,stroke-width:3px
    style M5 fill:#f5a623,color:#fff,stroke:#b87a1a,stroke-width:2px
    style A1 fill:#7ed321,color:#fff,stroke:#5a9a18
    style A2 fill:#7ed321,color:#fff,stroke:#5a9a18
    style A3 fill:#7ed321,color:#fff,stroke:#5a9a18
    style A4 fill:#7ed321,color:#fff,stroke:#5a9a18
    style A5 fill:#7ed321,color:#fff,stroke:#5a9a18
```

## 统计摘要

| 维度 | 数量 |
|------|------|
| 一级模块 | 6 |
| 二级子模块（task-summaries 下） | 9 |
| 原子化拆分目录 | 5 |
| 原子单元文件总数 | 47 |
| 模块 README 总数 | 15 |
| 元数据文档 | 4 |
| 原始文件迁移完成率 | 100% (72/72) |

## 模块功能速查

| 模块 | 核心用途 | 典型场景 |
|------|---------|---------|
| `project-reviews/` | 项目级阶段性全面复盘 | 季度回顾、里程碑总结 |
| `audit-reports/` | 质量审计与债务评估 | 技术债盘点、知识库质量审计 |
| `insights/` | 技术洞察与设计反思 | 架构反思、设计模式洞察 |
| `session-reviews/` | 单次会话复盘 | 重要会话过程记录 |
| `task-summaries/` | 任务执行总结（按主题分类） | 查找特定任务的执行记录 |
| `misc/` | 其他复盘 | 微信归档、知乎推广等 |

## 原子化拆分说明

5 份大型多主题文档（>500 行）已拆分为原子化目录，每个目录含：

- `index.md` — 索引文件，提供导航与章节映射
- 多个原子单元文件 — 每个专注单一主题，可独立阅读

| 原子化目录 | 所属模块 | 原始行数 | 原子单元数 |
|-----------|---------|---------|-----------|
| `agentforge-project-retrospective-20260523/` | project-reviews | 575 | 6 |
| `audit-report-superpowers-memory-debt-20260611/` | audit-reports | 398 | 4 |
| `task-summary-lint-python313-20260609/` | python-environment | 878 | 13 |
| `task-summary-agentforge-collaboration-system-20260524/` | misc | 777 | 12 |
| `task-summary-containerrun-refactor-20260610/` | refactoring | 546 | 12 |

## 使用指南

1. **快速浏览全局**：从上方思维导图入手，理解模块层级关系
2. **定位特定主题**：根据模块功能速查表，进入对应一级模块的 README
3. **深入大型文档**：进入原子化目录的 `index.md`，按章节导航
4. **理解依赖关系**：查看 [dependency-graph.md](./dependency-graph.md)
5. **验证迁移完整性**：查看 [migration-log.md](./migration-log.md)
