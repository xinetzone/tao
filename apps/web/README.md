# web/ 应用目录

## 定位

承载基于 AgentForge / taolib 构建的 Web 应用，包括前端应用、全栈应用和管理后台等。

## 技术栈建议

根据 `.agents/rules/frontend.md` 和 `.agents/rules/backend.md` 的模板，推荐在创建具体应用时明确以下事项：

- **前端框架**：React / Vue / Next.js / Svelte 等
- **样式方案**：Tailwind CSS / CSS Modules / Styled Components 等
- **状态管理**：Context API / Redux / Zustand / Pinia 等
- **后端服务**（如为全栈）：Python FastAPI / Node.js / Go 等

## 规范要求

1. **单一职责**：组件/模块保持单一职责，复杂逻辑需拆分。
2. **语义化**：优先使用语义化 HTML 标签。
3. **响应式**：移动端优先 (Mobile First) 的响应式设计。
4. **API 设计**：如暴露后端接口，遵循 RESTful 标准。
5. **安全防范**：防范 SQL 注入、XSS 等常见攻击；敏感数据加密存储。

## 目录示例

```
web/
├── my-web-app/              # 具体应用
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── README.md
└── README.md                # 本文件
```
