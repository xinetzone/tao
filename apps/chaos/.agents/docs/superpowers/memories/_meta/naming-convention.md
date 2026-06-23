# 命名规范

> **维护责任人**：Leader Agent
> **适用范围**：`memories/` 全目录及子模块

## 1. 目录命名

| 规则 | 说明 | 示例 |
|------|------|------|
| 纯 ASCII | 禁止中文、emoji、空格 | `principles/` ✅ `原则/` ❌ |
| kebab-case | 单词间用连字符 `-` 连接 | `principles/` ✅ |
| 一级模块 | 按记忆类型命名 | `principles/`、`experiences/`、`constraints/`、`methodologies/` |
| 元数据目录 | 以下划线前缀 | `_meta/` |

## 2. 文件命名

格式：`YYYY-MM-DD-{topic}-{type}.md`

| 元素 | 规则 | 示例 |
|------|------|------|
| 日期前缀 | `YYYY-MM-DD` 格式 | `2026-05-25` |
| topic | 英文 kebab-case，描述记忆主题 | `doc-maintenance-5-steps` |
| type | 记忆类型后缀 | `principle` / `experience` / `constraint` / `methodology` / `fact` |

示例：
- `2026-05-25-doc-maintenance-5-steps-experience.md`
- `2026-05-25-myst-cross-directory-link-constraint.md`
- `2026-06-11-document-debt-governance-three-phase-methodology.md`

## 3. 类型后缀说明

| 后缀 | 含义 | 示例 |
|------|------|------|
| `principle` | 通用原则、设计原则 | concept-first-documentation-second-principle |
| `experience` | 实战经验、最佳实践 | doc-maintenance-5-steps-experience |
| `constraint` | 技术约束、边界条件 | myst-cross-directory-link-constraint |
| `methodology` | 可复用方法论、流程框架 | document-debt-governance-three-phase-methodology |
| `fact` | 事实、约定（预留） | — |

## 4. 命名审计自检

在 `Write` 工具调用正式目录前，必须自问：

1. 文件名是否包含非 ASCII 字符？—— **必须为纯 ASCII**
2. 文件名格式是否与 `YYYY-MM-DD-{topic}-{type}.md` 一致？—— 如不一致，须说明理由
