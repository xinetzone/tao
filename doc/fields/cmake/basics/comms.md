# 与你的代码通信

## 配置文件

CMake 允许你使用 `configure_file` 从你的代码中访问 CMake 变量。这个命令将文件（传统上以 `.in` 结尾）从一个地方复制到另一个地方，并替换它找到的所有 CMake 变量。如果你想要避免替换输入文件中现有的 `${}` 语法，可以使用 `@ONLY` 关键字。如果你只是把它当作 f`ile(COPY` 的替代品，还有 `COPY_ONLY` 关键字。

这项功能使用非常频繁；例如，在 `Version.h.in` 上：

### `Version.h.in`

```ini
#pragma once

#define MY_VERSION_MAJOR @PROJECT_VERSION_MAJOR@
#define MY_VERSION_MINOR @PROJECT_VERSION_MINOR@
#define MY_VERSION_PATCH @PROJECT_VERSION_PATCH@
#define MY_VERSION_TWEAK @PROJECT_VERSION_TWEAK@
#define MY_VERSION "@PROJECT_VERSION@"
```

### CMake 行

```cmake
configure_file (
    "${PROJECT_SOURCE_DIR}/include/My/Version.h.in"
    "${PROJECT_BINARY_DIR}/include/My/Version.h"
)
```

在构建你的项目时，你也应该包含二进制包含目录。如果你想在头文件中放入任何 `true/false` 变量，CMake 有特定的 `#cmakedefine` 和 `#cmakedefine01` 替换来生成适当的定义行。

你也可以（而且经常这样做）使用它来生成 `.cmake` 文件，例如配置文件（参见[安装](https://cliutils.gitlab.io/modern-cmake/chapters/install/installing.html)）。

## 读取文件

另一个方向也可以实现；你可以从源文件中读取某些内容（比如版本号）。例如，如果你有仅包含头文件的库，并且希望它能够有或没有 CMake 的情况下可用，那么这将是处理版本的最佳方式。这看起来会像这样：

```cmake
# Assuming the canonical version is listed in a single line
# This would be in several parts if picking up from MAJOR, MINOR, etc.
set(VERSION_REGEX "#define MY_VERSION[ \t]+\"(.+)\"")

# Read in the line containing the version
file(STRINGS "${CMAKE_CURRENT_SOURCE_DIR}/include/My/Version.hpp"
    VERSION_STRING REGEX ${VERSION_REGEX})

# Pick out just the version
string(REGEX REPLACE ${VERSION_REGEX} "\\1" VERSION_STRING "${VERSION_STRING}")

# Automatically getting PROJECT_VERSION_MAJOR, My_VERSION_MAJOR, etc.
project(My LANGUAGES CXX VERSION ${VERSION_STRING})
```

在上面， `file(STRINGS file_name variable_name REGEX regex)` 选取匹配正则表达式的行；然后使用相同的正则表达式来选取括号捕获组中的版本部分。`Replace` 操作使用反向引用来输出仅该一组内容。