# 会话复盘+洞察+萃取:微信文章提取与学习全流程

> 日期：2026-06-24
> 类型：会话级复盘（含元认知）
> 关联：[`retrospective-to-asset-workflow.md`](retrospective-to-asset-workflow.md) 第 2 次独立触发

---

## 0. 会话全景

```
用户给 URL → 提取内容 → 学习总结
    → 用户要求"复盘+洞察" → 生成 HTML 报告（放错位置+错格式）
        → 用户纠正：没读 AGENTS.md → 迁移产物到 .temp/
        → 用户纠正：默认 Markdown → 记住
        → 改进计划 → 执行 P0-P2
        → 萃取归档到 docs/tech/
        → 内容洞察归档到 docs/tech/
            → 用户要求"复盘+洞察+萃取"（本文件）
```

**一句话总结**：一次"学习 URL"的单点任务，因用户两次纠正（AGENTS.md 路由、Markdown 默认），演变为完整的流程改进与资产沉淀闭环。

---

## 1. 复盘：会话时间线

| 阶段 | 动作 | 结果 | 问题 |
|------|------|------|------|
| 1. 提取 | content-parser 降级到 defuddle | ✅ 成功 | content-parser API 超时+配置缺失 |
| 2. 总结 | 四板块结构化摘要 | ✅ 超额 | 无 |
| 3. 复盘 | 生成 8 章 HTML 报告 | ⚠️ 格式错 | 未确认默认格式就用 HTML |
| 4. 纠正-1 | 用户指出未读 AGENTS.md | 产物放根目录 | 迁移到 .temp/ |
| 5. 纠正-2 | 用户指出默认应为 Markdown | 格式偏好未确认 | 记住规则 |
| 6. 改进 | P0×2 + P1×2 + P2×2 | ✅ 全部完成 | content-parser 不可用待恢复 |
| 7. 归档 | 萃取到 docs/tech/ | ✅ 2 份归档 | — |
| 8. 萃取 | 本文件 + topics 更新 | ✅ 进行中 | — |

---

## 2. 洞察：三层元认知

### 洞察 A：流程纪律 — "进仓库先读契约"

**事实**：未读 `AGENTS.md` 就放置产物，导致放错位置。

**根因**：将"提取内容"视为纯技术任务，忽略了仓库上下文。技能加载（content-parser/defuddle）抢占了第一步注意力，"读契约"被跳过。

**洞察**：任何仓库操作的第一步不是技能选择，而是**读契约**。技能选择是第二步。这与 `retrospective-to-asset-workflow.md` 的七步法一致 — Step 0 是"读 AGENTS.md"，Step 1 才是"单点研究"。

**五维准入自评**：

| 维度 | 评分 | 依据 |
|------|------|------|
| 频率 | 2/3 | 本次 + 上次 SPA 提取任务均出现 |
| 普适性 | ✅ | 不依赖个人偏好，任何仓库均适用 |
| 可执行性 | ✅ | "进入仓库 MUST 先读根目录 AGENTS.md" |
| 无害性 | ✅ | 只约束顺序，不预设解法 |
| 可验证性 | ✅ | PR review 可查产物路径是否合规 |

**状态**：2/3 频率，再触发 1 次即可提 PR 进入 `.agents/rules/`。

### 洞察 B：格式默认值 — "Markdown 优先"

**事实**：未确认格式偏好就套用 html-report 技能生成 HTML 报告。

**根因**：系统提示中"prefer_creating_files"建议默认 HTML，但用户偏好 Markdown。两者冲突时，应以用户偏好为准。

**洞察**：系统提示的默认值是"出厂设置"，用户的明确指示是"用户校准"。用户校准优先级 > 出厂设置。这不是"谁对谁错"，而是"谁更了解这个仓库的惯例"。

**五维准入自评**：

| 维度 | 评分 | 依据 |
|------|------|------|
| 频率 | 1/3 | 本次首次出现 |
| 普适性 | ⚠️ | 格式偏好可能因任务类型而异 |
| 可执行性 | ✅ | "报告默认 Markdown，除非用户明确指定其他格式" |
| 无害性 | ✅ | 只约束默认值，不阻止用户指定 |
| 可验证性 | ✅ | 产物文件扩展名可查 |

**状态**：1/3 频率，停留在经验层。需再触发 2 次才能考虑上升为规则。

### 洞察 C：技能韧性 — "降级决策树"

**事实**：content-parser 依赖缺失，降级到 defuddle。整个过程靠临场判断，没有预设路径。

**根因**：缺少"工具不可用时的标准应对流程"。每次降级都是重新决策，效率低。

**洞察**：任何依赖外部服务的技能都应有预设的降级路径。降级决策应在**任务开始前**就确定，而非**任务中断时**才临场判断。

**五维准入自评**：

| 维度 | 评分 | 依据 |
|------|------|------|
| 频率 | 2/3 | 本次 + 上次 SPA 提取任务均遇到技能降级 |
| 普适性 | ✅ | 任何技能链都可能有降级场景 |
| 可执行性 | ✅ | "依赖检查失败 MUST 立即降级，不卡在报错上" |
| 无害性 | ✅ | 只约束"降级速度"，不预设降级目标 |
| 可验证性 | ✅ | 复盘报告可查"降级是否及时" |

**状态**：2/3 频率，再触发 1 次即可提 PR。

---

## 3. 萃取：资产归位

### 3.1 已归档资产

| 资产 | 位置 | 类型 |
|------|------|------|
| 任务执行总结 | `docs/tech/task-summary-force-conf-recap-20260624.md` | 正式归档 |
| 内容洞察 | `docs/tech/content-insight-force-conf-20260624.md` | 正式归档 |
| 提取原文 | `apps/chaos/.agents/docs/superpowers/retrospectives/task-summaries/exploration/sources/doubao-seed-2.1-article-extract-20260624.md` | 已归档 |
| 复盘报告 | `apps/chaos/.agents/docs/superpowers/retrospectives/task-summaries/exploration/task-summary-force-conf-recap-20260624.md` | 已归档（HTML 转 Markdown） |
| 改进计划 | `.temp/improvement-plan-force-conf-recap-20260624.md` | 中间产物 |
| 降级决策树+SOP | `.temp/url-extract-sop-20260624.md` | 中间产物 |

### 3.2 本文件归位

本文件归档到 `apps/chaos/docs/topics/`，作为经验层资产。

### 3.3 对已有 topic 的影响

`retrospective-to-asset-workflow.md` 的五维准入检验中，频率维度从 **1/3 → 2/3**。本次是第二次独立触发完整的"复盘→洞察→沉淀"闭环。

---

## 4. 萃取后的经验沉淀

### 4.1 可复用 SOP（已固化）

URL → 学习摘要的 8 步标准流程（见 `.temp/url-extract-sop-20260624.md`）：

```
Step 0: 读 AGENTS.md → 确认产物路径和命名规范
Step 1: 确认报告格式（默认 Markdown）
Step 2: 技能选择（按降级决策树）
Step 3: 工具验证（--version / --help）
Step 4: 预览提取（stdout 先看质量）
Step 5: 持久化（-o 保存到 .temp/）
Step 6: 后处理（清理尾部噪声）
Step 7: 结构化总结（分板块 + 表格 + 洞察）
Step 8: 洞察提炼（2-4 个可迁移洞察 + 原文依据）
```

### 4.2 降级决策树（已固化）

```
URL 内容提取
├─ 首选：content-parser（API 级，支持摘要/评分/多模态）
│  └─ 不可用 → 降级
├─ 备选：defuddle（CLI 级，纯文本提取，无需 API Key）
│  └─ 未安装 → 降级
└─ 兜底：WebFetch（内置工具，最简但质量最低）
```

### 4.3 微信尾部噪声清理规则（已固化）

```powershell
# 清理微信尾部噪声
$content = Get-Content $file -Raw
$cleaned = $content -replace '(?ms)(微信扫一扫.*$)', ''
Set-Content $file -Value $cleaned.TrimEnd() -Encoding UTF8
```

---

## 5. 与七步法的对照

按 `retrospective-to-asset-workflow.md` 的七步骨架对照：

| # | 步骤 | 本次执行 | 产出 |
|---|------|---------|------|
| 1 | 单点研究 | ✅ defuddle 提取微信文章 | `apps/chaos/.agents/docs/superpowers/retrospectives/task-summaries/exploration/sources/doubao-seed-2.1-article-extract-20260624.md` |
| 2 | 横向对比 | ⏭ 跳过（合理：单篇文章无需横向对比） | — |
| 3 | 提炼洞察 | ✅ 四大核心洞察 | `docs/tech/content-insight-force-conf-20260624.md` |
| 4 | 封装资产 | ✅ SOP + 降级决策树 + 清理规则 | `.temp/url-extract-sop-20260624.md` |
| 5 | 配置落地 | ✅ SOP 增量更新到 `references/web-content-extraction-patterns.md` v1.3 | §12 Skill 级降级链 + §13 URL→学习摘要 SOP |
| 6 | 自动校验 | ✅ 创建产物路径合规检查脚本 | `references/check-artifact-paths.ps1` |
| 7 | 归档 | ✅ 归档到 docs/tech/ + docs/topics/ | 3 份归档文件 |

**跳步分析**：
- Step 2 跳过：合理，单篇文章无需横向对比
- Step 5 完成：SOP 已增量更新到 `web-content-extraction-patterns.md` §12-§13，降级链和清理规则进入长期参考文档
- Step 6 完成：`check-artifact-paths.ps1` 脚本已创建并验证通过（0 错误，26 警告均为历史文件）

---

## 6. 规则演化追踪

### 候选规则状态更新

| 候选规则 | 来源 | 频率 | 状态 |
|---------|------|------|------|
| `retrospective-to-asset-workflow` | 上次 SPA 提取 + 本次微信提取 | 2/3 | 经验层，再触发 1 次可提 PR |
| `read-agents-md-first` | 本次首次明确 | 1/3 | 经验层，需再触发 2 次 |
| `skill-degradation-tree` | 上次 SPA 降级 + 本次 content-parser 降级 | 2/3 | 经验层，再触发 1 次可提 PR |
| `default-markdown-format` | 本次首次 | 1/3 | 经验层，需再触发 2 次 |

### 下一步行动

- [x] 将 SOP 增量更新到 `references/web-content-extraction-patterns.md` §12-§13
- [x] 创建产物路径合规检查脚本 `references/check-artifact-paths.ps1`
- [ ] 在下次 URL 提取任务中验证 SOP 是否可复用
- [ ] 频率达 3/3 后，为 `retrospective-to-asset-workflow` 和 `skill-degradation-tree` 提 PR 进入 `.agents/rules/`

---

## 7. 会话产出物总索引

| # | 文件 | 位置 | 类型 | 状态 |
|---|------|------|------|------|
| 1 | 提取原文 | `apps/chaos/.agents/docs/superpowers/retrospectives/task-summaries/exploration/sources/doubao-seed-2.1-article-extract-20260624.md` | 已归档 | ✅ 已清理噪声 |
| 2 | 复盘报告 | `apps/chaos/.agents/docs/superpowers/retrospectives/task-summaries/exploration/task-summary-force-conf-recap-20260624.md` | 已归档 | ✅ HTML 转 Markdown |
| 3 | 改进计划 | `.temp/improvement-plan-force-conf-recap-20260624.md` | 中间产物 | ✅ 全部完成 |
| 4 | 降级决策树+SOP | `.temp/url-extract-sop-20260624.md` | 中间产物 | ✅ 已固化 |
| 5 | 任务执行总结 | `docs/tech/task-summary-force-conf-recap-20260624.md` | 正式归档 | ✅ 已归档 |
| 6 | 内容洞察 | `docs/tech/content-insight-force-conf-20260624.md` | 正式归档 | ✅ 已归档 |
| 7 | **本文件** | `docs/topics/session-recap-force-conf-20260624.md` | 经验层 | ✅ 萃取完成 |

---

*版本：v1.0 · 2026-06-24 · 第 2 次独立触发"复盘→洞察→沉淀"闭环*
