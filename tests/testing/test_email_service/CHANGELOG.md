# Email Service 邮件服务模块 - 更新日志

本文件记录 Email Service 模块的所有重要变更。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
项目遵循 [语义化版本](https://semver.org/lang/zh-CN/) 规范。

## [0.5.5] - 2026-04-06

### 新增

- **多提供商邮件服务**
  - 4 个邮件提供商实现：SMTP、SendGrid、Mailgun、Amazon SES
  - ProviderFailoverManager 自动故障转移
  - Redis / 内存双队列、Jinja2 模板引擎、退信处理、Webhook 端点
