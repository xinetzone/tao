# SPA Content Extractor — Prompt 模板

## 用途

当需要抓取现代 SPA / React/Vue/Next.js 网站内容时，复制此模板并填充占位符，然后提交给 AI 助手执行。

---

## 模板正文

```
【任务类型】网页内容抓取与分析
【目标 URL】{{目标网页地址，如 https://example.com/product}}
【抓取目标】{{简要描述要抓取的内容，如"产品定价"、"赛事规则"、"功能列表"、"客户案例"等}}
【输出要求】{{结构化报告/原始文本/对比分析/关键数据提取等}}

---

请按以下流程执行：

## Stage 1: 静态尝试（快、便宜）
1. 用 defuddle 抓取：`defuddle parse "{{目标URL}}" --md -o .temp/{{缩写}}-static.md`
2. 检查结果：如果内容 > 500 字节且包含有效信息，直接进入后处理阶段
3. 如果内容为空或仅标题，进入 Stage 2

## Stage 2: 浏览器抓取（主路径）
1. 打开页面：`agent-browser open "{{目标URL}}"`
2. 等待渲染：`agent-browser wait --load networkidle`
3. 额外等待：`agent-browser wait 1500`（确保 SPA 完全 hydration）
4. 提取文本：`agent-browser eval 'document.body.innerText' > .temp/{{缩写}}-text.txt`
5. 提取快照：`agent-browser snapshot -i --json -o .temp/{{缩写}}-snapshot.json`（可选，仅当需要交互元素）
6. 截图存档：`agent-browser screenshot --full .temp/{{缩写}}-full.png`

## Stage 3: 懒加载处理（按需）
1. 如果内容明显不完整，执行滚动：`agent-browser eval 'window.scrollTo(0, document.body.scrollHeight); "scrolled"'`
2. 等待加载：`agent-browser wait 2000`
3. 重新提取：`agent-browser eval 'document.body.innerText' > .temp/{{缩写}}-text-full.txt`
4. 重复 1-3 直到内容长度稳定

## Stage 4: 后处理与输出
1. 读取 `.temp/{{缩写}}-text.txt`
2. 按【输出要求】进行结构化处理：
   - 识别关键章节（标题、列表、表格）
   - 提取数字数据（价格、时间、百分比）
   - 整理成清晰的 Markdown 格式
3. 输出最终结果

## 注意事项
- URL 脱敏：输出时移除 `utm_source`、`user_id`、`token` 等追踪参数
- 中文编码：在 Windows/PowerShell 环境下，使用文件重定向而非终端打印
- 浏览器清理：完成后执行 `agent-browser close`
- Cloudflare 处理：如果被拦截，尝试更换 user-agent 或告知用户需要手动登录
```

---

## 占位符说明

| 占位符 | 说明 | 示例 |
|--------|------|------|
| `{{目标网页地址}}` | 要抓取的完整 URL | `https://cursor.com/pricing` |
| `{{简要描述要抓取的内容}}` | 明确抓取目标，帮助 AI 聚焦 | "4 档定价方案 + 功能对比" |
| `{{结构化报告/原始文本/对比分析/关键数据提取等}}` | 期望的输出形式 | "结构化 JSON + 中文摘要" |
| `{{缩写}}` | 文件命名用的简短标识（3-5 字符） | `cursor`、`trae`、`bolt` |

---

## 4 种典型场景模板

### 场景 A：完整 SPA 抓取（如 TRAE 大赛）

```
【任务类型】网页内容抓取与分析
【目标 URL】https://www.trae.cn/ai-creativity
【抓取目标】大赛完整信息：赛程、赛道、奖项、评委、学习资料
【输出要求】结构化 JSON + 中文洞察报告

请按以下流程执行：

## Stage 1: 静态尝试
defuddle parse "https://www.trae.cn/ai-creativity" --md -o .temp/trae-static.md
# 如果内容 > 500 字节，直接进入后处理；否则进入 Stage 2

## Stage 2: 浏览器抓取
agent-browser open "https://www.trae.cn/ai-creativity"
agent-browser wait --load networkidle
agent-browser wait 1500
agent-browser eval 'document.body.innerText' > .temp/trae-text.txt
agent-browser snapshot -i --json -o .temp/trae-snapshot.json
agent-browser screenshot --full .temp/trae-full.png

## Stage 3: 懒加载处理（按需）
# 如果内容完整，跳过此阶段

## Stage 4: 后处理
1. 读取 .temp/trae-text.txt
2. 按章节拆分（大赛介绍、领造官、赛程、赛道、评委、奖项、学习资料）
3. 提取关键数字（奖金金额、时间节点、参赛人数）
4. 生成结构化 JSON 和中文报告

## 注意事项
- snapshot 可能返回大量重复节点（轮播），优先使用 innerText
- 浏览器完成后执行 agent-browser close
```

### 场景 B：多页并行抓取（如 Cursor 官网 + 定价页）

```
【任务类型】网页内容抓取与分析（多页）
【目标 URL】https://cursor.com + https://cursor.com/pricing
【抓取目标】产品功能介绍 + 4 档定价方案 + 企业版信息
【输出要求】合并的结构化报告，包含价格对比表

请按以下流程执行：

## Stage 1: 静态尝试（两个页面）
defuddle parse "https://cursor.com" --md -o .temp/cursor-home-static.md
defuddle parse "https://cursor.com/pricing" --md -o .temp/cursor-price-static.md
# 如果两个都有内容，直接进入后处理；否则进入 Stage 2

## Stage 2: 浏览器抓取（并行）
# Terminal 1:
agent-browser open "https://cursor.com" && agent-browser wait --load networkidle && agent-browser wait 1500 && agent-browser eval 'document.body.innerText' > .temp/cursor-home.txt

# Terminal 2:
agent-browser open "https://cursor.com/pricing" && agent-browser wait --load networkidle && agent-browser wait 1500 && agent-browser eval 'document.body.innerText' > .temp/cursor-price.txt

## Stage 3: 懒加载处理（按需）

## Stage 4: 后处理
1. 读取两个文本文件
2. 合并信息，重点整理定价对比表
3. 提取 KOL 推荐语和产品功能亮点

## 注意事项
- PowerShell 环境下中文可能乱码，确保用文件重定向
- 完成后执行 agent-browser close
```

### 场景 C：静态优先（如 Bolt.new）

```
【任务类型】网页内容抓取与分析（静态优先）
【目标 URL】https://bolt.new
【抓取目标】产品功能、设计系统集成、企业功能
【输出要求】Markdown 格式的功能列表 + 客户案例

请按以下流程执行：

## Stage 1: 静态尝试
defuddle parse "https://bolt.new" --md -o .temp/bolt-static.md
# 如果内容完整，直接进入后处理

## Stage 2: 浏览器抓取（仅当静态失败时）
agent-browser open "https://bolt.new"
agent-browser wait --load networkidle
# 如果超时，尝试 agent-browser wait --load domcontentloaded
# 如果仍然超时，回到静态结果

## Stage 3: 后处理
1. 读取静态或浏览器结果
2. 整理设计系统合作案例（品牌列表）
3. 提取企业功能（数据库、认证、SEO、Hosting）

## 注意事项
- 某些现代网站 SSR 足够完整，不需要浏览器
- 完成后执行 agent-browser close（如果使用了浏览器）
```

### 场景 D：Cloudflare 拦截处理（如 Replit）

```
【任务类型】网页内容抓取与分析（反爬处理）
【目标 URL】https://replit.com/ai
【抓取目标】AI Agent 功能、定价、使用场景
【输出要求】基于可用信息的报告，注明数据来源

请按以下流程执行：

## Stage 1: 静态尝试
defuddle parse "https://replit.com/ai" --md -o .temp/replit-static.md
# 如果返回 Cloudflare 页面，进入 Stage 2

## Stage 2: 浏览器抓取
agent-browser open "https://replit.com/ai"
agent-browser wait --load networkidle
agent-browser eval 'document.body.innerText' > .temp/replit-text.txt

## Stage 3: 检查结果
1. 如果结果是 "You have been blocked" 或 Cloudflare 提示：
   - 尝试更换 user-agent：agent-browser --user-agent "Mozilla/5.0 ..." open "{{URL}}"
   - 如果仍然失败，告知用户需要手动登录或使用 --auto-connect
   - 改用公开资料（官网首页、新闻稿、第三方评测）补充

## Stage 4: 后处理
1. 基于可用信息整理报告
2. 明确标注数据来源和局限性

## 注意事项
- 不要无限重试，反爬站点通常需要人工介入
- 如果无法获取，提供替代数据源建议
```

---

## 使用指南

### 快速上手

1. 复制上方的通用模板
2. 替换 `{{占位符}}` 为实际内容
3. 提交给 AI 助手

### 进阶技巧

- **多页抓取**：复制模板多次，每个页面一个模板
- **对比分析**：先分别抓取，再用单独的分析任务汇总
- **定时更新**：保存模板，定期重新执行获取最新数据
- **批量处理**：用模板生成脚本，一次性抓取多个页面

---

*模板版本：v1.0*
*创建时间：2026-06-21*
*基于 spa-content-extractor skill 的 4 个实战案例整理*
