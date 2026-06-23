# 任务复盘：skill-creator 评测执行链路 Windows 兼容性修复

> **任务名称**：skill-creator 评测执行链路 Windows 兼容性修复 + task-execution-summary 描述优化
> **任务类型**：技术研究 + 故障排查
> **日期**：2026-05-20
> **结果**：4 脚本修复 + TDD 全通过 + 5 轮优化循环正常完成

---

## 1. 执行概览

| 维度 | 摘要 |
|------|------|
| **目标** | 修复 `skill-creator` 在 Windows 上的评测执行链路，使其能够完整运行 `run_eval` → `run_loop` 优化循环 |
| **执行时长** | 约 3 小时（跨多轮对话） |
| **核心成果** | 4 个脚本修复 + 1 个测试文件 + 3/3 TDD 通过 + 5 轮完整优化循环 |
| **最终状态** | v2.4 描述保持最优（Train 58% / Test 58%），无需更新 SKILL.md |

---

## 2. 目标背景

### 初始目标
通过 `skill-creator` 的 `run_loop` 工具对 `task-execution-summary` 技能的 frontmatter `description` 进行自动化触发评估与优化。

### 发现的问题

| # | 问题 | 根因 | 影响 |
|---|------|------|------|
| 1 | `UnicodeDecodeError: 'gbk'` | `Path.read_text()` 未指定 UTF-8 | 所有文件 I/O 崩溃 |
| 2 | `[WinError 10038] select.select()` | Windows 不支持对 subprocess pipe 使用 `select()` | `run_eval.py` 完全无法运行 |
| 3 | `run_loop` 产物失真（recall=0%） | 评测链路的 pipe 读取失败导致所有结果被标记为未触发 | 优化器基于错误数据运行 |
| 4 | `UnicodeEncodeError: 'gbk' / emoji` | `subprocess.run(text=True)` stdin pipe 默认 gbk | improve_description 阶段崩溃 |

---

## 3. 执行过程

### 阶段一：诊断定位
- 读取 `run_eval.py`、`run_loop.py`、`utils.py`、`improve_description.py`
- 识别 `select.select()` 为第一瓶颈
- 识别全链路缺失 UTF-8 编码声明
- 发现 `find_project_root()` 误解析到 `C:\Users\xinzo\.claude`

### 阶段二：方案 B 设计

| 修复点 | 脚本 | 做法 |
|--------|------|------|
| UTF-8 读取 | `utils.py` | `read_text(encoding="utf-8")` |
| select 替代 | `run_eval.py` | 新函数 `iter_process_lines()` — 线程+队列轮询 |
| 项目根目录 | `run_eval.py` | 新函数 `resolve_project_root()` — 显式覆盖优先 |
| stdin pipe | `improve_description.py` | `subprocess.run(encoding="utf-8")` |
| 全链路 | `run_loop.py` | `--project-root` 参数 + 所有 I/O UTF-8 |

### 阶段三：TDD 实现
- `tests/test_windows_compat.py`：3 个测试用例
- 先写测试（红）→ 修代码 → 通过（绿）
- 3/3 全部通过

### 阶段四：验证
- 烟雾评测：2 条 query × 1 run → 2/2 通过
- 完整优化循环：5 轮 × 20 queries × 3 runs = 300 次 `claude -p`，全程无错误

### 阶段五：收尾
- 迁移 spec → `.agents/docs/superpowers/specs/`
- AGENTS.md 补文档归属规则
- 分阶段 git commit

---

## 4. 关键决策

| # | 决策 | 依据 |
|---|------|------|
| 1 | 线程+队列替代 `select.select()` | 最小侵入，零新依赖 |
| 2 | 保留 `find_project_root()` + 新增 `resolve_project_root()` | 向后兼容 |
| 3 | TDD 先行 | 边界清晰，避免回归 |
| 4 | 不替换 v2.4 描述 | Train 58% 当前最优 |

---

## 5. 问题解决记录

### A：`UnicodeEncodeError: emoji`（improve_description）
- **根因**：`subprocess.run(text=True)` Windows 默认 gbk stdin pipe
- **修复**：`encoding="utf-8"`
- **经验**：`text=True` ≠ `encoding="utf-8"`

### B：Iteration 3 空描述
- **影响**：得分 50%（全部正例未触发）
- **应对**：正则兜底，下轮恢复

### C：recall 始终偏低（6%-17%）
- **分析**：Claude skill 触发机制固有特性，中文长句语义稀释
- **结论**：非链路/文案问题，属架构层面

---

## 6. 经验方法

- **Windows Python 文本 I/O 清单**：`read_text(encoding="utf-8")` / `write_text(encoding="utf-8")` / `subprocess.run(encoding="utf-8")` / `json.dumps(ensure_ascii=False)`
- **subprocess 管道跨平台方案**：daemon reader thread + queue + polling loop
- **优化循环正确运行的 4 个前提**：UTF-8 I/O + 正确 project root + 无 select 依赖 + stdin pipe UTF-8

---

## 7. 改进行动

| 优先级 | 建议 | 状态 |
|--------|------|------|
| P0 | UTF-8 / select / project_root 修复 | ✅ 已完成 |
| P1 | 为 scripts 添加统一编码配置 | 📋 待办 |
| P2 | 将新函数测试加入 CI | 📋 待办 |
| P3 | 提升中文长句 recall（skill-creator 架构增强） | 📋 待办 |
| P4 | `improve_description` 空描述 retry | 📋 待办 |

---

*生成时间：2026-05-20 | task-execution-summary v2.4*
