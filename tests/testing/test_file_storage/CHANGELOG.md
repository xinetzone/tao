# File Storage 文件存储模块 - 更新日志

本文件记录 File Storage 模块的所有重要变更。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
项目遵循 [语义化版本](https://semver.org/lang/zh-CN/) 规范。

## [0.5.5] - 2026-04-06

### 新增

- **文件存储与 CDN 系统**
  - S3 存储后端（aiobotocore）和本地文件系统后端
  - CDN 集成（CloudFront + 通用 CDN）
  - 图片处理管道（缩略图、验证）、分块上传、签名 URL、生命周期管理
  - 客户端 SDK 和 FastAPI 服务器

### 修改

- 文件存储服务依赖注入和 API 路由结构重构

### 安全

- 文件存储支持签名 URL 访问控制
