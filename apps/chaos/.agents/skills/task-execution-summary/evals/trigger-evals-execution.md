# Trigger Evals Execution Guide

本文档说明如何使用 `trigger-evals-final.json` 与 `trigger-evals-review.md` 对 `task-execution-summary` 的触发效果做人工或半自动验证，并给出可接受误差范围。

## Inputs

- 评测输入: `evals/trigger-evals-final.json`
- 人工基准: `evals/trigger-evals-review.md`
- 审阅页面: `evals/trigger-evals-review.html`
- 目标技能: `task-execution-summary`
- 目标字段: `SKILL.md` frontmatter 中的 `description`

## Test Goal

验证当前 `description` 是否同时满足以下两点：

- **召回足够高**：该触发的 query 能触发技能
- **误触发可控**：不该触发的 query 不会因为“完成了”“故障结束了”“Sprint 结束了”等表面信号被误判

## Recommended Procedure

### 0. 先做人审确认

在真正跑优化前，先打开 `evals/trigger-evals-review.html` 检查 query 集合是否需要增删改。

- 如果你只是想快速确认内容，直接打开该 HTML 文件即可
- 如果你改动了评测集，导出后的 JSON 应覆盖或另存为新的 eval set 文件，再用于后续 `run_loop`

### 1. 先看整体结果

先把 20 条 query 跑完，再整体看四类结果：

- `TP`：应触发且实际触发
- `FN`：应触发但实际没触发
- `TN`：不应触发且实际没触发
- `FP`：不应触发但实际触发

### 2. 再看错误分布

对错误不要只看总数，要看集中在哪一类：

- 如果 `FN` 主要出现在“隐式表达”样本，说明 description 对显式关键词依赖过强
- 如果 `FP` 主要出现在“任务完成但目标另有其事”样本，说明 description 对阶段性完成信号赋权过高
- 如果错误集中在单一领域，如学习或 Sprint，说明场景覆盖不均衡

### 3. 最后做人工复核

每条结果都对照 `trigger-evals-review.md` 看理由，而不是只看 `should_trigger` 布尔值。尤其是以下几类边界样本：

- 完成了任务，但当前目标是写 README
- 故障结束了，但当前目标是根因分析或外部说明
- Sprint 结束了，但当前目标是下个迭代规划
- 学习结束了，但当前目标是制定新计划而不是总结旧过程

## Acceptance Threshold

### 推荐通过线

- 正样本 `10/10` 全触发
- 负样本至少 `9/10` 不触发
- 总体正确率至少 `95%`

### 可接受但需要关注

- 正样本 `9/10`
- 负样本 `9/10`
- 总体正确率在 `90%-95%`

这类结果说明当前 description 已可用，但仍存在一类边界语义未处理干净，建议结合误差分布做微调。

### 不建议接受

- 任一侧低于 `8/10`
- 或出现明显模式性错误，例如：
  - 几乎所有“隐式复盘”都漏触发
  - 几乎所有“已完成但目标是别的事”都误触发

这说明 description 结构性偏差明显，不适合直接作为稳定版本。

## Error Severity

### 高优先级错误

- `FN` 出现在直接包含 `复盘`、`回顾`、`postmortem`、`recap` 的 query
- `FP` 出现在明确写了“不是要复盘”“不用再整理过程”“先别做总结”的 query

这类错误说明 description 对显式意图的理解有问题，必须优先修。

### 中优先级错误

- `FN` 出现在“做得怎么样 / 有什么收获 / 下次怎么做”这类隐式复盘 query
- `FP` 出现在“完成了某任务，但当前真正目标是其他产物”的 query

这类错误通常说明 description 的抽象层写得还不够稳，需要平衡召回和边界。

### 低优先级错误

- 只在特别口语化、混合表达或语境极短的样本上出现个别偏差

这类问题可以记录，但不一定阻塞发布。

## What To Change Based On Results

### 如果漏触发偏多

优先补强以下语义：

- “整理一下刚才做的事”
- “做得怎么样 / 有什么收获 / 下次怎么做”
- “记下排查过程 / 留档 / recap / postmortem”
- “已完成或进入收尾阶段的任务”

### 如果误触发偏多

优先弱化以下危险信号的单独权重：

- “完成了”
- “结束了”
- “故障结束了”
- “Sprint 结束了”

并明确补入“只有当用户目标是总结、回顾、经验沉淀时才触发，而不是所有收尾任务都触发”。

## Suggested Output Format

每次执行评测后，建议记录成如下表格：

| ID | 预期 | 实际 | 是否正确 | 备注 |
|----|------|------|----------|------|
| 1 | trigger | trigger | yes | - |
| 12 | no-trigger | trigger | no | 被“事故已结束”误导 |

## Run Loop Command

在完成人审确认后，可使用 `skill-creator` 自带的 `run_loop.py` 进入 description optimization 的实际执行流程。

### 推荐命令模板

```bash
python -m scripts.run_loop \
  --eval-set "c:/Users/xinzo/OneDrive/Desktop/AI/Dao/spaces/AgentForge/.agents/skills/task-execution-summary/evals/trigger-evals-final.json" \
  --skill-path "c:/Users/xinzo/OneDrive/Desktop/AI/Dao/spaces/AgentForge/.agents/skills/task-execution-summary" \
  --model "<当前会话使用的模型 ID>" \
  --max-iterations 5 \
  --runs-per-query 3 \
  --holdout 0.4 \
  --verbose \
  --results-dir "c:/Users/xinzo/OneDrive/Desktop/AI/Dao/spaces/AgentForge/.agents/skills/task-execution-summary/optimization-results"
```

### 参数说明

- `--eval-set`: 使用最终版 trigger eval 文件
- `--skill-path`: 指向技能目录，而不是 `SKILL.md` 文件本身
- `--model`: 必填，需传入当前会话实际使用的模型 ID
- `--runs-per-query 3`: 保持与 skill-creator 推荐一致，减少偶然波动
- `--holdout 0.4`: 维持 60/40 的 train/test 划分，降低过拟合风险
- `--results-dir`: 建议显式指定，便于保留每次运行产物

### 运行后会得到什么

- `results.json`: 每轮优化结果摘要
- `report.html`: 最终 HTML 报告
- `logs/`: 改写 description 过程中的日志

如果运行环境允许打开浏览器，`run_loop.py` 还会自动生成并尝试打开 live report。

## Release Recommendation

- **可发布**：达到推荐通过线，且没有高优先级错误
- **可观察发布**：达到可接受区间，但保留 1-2 个中优先级边界问题
- **不建议发布**：出现高优先级错误，或整体正确率跌破 90%
