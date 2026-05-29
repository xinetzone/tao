# worldsprout 项目骨架

本目录是从 AgentForge 脱胎而来的 WorldSprout 组织内容。去除了所有个人身份信息、哲学内容、私有配置。三个子目录以 **git submodule** 形式各自链接到独立 GitHub 仓库，均跟踪 `main` 分支。

> **状态**：✅ 脱胎完成，GitHub 上线，子模块就绪 · 详见 [RETROSPECTIVE.md](RETROSPECTIVE.md)

## 仓库映射

```
rebirth/                          ← AgentForge 本地母港
├── worldsprout/  (submodule)     → github.com/worldsprout/worldsprout
├── spec/         (submodule)     → github.com/worldsprout/spec
├── .github/      (submodule)     → github.com/worldsprout/.github
├── README.md                     ← AgentForge 跟踪（本文件）
└── RETROSPECTIVE.md              ← AgentForge 跟踪（全面复盘）
```

## 日常管理

```bash
# 拉取所有子模块最新代码
git submodule update --remote

# 进入子模块独立开发
cd rebirth/worldsprout
git pull origin main
# ... 修改、提交、推送 ...

# 回到主仓库锁定新版本
cd ../..
git add rebirth/worldsprout
git commit -m "chore: 更新 worldsprout 子模块"
```

## 脱胎规则

1. **删除**：xinetzone 身份、道德经/Ψ=Ψ(Ψ) 相关、马王堆帛书引用、个人 Token/密钥/路径
2. **中性化**："世界"隐喻保留但去哲学化、"哲学驱动"→"约定驱动"、"大道至简"→删除
3. **重命名**：taolib → sproutlib（已决策，源码实际改名待执行）
4. **排除**：`src/taolib/github_app/` 不迁移——属于 AgentForge 私有基础设施（Token 管理、事件处理），非通用标准
4. **保留**：三层架构、AGENTS.md 分离声明、.agents/ 目录约定、SKILL.md 规范、Registry + Fragment 模型、world CLI 工具链、constraints-check 脚本

## 后续路线

| 优先级 | 事项 |
|--------|------|
| P1 | 任命首位核心维护者 |
| P2 | taolib → sproutlib 重命名（首个 RFC 示范） |
| P3 | privacy-spec 起草 |
| P3 | Registry 首个 fragment 发布 |
