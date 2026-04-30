# AGENTS.md

> **注意**：本文档已拆分至多个独立文档中，以提高可维护性和可读性。请查看以下文档获取详细信息。

## 文档导航

- [README.md](README.md) - 项目概述与快速开始
- [Python 环境](doc/user_guide/python_environment.md) - Python 环境与 3.14 新特性
- [常用命令](doc/user_guide/commands.md) - 常用命令
- [架构说明](doc/architecture/architecture.md) - 架构说明
- [API 参考](doc/api_reference/api_reference.md) - API 参考与文档整合原则
- [编码规范](doc/developer_guide/coding_standards.md) - 编码规范
- [环境变量](doc/user_guide/environment_variables.md) - 环境变量
- [最佳实践](doc/developer_guide/best_practices.md) - 最佳实践
- [项目经验总结](doc/developer_guide/project_experience.md) - 项目经验总结
- [Qoder 规范](doc/developer_guide/qoder_rules.md) - Qoder 规范

## 核心功能速览

`taolib` 是一个 Python 库（Python >= 3.14），提供以下核心功能：
- **文档构建自动化**：基于 Sphinx 和 Invoke 的文档任务
- **远程 SSH 探测**：Conda 环境探测与远程命令执行
- **Matplotlib 字体配置**：中文文本渲染支持
- **中心化配置管理**：多环境配置管理、版本控制、审计日志和实时推送
- **MongoDB 数据同步**：ETL 管道、增量同步、自定义转换和定时调度
- **统一认证授权**：JWT + RBAC + API Key + Token 黑名单
- **用户行为分析**：事件采集、会话追踪、聚合分析
- **多提供商邮件服务**：SMTP/SendGrid/Mailgun/SES + 故障转移 + 模板引擎
- **文件存储与 CDN**：S3/本地存储 + CloudFront + 图片处理管道
- **OAuth2 第三方登录**：Google/GitHub + Token 加密 + 审计日志
- **API 限流中间件**：滑动窗口限流 + TOML 配置 + 违规追踪
- **后台任务队列**：Redis 优先级队列 + Worker 管理 + 重试策略
- **博客/CMS 平台**：FastAPI + SQLAlchemy + Markdown + RSS

核心设计理念：最小化核心依赖（`dependencies = []`），通过可选依赖组提供扩展功能。
