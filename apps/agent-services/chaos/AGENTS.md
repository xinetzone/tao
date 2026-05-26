# AGENTS.md

> **注意**：本文档已拆分至多个独立文档中，以提高可维护性和可读性。请查看以下文档获取详细信息。

## 文档导航

- [README.md](README.md) - 项目概述与快速开始
- [Python 环境](doc/user/python_environment.md) - Python 环境与 3.14 新特性
- [常用命令](doc/user/commands.md) - 常用命令
- [架构说明](doc/architecture/architecture.md) - 架构说明
- [API 参考](doc/api_reference/api_reference.md) - API 参考与文档整合原则
- [编码规范](doc/dev/coding_standards.md) - 编码规范
- [环境变量](doc/user/environment_variables.md) - 环境变量
- [最佳实践](doc/dev/best_practices.md) - 最佳实践
- [项目经验总结](doc/dev/project_experience.md) - 项目经验总结
- [Qoder 规范](doc/dev/qoder_rules.md) - Qoder 规范
- [测试指南](doc/dev/testing.md) - 测试命令、规范与策略
- [目录结构](doc/architecture/directory_structure.md) - 项目目录结构规范

---

## ⚠️ AI Agent 行为约束

### 执行原则

**核心约束**：AI Agent 在执行任何任务时，**必须**严格遵守以下目录管理规则。

### 目录管理矩阵

| 目录路径 | 状态 | 管理方 | 操作权限 |
|---------|------|--------|---------|
| `tests/chaos/` | ❌ **排除** | 独立管理 (`.agents/`) | 仅读取，禁止修改 |
| `tests/chaos/.agents/` | ❌ **排除** | 独立管理 | 仅读取，禁止修改 |
| `tests/chaos/.trae/` | ❌ **排除** | 独立管理 | 仅读取，禁止修改 |
| 其他 `tests/` 目录 | ✅ **受控** | 本文件 | 遵循项目规范 |

### 强制执行规则

#### 1. 禁止操作列表

以下操作**必须禁止**：

```
❌ 不要修改 tests/chaos 目录下的任何文件
❌ 不要在 tests/chaos 目录下创建新文件
❌ 不要将 tests/chaos 纳入跨目录重构任务
❌ 不要在根目录 AGENTS.md 中引用 tests/chaos 的详细内容
❌ 不要对 tests/chaos 执行任何测试相关的操作
```

#### 2. 允许操作列表

以下操作**被明确允许**：

```
✅ 可以读取 tests/chaos 目录了解项目结构
✅ 可以引用 tests/chaos 中的配置文件作为参考
✅ 可以在文档中说明 tests/chaos 是独立管理区域
✅ 可以在任务执行时标注涉及 tests/chaos 的边界
```

#### 3. 任务执行检查清单

在执行任何涉及 `tests/` 目录的任务前，AI Agent **必须**完成以下检查：

**Step 1: 范围确认**
- [ ] 确认目标目录是否属于 `tests/chaos` 排除范围
- [ ] 确认操作是否涉及 `tests/chaos` 及其子目录

**Step 2: 权限判断**
- [ ] 如果涉及 `tests/chaos`：执行 Step 3
- [ ] 如果不涉及 `tests/chaos`：正常执行任务

**Step 3: 排除处理**
- [ ] 明确告知用户该目录属于独立管理范围
- [ ] 建议用户通过 `tests/chaos/.agents/` 的配置进行操作
- [ ] 等待用户明确授权
- [ ] 获得授权后，仅执行用户授权的具体操作

#### 4. 违规响应协议

如果 AI Agent **意外**对 `tests/chaos` 执行了操作，应立即：
1. 停止当前操作
2. 撤销未完成的修改
3. 告知用户违规操作的详情
4. 建议恢复或更正措施

---

## 文件命名规范

项目中所有文档文件（`.md`、`.rst` 等）**必须使用连字符 `-` 连接单词**，**不得使用下划线 `_`**。此规范适用于所有新建文件，已有文件应在后续维护中逐步迁移。

### 示例

**正确**：
- `python-packages.md`
- `cli-tools.md`
- `online-services.md`
- `coding-standards.md`
- `directory-structure.md`

**错误**：
- ~~`python_packages.md`~~
- ~~`cli_tools.md`~~
- ~~`online_services.md`~~
- ~~`coding_standards.md`~~
- ~~`directory_structure.md`~~

### 适用范围
- `doc/` 目录下的所有文档文件
- 新建的 Markdown 文件及 reStructuredText 文件
- 项目根目录下的文档文件（如 `README.md`、`CONTRIBUTING.md` 等）

## 核心功能速览

`taolib` 是一个 Python 库（Python >= 3.13），核心功能列表详见 [README.md](README.md#核心功能)。

核心设计理念：最小化核心依赖（`dependencies = []`），通过可选依赖组提供扩展功能。

---

## 版本信息

| 属性 | 值 |
|------|-----|
| **生效日期** | 2026-05-20 |
| **版本** | v1.0 |
| **适用范围** | 所有 AI Agent 会话 |
| **最后更新** | 2026-05-20 |
