# 信息脱敏规则

> **核心原则**：项目内任何形式的产出（代码、文档、配置、聊天记录、日志）在提交至版本控制或对外发布前，必须完成敏感信息脱敏。脱敏不可逆——一旦敏感信息泄露至 Git 历史或公共空间，视为安全事件。

## 1. 脱敏信息类型与脱敏方式矩阵

| 信息类型 | 典型示例 | 脱敏方式 | 替换/占位符示例 | 说明 |
|---|---|---|---|---|
| **个人身份信息 (PII)** | 真实姓名、身份证号、护照号、家庭地址 | 替换为通用占位符 | `<REDACTED_NAME>`、`<REDACTED_ID>`、`<REDACTED_ADDRESS>` | 文档中涉及个人身份时统一使用占位符，禁止保留真实信息 |
| **联系方式** | 个人邮箱、手机号、微信号、社交媒体账号 | 部分隐藏或替换为角色邮箱 | `u***@example.com`、`138****5678`、`<MAINTAINER_EMAIL>` | 公开文档中仅保留项目公共联系渠道（如 `team@worldsprout.com`） |
| **认证凭证** | API Key、Access Token、OAuth Secret、数据库密码、SSH 私钥 | 替换为环境变量引用 | `$GITHUB_TOKEN`、`<YOUR_API_KEY>`、`sk-***...***` | 代码中凭证一律通过环境变量或密钥管理服务注入；配置示例文件中仅保留占位符 |
| **内部 URL 与服务端点** | 内网 IP、内部域名、数据库连接串、私有仓库地址 | 替换为通用占位符 | `localhost`、`<INTERNAL_HOST>`、`postgresql://<DB_HOST>:<DB_PORT>/<DB_NAME>` | 连接字符串中的主机、端口、用户名、密码全部脱敏；示例代码仅使用 `localhost` 或示意占位符 |
| **业务敏感数据** | 用户真实数据、财务数据、内部运营指标、未公开的商业计划 | 替换为示例数据或删除 | `John Doe`、`123-456-7890`、`[REDACTED]` | 测试数据应使用公开可得的虚构数据（如 Faker 生成）；文档中业务数据用 `[REDACTED]` 标记 |
| **私有基础设施路径** | 本地绝对路径（如 `/Users/xinzo/`、`C:\Users\xxx\`）、内部挂载点 | 替换为相对路径或通用占位符 | `~/project/`、`<WORKSPACE_ROOT>`、`/path/to/project` | 文档与配置中禁止出现个人用户目录路径；统一使用项目根相对路径或 `<WORKSPACE_ROOT>` 占位符 |
| **Git 远程凭据与私有仓库 URL** | 含用户名+Token 的 remote URL（如 `https://user:token@github.com/...`） | 替换为公开 URL 或 SSH 格式 | `git@github.com:org/repo.git`、`https://github.com/org/repo.git` | Git remote 中禁止嵌入凭据；统一使用 SSH 或配置 git credential manager |
| **内部监控与运维信息** | Prometheus 端点、Grafana Dashboard 内部链接、Sentinel/Sentry DSN | 替换为占位符 | `<MONITORING_ENDPOINT>`、`<SENTRY_DSN>` | 公开文档中仅描述监控架构，不暴露实际端点和凭据 |

## 2. 实施步骤

### 阶段一：开发阶段（编码时）

- **凭证外部化**：所有 API Key、Token、密码必须在首次写入代码时即使用环境变量引用，禁止硬编码。
- **配置文件模板化**：提交 `.example` 或 `.template` 版本的配置文件（如 `config.example.toml`），原始配置文件加入 `.gitignore`。
- **测试数据虚构化**：测试用例中的用户数据、业务数据必须使用 `Faker` 或手动构造的示例数据，不得粘贴真实数据。
- **路径通用化**：文档和代码注释中的路径引用一律使用相对路径或项目根变量，禁止出现个人用户目录路径。

### 阶段二：文档/配置阶段（提交前）

- **全局搜索**：在提交前运行敏感信息扫描（见第 3 节自动化扫描），确保无遗漏。
- **Git diff 检查**：逐文件检查 `git diff --staged`，确认无敏感信息混入。
- **配置文件复核**：检查 `config.toml`、`world.toml`、`constraints.toml` 等配置文件是否已脱敏。

### 阶段三：CI/CD 门禁阶段（提交后）

- **自动化扫描集成**：CI 流水线中集成正则扫描步骤，发现敏感模式立即阻断合并。
- **历史泄露响应**：若 CI 检测到合并请求中包含疑似敏感信息，该 PR 不得合并，需先清理 Git 历史。

## 3. 验证方法

### 3.1 自动化正则扫描

以下正则模式作为基线扫描规则，应在 CI 和本地 pre-commit 中执行：

| 扫描目标 | 正则模式（示意） | 匹配示例 |
|---|---|---|
| GitHub Token | `gh[pousr]_[A-Za-z0-9_]{36,}` | `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` |
| OpenAI API Key | `sk-[A-Za-z0-9]{32,}` | `sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` |
| AWS Access Key | `AKIA[0-9A-Z]{16}` | `AKIAIOSFODNN7EXAMPLE` |
| 通用私钥头 | `-----BEGIN (RSA\|EC\|DSA\|OPENSSH) PRIVATE KEY-----` | PEM 格式私钥 |
| 邮箱地址 | `[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}` | 需结合上下文判断是否为个人邮箱 |
| 内网 IP | `(10\.\d{1,3}\|172\.(1[6-9]\|2\d\|3[01])\|192\.168)\.\d{1,3}\.\d{1,3}` | 私有 IPv4 地址段 |
| 数据库连接串 | `(mysql\|postgres\|mongodb\|redis)://[^@\s]+@` | 含凭据的连接串 |

### 3.2 人工审查清单

| 检查项 | 通过标准 |
|---|---|
| 个人姓名/ID | 全文搜索无真实姓名或身份证号，仅保留占位符 |
| 个人邮箱/手机号 | 仅保留项目公共联系渠道，无个人联系方式 |
| API Key/Token | `grep -r "sk-\|ghp_\|gho_\|github_pat_"` 无结果 |
| 数据库连接串 | 连接串中的用户名、密码、主机均为占位符或环境变量 |
| 绝对路径 | `grep -r "/Users/\|C:\\\\Users\\\\"` 无结果（`C:\\` 需按 OS 调整） |
| `.git/config` | git remote 中无凭据嵌入 |
| 日志文件 | 无 `.log` 或 `.temp/` 中包含敏感信息的文件被提交 |

### 3.3 CI/CD 门禁集成

在 `.github/workflows/ci.yml` 中新增 `sensitive-data-scan` job，核心逻辑：

1. **凭证模式扫描**：使用 `gitleaks` 或等价正则扫描，检测 Token、私钥等强特征模式。
2. **路径模式扫描**：检测绝对路径 `/Users/`、`C:\Users\` 及内网 IP。
3. **阻断策略**：任一模式命中即 job 失败，阻断 PR 合并。
4. **白名单**：对于误报模式，通过 `.gitleaks.toml` 或扫描脚本配置白名单。

## 4. 适用范围与例外处理

### 4.1 适用范围

| 范围 | 说明 |
|---|---|
| **代码文件** | 所有提交至 Git 的源代码（`.py`、`.ts`、`.js`、`.go` 等） |
| **配置文件** | `world.toml`、`constraints.toml`、`registry.toml`、`.env`（若已加入 `.gitignore` 则无风险，若有 `.example` 版本则必须脱敏） |
| **文档文件** | `docs/`、`specs/`、`.agents/docs/`、`README.md`、`AGENTS.md` 等所有 Markdown/RST 文档 |
| **CI/CD 文件** | `.github/workflows/*.yml`、`Containerfile`、`Dockerfile` 中的环境变量和密钥引用 |
| **聊天/日志导出** | 任何可能被提交至仓库的对话记录、调试日志、错误报告 |

### 4.2 例外情况

| 例外情形 | 处理方式 | 说明 |
|---|---|---|
| **`.env.example` 中占位符值** | 允许保留以 `<YOUR_...>` 为格式的占位符 | 前提是不包含真实生产凭据 |
| **已过期的测试 Token** | 仍不建议提交 | Git 历史永久保留，过期 Token 泄露仍可能造成信息关联风险 |
| **CI 所需的公开 Secret 名称** | 允许引用 `${{ secrets.GITHUB_TOKEN }}` 等 CI 原生变量名 | 变量名本身不敏感，但不得在 CI 配置中 echo/print 其值 |
| **公开可得的项目公共邮箱/URL** | 允许保留 | 如 `team@worldsprout.com`、`https://github.com/worldsprout` |
| **紧急情况下的临时例外** | 需在 `.temp/exception-log.md` 中记录：例外类型、涉及文件、时间戳、批准人、计划清理时间 | 仅限临时性（≤ 24h），过期未清理升级为安全事件 |

> **例外审批流程**：任何新增例外需经项目维护者 review 并记录在案。例外必须有明确的到期时间，到期未处理自动失效并触发告警。

## 5. 更新与维护流程

### 5.1 触发修订的条件

| 触发条件 | 响应动作 | 责任人 |
|---|---|---|
| **新增信息类型**：项目中引入新类型的敏感数据（如生物特征数据、位置数据） | 评估风险等级 → 更新第 1 节矩阵表 → 新增对应的检测正则 | 项目维护者 |
| **新增服务/API**：接入新的第三方服务，需管理新的认证凭证类型 | 更新第 1 节凭证行和第 3 节正则表 | 引入方 + 维护者 |
| **安全事件复盘**：发生信息泄露事件（包括近失事件） | 复盘根因 → 更新本规则堵住漏洞 → 记录至 `RETROSPECTIVE.md` | 全体贡献者 |
| **行业标准变更**：OWASP、CWE 等标准新增相关最佳实践 | 评估对齐必要性 → 按需更新本规则 | 维护者 |
| **定期审查**：每季度 | 扫描规则集是否覆盖当前项目所有敏感信息类型 → 更新过时模式 | 维护者 |
| **工具链升级**：引入新的扫描工具或替换现有工具 | 更新第 3 节验证方法中的工具引用 | 维护者 |

### 5.2 修订流程

```mermaid
flowchart TD
    Trigger["触发条件满足"] --> Propose["提出修订 PR"]
    Propose --> Review["维护者 Review"]
    Review -->|"通过"| Update["更新本规则对应章节"]
    Update --> Sync["同步更新 CI 扫描规则"]
    Sync --> Deploy["规则生效"]
    Review -->|"驳回"| Feedback["反馈修改意见"]
    Feedback --> Propose
```

### 5.3 版本记录

本规则的变更历史在项目 `CHANGELOG.md` 中统一记录，格式遵循 `Keep a Changelog` 规范。每次修订需包含：

- **日期**：修订生效日期
- **变更类型**：Added / Changed / Removed / Fixed
- **变更摘要**：1-2 句话说明变更内容
- **关联 Issue/PR**：对应的追踪编号
