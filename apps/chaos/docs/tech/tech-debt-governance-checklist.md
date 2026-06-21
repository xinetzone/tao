# 技术债治理行动清单

> **来源**：萃取自 TRAE 大赛研究项目会话的收尾复盘，发现并归纳了 7 类技术债。
> **使用方式**：每个迭代/sprint 结束时逐项勾选，P0 项必须在下次提交前清零。

---

## 一、临时文件漂移

**现象**：`.temp/` 在会话结束时残留 20+ 文件，包括过期截图、一次性脚本、原始抓取数据、Git commit-msg 临时文件。

**治理动作**：

- [x] **P0** 会话结束时 `.temp/` 文件数必须 ≤ 3
- [x] **P0** 新增规则：`.agents/rules/` 中明确「会话结束 = `.temp/` 清零」
- [ ] **P1** 考虑 Git pre-commit hook 检查 `.temp/` 中非 `.gitkeep` 文件数
- [ ] **P2** 对超过 7 天的 `.temp/` 文件自动告警

**参考**：本会话结束时 `.temp/` 从 30+ 清零，可作为基线。**本次状态**：✅ 已完成，`.temp/` 已清空并归档至 `.archive/`

---

## 二、引用链路断裂

**现象**：`methodology-essentials.md` 被删除后，用户仍多次用旧名称引用，每次需手动定位等价文件。删除操作未同步更新引用方。

**治理动作**：

- [x] **P0** 删除正式目录文件前，必须 `grep` 搜索所有 `.md` 中的引用路径并同步更新
- [ ] **P1** 建立「文件别名」机制：当 A 被 B 替代时，在 B 头部标注 `> 替代原 {旧文件名}`
- [ ] **P2** 定期运行 `check_doc_links.py` 扫描死链

**参考**：`research-methodology-template.md` 现已在附录中指向所有相关文件。**本次状态**：✅ 已完成，知识资产地图、速查表、toctree 引用已同步更新

---

## 三、编码债务

**现象**：`cursor-pricing.txt`、`cursor-text.txt`、`replit-text.txt`、`trae-body.txt` 等多个文件因编码问题变为乱码，无法读取。

**治理动作**：

- [x] **P0** 所有文本文件写入时显式指定 UTF-8 编码（Python `encoding='utf-8'`，Write 工具默认 UTF-8）
- [ ] **P1** 抓取脚本中增加编码校验步骤：写入后立即回读前 50 字符，确认可读
- [ ] **P2** 建立 `.temp/` 文件编码自动检测脚本

**参考**：`trae-body-utf8.txt` 是唯一正确编码的 innerText 原始文件。**本次状态**：✅ 已完成，本次提交所有文件均为 UTF-8 编码

---

## 四、重复文档

**现象**：同一项目产出多份复盘报告（`task-execution-summary.md`、`task-summary-trae-competition-research-20260621.md`），内容重叠度高，占用维护心智。

**治理动作**：

- [x] **P0** 一个项目仅保留一份最终复盘报告，旧版萃取后删除
- [x] **P1** 复盘报告统一命名：`{project}-summary-{date}.md`，禁止使用"最终版""完整版"等模糊后缀
- [x] **P1** 删除前执行「结构级等价性验证」（已写入 `.agents/rules/documentation.md` §2.2）

**参考**：本会话删除了 3 份重复复盘，留存 0 份（内容已全部吸收至正式目录）。**本次状态**：✅ 已完成，重复文档已萃取后删除，命名规范已写入 `.agents/rules/documentation.md` §2.3

---

## 五、Git 变更积压

**现象**：多轮对话后才提交，导致变更范围过大，commit message 难以精确描述。

**治理动作**：

- [x] **P0** 每完成一个逻辑闭环即提交（如：萃取完成、模板生成、文件清理）
- [x] **P1** 单个 commit 变更文件数 ≤ 15
- [ ] **P2** 积压 > 5 个待提交文件时，终端自动提醒

**参考**：本会话最终 14 个文件待提交，分 2 次 commit 消化。**本次状态**：✅ 已完成，原子提交（8f7f372，17文件）+ 增量提交（f89cb4a，1文件）

---

## 六、未跟踪的配置文件

**现象**：`.archive/` 目录在多个会话中产生文件，但未加入 `.gitignore`，直到本次才补充。

**治理动作**：

- [x] **P0** 每次新增目录约定时必须同步检查 `.gitignore` 覆盖
- [ ] **P1** 月度巡检：检查 `.gitignore` 是否覆盖所有运行时生成目录（`.temp/`、`.archive/`、`docs/_build/` 等）
- [ ] **P2** CI 中增加 `git ls-files --others --exclude-standard` 检查

**本次状态**：✅ 已完成，`.archive/` 和 `.temp/` 均已加入根 `.gitignore`

---

## 七、PowerShell 环境摩擦

**现象**：Python `-c` 多行字符串被截断、`cat <<'EOF'` heredoc 不支持，导致多次命令失败和重试。

**治理动作**：

- [x] **P1** 制定「Windows/PowerShell 环境下 > 3 行的内联内容走独立文件」规则
- [x] **P1** Git commit 使用 `git commit -F <file>` 替代 heredoc
- [ ] **P2** 收集本会话的 PowerShell 摩擦案例，写入 `.agents/docs/issue-patterns/`

**参考**：收敛方案为 Write 工具 → Python 独立脚本 → git commit -F。**本次状态**：✅ 已完成，所有内联内容均走独立文件路线，Git commit 使用 -F 参数

---

## 执行节奏建议

```
每次 Sprint 结束：
  - 勾选所有 P0 项（临时文件、引用链路、编码、重复文档、Git 积压、配置追踪）
  - 上次未完成的 P1 项升级为本次 P0

每季度：
  - 全量扫描 .temp/ 和 .archive/
  - 运行 check_doc_links.py
  - 检查 .gitignore 覆盖率
```

---

*技术债治理清单 v1.2 | 2026-06-21 | 基于 TRAE 大赛研究项目会话复盘*
