# GitHub App Installation Token Override Design

## Goal

基于 GitHub 于 2026-05-15 公布的安装令牌请求级覆盖头能力，为 `AgentForge` 设计并落地一套可兼容 GitHub.com / GHEC 与 GHES 的 GitHub App 安装令牌管理机制，满足以下目标：

- 支持请求级切换 `enabled / disabled / auto` 三种策略
- 默认兼容 GHES 和未知环境的自动降级
- 统一库 API 与 CLI 双入口
- 通过缓存与单飞刷新提升高并发场景下的令牌调度效率
- 通过脱敏、最小权限与结构化诊断提升安全性与可运维性

## Background

GitHub 新增了针对 `POST /app/installations/{installation_id}/access_tokens` 的临时请求头 `X-GitHub-Stateless-S2S-Token`，用于按请求覆盖服务端 rollout 决策：

- `enabled`：强制返回新的无状态安装令牌
- `disabled`：强制返回旧的有状态安装令牌
- 缺省：遵循 GitHub 平台自身 rollout 逻辑

该能力的目标不是让业务永久依赖某个令牌格式，而是帮助集成方在迁移期同时验证两种格式，并在必要时临时回退。根据官方说明：

- 新的无状态令牌仍以 `ghs_` 开头，但长度显著增加，约为 520 字符
- 无状态令牌在 `ghs_` 之后包含两个点，呈现 JWT 形态
- 旧的有状态令牌长度更短，且不包含点
- 业务方仍应将两种令牌都视为 opaque secret，而不是依赖其内部结构
- 该请求头是临时兼容能力，未来会被移除
- 该变更适用于 GitHub Enterprise Cloud 与 Data Residency，不适用于 GHES

## Repository Assessment

当前 `AgentForge` 仓库尚未实现应用级 GitHub App 认证与 installation token 管理能力：

- `src/taolib/` 当前只有基础包入口，没有 GitHub API 客户端与认证抽象
- 现有 GitHub 相关逻辑主要位于 `.github/workflows/`，依赖 GitHub Actions 提供的 `GITHUB_TOKEN` 或特定外部 Secret
- 仓库内没有统一的 JWT 签发、installation token 交换、缓存、并发刷新去重、凭证脱敏与能力探测机制

这意味着本次工作不是对既有令牌层做局部修补，而是要补齐一个可长期维护的统一能力层，同时确保不破坏现有工作流。

## Scope

- 新增 `taolib.github_app` 子包，统一承载 GitHub App 认证、installation token 获取、缓存与策略控制
- 提供 Python API 与 CLI 双入口
- 支持对安装令牌请求级覆盖头的显式控制与自动降级
- 提供基础环境探测能力，用于区分 GitHub.com / GHEC 与 GHES / 未知环境
- 提供进程内缓存与单飞刷新能力
- 为未来接入工作流保留稳定接口，并新增验证型接入点
- 补充学习笔记、设计文档、测试报告与变更记录

## Non-Goals

- 不一次性替换现有全部 `.github/workflows/` 认证逻辑
- 不将安装令牌内容作为 JWT 做业务级解析与声明依赖
- 不在本次实现文件缓存、Redis 缓存或分布式锁
- 不实现完整的 GitHub API 通用 SDK，只实现与 GitHub App 安装令牌相关的最小闭环

## Design Principles

1. 兼容优先：默认兼容 GHES 与未知环境，避免把临时云端能力误当成通用协议。
2. 意图与实现分离：上层只表达“需要哪类 token 策略”，底层负责决定是否注入请求头。
3. Opaque secret 原则：无论新旧格式，都不依赖 token 内部结构开展业务逻辑。
4. 最小权限原则：仅在调用方明确指定时申请所需 repositories 与 permissions。
5. 渐进式集成：先提供验证型入口，不直接替换现有稳定工作流。
6. 可移除性：将覆盖头逻辑收敛于少量模块，便于未来官方下线该能力后平滑移除。

## Proposed Architecture

建议新增如下模块：

- `src/taolib/github_app/__init__.py`
- `src/taolib/github_app/config.py`
- `src/taolib/github_app/models.py`
- `src/taolib/github_app/errors.py`
- `src/taolib/github_app/cache.py`
- `src/taolib/github_app/client.py`
- `src/taolib/github_app/token_manager.py`
- `src/taolib/cli/github_app.py`

模块职责如下：

### `config.py`

- 统一解析 `app_id`、`installation_id`、私钥、GitHub API base URL、策略、缓存窗口等配置
- 支持 CLI 参数、环境变量、默认值三层优先级
- 在启动阶段完成配置校验，避免在运行中才暴露错误

### `models.py`

- 定义结构化模型，例如：
  - `InstallationTokenRequest`
  - `InstallationTokenResult`
  - `GitHubRuntimeProfile`
  - `EffectiveTokenStrategy`
- 明确返回给调用方的元数据，例如：
  - 请求策略与实际策略
  - 是否发生降级
  - 令牌是否识别为 stateless 或 stateful
  - 过期时间

### `errors.py`

- 提供稳定异常层次，区分配置错误、环境不支持、认证失败、缓存失败、刷新失败、降级失败等场景

### `cache.py`

- 提供进程内缓存抽象
- 按 `installation_id + permissions + repositories + effective_strategy` 生成缓存键
- 支持“过期预留窗口”判断，避免返回即将过期的 token

### `client.py`

- 负责 GitHub HTTP 交互与 App JWT 签发
- 调用 `POST /app/installations/{installation_id}/access_tokens`
- 根据有效策略决定是否发送 `X-GitHub-Stateless-S2S-Token`
- 只处理网络交互与响应解析，不承载缓存与并发编排

### `token_manager.py`

- 作为对外统一编排层
- 负责能力探测、策略计算、缓存命中、单飞刷新、失败降级与结果脱敏
- 作为 Python API 与 CLI 的共享核心入口

### `cli/github_app.py`

- 提供脚本化入口，支持本地调试、CI 验证与后续 workflow 逐步接入
- 典型能力包括：
  - 获取 installation token
  - 探测当前目标环境
  - 输出脱敏诊断信息

## Request Flow

标准流程如下：

1. 调用方传入 `installation_id`、可选 `repositories / permissions` 与目标策略 `auto | enabled | disabled`
2. `token_manager` 加载配置并识别当前环境
3. `token_manager` 计算有效策略
4. 查询缓存
5. 若缓存可用，则直接返回
6. 若缓存不可用或即将过期，则进入单飞刷新流程
7. `client` 使用 App 私钥签发 JWT 并调用 installation access token 接口
8. 按有效策略决定是否注入请求头
9. 解析响应并识别令牌类型
10. 刷新缓存并返回结构化结果

## Strategy Resolution

支持三种请求策略：

- `enabled`
  - 在支持环境中显式请求 stateless token
  - 主要用于迁移演练、兼容性验证与压力测试
- `disabled`
  - 在支持环境中显式请求 stateful token
  - 主要用于回归验证与临时回退
- `auto`
  - 作为默认策略
  - 业务逻辑只要求兼容两种格式，不强依赖某一种返回

`auto` 的默认实现如下：

- 在 GitHub.com / GHEC 环境下：默认不强制覆盖，让 GitHub 自身 rollout 决定返回格式
- 在 GHES / 未知环境下：不发送覆盖头

这样设计的原因是请求级覆盖头是临时能力，最适合用于验证、灰度与诊断，而不是长期作为生产主路径的硬依赖。

## Environment Detection And Fallback

环境识别主要基于 `base_url`：

- `https://api.github.com` 及明确的 GitHub Cloud 场景视为支持候选环境
- 自建 GHES 域名与未知环境默认视为不支持覆盖头

降级规则如下：

- `auto`
  - 若环境不支持覆盖头，则直接以“无覆盖头”方式请求
  - 若带头请求失败且检测为能力差异，可自动重试一次无头请求
- `enabled / disabled`
  - 若环境不支持覆盖头，不直接崩溃
  - 记录一次“请求策略与实际策略不一致”的降级结果
  - 默认不做静默行为替换，以便测试与诊断场景能准确暴露差异

## Concurrency And Cache Strategy

高并发场景的关键优化点如下：

- 对同一缓存键的刷新采用单飞机制
- 多个并发请求共享同一次上游刷新结果
- 设置过期预留窗口，例如在到期前 60 至 120 秒主动刷新
- 刷新成功后再原子替换缓存，避免失败请求污染缓存状态
- 若刷新失败且旧 token 仍处于安全窗口内，可按策略决定是否短暂复用旧 token

目标是将同一 installation 的高并发令牌请求从“多次上游请求”压缩为“一次上游刷新 + 多次缓存复用”。

## Security Constraints

- 私钥仅允许来自环境变量或明确指定的本地文件
- 禁止将私钥明文写入项目配置文件
- installation token、App JWT 与私钥内容全部视为敏感信息
- 默认日志与诊断输出中只展示脱敏信息，例如前缀、长度、令牌类型与过期时间
- 业务代码不得依赖 token 的 JWT 内部字段
- 所有 token 一律按 opaque secret 处理
- 当调用方指定 `repositories` 与 `permissions` 时，按最小权限范围申请 token

## Configuration Surface

建议支持以下关键配置：

- `GITHUB_APP_ID`
- `GITHUB_APP_INSTALLATION_ID`
- `GITHUB_APP_PRIVATE_KEY`
- `GITHUB_APP_PRIVATE_KEY_FILE`
- `GITHUB_API_URL`
- `GITHUB_APP_TOKEN_STRATEGY`
- `GITHUB_APP_TOKEN_EAGER_REFRESH_SECONDS`
- `GITHUB_APP_ALLOW_HEADER_FALLBACK`

优先级为：

1. CLI 参数
2. 环境变量
3. 默认值

## Workflow Integration

当前仓库工作流主要依赖 GitHub Actions 原生权限，不适合在本次任务中直接大规模替换。推荐的接入策略是：

1. 先新增验证型脚本或 CLI 命令，验证新令牌层行为
2. 再增加一个独立 workflow 或 job，验证云端与降级路径
3. 待机制稳定后，再评估哪些现有流程值得迁移到 GitHub App 模式

这样可以最大限度降低对 `release`、`pages`、`python-publish` 等现有稳定链路的影响。

## Testing Strategy

测试分为四层：

### Unit Tests

- 策略到请求头映射
- 环境探测与降级判定
- 令牌类型识别
- 缓存命中与过期刷新
- 脱敏输出与异常建模

### Integration Tests

- `token_manager -> client -> cache` 的完整编排
- `enabled` 返回 stateless token 的路径
- `disabled` 返回 stateful token 的路径
- `auto` 在云端与 GHES 下的差异路径

### Concurrency Tests

- 同一 installation 的高并发申请
- 过期边界下的并发刷新
- 刷新失败后的等待与恢复行为
- 单飞机制是否将上游请求压缩到一次

### Stress Tests

- 使用本地 mock server 或测试替身模拟 GitHub API
- 不直接打真实 GitHub API，避免触发限流与泄露风险
- 关注失败率、平均时延、P95/P99、缓存命中率与上游请求次数

## Success Metrics

优化成果应至少量化以下指标：

- 上游 installation token 请求次数压缩率
- 缓存命中率
- 并发场景下的失败率、平均时延与 P95/P99
- 单飞机制下的真实刷新次数
- 脱敏与最小权限路径覆盖率

若当前仓库缺少现成基线，可在 mock 环境中对比：

- 无缓存、无单飞版本
- 优化后版本

## Deliverables

本任务最终应提交以下成果：

1. 不少于 500 字的学习笔记，整理 GitHub 官方页面的核心技术内容与项目启发
2. 本设计文档
3. `taolib.github_app` 相关代码实现
4. Python API 与 CLI 入口
5. 功能测试、并发测试与压力测试代码
6. 测试报告与指标对比
7. 必要的 README / docs / CHANGELOG 说明更新

## File Plan

建议产出文件如下：

- `.agents/docs/superpowers/specs/2026-05-22-github-app-installation-token-override-design.md`
- `.agents/docs/superpowers/retrospectives/` 下对应测试报告或任务复盘
- `docs/` 下用于人类阅读的学习笔记与使用说明
- `src/taolib/github_app/` 下新增实现模块
- `tests/github_app/` 下新增测试

## Risks

- GitHub 的请求级覆盖头为临时能力，未来会下线，设计必须保持可移除
- 仓库当前没有 GitHub App 运行时配置基础，首次接入时需要较完整的本地与 CI 配置说明
- 若未来要在多进程或多实例环境复用缓存，当前进程内缓存方案需要继续演进
- 若工作流过早替换为 GitHub App 模式，可能给现有稳定链路带来不必要风险

## Validation Checklist

- 文档是否明确区分支持环境与不支持环境
- 是否避免把 token 内部结构作为业务依赖
- 是否为 `auto / enabled / disabled` 三种策略定义清晰行为
- 是否明确缓存、单飞、过期预留窗口的职责
- 是否明确学习笔记、实现代码、测试报告与文档更新的落点
- 是否将现有 workflow 的接入策略限定为渐进式验证
