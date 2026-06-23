# 命名规范

> **维护责任人**：Leader Agent
> **适用范围**：`retrospectives/` 全目录及子模块

## 1. 目录命名

| 规则 | 说明 | 示例 |
|------|------|------|
| 纯 ASCII | 禁止中文、emoji、空格 | `project-reviews/` ✅ `项目复盘/` ❌ |
| kebab-case | 单词间用连字符 `-` 连接 | `python-environment/` ✅ `python_environment/` ❌ |
| 一级模块 | 按文档类型命名 | `project-reviews/`、`audit-reports/`、`insights/`、`session-reviews/`、`task-summaries/`、`misc/` |
| 二级子模块 | 仅 `task-summaries/` 下按主题命名 | `ci-cd/`、`documentation/`、`skills/` 等 |
| 原子化目录 | `{topic}-{date}/` 格式 | `agentforge-project-20260523/` |
| 元数据目录 | 以下划线前缀 | `_meta/` |

## 2. 文件命名

### 2.1 单文件文档

格式：`{topic}-{date}.md`

| 元素 | 规则 | 示例 |
|------|------|------|
| topic | 英文 kebab-case，描述文档主题 | `ci-lint-linkcheck-fix` |
| date | YYYYMMDD 格式 | `20260609` |
| 连接 | topic 与 date 间用 `-` 连接 | `ci-lint-linkcheck-fix-20260609.md` |

### 2.2 原子单元文件

格式：`{section-name}.md`

| 元素 | 规则 | 示例 |
|------|------|------|
| section-name | 英文 kebab-case，描述单一主题 | `spec-achievement.md`、`engineering-maturity.md` |
| 位置 | 位于同名原子化目录内 | `agentforge-project-20260523/spec-achievement.md` |

### 2.3 索引文件

| 文件 | 位置 | 用途 |
|------|------|------|
| `index.md` | 原子化目录内 | 概述与原子单元索引 |
| `README.md` | 模块目录内 | 模块说明与文件清单 |

## 3. 日期格式

- 统一使用 `YYYYMMDD`（如 `20260523`）
- 禁止使用 `2026-05-23`、`2026/05/23`、`20260523` 以外格式
- 月级复盘可使用 `YYYY-MM` 格式（如 `2026-05`），仅限项目级复盘

## 4. 命名审计自检

在 `Write` 工具调用正式目录前，必须自问：

1. 文件名是否包含非 ASCII 字符？—— **必须为纯 ASCII**
2. 文件名格式是否与同层既有文件一致？—— 如不一致，须说明理由

## 5. 别名声明

文件重命名或合并后，须在新文件头部添加别名声明：

```markdown
> **别名**：曾用名 `old-filename.md`，已迁移至此
```
