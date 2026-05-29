# worldsprout 项目骨架

本目录是从 AgentForge 脱胎而来的新组织内容。去除了所有个人身份信息、哲学内容、私有配置。

> **状态**：✅ 核心文件全部脱胎完成 · 详见 [RETROSPECTIVE.md](RETROSPECTIVE.md)

## 目录结构

```
rebirth/
├── worldsprout/                 # 主项目（参考实现 + 工具链）✅
│   ├── .agents/
│   │   └── world.toml          # ✅ 去个人化的世界声明
│   ├── AGENTS.md               # ✅ 去哲学化的全局契约
│   └── GOVERNANCE.md           # ✅ 去个人化的项目治理

├── spec/                        # 标准规范仓库 ✅
│   └── worldsprout-spec-v1.0.md # ✅ 脱胎自 Spec v0.2

├── .github/                     # 组织级配置 ✅
│   └── profile/README.md       # ✅ 组织首页

├── privacy-spec/                # 🔲 隐私脱敏协议仓库（待创建）
├── registry/                    # 🔲 Registry 索引仓库（待创建）

├── RETROSPECTIVE.md             # ✅ 全面复盘
└── README.md                    # 本文件
```

## 脱胎规则

1. **删除**：xinetzone 身份、道德经/Ψ=Ψ(Ψ) 相关、马王堆帛书引用、个人 Token/密钥/路径
2. **中性化**："世界"隐喻保留但去哲学化、"哲学驱动"→"约定驱动"、"大道至简"→删除
3. **重命名**：taolib → sproutlib（已决策，源码实际改名待执行）
4. **保留**：三层架构、AGENTS.md 分离声明、.agents/ 目录约定、SKILL.md 规范、Registry + Fragment 模型、world CLI 工具链、constraints-check 脚本

## 脱胎进度

| 文件 | 状态 |
|------|------|
| `worldsprout/AGENTS.md` | ✅ 完成 |
| `worldsprout/.agents/world.toml` | ✅ 完成 |
| `worldsprout/GOVERNANCE.md` | ✅ 完成 |
| `spec/worldsprout-spec-v1.0.md` | ✅ 完成 |
| `.github/profile/README.md` | ✅ 完成 |
| `RETROSPECTIVE.md` | ✅ 完成 |
| 源码迁移（taolib → sproutlib） | 📋 已决策，待执行 |
| CI 配置迁移 | 📋 待执行 |
| `privacy-spec/` | 🔲 待创建 |
| `registry/` | 🔲 待创建 |

## 下一步

1. 将 rebirth/ 内容推送到 `github.com/worldsprout` 各仓库
2. 执行 `taolib → sproutlib` 全项目重命名
3. 任命首位核心维护者
4. 起草 privacy-spec 和 registry 内容
