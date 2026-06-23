# 命名规范

> **维护责任人**：Leader Agent
> **适用范围**：`specs/` 全目录及子模块

## 1. 目录命名

| 规则 | 说明 | 示例 |
|------|------|------|
| 纯 ASCII | 禁止中文、emoji、空格 | `ai-docs/` ✅ `AI文档/` ❌ |
| kebab-case | 单词间用连字符 `-` 连接 | `github-integration/` ✅ |
| 一级模块 | 按设计主题命名 | `ai-docs/`、`agent-system/`、`github-integration/`、`task-summaries/`、`misc/` |
| 元数据目录 | 以下划线前缀 | `_meta/` |
| 原子化目录 | 日期前缀 + 主题 + `-design/` | `2026-05-24-agent-collaboration-metamodel-design/` |

## 2. 文件命名

### 2.1 单文件设计文档

格式：`YYYY-MM-DD-{topic}-design.md`

| 元素 | 规则 | 示例 |
|------|------|------|
| 日期前缀 | `YYYY-MM-DD` 格式 | `2026-05-22` |
| topic | 英文 kebab-case，描述设计主题 | `ai-docs-navigation` |
| 后缀 | 统一使用 `-design.md` | `-design.md` |

示例：
- `2026-05-22-ai-docs-navigation-design.md`
- `2026-05-22-pygithub-adapter-design.md`
- `2026-05-24-role-review-workflow-design.md`

### 2.2 原子化目录内文件

格式：`{section-name}.md`

| 元素 | 规则 | 示例 |
|------|------|------|
| 索引文件 | 固定使用 `index.md` | `index.md` |
| 分区文件 | 英文 kebab-case，按 `part-{序号}-{主题}.md` 编号 | `part-1-overview-and-decision.md` |

示例：
- `index.md`
- `part-01-goal-and-background.md`
- `part-02-scope-and-non-goals.md`

## 3. 日期格式

| 规则 | 说明 |
|------|------|
| 格式 | `YYYY-MM-DD` |
| 分隔符 | 连字符 `-` |
| 顺序 | 年-月-日 |

示例：
- `2026-05-22` ✅
- `2026/05/22` ❌
- `05-22-2026` ❌
- `2026.05.22` ❌

## 4. 禁止事项

| 禁止项 | 说明 | 反例 |
|--------|------|------|
| 中文 | 文件名与目录名禁止包含中文字符 | `AI文档导航-design.md` ❌ |
| emoji | 禁止使用任何 emoji | `🚀-ai-docs-design.md` ❌ |
| 空格 | 禁止使用空格，单词间统一使用连字符 | `ai docs navigation.md` ❌ |
| 大写字母 | 目录与文件名统一使用小写 | `AI-Docs-Design.md` ❌ |
| 下划线 | 文件名中禁止使用下划线（`_meta/` 目录除外） | `ai_docs_design.md` ❌ |

## 5. 命名审计自检

在 `Write` 工具调用正式目录前，必须自问：

1. 文件名是否包含非 ASCII 字符？—— **必须为纯 ASCII**
2. 文件名格式是否与 `YYYY-MM-DD-{topic}-design.md` 一致？—— 如不一致，须说明理由
3. 原子化目录内的分区文件是否按 `part-{序号}-{主题}.md` 顺序编号？—— 必须连续编号
4. 目录名是否为 kebab-case 且全小写？—— 必须符合规范
