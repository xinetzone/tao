# 使用 Conan 管理依赖项

本章将详细介绍如何通过 Conan 实现依赖管理，主要内容包括：

- 基于 `CMake` 和 `zlib` 的 C 语言项目示例
- 使用 `conanfile.txt` 声明项目依赖
- 构建工具链管理（`CMake`/`msys2`/`MinGW` 等）
- 核心概念解析：`settings` 与 `options` 配置
- 从 `conanfile.txt` 迁移到 `conanfile.py`
- 跨平台编译配置（`build`/`host` 模式）
- 版本控制与依赖锁定机制

```{toctree}
build-simple-cmake-project
use-tools-as-conan-packages
configurations
how-to-use-conanfile-py
cross-building-with-conan
versioning
```
