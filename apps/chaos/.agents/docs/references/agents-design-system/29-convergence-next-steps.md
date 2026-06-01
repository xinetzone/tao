# 29. 收敛方向与下一步

30 条洞见、5 条元洞察、一份 Spec、一个 `world init`。需要收敛。以下三个方向，按影响力从高到低排列。

## 29.1 方向一：补上治理文档（GOVERNANCE.md）

> 对应洞见三十。这是目前最大的单一风险点。

**为什么排第一**：Spec v0.2 的 Phase 1 目标是把 Layer 1 作为独立标准发布。但一个没有治理模型的标准，对外发布后收到的第一个问题是"我怎么参与决策？"——如果答案是"找我"，标准就死了。

**具体动作**：
- 创建 `GOVERNANCE.md`，定义 RFC 流程、核心维护者、Layer 归属仲裁机制
- 把 Spec v0.2 文档从 `.agents/docs/superpowers/specs/` 移到项目顶级 `specs/` 目录（洞见二十八）
- 给 `world.toml` 加 `spec_role` 字段（洞见二十六）

**工作量**：2-3 个文件创建/移动，0 行代码。

## 29.2 方向二：补上 `world init` 后的下一步引导

> 对应洞见二十七。30 秒尖叫之后的沉默需要打破。

**为什么排第二**：`world init` 现在是断头路。用户生成了骨架，不知道下一步该干什么。这和 `npm init` 之后没有 `npm install` 是同一个级别的体验缺陷。

**具体动作**：
- `world guide` 命令：按项目类型推荐 fragments
- `world init` 完成后自动提示推荐安装
- `world fragment init --from-rules`：将已有 rules 一键打包为 fragment（洞见二十九）

**工作量**：约 200 行 Python，2 个新命令文件。

## 29.3 方向三：让 AgentForge 吃自己的 dogfood

> 对应洞见二十四。在 CI 里跑 constraints-check。

**为什么排第三**：这是"规范即代码"的终极验证。如果 AgentForge 自己的 CI 都不检查 constraints.toml，凭什么让别人遵守？

**具体动作**：
- 在 `.github/workflows/ci.yml` 加一步 `world constraints check --strict`
- 如果 CI 红了（比如某个 Role 绑定的 rule 文件不存在），修好它
- 这是 v0.2 设计哲学里"设计验证内嵌于规则本身"的兑现

**工作量**：CI 加 3 行 YAML + 可能的修复工作。

## 29.4 推荐起步顺序

**建议从方向一开始**——先立治理，再补体验，最后自证。因为方向一决定了"别人能不能参与进来"，而参与是后面一切的前提。
