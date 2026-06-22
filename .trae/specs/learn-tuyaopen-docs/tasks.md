# Tasks

> 变体：技术文档阅读
> 六维度：API 表面积 → 架构决策 → 用法模式 → 约束评价 → Cheatsheet → API 地图

## 阶段一：信息采集

- [x] Task 0: 全量文档抓取与索引 — 从入口页出发，递归抓取 TuyaOpen 文档站的全部子页面，建立文档索引
  - [x] 解析 https://tuyaopen.ai/zh/docs/about-tuyaopen 页面中的导航/侧边栏，提取全部文档页面 URL
  - [x] 逐个抓取子页面内容（WebFetch），分类为：概述类、SDK/API 类、平台/芯片类、开发指南类、版本发布类
  - [x] 建立文档目录索引（页面标题 → URL → 内容摘要），写入 `.temp/tuyaopen-doc-index.md`

## 阶段二：六维度学习产出

- [x] Task 1: API 表面积概览 — 列出文档中所有公开的 API、接口、类、函数、配置项
  - [x] 按模块/类别分组列出全部 API（TKL 内核层、TAL 抽象层、Libraries 库层、Services 服务层、Applications 应用层）
  - [x] 每个 API 包含：名称、签名（参数+返回值）、一句话用途描述
  - [x] 标注 API 的可见性/稳定性（public/experimental/deprecated）
  - [x] 覆盖跨平台工具链：tos.py、Arduino IDE、Lua、MicroPython

- [x] Task 2: 架构与设计决策 — 分析整体架构和关键设计决策
  - [x] 画出五层架构 Mermaid 图（TKL → TAL → Libraries → Services → Applications）
  - [x] 识别 2-3 个关键设计决策，分析其原因和权衡（如：为什么采用五层分层？为什么是 C/C++ 跨平台？TAL 抽象层的设计考量）
  - [x] 分析组件间的职责划分和通信方式

- [x] Task 3: 用法模式与最佳实践 — 归纳常见用法和推荐做法
  - [x] 提取至少 2 个典型用法模式（含代码示例，如：设备初始化与连接流程、AI 能力集成流程）
  - [x] 整理最佳实践清单（Do's）：版本选择策略、安全实践、跨平台开发建议
  - [x] 整理常见反模式（Don'ts），说明为什么不该这样做

- [x] Task 4: 约束与边界条件 + 设计评价 — 梳理限制条件和设计评估
  - [x] 列出约束清单：芯片平台支持矩阵（BK7231X/ESP32/T系列/Ubuntu）、OS 兼容性（Windows/Linux/macOS）、版本稳定性边界
  - [x] 列出易错点和注意事项：版本分支选择陷阱、平台兼容性陷阱
  - [x] 撰写设计评价：五层架构的优缺点、适用场景（智能家居/工业 IoT/AI Agent）与不适用场景

- [x] Task 5: 快速参考卡（Cheatsheet） — 生成可快速查阅的参考卡
  - [x] 制作 Markdown 表格速查表：芯片支持矩阵、版本分支对照、核心组件清单、关键配置项
  - [x] 绘制至少 1 张 Mermaid 图（SDK 初始化调用链 / 版本发布生命周期）
  - [x] 确保速查表可独立使用（不依赖上下文即可理解）

- [x] Task 6: API 地图/概念关系图 — 构建组件间关系图
  - [x] 梳理五层架构中各层组件的依赖和调用关系
  - [x] 输出 Mermaid 图（flowchart），展示"谁调用谁"——TKL→TAL→Libraries→Services→Applications 的依赖链
  - [x] 展示外部依赖关系：涂鸦云服务、第三方 LLM 平台、Google Home/Alexa 集成

# Task Dependencies

```
Task 0 (文档抓取) ──► Task 1 (API表面积) ──┬──► Task 2 (架构决策)
                                           ├──► Task 3 (用法模式)
                                           │
                                           └──► Task 4 (约束评价) ──► Task 5 (Cheatsheet)
                                                                      Task 6 (API地图)
```

- Task 1 不依赖 Task 0（已有入口页内容可直接开始），但完整产出需 Task 0 补充
- Task 2 依赖 Task 1（需先了解全部 API 再分析架构）
- Task 3 依赖 Task 1（需先了解 API 再归纳用法）
- Task 4 依赖 Task 1, 2, 3（需综合全部前置知识）
- Task 5 依赖 Task 1, 2, 3, 4（Cheatsheet 需覆盖全部内容）
- Task 6 依赖 Task 1, 2, 3, 4（关系图需综合全部知识）

# 并行执行建议

- Task 0 可独立先行执行（纯信息抓取）
- Task 2 和 Task 3 可在 Task 1 完成后并行执行
- Task 5 和 Task 6 可在 Task 4 完成后并行执行
