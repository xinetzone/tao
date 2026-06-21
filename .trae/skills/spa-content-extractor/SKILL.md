---
name: "spa-content-extractor"
description: "Extract clean Markdown from React/Vue/Next.js SPAs. Use when defuddle/WebFetch return empty, or user asks to scrape/summarize a modern website."
---

# SPA Content Extractor

A three-stage pipeline for extracting content from pages where static fetchers fail because the DOM is built by client-side JavaScript.

## When to Invoke

| Signal | Why it matters |
|--------|----------------|
| `defuddle parse <url> --md` returns only the title or empty body | Page is SPA, content is rendered by JS |
| `WebFetch` returns boilerplate, navigation, or "loading" placeholders | Same root cause |
| The user explicitly says "scrape", "抓取", "提取内容", "导出页面" with a modern URL | Most marketing/product sites are SPAs today |
| The page has `__NEXT_DATA__`, `__NUXT__`, or `window.__INITIAL_STATE__` | Hydrated SPA — must execute JS |

**Do NOT use** for: simple static docs (use `defuddle`), authenticated dashboards (use `agent-browser` with auth state).

## Core Pipeline (Three Stages)

### Stage 1 — Quick Static Try (cheap & fast)

Always attempt first. ~10% of "modern" sites still SSR enough for static tools.

```bash
defuddle parse "<url>" --md -o .temp/page-static.md
```

If the output is empty or < 500 bytes → escalate to Stage 2.

### Stage 2 — Browser + innerText (primary path)

```bash
# Open and wait for JS hydration
agent-browser open "<url>"
agent-browser wait --load networkidle
# Sometimes SPA needs an explicit settle wait
agent-browser wait 1500

# Pull the rendered text — much cleaner than DOM snapshot
agent-browser eval 'document.body.innerText' > .temp/page-text.txt

# Also grab a structural snapshot for repeated elements (cards, list items)
agent-browser snapshot -i --json -o .temp/page-snapshot.json
```

**Why `innerText` beats `snapshot`?**
- Snapshots explode on carousels / virtual lists (same item rendered 5x)
- `innerText` is what humans actually see, deduplicated by the browser
- Snapshots are for interaction (click/fill), not content extraction

### Stage 3 — Lazy-Load Scroll (only if content is truncated)

Many pages load sections as you scroll. Detect and force-load.

```bash
# Trigger lazy load by scrolling
agent-browser eval 'window.scrollTo(0, document.body.scrollHeight); "scrolled"'
agent-browser wait 2000
agent-browser eval 'document.body.innerText' > .temp/page-text-full.txt
```

Repeat 2-3 times until `innerText.length` stops growing.

## Captures to Save (recommended bundle)

| File | Command | Purpose |
|------|---------|---------|
| `page-text.txt` | `eval 'document.body.innerText'` | Primary text content |
| `page-snapshot.json` | `snapshot -i --json` | Interactive element refs |
| `page-full.png` | `screenshot --full` | Visual archive |
| `page-annotated.png` | `screenshot --annotate` | Numbered elements for spatial reasoning |

```bash
agent-browser screenshot --full .temp/page-full.png
agent-browser screenshot --annotate .temp/page-annotated.png
```

## URL Hygiene

Before saving any URL, strip tracking parameters to avoid polluting the knowledge base.

**Strip list**: `utm_source`, `utm_medium`, `utm_campaign`, `user_id`, `username`, `product`, `token`, `session`, `from`, `ref`, `fbclid`, `gclid`, `msclkid`.

```bash
# Keep only path-relevant query params
agent-browser open "<url>?utm_source=test"  # Browser will load as-is
# But when archiving the URL to notes/JSON, save the cleaned form:
# https://example.com/page
```

## Post-Processing: From Text to Structured Insight

Raw `innerText` is a wall of text. Convert to insight with three steps:

1. **Sectionize** — split on English/Chinese headers (`Introduction / >`, `日程`, `赛道`, etc.)
2. **Tabularize** — pull key-value pairs (prize amounts, dates, percentages)
3. **Cite** — preserve the URL and capture timestamp in every derived artifact

Output schema (recommended):

```json
{
  "meta": {"source": "<cleaned-url>", "fetched_at": "<ISO-8601>", "tool": "spa-content-extractor"},
  "sections": [{"title": "...", "items": [...]}],
  "key_numbers": {...},
  "raw_innerText_length": 12345
}
```

## Failure Modes & Recovery

| Symptom | Cause | Fix |
|---------|-------|-----|
| `innerText` returns just the loader/spinner | Wait too short or hydration pending | Increase wait; check for `#root`, `__NEXT_DATA__` readiness |
| Same content repeats 5+ times | Virtual list or carousel rendered the same node group | Use `innerText` (deduplicated) instead of snapshot |
| Page is in an iframe | Login wall, paywall, or embedded content | Use `agent-browser frame @eN` to enter, or authenticate first |
| Chinese text becomes garbled (`寰俊...`) | PowerShell console encoding | Use `eval` and redirect to file; don't print to terminal |
| Page returns 403/401 | Cloudflare or anti-bot | Set `agent-browser --user-agent "..."` or use `--auto-connect` with a real browser |

## Closing the Loop

Always close the browser when done to avoid leaked Chrome processes:

```bash
agent-browser close
```

## Example: End-to-End

```bash
# 1. Try static (will likely fail for SPAs)
defuddle parse "https://example.com/event" --md -o .temp/event-static.md
# Output empty → escalate

# 2. Browser path
agent-browser open "https://example.com/event"
agent-browser wait --load networkidle
agent-browser wait 1500
agent-browser eval 'document.body.innerText' > .temp/event-text.txt
agent-browser snapshot -i --json -o .temp/event-snapshot.json
agent-browser screenshot --full .temp/event-full.png

# 3. Lazy-load if needed
agent-browser eval 'window.scrollTo(0, document.body.scrollHeight); "ok"'
agent-browser wait 2000
agent-browser eval 'document.body.innerText' > .temp/event-text-full.txt

# 4. Cleanup
agent-browser close
```

## Real-World Examples (2026-06-19)

### Case 1: TRAE AI 创造力大赛 — 完整 SPA 抓取

**URL**: `https://www.trae.cn/ai-creativity`

**Challenge**: 官网是 React SPA，静态工具只能拿到标题。

```bash
# Stage 1: Static attempt
defuddle parse "https://www.trae.cn/ai-creativity" --md
# Result: Only title, all content empty → escalate

# Stage 2: Browser path
agent-browser open "https://www.trae.cn/ai-creativity"
agent-browser wait --load networkidle
agent-browser wait 1500
agent-browser eval 'document.body.innerText' > .temp/trae-text.txt
agent-browser snapshot -i --json -o .temp/trae-snapshot.json
agent-browser screenshot --full .temp/trae-full.png

# Stage 3: Lazy-load (not needed, all content loaded)
agent-browser close
```

**Outcome**: ✅ 完整抓取 7 个板块（介绍/领造官/赛程/赛道/评委/奖项/资料），生成结构化 JSON + 洞察报告。

**Key Learning**: `snapshot` 返回 150+ 个重复 `generic` 节点（轮播导致），`innerText` 才是正确选择。

---

### Case 2: Cursor 官网 + 定价页 — 多页并行抓取

**URLs**: `https://cursor.com` + `https://cursor.com/pricing`

**Challenge**: 需要同时抓主页和定价页，且定价页是关键决策数据。

```bash
# Parallel fetch (2 terminals)
# Terminal 1:
agent-browser open "https://cursor.com" && agent-browser wait --load networkidle && agent-browser eval 'document.body.innerText' > .temp/cursor-home.txt

# Terminal 2:
agent-browser open "https://cursor.com/pricing" && agent-browser wait --load networkidle && agent-browser eval 'document.body.innerText' > .temp/cursor-pricing.txt

# Cleanup
agent-browser close
```

**Outcome**: ✅ 主页拿到 9 位 KOL 推荐语 + 产品功能；定价页拿到 4 档价格（Hobby 免费 / Pro $20 / Pro+ $40 / Ultra 定制）。

**Key Learning**: 多页并行可节省时间，但要注意 PowerShell 中文编码问题（用文件重定向，不要打印到终端）。

---

### Case 3: Bolt.new — 静态成功 + 浏览器超时

**URL**: `https://bolt.new`

**Challenge**: 浏览器路径连续超时，但静态工具意外成功。

```bash
# Stage 1: Static attempt
defuddle parse "https://bolt.new" --md -o .temp/bolt-static.md
# Result: ✅ 完整内容（设计系统/功能/用户角色）

# Stage 2: Browser path (failed)
agent-browser open "https://bolt.new"
agent-browser wait --load networkidle  # Timeout
agent-browser wait --load domcontentloaded  # Still timeout
agent-browser wait 3000  # Still timeout
# Gave up, use static result
```

**Outcome**: ✅ 静态工具拿到了完整营销文案（Porsche/Material UI/WAPO 客户案例 + 功能列表）。

**Key Learning**: 不要假设所有"现代网站"都是纯 SPA，有些 SSR 足够完整。静态尝试永远值得先做。

---

### Case 4: Replit Agent — Cloudflare 拦截（失败兜底）

**URL**: `https://replit.com/ai`

**Challenge**: Cloudflare 反爬机制，浏览器直接被拦截。

```bash
# Stage 1: Static attempt
defuddle parse "https://replit.com/ai" --md
# Result: Cloudflare challenge page

# Stage 2: Browser path
agent-browser open "https://replit.com/ai"
agent-browser wait --load networkidle
agent-browser eval 'document.body.innerText' > .temp/replit-text.txt
# Result: "Sorry, you have been blocked"
```

**Outcome**: ❌ 浏览器被 Cloudflare 拦截，改用公开资料补充。

**Key Learning**: 反爬站点需要 `--auto-connect`（连接真实浏览器）或手动登录后保存 auth state，不在本 skill 范围内。

---

### Summary Table

| Site | Static | Browser | Lazy-Load | Result |
|------|--------|---------|-----------|--------|
| TRAE | ❌ Empty | ✅ Full | Not needed | ✅ Complete |
| Cursor | ❌ Empty | ✅ Full | Not needed | ✅ Complete |
| Bolt.new | ✅ Full | ⏱ Timeout | N/A | ✅ Static sufficient |
| Replit | ❌ Blocked | ❌ Blocked | N/A | ❌ Fallback to public data |

**Pattern**: 4 个案例覆盖了 4 种典型场景，验证了三阶段管道的实用性。

## Cross-References

- For pure content reading (no interaction): this skill
- For form filling / clicking / multi-step flows: `agent-browser`
- For clean markdown of static pages: `defuddle`
- For authenticated scraping with state persistence: `agent-browser` + `auth vault`

---

## Reusable Prompt Template

Use this template when invoking this skill. Fill in the placeholders and submit to the AI.

### Generic Template

```
【任务类型】网页内容抓取与分析
【目标 URL】{{目标网页地址}}
【抓取目标】{{简要描述要抓取的内容}}
【输出要求】{{结构化报告/原始文本/对比分析/关键数据提取等}}

请按以下流程执行：

## Stage 1: 静态尝试
defuddle parse "{{目标URL}}" --md -o .temp/{{缩写}}-static.md
# 如果内容 > 500 字节，直接进入后处理；否则进入 Stage 2

## Stage 2: 浏览器抓取
agent-browser open "{{目标URL}}"
agent-browser wait --load networkidle
agent-browser wait 1500
agent-browser eval 'document.body.innerText' > .temp/{{缩写}}-text.txt
agent-browser snapshot -i --json -o .temp/{{缩写}}-snapshot.json
agent-browser screenshot --full .temp/{{缩写}}-full.png

## Stage 3: 懒加载处理（按需）
agent-browser eval 'window.scrollTo(0, document.body.scrollHeight); "scrolled"'
agent-browser wait 2000
agent-browser eval 'document.body.innerText' > .temp/{{缩写}}-text-full.txt

## Stage 4: 后处理
1. 读取 .temp/{{缩写}}-text.txt
2. 按章节拆分、提取关键数字
3. 按【输出要求】整理最终报告

## 注意事项
- URL 脱敏：移除 utm_source、user_id、token 等参数
- 中文编码：PowerShell 用文件重定向
- 浏览器清理：完成后 agent-browser close
```

### Placeholder Reference

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{{目标网页地址}}` | Full URL to scrape | `https://cursor.com/pricing` |
| `{{简要描述要抓取的内容}}` | What to extract | "4-tier pricing + feature comparison" |
| `{{结构化报告/原始文本/对比分析/关键数据提取等}}` | Output format | "Structured JSON + Chinese summary" |
| `{{缩写}}` | Short file identifier (3-5 chars) | `cursor`, `trae`, `bolt` |

### Scenario Templates

**Scenario A: Full SPA scrape (e.g., TRAE competition)**

```
【目标 URL】https://www.trae.cn/ai-creativity
【抓取目标】大赛完整信息：赛程、赛道、奖项、评委、学习资料
【输出要求】结构化 JSON + 中文洞察报告
```

**Scenario B: Multi-page parallel scrape (e.g., Cursor home + pricing)**

```
【目标 URL】https://cursor.com + https://cursor.com/pricing
【抓取目标】产品功能介绍 + 4 档定价方案 + 企业版信息
【输出要求】合并的结构化报告，包含价格对比表

# Parallel: Terminal 1 for home, Terminal 2 for pricing
```

**Scenario C: Static-first (e.g., Bolt.new)**

```
【目标 URL】https://bolt.new
【抓取目标】产品功能、设计系统集成、企业功能
【输出要求】Markdown 格式的功能列表 + 客户案例

# Static success → skip browser. Browser timeout → fallback to static result.
```

**Scenario D: Cloudflare block (e.g., Replit)**

```
【目标 URL】https://replit.com/ai
【抓取目标】AI Agent 功能、定价、使用场景
【输出要求】基于可用信息的报告，注明数据来源

# Static block + browser block → use public materials
```

### Usage Workflow

1. **Copy** the generic template or pick a scenario template
2. **Replace** `{{占位符}}` with actual values
3. **Submit** to AI for execution
4. **Review** the `.temp/` output files
5. **Iterate** if needed (e.g., refine output format, add scenarios)

### When to Use Which Scenario

| Symptom in Static Attempt | Use Scenario |
|--------------------------|--------------|
| Empty result | A (full browser path) |
| Partial result | A + refine extraction |
| Complete result | C (skip browser) |
| Cloudflare page | D (fallback to public data) |
| Need multiple pages | B (parallel terminals) |
