# 28. 交付摘要与落地产物

## 28.1 AGENTS.md 开放标准与 AgentForge 的分离声明

**两处修改**：

1. **[AGENTS.md](file://d:/spaces/AgentForge/apps/chaos/AGENTS.md)** 顶部新增引用块，明确声明：
   - AGENTS.md 是独立的社区开放标准，30+ 工具原生支持，**不需要安装 AgentForge**
   - AgentForge 在此基础上提供渐进可选的扩展层
   - Markdown ≈ CommonMark 类比

2. **[Spec v0.2 规范文档](file://d:/spaces/AgentForge/apps/chaos/.agents/docs/superpowers/specs/2026-05-28-agentforge-spec-v0.2-three-layer-architecture.md)** 新增 §1.0 节，用表格明确划分：
   - 定义方、核心约定、最低门槛、独立性、适用范围
   - 结论句：**"AgentForge 不再要求标准采纳者接受它的世界观"**

## 28.2 长出肉："30 秒尖叫瞬间"

**三个新产物**：

| 产物 | 路径 | 作用 |
|------|------|------|
| Starter 模板 | `.agents/templates/starter/` | AGENTS.md + world.toml + rules/skills/docs 骨架 |
| `world init` 命令 | `src/taolib/cli/_world_commands/init.py` | 脚手架生成器，类比 `npm init` |
| CLI 入口注册 | `src/taolib/cli/world.py` | `init` 注册为 world 的第一个子命令 |

**用户体验**：

```bash
$ world init --name my-awesome-project
  使用模板: .agents/templates/starter
  已创建: AGENTS.md
  已创建: .agents/world.toml
  已创建: .agents/rules/
  已创建: .agents/skills/
  已创建: .agents/docs/

  ✨ 项目 'my-awesome-project' 已就绪！下一步：
    - 编辑 AGENTS.md 定制你的全局契约
    - 编辑 .agents/world.toml 声明项目元信息
    - 运行 world status 查看当前状态
```

`world init` 有两种工作模式：
- **模板模式**：找到 `.agents/templates/starter/` 时使用项目模板（AgentForge 仓库内）
- **内嵌模式**：未找到模板时使用硬编码的最小模板（作为独立 pip 包使用时）
