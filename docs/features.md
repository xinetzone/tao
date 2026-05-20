# 核心功能 (Core Features)

## 📁 目录结构与 AI 契约

- `AGENTS.md`：**AI 的最高宪法与导航路由**。任何 AI 进入本项目，都会首先读取此文件，了解全局规则并找到所需具体规范的路径。
- `.agents/`：**领域知识库与工具箱**。包含按需读取的详细规则，降低 Token 消耗，提高指令遵循度。
  - `rules/`：具体技术栈规范（如 `frontend.md`, `backend.md`）。
  - `workflows/`：工作流检查清单（如 `pr-review.md`）。
  - `scripts/`：供 AI 调用的自动化脚本工具。
