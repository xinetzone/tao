# Changelog

## Unreleased

### Added

- 新增 `taolib.remote` 子包：SSH 配置读取/脱敏、prefix 上下文管理、远端探测接口（支持注入连接工厂，便于测试）。
- 文档新增 API 文档入口，并补充 `taolib.remote` 使用说明与最佳实践页面。

### Security

- `remote/ssh.toml` 示例配置移除明文密码，改为占位符。

