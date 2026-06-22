# TuyaOpen 文档索引

> 来源：https://tuyaopen.ai/zh/docs/about-tuyaopen
> 归档日期：2026-06-22

## 一、概述类

| 页面标题 | URL | 摘要 |
|----------|-----|------|
| 关于 TuyaOpen | /zh/docs/about-tuyaopen | 概述、五层SDK架构、芯片支持矩阵、版本策略、开源链接 |
| 目录结构 | /zh/docs/project-walkthrough | src/apps/examples/platform/boards/tools/tos.py 目录说明 |

## 二、快速开始

| 页面标题 | URL | 摘要 |
|----------|-----|------|
| 快速开始（总览） | /zh/docs/quick-start | 名词解释(UUID/AuthKey/PID)、授权码获取、准备工作 |
| 极速体验 | /zh/docs/quick-start/unboxing | 预编译bin烧录体验流程 |
| Step 1: 项目编译 | /zh/docs/quick-start/project-compilation | 编译项目流程 |
| Step 2: 固件烧录 | /zh/docs/quick-start/firmware-burning | tos.py flash / tos.py monitor |
| Step 3: 设备授权 | /zh/docs/quick-start/equipment-authorization | auth命令写入UUID/AuthKey、头文件方式 |
| Step 4: 设备手机配网 | /zh/docs/quick-start/device-network-configuration | 智能生活App配网、扫码配网 |
| 设备调试 | /zh/docs/quick-start/device-debug | 设备调试方法 |

## 三、CLI 工具

| 页面标题 | URL | 摘要 |
|----------|-----|------|
| CLI - tos.py 开发工具 | /zh/docs/tos-tools/tos-guide | version/check/config/build/flash/monitor/update/new/dev/idf命令 |
| tos.py idf 命令参考 | /zh/docs/tos-tools/tos-idf-reference | ESP32 idf.py透传 |
| GUI - tyutool 图形化工具 | /zh/docs/tos-tools/tools-tyutool | 图形化烧录和授权工具 |

## 四、构建系统

| 页面标题 | URL | 摘要 |
|----------|-----|------|
| 编译指导 | /zh/docs/build-system/compilation-guide | tos.py build流水线：配置→平台下载→CMake/Ninja→输出校验 |
| CMake、Kconfig 与组件模型 | /zh/docs/build-system/cmake-kconfig-and-components | CMake结构、组件模型 |
| Kconfig 与工程配置 | /zh/docs/peripheral/tutorials/kconfig-and-project-configuration | 配置系统详解 |

## 五、硬件适配

| 页面标题 | URL | 摘要 |
|----------|-----|------|
| 适配新 Platform | /zh/docs/new-hardware/porting-platform | 芯片适配流程、编译流程、TKL层适配、蜂窝网络适配 |
| 创建 Platform | /zh/docs/new-hardware/new-platform | tos.py new platform命令详解、后续操作（工具链/代码补充） |
| 创建 Board | /zh/docs/new-hardware/new-board | tos.py new board、命名规则、适配开发板 |
| 创建 Project | /zh/docs/new-hardware/new-project | tos.py new project命令 |

## 六、DuckyClaw

| 页面标题 | URL | 摘要 |
|----------|-----|------|
| DuckyClaw 与 T5-AI | /zh/docs/duckyclaw/ducky-quick-start-T5AI | 编译烧录激活DuckyClaw固件、LLM/IM配置 |
| DuckyClaw 连接 TuyaClaw | /zh/docs/duckyclaw/DuckyClaw-TuyaClaw | 链接TuyaClaw相关 |

## 七、平台特定

| 页面标题 | URL | 摘要 |
|----------|-----|------|
| ESP32 快速开始 | /zh/docs/hardware-specific/espressif/esp32-quick-start | ESP32平台快速上手 |
| TUYA T5AI 管脚映射 | /zh/docs/hardware-specific/tuya-t5/develop-with-Arduino/Pinmux | T5AI管脚映射 |

## 八、AI 应用

| 页面标题 | URL | 摘要 |
|----------|-----|------|
| MCP 工具合集 | /zh/docs/applications/tuya.ai/ai-components/ai-mcp-tools | AI MCP工具集合 |

## 九、贡献指南

| 页面标题 | URL | 摘要 |
|----------|-----|------|
| 贡献指南 | /zh/docs/contribute/contribute-guide | Fork/Push Requests流程、CLA签署 |
| 编码风格指南 | /zh/docs/contribute/coding-style-guide | Linux内核风格、函数/宏/缩进规范、clang-format |
| Markdown 语法快速指南 | /zh/docs/contribute/template/markdown-syntax | Docusaurus MDX语法、告示/详情/Front Matter |

## 十、常见问题

| 页面标题 | URL | 摘要 |
|----------|-----|------|
| 常见问题(FAQs) | /zh/docs/faqs | 环境/构建/硬件/配置/授权/烧录/连接/外设/Linux等大类FAQ |
| 免费领取开发者授权码 | /zh/docs/faqs/get-developer-license | 涂鸦开发者平台领取2个免费License流程 |

## 十一、发布与维护

| 页面标题 | URL | 摘要 |
|----------|-----|------|
| 技术 Roadmap 与发布 | /zh/docs/maintenance-and-releases | 维护计划、平台支持、Roadmap、v1.0.0~v1.5.0发布说明、社区支持 |

---

## 文档站结构（按导航层级）

```
TuyaOpen 文档
├── 关于 TuyaOpen (概述+架构+平台+版本)
├── 技术 Roadmap 与发布
├── 目录结构
├── DuckyClaw
│   ├── DuckyClaw 与 T5-AI
│   └── DuckyClaw 连接 TuyaClaw
├── 快速开始
│   ├── 极速体验
│   ├── Step 1: 项目编译
│   ├── Step 2: 固件烧录
│   ├── Step 3: 设备授权
│   ├── Step 4: 设备手机配网
│   └── 设备调试
├── CLI 工具
│   ├── CLI - tos.py 开发工具
│   ├── tos.py idf 命令参考
│   └── GUI - tyutool 图形化工具
├── 构建系统
│   ├── 编译指导
│   ├── CMake、Kconfig 与组件模型
│   └── Kconfig 与工程配置
├── 硬件适配
│   ├── 适配新 Platform
│   ├── 创建 Platform
│   ├── 创建 Board
│   └── 创建 Project
├── 平台特定
│   ├── ESP32 快速开始
│   └── TUYA T5AI 管脚映射
├── AI 应用
│   └── MCP 工具合集
├── 常见问题
│   ├── 常见问题
│   └── 免费领取开发者授权码
├── 贡献指南
│   ├── 贡献指南
│   ├── 编码风格指南
│   └── Markdown 语法快速指南
└── 发布版本(v1.0.0 ~ v1.5.0)
```
