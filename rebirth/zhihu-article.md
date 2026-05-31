# 我把个人 AI Agent 项目"脱胎"成了一个开源标准组织——WorldSprout 诞生记

> 从一个人的哲学实验，到一个社区共建的开放标准。这是一篇关于"如何把一个充满个人印记的项目，变成一个别人也能放心用的公共基础设施"的完整复盘。

---

## 一、背景：AgentForge 是什么？

时间回到半年前。我在做一个 AI Agent 相关的开源项目，名字叫 **AgentForge**。它的核心思想是：让多个 AI Agent 在一个共享的"世界"里协作，每个 Agent 有自己的角色（role）、技能（skill）、记忆，以及一套可声明的行为约束。

听起来很像现在流行的 Multi-Agent 框架对吧？但当时我的想法更偏哲学——我用《道德经》里的"大道至简"来解释架构设计，用 Ψ=Ψ(Ψ) 来描述世界自指涉的模型，甚至在规范文档里引用了马王堆帛书。

项目确实在技术上跑通了：world.toml 声明文件、SKILL.md 技能规范、AGENTS.md 桥接标准、约束校验器、CLI 工具链……但问题也很明显——

> **这个项目太"我"了。**

别人一打开仓库，看到的不是技术文档，是哲学论文。参数名叫 `tao`，包名叫 `taolib`，注释里引用的是"无名天地之始，有名万物之母"。如果你是一个普通的 Python 开发者，只想给 AI 配个规则让它在你的项目里老实干活——你看到这些会怎么想？

**所以我决定做一件事：脱胎。**

---

## 二、目标：从 AgentForge 到 WorldSprout

"脱胎"这个词我用得很认真。它不是简单的重命名，而是：

1. **剥离个人身份**：删除所有 xinetzone 的个人信息、Token、密钥、私有路径
2. **去哲学化**：道德经引用、自指涉模型、马王堆帛书——全部移除
3. **品牌重建**：从 AgentForge（个人烙印）变为 WorldSprout（社区隐喻）
4. **标准分离**：把 AGENTS.md 这个开放标准从实现中分离出来，让任何人可以不依赖 WorldSprout 单独使用
5. **建立治理**：写一份正经的 GOVERNANCE.md，定义核心维护者、领域维护者、RFC 流程

最终产出了一个三层架构的规范（WorldSprout Spec v1.0）：

```
Layer 1: Project Protocol    → 零前提采用（AGENTS.md + .agents/ 目录约定）
Layer 2: Collaboration Protocol → 多智能体协作（roles/teams、constraints.toml）
Layer 3: World Runtime       → 示范实现（world CLI、Session 引擎、sproutlib）
```

这三个 Layer 的关系是：**Layer 1 可以独立使用，Layer 2 依赖 Layer 1，Layer 3 是可选的参考实现。** 一个 VS Code 用户只想要 AI 读一下他的 .agents/rules/ 目录？那只需要 Layer 1。不绑定任何运行时。

---

## 三、命名：为什么叫 WorldSprout？

命名是整个脱胎过程中最纠结的环节，没有之一。

最初的方案有一长串：WorldSeed、WorldCore、WorldStack、AgentMark……每个都有问题：

- **WorldSeed**：GitHub 上已经有 org 了，抢注失败
- **AgentMark**：太像"Agent 标记语言"，窄化了定位
- **WorldCore**：太"底层"，和 Layer 1 的轻量定位矛盾

最终锁定 **WorldSprout**，取两层含义：

- **World**：每个开发者的项目就是一个"世界"，Agent 在这个世界里感知和行动
- **Sprout**："种子发芽"。每个人都是一颗世界种子，WorldSprout 是帮助你让这颗种子长出来的脚手架

这个隐喻完美契合了三层架构的设计哲学：你从一个 AGENTS.md 文件开始（种子），需要时加上 .agents/ 目录（发芽），再需要时引入 World Runtime（生长）。每一步都是可选的。

> 顺便提一句：GitHub 组织的 Handle 是 `worldsprout`，Display Name 是 `WorldSprout`。之前想用 `worldseed` 可惜被抢注了……起名要趁早。

---

## 四、执行：脱胎全流程

### 4.1 Spec 演进：从 v0.1 到 v1.0

脱胎前先理清规范。Spec 经历了三次迭代：

| 版本 | 核心变更 |
|------|----------|
| v0.1 | 渐进式复杂度 Level 0-4，从单个 AGENTS.md 到 kernel + immutable rules |
| v0.2 | 三层分离架构，Layer × Level 正交矩阵，哲学内核从必需降格为可选 fragment |
| v1.0 | 去个人化脱胎版，去除所有哲学引用，纯技术规范 |

最大的认知跃迁在 v0.2：意识到"哲学驱动"和"技术标准"必须解耦。不是所有用户都需要道德经，但他们都需要清晰的目录约定和条件加载规则。

### 4.2 脱胎规则

建了一个 `rebirth/` 目录，制定了四条脱胎规则：

```
1. 删除：xinetzone 身份、道德经/Ψ=Ψ(Ψ)、马王堆帛书、个人 Token/密钥
2. 中性化："哲学驱动"→"约定驱动"、"大道至简"→删除
3. 重命名：taolib → sproutlib
4. 排除：github_app/ 不迁移（属于私有基础设施）
5. 保留：三层架构、AGENTS.md 分离声明、.agents/ 目录约定、CLI 工具链
```

### 4.3 文件产出

脱胎后产出了 7 个核心文件：

- `worldsprout/AGENTS.md` — 去哲学化的全局契约
- `worldsprout/.agents/world.toml` — 去个人化的世界声明
- `worldsprout/GOVERNANCE.md` — 项目治理章程（含 RFC 流程、角色定义）
- `spec/worldsprout-spec-v1.0.md` — 正式规范（553 行）
- `.github/profile/README.md` — 组织首页
- `README.md` — 项目入口
- `RETROSPECTIVE.md` — 全面复盘

### 4.4 GitHub 组织上线

这里遇到了整个过程中最折腾的技术环节。

**问题 1：GitHub 沙箱限制**

我们的开发环境有沙箱限制，`.github` 仓库（组织主页）的 git push 被阻断。常规做法是 `git clone https://github.com/worldsprout/.github` 然后推送，但沙箱直接拦截了网络操作。

**解决方案**：删掉空仓库，用 `gh repo create --add-readme` 重建（让它有一个初始 commit），然后用 Browser 自动化直接打开 GitHub 网页，在编辑器中粘贴 `profile/README.md` 的内容。

**问题 2：gh auth 权限不足**

删除仓库需要 `delete_repo` scope，但初始的 `gh auth login` 没有这个权限。需要 `gh auth refresh -h github.com -s delete_repo`，然后在浏览器完成二次授权。

**问题 3：PowerShell 的 `2>&1` 陷阱**

在 Windows PowerShell 中，`git push 2>&1` 会导致沙箱报错 "StandardErrorEncoding is only supported when standard error is redirected"。原因是 PowerShell 的管道重定向和沙箱的 stdout/stderr 处理不兼容。解决方案很简单：去掉 `2>&1`，直接用 `git push`。

### 4.5 治理启动：任命首位核心维护者

GOVERNANCE.md 写得很漂亮——核心维护者至少 2 人、任命需全票通过、任期 2 年……但问题是：

> **只有一个人，怎么"全票通过"？**

这是一个经典的治理启动悖论。解决方案是增加了"启动期例外条款"：

> 组织创始阶段人数不足 2 人时，唯一核心维护者可独立行使全部职权（含任命下一位核心维护者）。当核心维护者达到 2 人后，本例外条款自动废止，后续任命恢复全票规则。

既保持了规则的严肃性，又解决了从 0 到 1 的问题。**@xinetzone** 正式任命为首位核心维护者，任期至 2028-05-29。

---

## 五、子模块架构：如何管理多仓库项目

脱胎后我们有 3 个独立 GitHub 仓库：

```
github.com/worldsprout/worldsprout  → 主项目（参考实现 + 工具链）
github.com/worldsprout/spec         → 标准规范
github.com/worldsprout/.github      → 组织配置
```

而我们又不想放弃原始的 AgentForge 仓库（它记录了整个脱胎前的上下文）。怎么办？

### 方案对比

| 方案 | 优点 | 缺点 |
|------|------|------|
| A. 手动各自管理 | 最简单 | 容易忘记哪个仓库有未推送的修改 |
| B. Git Subtree | 单仓库工作流 | 历史臃肿，合并冲突噩梦 |
| **C. Git Submodule** ✅ | Git 原生支持，清晰 | 需要额外学习 `git submodule update --remote` |

选了方案 C，并且强调一个关键配置：**每个子模块必须设 `branch = main`**。

```toml
# .gitmodules
[submodule "rebirth/worldsprout"]
    path = rebirth/worldsprout
    url = https://github.com/worldsprout/worldsprout.git
    branch = main
[submodule "rebirth/spec"]
    path = rebirth/spec
    url = https://github.com/worldsprout/spec.git
    branch = main
[submodule "rebirth/.github"]
    path = rebirth/.github
    url = https://github.com/worldsprout/.github.git
    branch = main
```

日常操作也非常简单：

```bash
# 拉取所有子模块最新
git submodule update --remote

# 进入子模块独立开发
cd rebirth/worldsprout
# ... 修改、提交 ...
git push origin main

# 回到父仓库锁定版本
cd ../..
git add rebirth/worldsprout
git commit -m "chore: 更新 worldsprout 子模块"
```

这样，`rebirth/` 目录成了 AgentForge 的"母港"——本地文件（README.md + RETROSPECTIVE.md）记录上下文，子模块链接到独立仓库，各司其职。

---

## 六、关键经验

### 6.1 个人项目 ≠ 烂，但它自己也不知道自己很"个人"

AgentForge 的技术实现没有大问题。但当一个项目只有一个人在写、在看、在用的时候，你会不自觉地往里面塞各种"个人趣味"——哲学隐喻、文化引用、私有的命名偏好。这些东西对作者来说很自然，对新人来说就是理解障碍。

**脱胎的第一步，是意识到"我不等于项目"。**

### 6.2 AGENTS.md 的分离是最正确的决策

AGENTS.md 是一个让 AI Agent 读取项目约定的文件格式。Coursor、Windsurf、Codex、Claude Code、Copilot Chat……几乎所有主流 AI 编程工具都支持在项目根目录放一个 AGENTS.md。

WorldSprout 的 Layer 1 扩展了这个标准——.agents/ 目录、条件加载（`paths:` glob）、YAML frontmatter。但关键是：**我们把 AGENTS.md 本身声明为一个独立于 WorldSprout 的开放标准。**

这意味着：
- 你只用一个 AGENTS.md → 完全兼容所有工具
- 你加上 .agents/ 目录 → WorldSprout 增强
- 你不用 WorldSprout CLI → 不影响任何东西

这就是"零前提采用"——不绑架用户。

### 6.3 治理要早于代码

GOVERNANCE.md 是我在只有自己一个人的时候写的。很多人觉得"一个人搞什么治理"，但恰恰相反——**治理章程的使命不是约束当下，是为未来开门。**

一个清晰的 RFC 流程、明确的角色定义、透明化的决策机制，是吸引第二个、第三个贡献者的前置条件。没人愿意把自己的精力投入一个"看作者心情"的项目。

### 6.4 沙箱环境的教训

GitHub Actions、沙箱 CI、容器化环境——这些东西在日常开发时感觉不到存在，一旦遇到限制就会耗费大量时间。

本次遇到的 PowerShell `2>&1` 兼容问题、gh auth scope 问题、空仓库 API 问题……每一个都是五分钟能搞定的小事，但叠加在一起就是半天。**教训：在受限环境中操作前，先用最简单的命令测试连通性。**

---

## 七、当前状态与后续路线

### 已完成 ✅

| 事项 | 细节 |
|------|------|
| WorldSprout Spec v1.0 | 三层架构规范发布 |
| GitHub 组织 | worldsprout 注册，3 个仓库上线 |
| 治理章程 | GOVERNANCE.md + 首位核心维护者任命 |
| 脱胎文件 | 7 个核心文件完成去个人化 |
| 子模块架构 | AgentForge 统一管理 3 个子仓库 |
| 全面复盘 | RETROSPECTIVE.md 归档 |

### 待推进 📋

| 优先级 | 事项 |
|--------|------|
| P2 | taolib → sproutlib 全项目重命名（首个 RFC 示范） |
| P3 | privacy-spec 隐私脱敏协议起草 |
| P3 | Registry 首个 Fragment 发布，验证 Fragment 模型 |

---

## 八、结语

WorldSprout 现在还很小。一个 Spec，三个仓库，一位维护者，一段从哲学实验中长出来的代码。

但它的起点是干净的——没有不可说的历史包袱，没有绑定到任何人的个人偏好，没有"先装 CLI 再看文档"的绑架式入门路径。一个开发者只需要在项目根目录放一个 AGENTS.md，就完成了"加入生态"的第一个动作。

如果你也在考虑把自己的个人项目变成一个更开放的东西，希望这篇复盘能给你一些参考。核心就一句话：

> **脱胎不是删除自己，是把"我的"变成"我们的"。**

---

*WorldSprout：[github.com/worldsprout](https://github.com/worldsprout)*

*本文同步归档于项目仓库：`rebirth/RETROSPECTIVE.md`*
