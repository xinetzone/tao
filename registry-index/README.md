# AgentForge Registry Index（本地原型）

本目录是 AgentForge 世界组件 Registry 的**本地原型**，用于在独立仓库化之前承载 Fragment / Capability 等世界组件的索引元数据。

## 协议依据

本 Registry 严格遵循 [`docs/tech/world-registry-protocol.md`](../docs/tech/world-registry-protocol.md) 定义的 World Registry Protocol（WRP）。所有索引条目的字段语义、版本管理、签名约束以协议文档为准。

## 目录结构约定

```
registry-index/
├── registry-meta.toml          # Registry 仓库自身元数据
├── README.md                   # 本说明
├── fragments/                  # Fragment 类型组件索引
│   ├── py/                     # 类目缩写：Python 工程
│   │   └── <name>.toml
│   ├── do/                     # 文档治理
│   ├── ps/                     # Ψhē 哲学映射
│   ├── ci/                     # 引用与来源
│   ├── fe/                     # 前端
│   ├── be/                     # 后端
│   └── pr/                     # PR Review
└── capabilities/               # Capability 类型组件索引（按需扩展）
```

约定：

- `fragments/{category}/<name>.toml` 中 `category` 为两字母缩写。
- 每个条目文件代表**一个组件**，内含 `[metadata]`、`[source]`、`[[versions]]`、`[latest]` 段。
- 同一组件多个版本通过追加 `[[versions]]` 数组项管理，`yanked = true` 表示版本已下架。

## 如何添加新条目

1. 在 `fragments/<category>/` 下新建 `<name>.toml`，按现有条目结构填写。
2. 至少提供一个 `[[versions]]`，并在 `[latest].stable` 标注当前稳定版本。
3. `manifest_path` 指向上游仓库内的 `fragment.toml` 路径，`git_ref` 推荐使用 tag 或不可变 commit。
4. 提交前在本地通过 `world` CLI（接入后）执行索引校验。

## 未来演进

- 本目录会**独立为 GitHub 仓库** `agentforge/registry-index`，作为 AgentForge 官方 Registry 的真实源。
- 与世界级 `.agents/registry.toml` 的 `local` / `default` 源协同，逐步引入 HTTP API、签名校验与全文检索能力。
