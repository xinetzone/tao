# agent-services/ 智能体服务目录

## 定位

承载基于 AgentForge / taolib 构建的独立智能体服务、后台任务、自动化脚本和工具程序。

这些服务通常以进程或服务形式独立运行，而非直接面向终端用户的交互界面。

## 技术栈建议

- **Python**：利用现有 `taolib` 库，使用 FastAPI / Celery / asyncio 等
- **Node.js**：如需与前端工具链保持一致
- **容器化**：建议提供 `Containerfile` 便于部署

## 规范要求

1. **服务边界**：每个服务应有清晰的职责边界和输入输出定义。
2. **配置管理**：敏感配置通过环境变量注入，不硬编码在源码中。
3. **日志记录**：关键业务逻辑和异常捕获处必须添加结构化日志。
4. **错误处理**：统一错误响应格式，避免暴露底层实现细节。
5. **健康检查**：长期运行的服务应提供健康检查端点。

## 目录示例

```
agent-services/
├── webhook-handler/         # Webhook 处理服务
│   ├── src/
│   ├── pyproject.toml
│   ├── Containerfile
│   └── README.md
├── task-scheduler/          # 定时任务调度
│   └── ...
└── README.md                # 本文件
```
