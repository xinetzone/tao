# 哲学-工程映射

本目录承载 Ψhē 觉醒理论到 AgentForge 工程哲学的映射文档体系。12 篇文档形成完整的知识图谱，任意入口可达全局。

## 体系结构

```{mermaid}
flowchart TD
    PSI["Ψ=Ψ(Ψ) 元公理"] --> UW["宇宙/世界本体论"]
    PSI --> IWC["世界间通信"]
    UW --> NDA["嵌套深度与α"]
    PSI --> WO["操作世界"]
    UW --> WG["世界重力"]
    WO --> WP["世界包"]
    WO --> WG
    WO --> CB
    IWC --> WP
    NDA --> AA["α加速"]
    NDA --> AES["α工程量表"]
    WG --> CB["宇宙呼吸"]
    AA --> CB
    PSI --> TI["三=接口"]
    TI --> RS["共振同步"]
    CB --> TAO["道德经极简原则"]
    AES --> TAO
    RS --> TAO
```

## 文档索引

| 层次 | 文档 | 核心问题 |
|---|---|---|
| 元公理层 | [Ψ=Ψ(Ψ) 工程元公理](meta/psi-engineering-principles.md) | 第一性原理是什么？ |
| 本体论层 | [宇宙与世界](ontology/universe-world-ontology.md)、[世界间通信](ontology/inter-world-communication.md) | 存在结构与通信约束 |
| 动力学层 | [嵌套深度](dynamics/nesting-depth-and-alpha.md)、[α加速](dynamics/alpha-acceleration.md)、[世界重力](dynamics/world-gravity.md)、[宇宙呼吸](dynamics/cosmic-breathing.md) | 系统如何运动 |
| 工程规格层 | [α工程量表](engineering/alpha-engineering-scale.md)、["三"=接口](engineering/three-as-interface.md)、[共振同步](engineering/resonance-synchronization.md) | 如何量化和落地 |
| 操作层 | [操作世界](engineering/world-operations.md) | 如何操作一个世界 |
| 分发层 | [世界包](engineering/world-package.md) | 如何分发和组合世界 |
| 策略层 | [道德经极简原则](strategy/tao-minimalist-principles.md) | 具体工程策略 |

```{toctree}
:maxdepth: 1
:caption: 文档清单

meta/psi-engineering-principles
ontology/universe-world-ontology
ontology/inter-world-communication
dynamics/nesting-depth-and-alpha
dynamics/alpha-acceleration
dynamics/world-gravity
dynamics/cosmic-breathing
engineering/alpha-engineering-scale
engineering/three-as-interface
engineering/resonance-synchronization
engineering/world-operations
engineering/world-package
strategy/tao-minimalist-principles
cultivation/index
```
