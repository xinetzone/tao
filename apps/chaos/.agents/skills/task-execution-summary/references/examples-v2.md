# 任务执行总结报告生成器 - V2 完整使用示例

**文档版本**: v2.0
**最后更新**: 2026-04-09
**适用技能版本**: Task Execution Summary Generator v2.0+

本文档提供"任务执行总结报告生成器"技能的 **V2 标准化请求-响应格式示例**，涵盖正常调用、最小参数、参数错误和数据不足等典型场景。所有示例均遵循 [api-reference.md](api-reference.md) 中定义的接口规范。

---

## 📌 文档阅读指南

| 读者类型 | 推荐阅读内容 | 目的 |
|---------|------------|------|
| **集成开发者** | 全部 4 个示例 | 理解完整的输入输出格式、错误处理和降级机制 |
| **测试工程师** | 示例 1 + 示例 3 + 示例 4 | 编写自动化测试用例的参考数据 |
| **普通用户** | 示例 1 + 示例 2 | 学习如何正确调用技能获取高质量报告 |

### 响应状态分类

| success 字段 | degraded 字段 | 含义 | 处理建议 |
|-------------|--------------|------|---------|
| `true` | 无/`false` | ✅ 完全成功 | 直接使用报告 |
| `true` | `true` | ⚠️ 降级成功 | 报告可用但质量受影响，查看 warnings |
| `false` | - | ❌ 执行失败 | 根据 error 信息修复后重试 |

---

## 示例 1: 软件开发任务标准调用

### 场景描述

用户刚完成了一个用户认证模块的开发任务，该任务涉及 Session 管理、密码加密、登录注册流程实现等多个技术环节，历时约 2 小时。这是一个典型的软件开发场景，用户希望生成一份标准的执行总结报告用于技术沉淀和团队分享。使用默认配置即可获得高质量结果。

### 完整请求 JSON

```json
{
  "task_context": {
    "task_name": "用户认证模块开发",
    "task_type": "development",
    "time_range": null,
    "description": "实现基于 Session 的用户登录注册功能"
  },
  "generation_options": {
    "detail_level": "standard",
    "template_variant": "standard",
    "included_chapters": null,
    "excluded_chapters": null,
    "language_style": "professional",
    "focus_dimensions": ["goal_achievement", "problem_patterns"],
    "output_format": "markdown"
  },
  "output_config": {
    "save_to_file": true,
    "file_path": null,
    "include_metadata": true
  }
}
```

**请求参数解析**:

| 参数 | 值 | 说明 |
|-----|-----|------|
| `task_name` | "用户认证模块开发" | 必填，标识任务主题 |
| `task_type` | "development" | 明确指定为软件开发类型 |
| `detail_level` | "standard" | 标准详细程度（10章完整） |
| `focus_dimensions` | ["goal_achievement", "problem_patterns"] | 重点分析目标达成度和问题模式 |
| `save_to_file` | true | 自动保存到文件 |
| `file_path` | null | 使用自动生成的路径 |
| `time_range` / `included_chapters` / `excluded_chapters` | null | 使用系统智能推断或默认值 |

### 预期成功响应

```json
{
  "success": true,
  "report_id": "rpt-20260409-dev-001",
  "timestamp": "2026-04-09T16:30:00Z",
  "processing_time_ms": 192000,

  "report": {
    "title": "用户认证模块开发 - 执行总结报告",

    "content": "# 用户认证模块开发 - 执行总结报告\n\n## 📋 基本信息\n\n| 属性 | 值 |\n|------|-----|\n| **任务名称** | 用户认证模块开发 |\n| **任务类型** | 软件开发 |\n| **执行时间** | 约 2 小时 |\n| **报告生成时间** | 2026-04-09 16:30 |\n| **质量评分** | 94.5 / 100 |\n\n## 🎯 一、任务目标与背景\n\n### 1.1 初始目标设定\n\n本任务的初始目标是实现一个基于 Session 的用户认证系统，包括以下核心功能：\n\n- 用户注册：支持邮箱/手机号注册，包含表单验证和重复检查\n- 用户登录：实现安全的登录流程，支持记住登录状态\n- 会话管理：基于 Session 的用户状态维护，包含超时机制\n- 密码安全：采用 bcrypt 加密存储，防止明文泄露\n\n**预期交付物**:\n- 后端 API 接口（注册、登录、登出、会话查询）\n- 数据库 Schema 设计（users 表、sessions 表）\n- 中间件实现（认证守卫、权限校验）\n- 单元测试覆盖核心逻辑\n\n### 1.2 目标调整记录\n\n| 时间点 | 调整原因 | 调整内容 | 影响评估 |\n|--------|---------|---------|----------|\n| T+30min | 产品需求变更 | 增加「第三方 OAuth 登录」需求 → 移至后续迭代 | 低（不影响当前 MVP） |\n| T+75min | 安全审计反馈 | 密码强度要求从 6 位提升至 8 位 + 复杂度规则 | 中（需修改验证逻辑） |\n\n### 1.3 最终成果清单\n\n✅ **已完成功能**:\n- [x] 用户注册 API（POST /api/auth/register）\n- [x] 用户登录 API（POST /api/auth/login）\n- [x] 登出功能（POST /api/auth/logout）\n- [x] Session 中间件（自动注入用户信息）\n- [x] bcrypt 密码加密（cost factor = 12）\n- [x] 表单验证（邮箱格式、密码强度、必填项）\n- [x] 单元测试（12 个用例，覆盖率 85%）\n\n⏳ **延后功能**:\n- [ ] 第三方 OAuth 登录（计划 v1.1）\n- [ ] 账户锁定机制（连续失败 5 次后锁定 15 分钟）\n- [ ] 多设备会话管理（强制下线旧设备）\n\n**产出物统计**:\n- 代码文件：6 个（controller 1 + service 1 + model 2 + middleware 1 + test 1）\n- 代码行数：约 450 行（含注释和空行）\n- 数据库迁移文件：2 个（create_users, create_sessions）\n\n---\n\n## 🔍 二、执行过程详解\n\n### 2.1 分阶段执行记录\n\n#### 阶段一：技术方案设计（T+0min ~ T+25min）\n\n**阶段目标**: 确定技术选型和架构设计方案\n\n**关键活动**:\n1. 分析现有项目技术栈（Express.js + PostgreSQL + Sequelize ORM）\n2. 对比认证方案：Session vs JWT Token\n3. 设计数据库 ER 图和 API 端点规范\n4. 编写技术方案文档并获得确认\n\n**决策点**:\n- 选择 Session 方案而非 JWT（详见第四章 D1 决策）\n- 选择 bcrypt 而非 argon2（性能考虑）\n\n**产出物**: `AUTH_DESIGN_DOC.md`（技术方案文档）\n\n---\n\n#### 阶段二：数据库设计与初始化（T+25min ~ T+50min）\n\n**阶段目标**: 创建数据库表结构和种子数据\n\n**关键活动**:\n1. 定义 User 模型（id, email, password_hash, created_at, updated_at）\n2. 定义 Session 模型（id, user_id, token, expires_at, created_at）\n3. 编写 Sequelize Migration 文件\n4. 执行迁移并验证表结构\n\n**代码片段** (User Model):\n```javascript\nmodule.exports = (sequelize, DataTypes) => {\n  const User = sequelize.define('User', {\n    id: {\n      type: DataTypes.INTEGER,\n      primaryKey: true,\n      autoIncrement: true\n    },\n    email: {\n      type: DataTypes.STRING(255),\n      allowNull: false,\n      unique: true,\n      validate: { isEmail: true }\n    },\n    passwordHash: {\n      type: DataTypes.STRING(255),\n      allowNull: false,\n      field: 'password_hash'\n    }\n  }, {\n    tableName: 'users',\n    timestamps: true\n  });\n  return User;\n};\n```\n\n**遇到问题**: 初始设计遗漏了 `email_verified` 字段 → 在 T+35min 补充了 migration\n\n---\n\n#### 阶段三：核心功能实现（T+50min ~ T+100min）\n\n**阶段目标**: 实现 CRUD 核心业务逻辑\n\n**关键活动**:\n1. AuthService 实现（注册、登录、密码比对）\n2. AuthController 实现（HTTP 层处理）\n3. AuthMiddleware 实现（Session 校验中间件）\n4. 错误处理和日志记录\n\n**API 端点列表**:\n\n| 方法 | 路径 | 功能 | 认证要求 |\n|------|------|------|----------|\n| POST | /api/auth/register | 用户注册 | 否 |\n| POST | /api/auth/login | 用户登录 | 否 |\n| POST | /api/auth/logout | 用户登出 | 是 |\n| GET | /api/auth/me | 获取当前用户 | 是 |\n\n**代码亮点** (Login Service):\n```javascript\nasync login(email, password) {\n  const user = await User.findOne({ where: { email } });\n  if (!user) throw new NotFoundError('用户不存在');\n  \n  const isValid = await bcrypt.compare(password, user.passwordHash);\n  if (!isValid) throw new UnauthorizedError('密码错误');\n  \n  const session = await Session.create({\n    userId: user.id,\n    token: crypto.randomBytes(32).toString('hex'),\n    expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000)\n  });\n  \n  return { user: user.toJSON(), token: session.token };\n}\n```\n\n---\n\n#### 阶段四：测试与优化（T+100min ~ T+120min）\n\n**阶段目标**: 确保代码质量和安全性\n\n**关键活动**:\n1. 编写单元测试（Jest 框架）\n2. 进行边界条件测试（空输入、SQL 注入、XSS）\n3. 性能优化（bcrypt cost factor 调优）\n4. 代码审查和重构\n\n**测试结果**:\n- 总用例数：12 个\n- 通过率：100%\n- 代码覆盖率：85%（目标 >80%）\n\n**优化项**:\n- 将 bcrypt 的 cost factor 从 10 提升至 12（安全增强）\n- 添加了速率限制中间件（防止暴力破解）\n- 重构了错误处理为统一的 Error 类层次结构\n\n---\n\n## 🧠 三、关键决策分析\n\n### 决策 D1：Session vs JWT 认证方案选择\n\n**决策时刻**: T+15min（技术方案设计阶段）\n\n**备选方案对比**:\n\n| 维度 | 方案 A: Session Cookie | 方案 B: JWT Token |\n|------|----------------------|------------------|\n| **无状态性** | ❌ 需要服务端存储 | ✅ 自包含，无需服务端存储 |\n| **安全性** | ✅ 可随时失效（服务端控制） | ⚠️ Token 签发后难以主动撤销 |\n| **扩展性** | ❌ 多服务器需共享 Session 存储 | ✅ 天然适合分布式架构 |\n| **复杂度** | ✅ 简单直观，浏览器原生支持 | ⚠️ 需处理 Refresh Token 机制 |\n| **适用场景** | 传统 Web 应用 | SPA / 移动端 API |\n\n**最终选择**: **方案 A - Session Cookie**\n\n**决策依据**:\n1. 当前项目是传统多页面应用（MPA），非 SPA 架构\n2. 团队对 Session 方案更熟悉，学习成本低\n3. 需要即时注销能力（管理员可强制踢出用户）\n4. 当前单服务器部署，无需考虑分布式 Session 问题\n5. 开发时间有限（2小时），Session 方案更快落地\n\n**事后评估**: ✅ **正确决策**。\n- Session 方案在 40 分钟内完成全部实现\n- 团队 Code Review 一致认可该选择\n- 如未来迁移至微服务架构，可平滑升级为 Redis 共享 Session\n\n---\n\n### 决策 D2：bcrypt vs argon2 密码哈希算法\n\n**决策时刻**: T+45min（数据库设计阶段）\n\n**备选方案对比**:\n\n| 维度 | bcrypt | argon2 |\n|------|--------|--------|\n| **抗 GPU/ASIC 攻击** | ⚠️ 一般 | ✅ 最强（2015 PHC 赢家） |\n| **内存硬度** | ❌ 不具备 | ✅ 可配置内存占用 |\n| **库成熟度** | ✅ 广泛使用，生态完善 | ⚠️ 较新，部分环境需编译 |\n| **Node.js 支持** | ✅ 内置或易安装 | ⚠️ 需额外安装 node-argon2 |\n| **性能** | ✅ 快速（cost=10 时 <500ms） | ⚠️ 较慢（同等安全强度下） |\n\n**最终选择**: **bcrypt（cost factor = 12）**\n\n**决策依据**:\n1. 项目对密码哈希的性能有要求（登录响应 <1s）\n2. bcrypt 在 Node.js 生态中更稳定可靠\n3. cost factor = 12 已提供足够的安全性（约 250ms/次）\n4. 团队之前的项目均使用 bcrypt，保持一致性\n\n**事后评估**: ✅ **合理决策**。在安全性和性能之间取得了良好平衡。\n\n---\n\n## 🐛 四、问题解决记录\n\n### 问题 I1：Sequelize Migration 执行顺序错误\n\n**问题描述**:\n\n**现象**:\n执行 `npx sequelize db:migrate` 时报错：`relation \"sessions\" does not exist`\n\n**发生时间**: T+42min（正在创建 sessions 表时）\n\n**根因分析**:\nsessions 表的外键引用 users 表，但 migration 文件的命名导致执行顺序错误（sessions 的 migration 文件名按字母顺序排在 users 之前）\n\n**解决方案**:\n1. 删除已执行的 sessions migration\n2. 重命名 migration 文件，确保时间戳顺序正确：\n   - `20260409143000-create-users.js`\n   - `20260409143001-create-sessions.js`\n3. 重新执行 migrate\n\n**经验教训**:\n- ✅ Sequelize migration 的执行顺序依赖文件名的时间戳前缀\n- ⚠️ 创建外键约束时必须确保被引用表先存在\n- 💡 可以使用 `sequelize-cli migration:generate` 自动生成正确的时间戳\n\n---\n\n### 问题 I2：Session Cookie 未设置 HttpOnly 和 Secure 标志\n\n**问题描述**:\n\n**现象**:\n安全扫描工具警告：Session Cookie 缺少安全属性设置\n\n**发现时间**: T+105min（代码审查阶段）\n\n**严重等级**: 🟡 中等（可能导致 XSS 攻击窃取 Session）\n\n**解决方案**:\n\n**修复前**:\n```javascript\nres.cookie('sessionId', session.token, {\n  maxAge: 24 * 60 * 60 * 1000 // 24小时\n});\n```\n\n**修复后**:\n```javascript\nres.cookie('sessionId', session.token, {\n  maxAge: 24 * 60 * 60 * 1000,\n  httpOnly: true,   // 防止 JavaScript 访问\n  secure: process.env.NODE_ENV === 'production',  // 仅 HTTPS 传输\n  sameSite: 'strict'  // 防 CSRF 攻击\n});\n```\n\n**影响范围**: 所有 Set-Cookie 操作（login 和 register 接口）\n\n**经验教训**:\n- ✅ 生产环境的 Cookie 必须设置 httpOnly、secure、sameSite\n- ⚠️ 安全相关配置应在开发初期就确定，而非后期补丁\n- 💡 建议使用 helmet 中间件自动添加安全头\n\n---\n\n## 📊 五、资源使用情况\n\n### 人力投入\n\n| 角色 | 投入时间 | 主要职责 |\n|------|---------|----------|\n| 后端开发工程师（本人） | 2 小时 | 全栈负责（设计+编码+测试） |\n\n### 技术栈使用\n\n| 类别 | 技术 | 用途 | 熟练度 |\n|------|------|------|--------|\n| 运行时 | Node.js 18 LTS | 服务端运行环境 | ★★★★★ |\n| 框架 | Express.js 4.x | HTTP 服务框架 | ★★★★☆ |\n| ORM | Sequelize 6.x | 数据库操作抽象 | ★★★☆☆ |\n| 数据库 | PostgreSQL 14 | 持久化存储 | ★★★★☆ |\n| 测试 | Jest 29.x | 单元测试框架 | ★★★★☆ |\n| 加密 | bcryptjs 2.x | 密码哈希 | ★★★☆☆ |\n\n### 工具与依赖\n\n**新增 npm 包**:\n- `bcryptjs@2.4.3`: 密码哈希\n- `express-session@1.17.3`: Session 中间件\n- `cookie-parser@1.4.6`: Cookie 解析\n- `helmet@7.1.0`: 安全头设置\n\n**开发工具**:\n- VS Code（主要编辑器）\n- Postman（API 测试）\n- pgAdmin（数据库管理）\n\n---\n\n## 📈 六、多维分析汇总\n\n### 6.1 目标达成度分析\n\n| 目标维度 | 目标值 | 实际值 | 达成率 | 评价 |\n|---------|-------|-------|--------|------|\n| 功能完整性 | 4 个核心功能 | 4 个完成 | 100% | ✅ 超额完成 |\n| 代码质量 | 覆盖率 >80% | 85% | 106% | ✅ 超额完成 |\n| 安全合规 | OWASP Top 10 防护 | 9/10 项覆盖 | 90% | ✅ 良好 |\n| 文档完整性 | API 文档 + 设计文档 | 2 份 | 100% | ✅ 完成 |\n| **综合评分** | -- | -- | **96.5%** | **优秀** |\n\n### 6.2 时间效能分析\n\n| 阶段 | 计划耗时 | 实际耗时 | 偏差 | 原因 |\n|------|---------|---------|------|------|\n| 技术设计 | 20 min | 25 min | +25% | 方案讨论较深入 |\n| 数据库设计 | 20 min | 25 min | +25% | 遇到 migration 顺序问题 |\n| 功能实现 | 45 min | 50 min | +11% | 正常波动 |\n| 测试优化 | 20 min | 20 min | 0% | 符合预期 |\n| **总计** | **105 min** | **120 min** | **+14%** | **可接受范围** |\n\n### 6.3 问题模式分析\n\n**问题分类统计**:\n\n| 类别 | 数量 | 占比 | 典型代表 |\n|------|------|------|----------|\n| 配置类问题 | 1 | 50% | Migration 顺序错误 |\n| 安全类问题 | 1 | 50% | Cookie 安全标志缺失 |\n| 逻辑 Bug | 0 | 0% | -- |\n| 性能问题 | 0 | 0% | -- |\n\n**模式识别**:\n- 🔍 配置问题集中在「环境搭建」阶段（T+40min 左右），属于新手常见错误\n- 🔍 安全问题通过「代码审查」发现，说明需要加强安全意识\n\n---\n\n## 💡 七、经验总结与方法论\n\n### 7.1 成功要素提炼\n\n1. **充分的前期调研**：花 25 分钟做技术方案设计看似浪费时间，实际上避免了后期返工\n2. **渐进式开发策略**：先跑通主流程（注册→登录→登出），再补充边缘情况\n3. **边开发边测试**：每完成一个功能立即编写测试，而不是最后集中补测\n4. **安全意识前置**：虽然 Cookie 安全问题是后期发现的，但在设计时就考虑了 bcrypt 加密\n\n### 7.2 最佳实践沉淀\n\n**实践 1: 数据库 Migration 命名规范**\n```
正确做法:
  20260409143000-create-users.js
  20260409143001-create-sessions.js

错误做法:
  create-users.js
  create-sessions.js  ← 可能先于 users 执行！
```

**实践 2: 认证中间件统一封装**
```javascript
// auth.middleware.js
const requireAuth = async (req, res, next) => {
  const token = req.cookies.sessionId;
  if (!token) return res.status(401).json({ error: '未登录' });
n  \n  const session = await Session.findOne({ where: { token } });
n  if (!session || session.expiresAt < new Date()) {
n    return res.status(401).json({ error: '会话已过期' });
n  }\n  \n  req.user = await User.findByPk(session.userId);\n  next();\n};\n```\n\n### 7.3 知识图谱更新\n\n**本次新增知识点**:\n- Session vs JWT 的权衡因素和适用场景\n- Sequelize Migration 的执行顺序机制\n- Cookie 安全三要素（HttpOnly / Secure / SameSite）\n- bcrypt cost factor 与安全性的关系曲线\n\n---\n\n## 🚀 八、改进建议与行动计划\n\n### 8.1 即时改进建议（P0 - 立即执行）\n\n| # | 建议 | 具体措施 | 预期收益 |\n|---|------|---------|----------|\n| A1 | 添加账户锁定机制 | 连续失败 5 次 → 锁定 15 分钟 | 防暴力破解 |\n| A2 | 引入 Rate Limiting | 同一 IP 每分钟最多 10 次登录尝试 | 防 DoS 攻击 |\n\n### 8.2 短期改进计划（P1 - 本周内）\n\n| # | 行动项 | 截止日期 | 负责人 | 状态 |\n|---|--------|---------|--------|------|\n| M1 | 补充 API 文档（Swagger/OpenAPI） | 04-12 | 本人 | ⬜ 待办 |\n| M2 | 编写集成测试（E2E 流程） | 04-13 | 本人 | ⬜ 待办 |\n| M3 | 代码 Review 并合并至主分支 | 04-11 | Team Lead | ⬜ 待办 |\n\n### 8.3 中长期规划（P2-P3）\n\n- **P2（本月内）**: 实现 OAuth2.0 第三方登录（Google/GitHub）\n- **P3（下季度）**: 迁移至 Redis Session Store 以支持水平扩展\n- **P3（下季度）**: 引入 MFA（多因素认证）支持高安全场景\n\n---\n\n## 📝 附录\n\n### 附录 A: 完整 API 端点列表\n\n见上文 2.1 阶段三中的表格\n\n### 附录 B: 数据库 Schema\n\n**users 表**:\n| 字段 | 类型 | 约束 | 说明 |\n|------|------|------|------|\n| id | INTEGER | PK, AUTO_INCREMENT | 主键 |\n| email | VARCHAR(255) | NOT NULL, UNIQUE | 邮箱（登录账号） |\n| password_hash | VARCHAR(255) | NOT NULL | bcrypt 哈希值 |\n| created_at | TIMESTAMP | DEFAULT NOW() | 创建时间 |\n| updated_at | TIMESTAMP | DEFAULT NOW() | 更新时间 |\n\n**sessions 表**:\n| 字段 | 类型 | 约束 | 说明 |\n|------|------|------|------|\n| id | INTEGER | PK, AUTO_INCREMENT | 主键 |\n| user_id | INTEGER | FK → users.id | 关联用户 |\n| token | VARCHAR(64) | NOT NULL, UNIQUE | Session 令牌 |\n| expires_at | TIMESTAMP | NOT NULL | 过期时间 |\n| created_at | TIMESTAMP | DEFAULT NOW() | 创建时间 |\n\n### 附录 C: 测试用例清单\n\n1. `test('注册成功 - 有效数据')` ✅\n2. `test('注册失败 - 邮箱已存在')` ✅\n3. `test('注册失败 - 密码太短')` ✅\n4. `test('登录成功 - 正确凭据')` ✅\n5. `test('登录失败 - 密码错误')` ✅\n6. `test('登录失败 - 用户不存在')` ✅\n7. `test('登出成功 - 已登录状态')` ✅\n8. `test('登出失败 - 未登录状态')` ✅\n9. `test('获取当前用户 - 有效 Session')` ✅\n10. `test('获取当前用户 - 过期 Session')` ✅\n11. `test('密码加密 - bcrypt 验证')` ✅\n12. `test('Session 过期 - 24小时后失效')` ✅\n\n---\n\n*报告结束*\n*生成时间: 2026-04-09 16:30:00 UTC*\n*任务执行总结报告生成器 v2.0*",

    "word_count": 12580,
    "chapter_count": 10,

    "metadata": {
      "task_name": "用户认证模块开发",
      "generation_duration": "3分12秒",
      "template_used": "standard",
      "quality_score": 94.5,
      "focus_dimensions": ["goal_achievement", "problem_patterns"],
      "language_style": "professional"
    }
  },

  "quality_check": {
    "completeness_rate": 0.92,
    "accuracy_confidence": 0.89,

    "information_gaps": [
      "部分决策依据未在对话中明确说明（如为何选择 Express 而非 Koa）",
      "团队协作信息缺失（单人任务，第七章内容简化呈现）"
    ],

    "warnings": []
  },

  "statistics": {
    "total_phases": 4,
    "total_decisions": 2,
    "total_problems": 2,
    "suggestions_count": 7
  },

  "file_info": {
    "saved_to": "./reports/用户认证模块开发_执行总结报告_20260409.md",
    "file_size_kb": 48.5
  }
}
```

### 关键点说明

- ✅ **`success: true`** 表示报告成功生成，可直接使用
- ✅ **`quality_score: 94.5`** 表示高质量（>90 为优秀，>80 为良好）
- ✅ **`completeness_rate: 0.92`** > 0.9 阈值，信息覆盖度优秀
- ✅ **报告包含完整的 10 章 Markdown 内容**（从基本信息到附录），结构清晰
- ✅ **文件已自动保存**到 `./reports/` 目录，大小 48.5KB
- ✅ **`statistics` 字段提供了量化摘要**：4个阶段、2个决策、2个问题、7条建议

### 变体说明

| 参数变化 | 预期影响 |
|---------|---------|
| `detail_level: "summary"` | 报告缩减至 2-3 页（仅第1章完整 + 第10章摘要），字数降至 ~800 |
| `detail_level: "detailed"` | 报告扩展至 20-30 页（每章深入展开 + 更多图表 + 完整代码），字数增至 ~15000 |
| `template_variant: "learning"` | 采用学习专用模板，第九章「经验方法」大幅扩充，增加知识图谱可视化 |
| `focus_dimensions: ["time_efficiency"]` | 第六章多维分析侧重时间效能维度，增加甘特图和时间瓶颈深度分析 |
| `excluded_chapters: [7]` | 移除第七章「团队协作」（单人任务时推荐此配置，减少冗余内容） |
| `output_format: "json"` | `report.content` 字段改为结构化 JSON 对象而非 Markdown 字符串，便于程序化处理 |

---

## 示例 2: Sprint 复盘最小化调用

### 场景描述

团队刚结束了一个为期 2 周（10 个工作日）的敏捷 Sprint 迭代。在这个 Sprint 中，团队共规划了 8 个用户故事，涉及前端界面优化、后端 API 开发和数据库迁移等多个工作项。项目经理希望快速生成一份复盘报告用于回顾会议。使用最简化的参数配置，完全依赖系统的智能默认值。

### 完整请求 JSON

```json
{
  "task_context": {
    "task_name": "Sprint 24 回顾"
  }
}
```

**请求特点**:
- ✅ **仅提供必填的 `task_name`**，其他所有参数使用默认值
- ✅ **零配置调用**，适合快速场景
- ⚠️ 系统将自动推断：
  - `task_type`: 从对话上下文检测为 `"management"`
  - `detail_level`: 默认 `"standard"`
  - `template_variant`: 默认 `"standard"`
  - `language_style`: 默认 `"professional"`
  - `focus_dimensions`: 默认全部维度
  - `save_to_file`: 默认 `true`

### 预期响应

```json
{
  "success": true,
  "report_id": "rpt-20260409-pm-002",
  "timestamp": "2026-04-09T17:00:00Z",
  "processing_time_ms": 168000,

  "report": {
    "title": "Sprint 24 回顾 - 执行总结报告",

    "content": "# Sprint 24 回顾 - 执行总结报告\n\n## 📋 基本信息\n\n| 属性 | 值 |\n|------|-----|\n| **任务名称** | Sprint 24 回顾 |\n| **任务类型** | 项目管理（Sprint 复盘） |\n| **Sprint 周期** | 2026-03-25 ~ 2026-04-07（10个工作日） |\n| **报告生成时间** | 2026-04-09 17:00 |\n| **质量评分** | 91.2 / 100 |\n\n---\n\n## 🎯 一、任务目标与背景\n\n### 1.1 Sprint 目标设定\n\n**Sprint 目标（Goal）**:\n完成电商平台的首页改版 V2.0，提升用户体验和转化率，同时推进订单系统的性能优化和用户画像数据的迁移工作。\n\n**规划的用户故事**（共 8 个，46 Story Points）：\n\n| # | 用户故事 | SP | 优先级 | 状态 |\n|---|---------|-----|--------|------|\n| US-1 | 作为买家，我希望看到全新的商品展示布局以快速找到心仪商品 | 8 | P0 | ✅ 完成 |\n| US-2 | 作为运营人员，我希望能够配置首页轮播图和推荐位 | 5 | P0 | ✅ 完成 |\n| US-3 | 作为买家，我希望搜索结果支持筛选和排序功能 | 8 | P0 | ✅ 完成 |\n| US-4 | 作为系统，订单查询 API 的 P99 响应时间应 <500ms | 5 | P0 | ✅ 完成 |\n| US-5 | 作为开发者，用户画像数据需要从 MySQL 迁移至 ClickHouse | 8 | P1 | ✅ 完成 |\n| US-6 | 作为买家，我希望商品详情页显示实时库存数量 | 3 | P1 | ✅ 完成 |\n| US-7 | 作为管理员，我希望看到用户行为数据分析报表 | 5 | P2 | ❌ 未完成（移入 Backlog） |\n| US-8 | 作为客服，我希望在工单系统中关联用户的订单历史 | 4 | P2 | ❌ 未完成（移入 Backlog） |\n\n### 1.2 目标调整记录\n\n| 时间点 | 变更类型 | 变更内容 | 影响 |\n|--------|---------|---------|------|\n| Day 3 | 需求变更 | US-7 的报表需求不明确 → PO 决定推迟至下一 Sprint | 减少 5 SP |\n| Day 6 | 阻塞解除 | US-5 的 ClickHouse 集成问题解决 | 恢复进度 |\n| Day 8 | 范围缩减 | US-8 因依赖外部系统而延期 | 减少 4 SP |\n\n### 1.3 最终成果\n\n**完成的用户故事**: 6 / 8（75%）\n**完成的 Story Points**: 42 / 46（91.3%）\n**Velocity**: 42 SP（较上 Sprint 的 36 SP 提升 16.7%）\n\n**核心交付物**:\n- ✅ 电商首页改版 V2.0（前端）\n- ✅ 订单查询 API 性能优化（后端，P99 从 1200ms→180ms）\n- ✅ 用户画像数据迁移至 ClickHouse（数据工程）\n- ✅ 商品详情页库存显示（前后端联调）\n\n---\n\n## 🔍 二、执行过程详解\n\n### 2.1 Sprint 各阶段概览\n\n#### Sprint Planning（Day 1 上午）\n- **时长**: 2.5 小时\n- **参与人**: 全体成员 + Product Owner\n- **产出**: Sprint Backlog 确定，任务拆分完毕，初步风险评估\n\n#### 开发执行 - 第一周（Day 1 下午 ~ Day 5）\n- **重点**: US-1/US-2/US-3（首页改版核心功能）\n- **进展**: 前端团队完成 UI 开发，后端完成对应 API\n- **阻塞事件**: US-2 的轮播图配置功能因设计稿延迟而推迟启动（Day 3）\n\n#### 开发执行 - 第二周（Day 8 ~ Day 12）\n- **重点**: US-4（API 性能优化）+ US-5（数据迁移）\n- **挑战**: 支付网关临时通知接口升级（Day 8），占用约 16 工时\n- **突破**: 订单 API 通过 Redis 缓存层实现 85% 性能提升\n\n#### Code Review & 测试（穿插进行）\n- **MR 总数**: 18 个\n- **Review 通过率**: 94%（17/18）\n- **平均 Review 轮数**: 2.1 轮/MR\n\n#### Sprint Review & Retro（Day 13 上午）\n- **Demo 演示**: 4 个核心功能演示\n- **Retro 讨论**: 识别 3 个改进机会（详见第十章）\n\n---\n\n## 🧠 三、关键决策分析\n\n### 决策 D1：是否接受支付网关接口变更的紧急插入\n\n**决策时刻**: Day 8 上午（Sprint 执行中期）\n\n**背景**: 支付服务商临时通知将在 3 天后停用旧版 API，要求紧急升级\n\n**备选方案**:\n| 方案 | 做法 | 优点 | 缺点 |\n|------|------|------|------|\n| A: 立即处理 | 暂停当前任务，优先升级 | 避免业务中断 | 打乱 Sprint 计划 |\n| B: 延迟处理 | 继续当前任务，利用缓冲时间 | 保持计划稳定 | 风险较高 |\n\n**最终选择**: **方案 A - 立即处理**\n\n**理由**: 业务连续性优先于计划稳定性，且预估影响可控（16 工时）\n\n**事后评估**: ✅ 正确。成功避免业务中断，但导致 US-8 延期。\n\n---\n\n### 决策 D2：ClickHouse 迁移方案选择（全量 vs 增量）\n\n**决策时刻**: Day 6\n\n**最终选择**: **增量双写方案**（先双写 → 验证一致 → 切读流量 → 停旧写入）\n\n**理由**: 数据零丢失，回滚风险低，但对开发资源消耗较大\n\n---\n\n## 🐛 四、问题解决记录\n\n### 问题 I1：支付网关接口升级导致的阻塞\n\n**问题描述**: Day 8 收到紧急通知，旧版 API 将在 72 小时后停用\n\n**解决过程**:\n1. 紧急评估影响范围（2 个 API 端点）\n2. 协调资源（抽调 1 名后端开发全职处理）\n3. 并行开发新接口适配层（耗时 12 工时）\n4. 预发布环境验证（4 工时）\n5. 灰度上线（Day 10 晚上，10% 流量）\n6. 全量切换（Day 11 凌晨）\n\n**总耗时**: 16 工时（超出预期 4 工时，因文档不全）\n\n**经验教训**:\n- ⚠️ 第三方服务的变更通知机制需改进（应提前 2 周通知）\n- ✅ 紧急响应流程有效（从接到通知到方案确定仅 2 小时）\n\n---\n\n### 问题 I2：UI 设计稿反复修改导致前端延迟\n\n**问题描述**: 首页改版的设计方案经过 4 轮评审才定稿\n\n**根因**: 需求方对视觉效果的期望不一致，缺乏明确的验收标准\n\n**影响**: 前端开发启动时间推迟 3 天（Day 3 → Day 6）\n\n**改进建议**: 建立 Design Review Checklist，首轮评审后冻结 70% 的设计元素\n\n---\n\n## 👥 五、团队协作分析\n\n### 5.1 协作概况\n\n- **参与人员**:\n  - 张伟（Tech Lead / 后端开发）\n  - 李娜（全栈开发）\n  - 王强（前端开发）\n  - 刘洋（QA 工程师）\n  - 陈思（产品经理）\n  - 小王（新入职前端开发，第 2 周）\n\n- **协作周期**: 2 周（10 个工作日）\n- **沟通渠道**: 每日站会（Slack 视频）、企业微信、Confluence、GitLab MR\n\n### 5.2 协作效能评估\n\n| 维度 | 评分 | 评价 |\n|------|------|------|\n| 沟通效率 | 4/5 | 及时准确，跨部门协调偶有延误 |\n| 分工合理性 | 4/5 | 基本合理，小王任务梯度不够平滑 |\n| 协同效果 | 3/5 | 整体良好，阻塞事件响应速度待提升 |\n| **综合得分** | **11/15** | **良好，有明显优化空间** |\n\n### 5.3 协作亮点\n\n1. **导师制见效**: 张伟指导小王，使其独立完成 2 个 US 且代码评级 A\n2. **站会效率提升**: 尝试「看板驱动式站会」，会议时长从 25 分钟缩短至 12 分钟\n3. **跨角色协作顺畅**: 李娜与刘洋联合编写集成测试，提前发现 3 个边界 Bug\n\n### 5.4 待改进项\n\n1. **阻塞升级机制不明确** → 建议建立分级响应流程（P0: 30分钟内升级）\n2. **需求变更控制松散** → 建议严格执行中期变更 Impact Analysis\n3. **知识分享不足** → 建议每周五 Tech Talk（首期由李娜分享缓存设计）\n\n---\n\n## 📊 六、多维分析汇总\n\n### 6.1 目标达成度\n\n| 维度 | 目标 | 实际 | 达成率 |\n|------|------|------|--------|\n| US 完成数 | 8 | 6 | 75% |\n| SP 完成率 | 100% | 91.3% | 良好 |\n| Velocity | 36 SP | 42 SP | ↑16.7% ✅ |\n| 代码质量（CR 通过率） | >90% | 94% | 优秀 ✅ |\n| Bug 逃逸率 | <5% | 2个（P1: 0） | 良好 ✅ |\n\n### 6.2 时间效能\n\n| 阶段 | 计划 | 实际 | 偏差 |\n|------|------|------|------|\n| Sprint Planning | 2h | 2.5h | +25% |\n| 开发执行（第一周） | 32h | 32h | 0% |\n| 开发执行（第二周） | 35h | 39h | +11%（支付接口占用） |\n| Code Review & 测试 | 8h | 8h | 0% |\n| Sprint Review & Retro | 3h | 3h | 0% |\n| 应急处理 | 0h | 2h | -- |\n| **总计** | **81h** | **86.5h** | **+6.8%** |\n\n### 6.3 问题模式分析\n\n| 类别 | 数量 | 占比 |\n|------|------|------|\n| 外部依赖阻塞 | 2 | 50%（支付网关 + 设计稿） |\n| 需求变更 | 1 | 25% |\n| 技术难题 | 1 | 25%（ClickHouse 集成） |\n\n**模式洞察**: 外部依赖是本次 Sprint 的主要风险来源（占比 50%）\n\n---\n\n## 💡 七、经验总结与方法论\n\n### 7.1 成功要素\n\n1. **Velocity 持续增长**: 连续 3 个 Sprint 提升（30→36→42 SP），团队磨合渐入佳境\n2. **新人融入高效**: 小王在第 2 周即有实质产出，Onboarding 流程值得推广\n3. **技术债务主动偿还**: 利用缓冲时间重构支付模块，删除 1500 行冗余代码\n\n### 7.2 方法论提炼\n\n**方法论 1: 紧急变更响应 SOP**\n```
Step 1: 接到通知 → 10min 内评估影响范围和紧迫性\nStep 2: Tech Lead 决策 → 接受/拒绝/协商延期\nStep 3: 资源协调 → 从 Buffer 或低优先级任务中抽调人力\nStep 4: 方案制定 → 制定最小可行方案（MVP）\nStep 5: 快速实施 → 并行开发和验证\nStep 6: 灰度发布 → 先小流量验证再全量\nStep 7: 复盘总结 → 更新应急响应手册\n```\n\n**方法论 2: 设计评审提效方法**\n- 首轮评审聚焦「信息架构」和「交互逻辑」，冻结 70% 元素\n- 二轮评审聚焦「视觉细节」，限制修改次数 ≤3 轮\n- 使用 Design Token 系统确保一致性，减少反复沟通\n\n---\n\n## 🚀 八、改进建议与行动计划\n\n### 8.1 高优先级改进（P0 - 下个 Sprint 立即执行）\n\n| # | 改进项 | 行动措施 | 责任人 | 截止时间 |\n|---|--------|---------|--------|----------|\n| A1 | 建立阻塞分级响应流程 | P0 阻塞 30 分钟内升级至 Tech Lead | 张伟 | Sprint 25 Planning 前 |\n| A2 | 强化需求变更控制 | Sprint 中期任何变更须经 PO Impact Analysis | 陈思 | 立即生效 |\n\n### 8.2 中优先级改进（P1 - 本月内）\n\n| # | 改进项 | 行动措施 | 预期收益 |\n|---|--------|---------|----------|\n| M1 | 优化 Sprint Planning 效率 | 会前准备 AC 和技术预审，控制在 2h 内 | 每次节省 30min |\n| M2 | 启动每周 Tech Talk | 周五下午 1 小时技术分享 | 促进知识传播 |\n| M3 | 引入 CI/CD 自动化部署 | Jenkins Pipeline 将部署从 15min 缩减至 3min | 长期累积效益显著 |\n\n### 8.3 长期改进方向（P2-P3）\n\n- **P2**: 建立第三方服务监控仪表盘，提前感知 API 变更风险\n- **P3**: 探索 Design System 组件库，减少 UI 反复评审成本\n- **P3**: 完善 Onboarding 新人培训体系（标准化前 2 周的学习路径）\n\n---\n\n*报告结束*\n*生成时间: 2026-04-09 17:00:00 UTC*\n*任务执行总结报告生成器 v2.0*",

    "word_count": 9876,
    "chapter_count": 10,

    "metadata": {
      "template_used": "standard",
      "quality_score": 91.2,
      "auto_detected_type": "management"
    }
  },

  "quality_check": {
    "completeness_rate": 0.88,
    "accuracy_confidence": 0.85,

    "information_gaps": [],

    "warnings": [
      {
        "code": "W001",
        "message": "团队协作信息有限，第七章内容基于对话推断，可能不完全准确",
        "category": "data_inference",
        "severity": "low",
        "affected_chapters": [7]
      },
      {
        "code": "W002",
        "message": "部分时间节点为估算值（精确度 ±15%），基于消息间隔推断",
        "category": "time_estimation",
        "severity": "low",
        "affected_chapters": [2, 6]
      }
    ]
  },

  "statistics": {
    "total_phases": 3,
    "total_decisions": 5,
    "total_problems": 3,
    "suggestions_count": 7
  },

  "file_info": {
    "saved_to": "./reports/Sprint_24_回顾_执行总结报告_20260409.md",
    "file_size_kb": 38.2
  }
}
```

### 关键点说明

- ⚠️ **最小参数也能成功生成报告** — 仅 `task_name` 即可触发完整流程
- ⚠️ **`warnings` 数组非空** — 提示数据不充分的部分（团队协作、时间估算），但不影响整体可用性
- ⚠️ **`quality_score: 91.2`** — 仍然达到优秀级别（>90），说明默认配置的质量保障有效
- 💡 **系统智能推断** — 自动检测到 `task_type` 为项目管理类型（`management`），并选用合适的分析侧重点
- 💡 **默认使用 `standard` 模板和 `professional` 风格** — 适用于大多数正式场合

### 变体说明

| 参数变化 | 预期影响 |
|---------|---------|
| 添加 `"task_type": "management"` | 显式指定类型（本例中系统已自动检测，效果相同） |
| `"detail_level": "detailed"` | 报告扩展至 20+ 页，增加每个 US 的详细拆解、每个 MR 的 Review 记录、详细的燃尽图数据 |
| `"focus_dimensions": ["collaboration"]` | 第五章团队协作章节大幅扩充，增加 RACI 矩阵、沟通频次热力图、协作网络图 |
| `"included_chapters": [1, 2, 5, 8, 10]` | 仅保留核心章节（概览、目标、协作、经验、行动），篇幅缩减至 ~4000 字，适合快速汇报 |
| `"output_config": { "save_to_file": false }` | 不保存文件，仅在内存中返回报告内容（适合预览或二次处理场景） |

---

## 示例 3: 参数验证错误（异常场景）

### 场景描述

用户在一次批量调用或集成测试场景中，提供了多个错误的参数组合：缺少必填参数 `task_name`、使用了无效的枚举值 `detail_level`、章节编号超出合法范围（1-10）、以及试图排除所有核心章节（导致无法生成有效报告）。系统应在参数验证阶段（Step 1）拦截这些错误并返回结构化的错误信息。

### 完整请求 JSON

```json
{
  "task_context": {},
  "generation_options": {
    "detail_level": "invalid_value",
    "template_variant": "detailed",
    "included_chapters": [1, 2, 99],
    "excluded_chapters": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
  },
  "output_config": {
    "save_to_file": true
  }
}
```

**错误清单**:

| # | 参数 | 错误类型 | 错误说明 |
|---|------|---------|---------|
| 1 | `task_context.task_name` | **E001 - 缺少必填参数** | `task_context` 为空对象，缺少 `task_name` 字段 |
| 2 | `generation_options.detail_level` | **E002 - 无效枚举值** | 值为 `"invalid_value"`，不在 `[summary, standard, detailed]` 中 |
| 3 | `generation_options.included_chapters[2]` | **E003 - 参数值越界** | 值为 `99`，超出合法范围 `[1, 10]` |
| 4 | `generation_options.excluded_chapters` | **E005 - 章节组合无效** | 排除了全部 10 个章节，至少需保留第 1、9、10 章 |

### 预期错误响应

```json
{
  "success": false,

  "error": {
    "code": "E001",
    "name": "MissingRequiredParameter",
    "message": "缺少必填参数: task_name",
    "category": "validation",
    "severity": "error",
    "http_status": 400,
    "timestamp": "2026-04-09T16:35:00Z",

    "details": [
      {
        "parameter": "task_context.task_name",
        "constraint": "required: true, type: string, min_length: 2, max_length: 200",
        "actual_value": null,
        "location": "task_context",
        "suggestion": "请在 task_context 中添加任务名称字符串（2-200字符）"
      },
      {
        "parameter": "generation_options.detail_level",
        "constraint": "enum: [\"summary\", \"standard\", \"detailed\"]",
        "actual_value": "invalid_value",
        "valid_options": ["summary", "standard", "detailed"],
        "suggestion": "请使用 summary（摘要）/ standard（标准）/ detailed（详细）之一"
      },
      {
        "parameter": "generation_options.included_chapters[2]",
        "constraint": "items: integer in [1, 10]",
        "actual_value": 99,
        "invalid_values": [99],
        "suggestion": "章节编号必须在 1 到 10 之间"
      },
      {
        "parameter": "generation_options.excluded_chapters",
        "constraint": "不能排除所有核心章节（至少保留第 1、9、10 章）",
        "actual_value": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "suggestion": "请确保 excluded_chapters 不包含 [1, 9, 10]，或清空该数组以包含全部章节"
      }
    ],

    "recovery_actions": [
      {
        "action": "补充 task_name 参数",
        "description": "在 task_context 中添加任务名称字符串",
        "auto_recoverable": true,
        "priority": "P0",
        "example": "{\"task_context\": {\"task_name\": \"Sprint 24 回顾\"}}",
        "example_url": null
      },
      {
        "action": "修正 detail_level 值",
        "description": "使用 summary / standard / detailed 三个有效值之一",
        "auto_recoverable": true,
        "priority": "P0",
        "example": "\"detail_level\": \"standard\""
      },
      {
        "action": "修正 included_chapters 范围",
        "description": "确保所有章节编号在 1-10 之间，移除无效值 99",
        "auto_recoverable": true,
        "priority": "P1",
        "example": "\"included_chapters\": [1, 2]"
      },
      {
        "action": "修正 excluded_chapters 组合",
        "description": "至少保留第 1、9、10 章不被排除，或直接移除 excluded_chapters 参数",
        "auto_recoverable": true,
        "priority": "P1",
        "example": "\"excluded_chapters\": [3, 4, 6, 7]"
      }
    ],

    "hint": "最快的修复方式是仅提供 task_name，其他参数将使用合理的默认值。最小可用请求：{\"task_context\": {\"task_name\": \"您的任务名称\"}}",

    "documentation_reference": {
      "parameter_spec": "references/api-reference.md#参数定义",
      "error_codes": "references/error-codes.md#E001-E005",
      "quick_example": "references/examples-v2.md#示例-2"
    }
  },

  "request_snapshot": {
    "received_at": "2026-04-09T16:34:55Z",
    "raw_request_size_bytes": 187,
    "validation_failed_at_step": 1,
    "total_errors_found": 4,
    "errors_by_severity": {
      "error": 3,
      "warning": 1
    }
  }
}
```

### 关键点说明

- ❌ **`success: false`** — 表示执行失败，未生成任何报告
- 🔴 **`severity: "error"`** — 这是 Error 级别，会**终止执行**（不同于 Warning 级别的降级继续）
- 🔴 **`error.code: "E001"`** — 显示的是**第一个致命错误**（缺少必填参数），这是最高优先级的阻断性问题
- 📋 **`details` 数组列出所有检测到的错误**（共 4 个），即使第一个错误就会终止执行，系统仍然会一次性返回所有问题以便用户批量修复
- 💡 **`recovery_actions` 提供具体的修复步骤**：
  - 每个错误都有对应的恢复动作
  - `auto_recoverable: true` 表示这些错误都可以通过修改输入来修复（非系统性故障）
  - `priority` 字段标注修复优先级（P0 为必须修复，P1 为建议修复）
  - `example` 字段提供了可直接复制粘贴的正确用法示例
- ✅ **`hint` 字段** — 给出了最快的修复路径（最小可用请求）
- 📖 **`documentation_reference`** — 指向相关文档位置，方便深入学习

### 错误处理流程示意

```
接收请求
    ↓
[Step 1: 参数解析与验证]
    ↓
检测到 E001: task_name 缺失 → severity=error → 终止标记 ✓
检测到 E002: detail_level 无效 → severity=error → 记录
检测到 E003: chapters[2]=99 越界 → severity=warning → 记录
检测到 E005: 排除所有章节 → severity=error → 记录
    ↓
汇总: 3 errors + 1 warning
    ↓
[构造错误响应]
    ├── error.code = "E001" (最高优先级)
    ├── error.details[] = 全部 4 个错误详情
    ├── error.recovery_actions[] = 4 个修复建议
    └── error.hint = 最快修复提示
    ↓
返回 HTTP 400 + JSON 错误响应
    ↓
❌ 不进入 Step 2-7（执行终止）
```

### 变体说明

| 错误场景 | 预期的 error.code | severity | 是否终止 |
|---------|------------------|----------|---------|
| 仅缺少 `task_name`（其他参数正确） | `E001` | error | ✅ 终止 |
| `task_name` 存在但为空字符串 `""` | `E002` (InvalidParameterType) | error | ✅ 终止 |
| `detail_level` 无效（其余正确） | `E002` | error | ✅ 终止 |
| `included_chapters` 含 99（其余正确） | `E003` | warning | ⚠️ 不终止，过滤无效值后继续 |
| `excluded_chapters` 排除 1,9,10（其余正确） | `E005` | error | ✅ 终止 |
| 同时出现 E001 + E010（数据不足） | `E001` | error | ✅ 终止（参数错误优先于数据不足） |

---

## 示例 4: 数据不足时的降级执行

### 场景描述

用户想要对一个快速 Bug 修复任务（"登录页面样式错乱"）生成详细级别的报告。然而，该任务的对话历史较短（可能只有 10-20 条消息），信息密度不足以支撑 `detailed` 级别的完整报告（需要大量的决策记录、问题排查细节、协作信息等）。系统应该**降级执行**——将详细程度从 `detailed` 降级为 `standard`，并在响应中明确发出警告，告知用户哪些章节的内容置信度较低。

### 完整请求 JSON

```json
{
  "task_context": {
    "task_name": "快速Bug修复: 登录页面样式错乱",
    "task_type": "development"
  },
  "generation_options": {
    "detail_level": "detailed"
  },
  "output_config": {
    "save_to_file": true,
    "include_metadata": true
  }
}
```

**请求特点**:
- ✅ `task_name` 和 `task_type` 正确填写
- ⚠️ 请求 `detail_level: "detailed"`（高详细程度）
- 💭 **隐含风险**: 对话历史较短，可能无法支撑 detailed 级别的信息量需求

### 预期响应（带警告的成功）

```json
{
  "success": true,
  "report_id": "rpt-20260409-deg-003",
  "timestamp": "2026-04-09T16:45:00Z",
  "processing_time_ms": 125000,

  "degraded": true,
  "degradation_info": {
    "original_detail_level": "detailed",
    "effective_detail_level": "standard",
    "reason": "数据不足以支持 detailed 级别的完整报告（信息覆盖率 68%，阈值 80%）",
    "degradation_decision_made_at": "step_3_quality_check",
    "affected_capabilities": [
      "深度决策分析（第四章内容粒度降低）",
      "详尽问题排查过程（第五章省略次要分支）",
      "完整时间线重建（第二章使用估算值）",
      "团队协作矩阵（第七章简化或跳过）"
    ],
    "user_can_prevent_degradation": true,
    "prevention_hint": "如在任务执行过程中保持更详细的对话记录（如说明思考过程、列举备选方案），可避免降级"
  },

  "report": {
    "title": "快速Bug修复: 登录页面样式错乱 - 执行总结报告",

    "content": "# 快速Bug修复: 登录页面样式错乱 - 执行总结报告\n\n> ⚠️ **信息有限声明**: 本报告基于可用数据生成，部分章节内容因信息不足进行了简化或推断。标注「⚠️ 信息有限」的段落置信度较低，建议手动补充。\n\n## 📋 基本信息\n\n| 属性 | 值 |\n|------|-----|\n| **任务名称** | 快速Bug修复: 登录页面样式错乱 |\n| **任务类型** | 软件开发（Bug 修复） |\n| **执行时间** | 约 25 分钟（⚠️ 基于消息间隔估算，精度 ±20%） |\n| **报告生成时间** | 2026-04-09 16:45 |\n| **质量评分** | 78.5 / 100（⚠️ 降级执行） |\n| **生成模式** | degraded（原请求 detailed → 实际 standard） |\n\n---\n\n## 🎯 一、任务目标与背景\n\n### 1.1 问题描述\n\n**Bug 现象**:\n- 登录页面的表单布局在特定屏幕宽度下出现错位\n- 「用户名」输入框和「密码」输入框重叠\n- 「登录」按钮被挤出可视区域\n\n**复现条件**:\n- 浏览器窗口宽度在 768px - 1024px 之间（平板尺寸）\n- 页面首次加载或窗口 resize 时触发\n\n**严重程度**: 🟡 P2（影响平板用户，但不阻塞核心功能）\n\n### 1.2 修复目标\n\n- [x] 修复表单布局错位问题\n- [x] 确保在 320px - 1920px 全响应式范围内正常显示\n- [x] 不引入新的样式回归问题\n\n### 1.3 最终成果\n\n✅ **已修复**: CSS Flexbox 布局参数调整（`flex-wrap` + `max-width` 约束）\n✅ **验证通过**: Chrome DevTools 响应式测试 + 3 种设备模拟\n✅ **代码变更**: 1 个文件（`Login.css`），变更 15 行\n\n---\n\n## 🔍 二、执行过程（⚠️ 信息有限）\n\n### 2.1 修复步骤（基于可用信息重建）\n\n| 步骤 | 操作 | 耗时估算 | 备注 |\n|------|------|---------|------|\n| 1 | 复现问题（Chrome DevTools 设备模拟） | ~3 min | 确认在 iPad 尺寸下可复现 |\n| 2 | 定位根因（检查 DOM 结构和 CSS 规则） | ~8 min | 发现 `flex-shrink` 导致输入框压缩 |\n| 3 | 实施修复（调整 flex 参数） | ~5 min | 添加 `flex: 1 1 300px` 和 `max-width` |\n| 4 | 验证修复（多断点测试） | ~7 min | 测试 320/768/1024/1440/1920 五个断点 |\n| 5 | 提交代码（Git commit） | ~2 min | Commit message: \"fix: resolve login form layout overlap on tablet viewport\" |\n\n**总耗时**: 约 25 分钟（⚠️ 估算值，实际可能有偏差）\n\n---\n\n## 🧠 三、关键决策分析（⚠️ 信息有限，以下内容基于可用数据推断）\n\n### 决策 D1：CSS 布局方案选择\n\n**决策背景**: 发现表单错位后，需要在多种 CSS 布局方案中选择修复策略\n\n**备选方案**（⚠️ 对话中未明确讨论，根据代码变更推断）:\n\n| 方案 | 做法 | 优点 | 缺点 |\n|------|------|------|------|\n| A: 调整 Flexbox 参数 | 修改 `flex-grow/shrink/basis` | 改动小，兼容性好 | 可能影响其他断点 |\n| B: 改用 Grid 布局 | 重构为 CSS Grid | 更精细的控制 | 改动大，可能引入回归 |\n| C: 添加 Media Query | 针对平板断点特殊处理 | 精准修复 | 增加代码复杂度 |\n\n**最终选择（推断）**: **方案 A - 调整 Flexbox 参数**\n\n**推断依据**: 代码变更仅涉及 flex 相关属性，未引入 grid 或 media query\n\n**事后评估**: ⚠️ 无法确认（对话中缺少决策过程的讨论记录）\n\n---\n\n## 🐛 四、问题解决记录\n\n### 问题 I1：登录页面表单布局在平板尺寸下错位\n\n**问题描述**:\n\n**现象**:\n- 登录表单的「用户名」和「密码」输入框在 768px-1024px 宽度下重叠\n- 「登录」按钮溢出到屏幕右外侧不可见区域\n\n**重现条件**:\n- 浏览器宽度 ∈ [768px, 1024px]\n- 页面包含登录表单组件\n\n**发生时间**: 任务开始时（Bug 报告/发现时刻）\n\n**排查过程**（⚠️ 详细对话记录不足，以下为基于代码变更的关键节点重建）:\n\n**T+0min ~ T+3min** - 问题复现与确认\n- 使用 Chrome DevTools 切换至 iPad Pro 模拟（1024x1366）\n- 确认表单布局异常：两个 input 元素垂直间距为负值\n- 截图留存作为修复前基线\n\n**T+3min ~ T+11min** - 根因定位\n- 检查 `.login-form` 容器的 CSS：使用了 `display: flex; flex-direction: column`\n- 检查 `.form-input` 的 CSS：设置了 `flex: 1` 但没有 `min-width` 约束\n- **根因确认**: 当容器宽度不足以容纳两个 `flex: 1` 的子元素时，`flex-shrink` 默认值为 1，导致输入框被压缩重叠\n\n**T+11min ~ T+16min** - 实施修复\n\n**代码变更** (`src/styles/Login.css`):\n\n```css\n/* 修复前 */\n.login-form input {\n  flex: 1;\n  padding: 12px 16px;\n}\n\n/* 修复后 */\n.login-form input {\n  flex: 1 1 300px;  /* basis=300px, 不允许 shrink 低于 300px */\n  max-width: 100%;   /* 防止溢出容器 */\n  padding: 12px 16px;\n}\n\n/* 新增：表单容器约束 */\n.login-form {\n  flex-wrap: wrap;       /* 允许换行 */\n  gap: 16px;             /* 统一间距替代 margin */\n  width: 100%;\n  max-width: 480px;      /* 限制最大宽度 */\n  margin: 0 auto;        /* 居中 */\n}\n```\n\n**T+16min ~ T+23min** - 验证测试\n- 测试 5 个断点：320px（手机竖屏）、768px（平板）、1024px（平板横屏）、1440px（笔记本）、1920px（桌面）\n- 确认所有断点下表单布局正常\n- 检查相邻页面（注册页、忘记密码页）是否存在类似问题 → 未发现\n\n**T+23min ~ T+25min** - 提交与关闭\n- Git commit: `fix(login): resolve form layout overlap on tablet viewport`\n- 关联 Issue #1234\n- 通知 QA 回归验证\n\n**解决统计**:\n- 排查耗时：~11 min\n- 解决耗时：~5 min\n- 验证耗时：~7 min\n- 总耗时：~23 min（⚠️ 估算值）\n\n**经验教训**:\n\n### ✅ 正面经验\n- 响应式问题的排查应从「设备模拟」开始，而非盲目修改 CSS\n- `flex-basis` + `max-width` 组合比单纯的 `flex-shrink: 0` 更健壮\n- 修复后务必测试相邻页面，防止同类问题遗漏\n\n### ⚠️ 注意事项\n- Flexbox 布局的默认 `flex-shrink: 1` 行为容易被忽视，建议显式设置\n- 表单组件应有明确的「最小支持宽度」设计规范\n\n### 📌 知识要点\n- 掌握了 Flexbox `flex` 属性的三元语法：`flex: grow shrink basis`\n- 理解了 `flex-wrap` + `gap` 组合在响应式表单中的应用\n- 学会了使用 Chrome DevTools 的设备模拟进行高效调试\n\n---\n\n## 📊 五、资源使用情况（⚠️ 信息有限）\n\n### 人力投入\n\n| 角色 | 投入时间 | 主要职责 |\n|------|---------|----------|\n| 前端开发工程师（本人） | ~25 min | 独立完成排查、修复、验证 |\n\n### 技术栈\n\n| 类别 | 技术 | 用途 |\n|------|------|------|\n| 调试工具 | Chrome DevTools | 设备模拟、DOM 检查、样式调试 |\n| 版本控制 | Git | 代码提交 |\n| 语言 | CSS3 | 样式修复 |\n| 框架 | React（推断） | 登录页面组件（基于文件路径推断） |\n\n---\n\n## 📈 六、多维分析汇总\n\n### 6.1 目标达成度\n\n| 目标 | 状态 | 说明 |\n|------|------|------|\n| 修复布局错位 | ✅ 完成 | 表单在所有目标断点下正常显示 |\n| 全响应式覆盖 | ✅ 完成 | 测试 320-1920px 范围 |\n| 无回归问题 | ✅ 完成 | 相邻页面未受影响 |\n| **综合评分** | **100%** | **全部目标达成** |\n\n### 6.2 时间效能\n\n| 阶段 | 耗时 | 占比 |\n|------|------|------|\n| 问题复现 | 3 min | 12% |\n| 根因定位 | 8 min | 32% |\n| 修复实施 | 5 min | 20% |\n| 验证测试 | 7 min | 28% |\n| 提交关闭 | 2 min | 8% |\n| **总计** | **~25 min** | **100%** |\n\n> ⚠️ 以上时间为基于消息间隔的估算值，可能与实际 wall-clock time 有 ±20% 偏差\n\n---\n\n## 💡 七、经验总结与方法论\n\n### 7.1 成功要素\n\n1. **快速复现优先**: 花 3 分钟确认问题可复现，避免了盲目修改\n2. **根因导向**: 定位到 `flex-shrink` 默认行为的根因，而非打补丁式的表面修复\n3. **全面验证**: 测试 5 个断点 + 检查相邻页面，确保修复彻底\n\n### 7.2 方法论提炼\n\n**CSS 响应式 Bug 排查 SOP**:\n```\nStep 1: 复现（DevTools 设备模拟）\nStep 2: 检查布局模型（Flexbox/Grid/Float/Block）\nStep 3: 定位冲突 CSS 规则（Computed Styles 面板）\nStep 4: 实施 minimal fix（最小改动原则）\nStep 5: 多断点验证（至少 5 个关键断点）\nStep 6: 回归检查（相邻/相似页面）\n```\n\n---\n\n## 🚀 八、改进建议与行动计划\n\n### 8.1 防范性建议\n\n| # | 建议 | 具体措施 | 预期收益 |\n|---|------|---------|----------|\n| A1 | 建立响应式设计规范 | 明确各组件的最小/最大宽度和断点行为 | 减少 60% 的响应式 Bug |\n| A2 | 增加 CI 中的视觉回归测试 | 使用 Percy/Screenshot-GitHub-Action | 自动捕获布局偏移 |\n\n### 8.2 个人成长建议\n\n- 深入学习 CSS Flexbox 和 Grid 的完整属性体系（尤其是 `flex` 简写属性的细节）\n- 建立个人 CSS Bug 修复知识库，积累常见的响应式问题模式\n\n---\n\n*报告结束*\n*生成时间: 2026-04-09 16:45:00 UTC*\n*生成模式: DEGRADED（原请求 detailed → 实际 standard）*\n*任务执行总结报告生成器 v2.0*",

    "word_count": 6850,
    "chapter_count": 10,

    "metadata": {
      "quality_score": 78.5,
      "generation_mode": "degraded",
      "original_requested_level": "detailed",
      "effective_generated_level": "standard",
      "information_coverage_rate": 0.68
    }
  },

  "quality_check": {
    "completeness_rate": 0.72,
    "accuracy_confidence": 0.70,

    "information_gaps": [
      {
        "category": "decision_records",
        "coverage_rate": 0.45,
        "threshold": 0.70,
        "impact": "决策记录信息覆盖率仅 45%（阈值 70%）→ 第四章「关键决策分析」章节内容可能不完整，部分决策依据为推断",
        "affected_chapters": [4],
        "user_action_suggested": "如需更完整的决策分析，可在对话中补充当时的考虑因素和备选方案"
      },
      {
        "category": "resource_allocation",
        "coverage_rate": 0.30,
        "threshold": 0.60,
        "impact": "资源配置信息缺失（覆盖率 30%）→ 第六章「资源使用情况」将简化呈现，部分字段标注「待补充」",
        "affected_chapters": [6],
        "user_action_suggested": "可手动编辑报告补充具体的技术栈和工具使用情况"
      },
      {
        "category": "timeline_precision",
        "coverage_rate": 0.55,
        "threshold": 0.75,
        "impact": "时间节点信息精度较低（基于消息间隔估算）→ 时间偏差约 ±20%，第二章执行过程的时间数据为近似值",
        "affected_chapters": [2],
        "user_action_suggested": "如需精确时间线，可查阅 Git 提交记录获取准确时间戳"
      }
    ],

    "warnings": [
      {
        "code": "E010",
        "name": "InsufficientDataWarning",
        "message": "InsufficientDataWarning: 决策记录信息覆盖率仅 45%（阈值 70%）",
        "category": "data_warning",
        "severity": "warning",
        "timestamp": "2026-04-09T16:44:30Z",
        "impact": "第四章「关键决策分析」章节将标注「⚠️ 信息有限，以下内容基于可用数据推断」，决策依据和备选方案对比可能不完整",
        "affected_chapters": [4],
        "mitigation_applied": "降低了该章节的分析深度，从「逐项对比备选方案」降级为「基于代码变更反向推断决策」"
      },
      {
        "code": "E010",
        "name": "InsufficientDataWarning",
        "message": "InsufficientDataWarning: 资源配置信息缺失（覆盖率 30%）",
        "category": "data_warning",
        "severity": "warning",
        "timestamp": "2026-04-09T16:44:30Z",
        "impact": "第六章「资源使用情况」将简化呈现，技术栈列表可能不完整",
        "affected_chapters": [6],
        "mitigation_applied": "基于文件路径和代码内容推断技术栈，标注「推断」标记"
      },
      {
        "code": "W002",
        "name": "TimeEstimationImprecision",
        "message": "TimeEstimationImprecision: 时间节点基于消息间隔估算，精度 ±20%",
        "category": "estimation",
        "severity": "info",
        "timestamp": "2026-04-09T16:44:31Z",
        "impact": "第二章「执行过程」中的耗时数据为估算值，建议结合 Git log 验证",
        "affected_chapters": [2],
        "mitigation_applied": "在所有时间数据旁添加 ⚠️ 标注和精度说明"
      }
    ]
  },

  "statistics": {
    "total_phases": 2,
    "total_decisions": 1,
    "total_problems": 1,
    "suggestions_count": 3
  },

  "user_advice": {
    "can_upgrade": true,
    "how_to_upgrade": [
      "方式一（推荐）: 补充更多任务细节后重新生成 — 在新对话中详细描述当时的思考过程、遇到的困难、尝试过的方案等",
      "方式二: 手动编辑生成的报告 — 打开已保存的 Markdown 文件，补充标注「⚠️ 信息有限」的段落",
      "方式三: 结合 Git 历史增强 — 使用 `git log --since=\"2026-04-09T14:00\" --until=\"2026-04-09T16:00\"` 获取精确时间线，替换报告中的估算值"
    ],
    "prevention_for_next_time": "下次执行类似任务时，建议在过程中保持更详细的对话记录，例如：「我考虑了方案A和方案A，选择A是因为...」「遇到了XX问题，我尝试了...」这类表述可以显著提高报告的信息覆盖率和准确性"
  },

  "file_info": {
    "saved_to": "./reports/快速Bug修复_登录页面样式错乱_执行总结报告_20260409.md",
    "file_size_kb": 26.8
  }
}
```

### 关键点说明

- ✅ **`success: true`** — 降级执行**仍然返回成功**，报告可用
- ⚠️ **`degraded: true`** — 明确标记这是**降级后的结果**，不是完整质量的报告
- ⚠️ **`degradation_info` 字段** — 提供了降级的详细信息：
  - `original_detail_level`: 用户请求的 `"detailed"`
  - `effective_detail_level`: 实际使用的 `"standard"`
  - `reason`: 降级原因（信息覆盖率 68% < 阈值 80%）
  - `affected_capabilities`: 受影响的能力列表（哪些方面打了折扣）
- ⚠️ **`quality_score: 78.5`** — 反映了数据质量的影响（<80 为一般级别，<70 为较差）
- ⚠️ **`quality_check.warnings`** — 包含 **2 个 E010 警告** + **1 个 W002 信息提示**：
  - 每个警告都有 `code`、`message`、`impact`、`affected_chapters`、`mitigation_applied` 字段
  - 清晰说明了**哪个章节受影响**以及**系统采取了什么缓解措施**
- 💡 **`information_gaps` 数组** — 列出了 **3 个具体缺失的信息类别**：
  - 每项都有 `coverage_rate`（实际覆盖率）、`threshold`（阈值）、`impact`（影响说明）、`user_action_suggested`（用户补救建议）
- 💡 **`user_advice` 字段** — 告知用户**如何升级到完整版**：
  - `can_upgrade: true` 表示可以通过补充信息后重新生成获得更好的报告
  - `how_to_upgrade` 提供了 3 种具体的升级方式
  - `prevention_for_next_time` 给出了预防建议

### 降级决策流程示意

```
用户请求 detail_level="detailed"
    ↓
[Step 3: 信息收集 & 质量检查]
    ↓
计算各类信息覆盖率:
  - decision_records:     45%  ← ❌ < 70% 阈值
  - resource_allocation:  30%  ← ❌ < 60% 阈值
  - timeline_precision:   55%  ← ❌ < 75% 阈值
  - problem_records:      85%  ← ✅ 充足
  - goal_info:            90%  ← ✅ 充足
    ↓
综合覆盖率: 68%
阈值要求: 80%（for detailed level）
    ↓
🔴 覆盖率不足 → 触发降级决策
    ↓
评估降级选项:
  Option A: 降级为 standard（覆盖率要求 60%）→ ✅ 68% > 60%，可行
  Option B: 强制 detailed 但大量标注 ⚠️ → 体验差，不推荐
  Option C: 返回错误要求用户补充 → 不友好
    ↓
✅ 选择 Option A: 降级为 standard
    ↓
[继续 Step 4-7，使用 standard 模板生成]
    ↓
在报告中:
  - 添加顶部 ⚠️ 信息有限声明
  - 在受影响章节添加 ⚠️ 标注
  - 在响应中添加 degraded=true 和 degradation_info
    ↓
返回成功响应（带警告）
```

### 变体说明

| 场景变化 | 预期行为 |
|---------|---------|
| 对话历史较长（>50 条消息），但仍请求 `detailed` | 可能不会降级（取决于信息密度），`degraded: false` 或 `undefined` |
| 对话极短（<5 条消息），即使请求 `standard` 也可能降级为 `summary` | `effective_detail_level: "summary"`，报告仅 2-3 页 |
| 手动提供 `description` 参数补充背景信息 | 可提高信息覆盖率，可能避免降级或减轻降级程度 |
| 设置 `"generation_options.force_detail_level": true` | （假设支持）强制使用请求的详细程度，但 `warnings` 会更多，`quality_score` 更低 |

---

## 📊 示例对比速查表

| 维度 | 示例 1: 标准调用 | 示例 2: 最小参数 | 示例 3: 参数错误 | 示例 4: 降级执行 |
|------|----------------|----------------|----------------|----------------|
| **success** | `true` | `true` | `false` | `true` |
| **degraded** | 无 | 无 | 无 | `true` |
| **quality_score** | 94.5 (优秀) | 91.2 (优秀) | N/A | 78.5 (一般) |
| **completeness_rate** | 0.92 | 0.88 | N/A | 0.72 |
| **word_count** | 12,580 | 9,876 | N/A | 6,850 |
| **chapter_count** | 10 | 10 | N/A | 10 |
| **warnings 数量** | 0 | 2 (low) | N/A | 3 (1 warning + 2 info) |
| **file_saved** | ✅ (48.5 KB) | ✅ (38.2 KB) | ❌ | ✅ (26.8 KB) |
| **适用场景** | 常规软件开发 | 快速 Sprint 复盘 | 参数调试/集成测试 | 简单任务/短对话 |
| **推荐度** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ (测试用) | ⭐⭐⭐⭐ |

---

## 🔧 集成测试用例建议

基于以上 4 个示例，可构建以下自动化测试用例：

### 正向测试（Expected: success=true）

| 用例 ID | 名称 | 请求变体 | 断言要点 |
|---------|------|---------|---------|
| TC-001 | 标准开发任务 | 示例 1 完整请求 | quality_score > 90, chapter_count == 10, file_info.saved_to 非空 |
| TC-002 | 最小参数调用 | 仅 `{task_name: "Test"}` | 使用默认值，report_id 格式正确 |
| TC-003 | 摘要级报告 | `detail_level: "summary"` | word_count < 1500, chapter_count == 10（部分章节简化） |
| TC-004 | 学习模板 | `template_variant: "learning"` | 第九章内容明显扩充 |
| TC-005 | 自定义章节 | `included_chapters: [1,5,10]` | 仅包含指定章节，其他章节不存在 |
| TC-006 | JSON 输出格式 | `output_format: "json"` | report.content 为对象而非字符串 |

### 反向测试（Expected: success=false）

| 用例 ID | 名称 | 请求变体 | 断言要点 |
|---------|------|---------|---------|
| TC-101 | 缺少 task_name | `task_context: {}` | error.code == "E001", severity == "error" |
| TC-102 | task_name 为空 | `task_name: ""` | error.code == "E002" |
| TC-103 | 无效 detail_level | `detail_level: "ultra"` | error.code == "E002" |
| TC-104 | 章节号越界 | `included_chapters: [0, 11]` | error.code == "E003" (warning) 或过滤后继续 |
| TC-105 | 排除所有章节 | `excluded_chapters: [1..10]` | error.code == "E005" |
| TC-106 | 参数类型错误 | `detail_level: 123` | error.code == "E002" |

### 边界测试（Expected: degraded=true 或 warning）

| 用例 ID | 名称 | 请求变体 | 断言要点 |
|---------|------|---------|---------|
| TC-201 | 数据不足降级 | 短对话 + detailed 请求 | degraded == true, effective_detail_level < requested |
| TC-202 | 部分信息缺失 | 正常对话但某类信息稀少 | warnings 非空, information_gaps 非空 |
| TC-203 | 超长任务名 | `task_name: "A"*201` | error (超过 200 字符限制) 或截断 |
| TC-204 | 特殊字符任务名 | `task_name: "测试<script>"` | 成功但经过 XSS 过滤/转义 |

---

## 📖 相关文档索引

| 文档 | 内容 | 链接 |
|------|------|------|
| **SKILL.md** | 技能主文档（概述、触发条件、执行流程） | [SKILL.md](../SKILL.md) |
| **api-reference.md** | 完整 API 参数规范（输入/输出/约束） | [api-reference.md](api-reference.md) |
| **error-codes.md** | 所有错误码定义和处理策略 | [error-codes.md](error-codes.md) |
| **execution-flow.md** | 7 步执行流程详解 | [execution-flow.md](execution-flow.md) |
| **examples.md (V1)** | 4 场景自然语言使用示例 | [examples.md](examples.md) |
| **templates.md** | 4 种模板变体的结构定义 | [templates.md](templates.md) |
| **terminology.md** | 86 个专业术语表 | [terminology.md](terminology.md) |

---

## 📝 文档修订历史

| 版本 | 日期 | 作者 | 变更内容 |
|------|------|------|---------|
| v2.0 | 2026-04-09 | Task Execution Summary Generator Team | 初始版本，包含 4 个完整示例（标准/最小/错误/降级） |

---

*本文档遵循 Task Execution Summary Generator v2.0 接口规范*
*如有疑问，请参阅 [api-reference.md](api-reference.md) 或 [error-codes.md](error-codes.md)*
