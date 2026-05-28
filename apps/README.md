# Apps

`apps/` 是当前仓库的应用层入口目录。

目前这个目录下最主要的工作区是 `chaos/`。如果你是第一次进入应用层，建议先从这里理解目录定位，再进入具体子项目。

## 当前目录状态

当前 `apps/` 的组织方式可以概括为：

- `chaos/`：当前主工作区，承载现行代码、文档、AI 规则与测试

如果你要开发、调试、阅读实现，优先进入 `chaos/`。

## 从哪里开始

### 面向开发者

建议按下面顺序进入：

1. 先阅读 `chaos/README.md`
2. 再进入 `chaos/docs/tech/quickstart.md`
3. 需要看代码时进入 `chaos/src/taolib/`

### 面向 AI 协作者

建议按下面顺序进入：

1. 先阅读 `../AGENTS.md`
2. 再进入 `chaos/AGENTS.md`
3. 需要具体规则时进入 `chaos/.agents/`

### 面向维护者

如果你关心应用层演化与重构进度，可继续阅读：

- `chaos/README.md`
- `chaos/docs/`
- `../CHANGELOG.md`

## 目录导航

| 路径 | 作用 |
|---|---|
| `README.md` | `apps/` 目录入口页 |
| `chaos/` | 当前主子项目与核心工作区 |

## 快速进入主工作区

如果你现在就要开始实际工作，直接进入：

```bash
cd apps/chaos
```

然后继续阅读：

- `chaos/README.md`
- `chaos/docs/tech/quickstart.md`
- `chaos/AGENTS.md`

## 说明

这份 `README.md` 的职责是提供 `apps/` 目录级导航，而不是承载全部仓库细节。

随着后续重构推进，如果应用层结构、主工作区或入口方式发生变化，应同步更新本页，确保进入 `apps/` 的读者能够快速找到正确入口。
