# 命名规范

> **维护责任人**：Leader Agent
> **适用范围**：`plans/` 全目录及子模块

## 1. 目录命名

| 规则 | 说明 | 示例 |
|------|------|------|
| 纯 ASCII | 禁止中文、emoji、空格 | `ai-docs/` ✅ `AI文档/` ❌ |
| kebab-case | 单词间用连字符 `-` 连接 | `agent-system/` ✅ `agent_system/` ❌ |
| 一级模块 | 按计划主题命名 | `ai-docs/`、`agent-system/`、`exploration/`、`github-integration/`、`docs-governance/`、`python-environment/` |
| 原子化目录 | `YYYY-MM-DD-{topic}/` 格式 | `2026-05-22-ai-reference-wiki/` ✅ |
| 元数据目录 | 以下划线前缀 | `_meta/` |

## 2. 文件命名

### 2.1 单文件计划

格式：`YYYY-MM-DD-{topic}.md`

| 元素 | 规则 | 示例 |
|------|------|------|
| 日期前缀 | `YYYY-MM-DD` 格式 | `2026-05-22` |
| topic | 英文 kebab-case，描述计划主题 | `ai-docs-navigation` |
| 连接 | 日期与 topic 间用 `-` 连接 | `2026-05-22-ai-docs-navigation.md` |

示例：
- `2026-05-22-ai-docs-navigation.md`
- `2026-05-22-ai-docs-search-keywords.md`
- `2026-05-24-agent-context-structure-optimization.md`
- `2026-05-23-init-onboarding-output.md`

### 2.2 原子单元文件

格式：`{section-name}.md`

| 元素 | 规则 | 示例 |
|------|------|------|
| section-name | 英文 kebab-case，描述单一主题 | `task-1-reference-page.md`、`file-structure.md` |
| 位置 | 位于同名原子化目录内 | `2026-05-22-ai-reference-wiki/task-1-top-level-directories.md` |

### 2.3 索引文件

| 文件 | 位置 | 用途 |
|------|------|------|
| `index.md` | 原子化目录内 | 概述与原子单元索引 |
| `README.md` | 模块目录内 | 模块说明与文件清单 |

## 3. 日期格式

- 统一使用 `YYYY-MM-DD`（如 `2026-05-22`）
- 禁止使用 `20260522`、`2026/05/22`、`22-05-2026` 等其他格式
- 日期须为计划创建或启动日期，不随更新而变动

## 4. 命名审计自检

在 `Write` 工具调用正式目录前，必须自问：

1. 文件名是否包含非 ASCII 字符？—— **必须为纯 ASCII**
2. 单文件命名格式是否与 `YYYY-MM-DD-{topic}.md` 一致？—— 如不一致，须说明理由
3. 原子单元文件名是否为 `{section-name}.md`？—— 如不一致，须说明理由
4. 目录名是否为纯 ASCII kebab-case？—— 原子化目录须为 `YYYY-MM-DD-{topic}/` 格式

## 5. 别名声明

文件重命名或合并后，须在新文件头部添加别名声明：

```markdown
> **别名**：曾用名 `old-filename.md`，已迁移至此
```
