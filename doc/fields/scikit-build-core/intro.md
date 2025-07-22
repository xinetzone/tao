# `scikit-build-core` 概述

Scikit-build-core 是使用 CMake 构建 Python 扩展模块的构建后端。它在 `pyproject.toml` 中拥有简单而强大的静态配置系统，并通过 CMake 支持几乎无限的灵活性。它最初是为了满足科学用户的高要求而开发的，但可以构建任何使用 CMake 的包。

Scikit-build-core 是对经典 Scikit-build 的完全重写。Scikit-build 经典（基于 `setuptools`）的关键特性在这里也都有：

- 对大多数操作系统、编译器、IDE 和库的强大支持
- 支持 C++ 特性以及其他语言如 Fortran
- 支持多线程构建
- 简洁的 `CMakeFiles.txt`，替代长达数千行的易碎 `setuptools`/`distutils` 代码
- 支持在 Apple Silicon 和 Windows ARM 上进行交叉编译

Scikit-build-core 是基于 scikit-build（经典版）编写后发展的 Python 打包标准构建的。直接使用它提供了比经典 Scikit-build 以下功能：

- 更好的警告、错误和日志记录
- 没有关于未使用变量的警告
- 根据需要自动添加 Ninja 和/或 CMake
- 不依赖 `setuptools`、`distutils` 或 `wheel`
- 强大的配置系统，包括配置选项支持
- 自动包含 `CMAKE_PREFIX_PATH` 中的 `site-packages`
- FindPython 如果在 CMake < 3.26.1 上运行则回退移植（可配置），支持 PyPY SOABI 和有限 API / 稳定 ABI
- 通过配置选项支持 Limited API / Stable ABI 和无 python 标签
- 默认不使用慢速生成器搜索，不默认使用 ninja/make 或 MSVC，尊重 CMAKE_GENERATOR
- SDists 默认可重复生成（推荐使用 UNIX、Python 3.9+、未压缩比较）
- 支持在构建之间缓存（通过设置 build-dir 启用）
- 支持将内容写入额外的轮子文件夹（脚本、头文件、数据）
- 支持选择安装组件和构建目标
- 为模块和前缀目录提供专用入口点
- 几个集成的动态元数据插件（即将提供标准化支持）
- 实验性的可编辑模式支持，支持导入时的可选实验性自动重建和可选就地模式
- 支持 WebAssembly（Emscripten/ Pyodide）。
- 支持自由线程的 Python 3.13。

与经典 scikit-build 相比，存在以下限制：

- 最低支持的 CMake 版本是 3.15
- 最低支持的 Python 版本是 3.8（0.10.x 及更早版本支持 3.7+）
- 一些已知缺失的功能将在不久后开发：
- Wheels 不是完全可重复生成的（也不是大多数其他系统中的情况，包括 `setuptools`）
轮包尚未完全可重复生成（大多数其他系统，包括 setuptools 也是如此）
- 一些可编辑模式的注意事项（文档中已提及）。

也计划了其他后端：

- Setuptools 集成高度实验性
- Hatchling 插件高度实验性

## 示例

要使用 `scikit-build-core`，将其添加到你的 `build-system.requires` 中，并将 `scikit_build_core.build` 构建器指定为你的 `build-system.build-backend`。你不需要指定 `cmake` 或 `ninja`；如果系统版本不满足要求，`scikit-build-core` 将自动要求它们。

```toml
[build-system]
requires = ["scikit-build-core"]
build-backend = "scikit_build_core.build"

[project]
name = "scikit_build_simplest"
version = "0.0.1"
```

你可以（也应该）指定 `project` 中的其余条目，但这些是开始使用的最小要求。

示例 `CMakeLists.txt`:
```cmake
cmake_minimum_required(VERSION 3.15...3.30)
project(${SKBUILD_PROJECT_NAME} LANGUAGES C)

find_package(Python COMPONENTS Interpreter Development.Module REQUIRED)

Python_add_library(_module MODULE src/module.c WITH_SOABI)
install(TARGETS _module DESTINATION ${SKBUILD_PROJECT_NAME})
```

scikit-build-core 将从 CMake 3.26.1 中回退 FindPython 到较旧的 Python 版本，如果你是从 PyPy 构建，它将为你处理 PyPy。你需要将你想要的所有内容安装到 site-modules 内的完整最终路径中（因此你通常需要用包名作为前缀）。

更多示例在 [`tests/packages`](https://github.com/scikit-build/scikit-build-core/tree/main/tests/packages) 中。

## 配置

所有配置选项都可以放在 pyproject.toml 中，通过 `-C` / `--config-setting` 在构建时传递，或在 `-C` / `--config-settings` 中通过 `pip` 设置，也可以作为环境变量设置。`tool.scikit-build` 用于 `toml`， `skbuild.` 用于 `-C` 选项，或 `SKBUILD_*` 用于环境变量。

有关变量的完整参考和说明，请参阅[在线文档](https://scikit-build-core.readthedocs.io/en/latest/reference/configs.html)。

以下是一些快速总结和默认值：

```toml
[tool.scikit-build]
# The versions of CMake to allow as a python-compatible specifier.
cmake.version = ""

# A list of args to pass to CMake when configuring the project.
cmake.args = []

# A table of defines to pass to CMake when configuring the project. Additive.
cmake.define = {}

# The build type to use when building the project.
cmake.build-type = "Release"

# The source directory to use when building the project.
cmake.source-dir = "."

# The versions of Ninja to allow.
ninja.version = ">=1.5"

# Use Make as a fallback if a suitable Ninja executable is not found.
ninja.make-fallback = true

# The logging level to display.
logging.level = "WARNING"

# Files to include in the SDist even if they are skipped by default. Supports gitignore syntax.
sdist.include = []

# Files to exclude from the SDist even if they are included by default. Supports gitignore syntax.
sdist.exclude = []

# Try to build a reproducible distribution.
sdist.reproducible = true

# If set to True, CMake will be run before building the SDist.
sdist.cmake = false

# A list of packages to auto-copy into the wheel.
wheel.packages = ["src/<package>", "python/<package>", "<package>"]

# The Python version tag used in the wheel file.
wheel.py-api = ""

# Fill out extra tags that are not required.
wheel.expand-macos-universal-tags = false

# The CMake install prefix relative to the platlib wheel path.
wheel.install-dir = ""

# A list of license files to include in the wheel. Supports glob patterns.
wheel.license-files = ""

# Run CMake as part of building the wheel.
wheel.cmake = true

# Target the platlib or the purelib.
wheel.platlib = ""

# A set of patterns to exclude from the wheel.
wheel.exclude = []

# The build tag to use for the wheel. If empty, no build tag is used.
wheel.build-tag = ""

# If CMake is less than this value, backport a copy of FindPython.
backport.find-python = "3.26.1"

# Select the editable mode to use. Can be "redirect" (default) or "inplace".
editable.mode = "redirect"

# Turn on verbose output for the editable mode rebuilds.
editable.verbose = true

# Rebuild the project when the package is imported.
editable.rebuild = false

# Extra args to pass directly to the builder in the build step.
build.tool-args = []

# The build targets to use when building the project.
build.targets = []

# Verbose printout when building.
build.verbose = false

# Additional ``build-system.requires``.
build.requires = []

# The components to install.
install.components = []

# Whether to strip the binaries.
install.strip = true

# The path (relative to platlib) for the file to generate.
generate[].path = ""

# The template string to use for the file.
generate[].template = ""

# The path to the template file. If empty, a template must be set.
generate[].template-path = ""

# The place to put the generated file.
generate[].location = "install"

# A message to print after a build failure.
messages.after-failure = ""

# A message to print after a successful build.
messages.after-success = ""

# Add the python build environment site_packages folder to the CMake prefix paths.
search.site-packages = true

# List dynamic metadata fields and hook locations in this table.
metadata = {}

# Strictly check all config options.
strict-config = true

# Enable early previews of features not finalized yet.
experimental = false

# If set, this will provide a method for backward compatibility.
minimum-version = "0.11"  # current version

# The CMake build directory. Defaults to a unique temporary directory.
build-dir = ""

# Immediately fail the build. This is only useful in overrides.
fail = false
```

大多数 CMake 环境变量都应该得到支持，并且可以使用 `CMAKE_ARGS` 来设置额外的 CMake 参数。`ARCHFLAGS` 用于指定 macOS universal2 或交叉编译，就像 setuptools 一样。

您也可以指定 `[[tool.scikit-build.overrides]]` 来为不同系统自定义值。

## 用于构建的其他项目

Scikit-build-core 是二进制构建后端。还有其他二进制构建后端：

- [`py-build-cmake`](https://tttapa.github.io/py-build-cmake)：对 CMake 标准兼容构建器的另一种尝试。重点在于交叉编译。使用 Flit 内部实现。
- [`cmeel`](https://github.com/cmake-wheel/cmeel): 尝试创建符合标准的 CMake 构建器。专注于围绕 site-packages 中的一个特殊不可导入文件夹构建生态系统（类似于 scikit-build 使用 `cmake.*` 入口点，但基于文件夹）。
- [`meson-python`](https://mesonbuild.com/meson-python): 基于 meson 的构建后端；与 scikit-build-core 有一些维护者重叠。
- [`maturin`](https://www.maturin.rs/): 用于 Rust 项目的构建后端，使用 Cargo。
- [`enscons`](https://pypi.org/project/enscons): 基于 SCons 的后端，开发活动不多（但它早于所有现代标准支持的其他后端！）

如果你不需要二进制构建，就不需要使用二进制构建后端！有一些非常优秀的 Python 构建后端；推荐 [`hatchling`](https://hatch.pypa.io/latest)，它在为初学者提供良好默认值和支持高级用例方面取得了很好的平衡。这是 scikit-build-core 本身使用的工具。
