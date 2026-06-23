# Tasks

## Phase 1: 提取与归纳

- [x] Task 1: 从 refactor-retrospectives-modularization 提取工作流程与决策点
  - [x] SubTask 1.1: 提取 5 阶段流程的目标、输入、输出、决策点
  - [x] SubTask 1.2: 归纳关键决策点（拆分阈值、分类层级、命名规范、元数据组织）
  - [x] SubTask 1.3: 提取子智能体提示词的共性结构（角色、任务、输入、步骤、输出、约束）

## Phase 2: 框架编写

- [x] Task 2: 编写方法论框架文档
  - [x] SubTask 2.1: 编写 5 阶段标准化流程（每阶段含目标、输入、输出、决策点）
  - [x] SubTask 2.2: 编写 5 类可复用提示词模板（含参数化占位符）
  - [x] SubTask 2.3: 编写 6 类常见场景处理指南
  - [x] SubTask 2.4: 编写 4 维度质量评估标准（含可量化指标）
  - [x] SubTask 2.5: 编写适用性边界（适用与不适用场景）

## Phase 3: 验证与示例

- [x] Task 3: 用原重构实例验证框架的覆盖度与可操作性
  - [x] SubTask 3.1: 将原重构的每个任务映射至框架阶段，验证覆盖度（8/8=100%）
  - [x] SubTask 3.2: 验证提示词模板可参数化复用至其他目录（如 plans/、memories/）

# Task Dependencies

- [Task 2] depends on [Task 1]
- [Task 3] depends on [Task 2]
