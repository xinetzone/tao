# mise 开发环境工具技术调研文档

> 📋 **文档说明：** 本文档为 mise 的原始技术调研记录，已归档保存。日常使用请优先查阅系列知识库文档（01-08），本文档仅保留调研特有的深层技术细节作为补充参考。

---

## 产品概述

详细的 mise 产品介绍请查阅 [产品介绍](../../references/mise/01-产品介绍.md)。

### 什么是 mise？

**mise**（官方标注为 pronounced "meez"，读作 /miːz/）是一个在一个 CLI 中管理开发工具、环境变量与任务的开发环境工具。它的设计理念来自专业厨房中的 "mise en place"（/miːz ɑːn ˈplɑːs/，意为“准备就绪”）概念，即在开始工作前将所有工具和材料准备妥当。

### GitHub 统计
- Star 数：28.3k+
- 校准时 GitHub 最新 Release：v2026.5.13
- 主要语言：Rust

---

## 安装与配置

### 支持的操作系统

| 操作系统 | 支持状态 | 备注 |
|---------|---------|------|
| Linux (所有发行版) | ✅ 支持 | 通过 apt、dnf、apk、pacman 等包管理器 |
| macOS | ✅ 支持 | 通过 Homebrew、安装脚本 |
| Windows | ✅ 支持 | 通过 Scoop、winget、手动安装 |

### 安装方式

#### 1. 快速安装脚本（推荐）
详见 [快速入门 > 安装 mise](../../references/mise/02-快速入门.md)

#### 2. Shell 特定安装（自动配置激活）
```bash
# zsh
curl https://mise.run/zsh | sh

# bash
curl https://mise.run/bash | sh

# fish
curl https://mise.run/fish | sh
```

#### 3. 包管理器安装
详见 [快速入门 > 安装 mise](../../references/mise/02-快速入门.md)

#### 4. Cargo 安装（Rust 用户）
```bash
# 从源码编译
cargo install --locked mise

# 使用 cargo-binstall（更快）
cargo install cargo-binstall
cargo binstall mise
```

#### 5. npm 安装
```bash
npm install -g @jdxcode/mise
```

#### 6. GitHub Releases 手动下载
```bash
curl -L https://github.com/jdx/mise/releases/download/v2026.5.13/mise-v2026.5.13-linux-x64 > /usr/local/bin/mise
chmod +x /usr/local/bin/mise
```

### Shell 激活配置

Shell 激活的完整步骤详见 [快速入门 > 配置 Shell 激活](../../references/mise/02-快速入门.md)。

### 验证安装
```bash
# 检查版本
~/.local/bin/mise --version

# 运行诊断
mise doctor
```

### 配置文件

#### 全局配置
- 位置：`~/.config/mise/config.toml`

#### 项目配置
- 位置：项目根目录下的 `mise.toml` 或 `.mise.toml`
- 支持遗留格式：`.tool-versions`（与 asdf 兼容）

#### 配置层级
mise 支持嵌套配置，配置从全局到项目层级叠加：
```
~/.config/mise/config.toml    # 全局默认
~/work/mise.toml              # 工作区特定
~/work/project/mise.toml      # 项目特定覆盖
```

---

## 核心功能特性

各功能的详细说明请分别查阅 [基础使用](../../references/mise/03-基础使用.md)、[进阶功能](../../references/mise/04-进阶功能.md)、[配置详解](../../references/mise/05-配置详解.md)。

### 1. 后端架构

mise 支持多种后端（Backends）来安装工具：

关于多后端架构的完整说明，详见 [进阶功能 > 多后端架构](../../references/mise/04-进阶功能.md)。

### 2. 工具选项

#### 安装后钩子（postinstall）
```toml
[tools]
node = { version = "22", postinstall = "corepack enable" }
```

#### 操作系统限制
```toml
[tools]
# 仅在 Linux 和 macOS 安装
ripgrep = { version = "latest", os = ["linux", "macos"] }

# 仅在 Windows 安装
"npm:windows-terminal" = { version = "latest", os = ["windows"] }
```

#### 操作系统/架构组合
```toml
[tools]
# 仅在 macOS ARM64 和所有 Linux 安装（跳过 macOS x86_64）
hk = { version = "latest", os = ["linux", "macos/arm64"] }

# 仅在 Linux x86_64 安装
mytool = { version = "latest", os = ["linux/x64"] }
```

支持的架构标识：
- `arm64` 或 `aarch64`
- `x64` 或 `x86_64` 或 `amd64`

#### 工具依赖
```toml
[tools]
python = "3.12.11"
"pipx:ruff" = { version = "latest", depends = ["python"] }
```

---

## 主要命令详解

命令的详细使用说明请查阅 [基础使用](../../references/mise/03-基础使用.md)。

### 1. `mise shell` - 设置 Shell 环境

**功能：** 为当前 Shell 会话设置工具版本

```bash
# 在当前 Shell 使用特定版本
mise shell node@18

# 多个工具
mise shell node@18 python@3.10
```

### 2. `mise local/global` - 设置本地/全局版本

**功能：** 与 asdf 兼容的命令

```bash
# 设置本地版本（写入 .tool-versions）
mise local node 20.11.0

# 设置全局版本
mise global node 20.11.0
```

### 3. `mise trust` - 信任配置文件

**功能：** 安全机制 - 首次使用项目配置时需要确认信任

```bash
# 信任当前目录的配置
mise trust

# 信任所有配置（不推荐，仅在受控环境中使用）
mise settings trusted_config_paths=["/"]
```

---

## 插件生态系统

### 支持的工具语言

mise 支持 900+ 工具，包括但不限于：

| 类别 | 工具示例 |
|-----|---------|
| **编程语言** | node, python, ruby, go, rust, java, deno, php, elixir, swift |
| **基础设施** | terraform, kubectl, helm, docker, kustomize |
| **开发工具** | ripgrep, fd, bat, exa, jq, yq |
| **数据库** | postgresql, mysql, redis, mongodb |

### 插件开发

mise 支持三种类型的插件开发：

#### 1. 工具插件（Tool Plugins）
用于管理特定语言或工具的版本

#### 2. 后端插件（Backend Plugins）
扩展支持新的包管理生态系统

#### 3. 环境插件（Environment Plugins）
扩展环境变量管理功能

### 插件 API

#### Lua 模块系统
mise 使用 Lua 作为插件开发语言：
```lua
-- metadata.lua
PLUGIN = {
  name = "my-plugin",
  version = "1.0.0",
  depends = { "go" },
}
```

### 与 asdf 插件兼容性

mise 兼容 asdf `.tool-versions` 并可按需使用 asdf 插件 插件，但提供了增强功能：
- 更好的安全性
- 更快的性能
- 更丰富的 API

---

## 与其他版本管理工具对比

mise 相比 asdf、nvm、pyenv/rbenv/goenv 等工具，在性能（Rust 实现/工具调用无 shim 额外跳转）、安全性（信任机制、GitHub Release/后端校验与安装来源治理）和用户体验（统一管理/模糊匹配）方面具有显著优势。完整的竞品对比速查表详见 [mise 特性一览](../../references/mise/mise-特性一览.md)。

### 关键差异说明

**性能：**
- asdf 的 shim 设计会让工具调用经过 shim 分发路径
- mise 的官方说明强调其不依赖工具调用时的 shim 额外跳转，并通过目录切换时的激活机制更新环境
- 归档调研结论保留为定性对比：mise 在日常交互中的延迟感通常更低，但此处不记录缺乏官方证据支撑的具体耗时数值

**安全性：**
- asdf 插件由社区个人维护，无代码审查
- mise 积极将插件迁移到受控组织
- mise 支持 GPG、Cosign、SLSA 等签名验证

**UX 差异：**
- asdf 需要多步操作：`asdf plugin add node` → `asdf install node latest:20` → `asdf local node latest:20`
- mise 一步完成：`mise use node@20`
- mise 处处支持模糊匹配

---

## 常见问题与解决方案

更多常见问题及解决方案详见 [常见问题](../../references/mise/07-常见问题.md)。

---

## 最佳实践与使用技巧

完整的最佳实践指南详见 [最佳实践](../../references/mise/06-最佳实践.md)。

---

## 总结

本文档为 mise 技术调研的原始记录。完整的知识库请从 [README](../../references/mise/README.md) 开始查阅。

---

**最后更新：** 2026-05-22
**文档版本：** v2.0
**调研范围：** 官方文档、GitHub 仓库、社区资源
