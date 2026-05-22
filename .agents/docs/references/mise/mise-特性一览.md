# mise 特性一览

> 快速了解 mise 的核心特性和对比优势。完整的产品介绍请阅读 [产品介绍](./01-产品介绍.md)。

---

## 核心特性

| 特性 | 说明 |
|-----|------|
| ⚡ **极快** | Rust 实现；激活后工具调用走真实二进制路径 |
| 🔧 **多语言** | 一个工具管理 900+ tools |
| 🪟 **跨平台** | Linux / macOS / Windows 支持 |
| 🔐 **安全** | 信任机制、安装来源与后端校验 |
| 📦 **一体化** | 开发工具 + 环境变量 + 任务管理 |
| 🔄 **兼容 asdf** | 兼容 `.tool-versions`；asdf 插件需按项目验证 |

---

## 与竞品对比

| 对比维度 | mise | asdf | nvm | pyenv / rbenv |
|---------|------|------|-----|---------------|
| 支持工具范围 | 900+ tools | 数百 | 仅 Node.js | 单一语言 |
| 工具调用路径 | 真实二进制路径 | 常见 shim 跳转 | shell 函数 | shim/真实路径取决于工具 |
| Windows 支持 | ✅ 支持 | ❌ 有限 | ❌ 不支持 | ❌ 不支持 |
| 环境变量管理 | ✅ 内置 | ❌ 无 | ❌ 无 | ❌ 无 |
| 任务管理 | ✅ 内置 | ❌ 无 | ❌ 无 | ❌ 无 |
| 安全机制 | ✅ trust 与后端/来源校验 | 插件生态依赖 | 依赖安装来源 | 依赖安装来源 |
| asdf 兼容 | ✅ `.tool-versions` 兼容 | - | ❌ | ❌ |

💡 详细的竞品分析与性能数据请查阅 [产品介绍](01-产品介绍.md)。

---
## 导航

🏠 [返回首页](./README.md) | 📖 [产品介绍](./01-产品介绍.md)

---

**文档版本**：v2.0  
**最后更新**：2026-05-22  
**按官方资料校准**：2026-05-22；校准时 GitHub 最新 Release 为 v2026.5.13
---

## Search Keywords

- mise feature overview
- mise cheat sheet
- mise vs asdf
- mise vs nvm
- mise vs pyenv
- real binary path
- cross platform
- task management
- environment variable management

## Trigger Phrases

- mise 有哪些核心特性？
- mise 和 nvm/asdf/pyenv 快速对比
- 我需要一页看懂 mise 优势
- mise 是否支持 Windows？
- mise 是否支持任务管理？

