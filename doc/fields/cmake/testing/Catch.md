# Catch

[Catch2](https://github.com/catchorg/Catch2)（仅支持 C++11 的版本）是功能强大、符合习惯的测试解决方案，其哲学理念与 Python 的 PyTest 相似。它支持的编译器范围比 GTest 更广，并且能够快速支持新事物，例如在 macOS 上支持 M1 构建。它还有更小但更快的双胞胎版本 [doctest](https://github.com/onqtam/doctest)，后者编译速度快但缺少匹配器等特性。要在 CMake 项目中使用 Catch，有几种选项。

## 配置方法 

Catch 拥有良好的 CMake 支持，不过要使用它，你需要完整仓库。这可以通过子模块或 FetchContent 实现。[extended-project](https://gitlab.com/CLIUtils/modern-cmake/-/tree/master/examples/extended-project) 和 [fetch](https://gitlab.com/CLIUtils/modern-cmake/-/tree/master/examples/fetch) 示例都使用了 FetchContent。请参阅[文档](https://github.com/catchorg/Catch2/blob/v2.x/docs/cmake-integration.md#top)。

## 快速下载

这可能是最简单的方法，并且支持较旧版本的 CMake。你可以一次性下载包含所有内容的头文件：

```cmake
add_library(catch_main main.cpp)
target_include_directories(catch_main PUBLIC "${CMAKE_CURRENT_SOURCE_DIR}")
set(url https://github.com/philsquared/Catch/releases/download/v2.13.6/catch.hpp)
file(
  DOWNLOAD ${url} "${CMAKE_CURRENT_BINARY_DIR}/catch.hpp"
  STATUS status
  EXPECTED_HASH SHA256=681e7505a50887c9085539e5135794fc8f66d8e5de28eadf13a30978627b0f47)
list(GET status 0 error)
if(error)
  message(FATAL_ERROR "Could not download ${url}")
endif()
target_include_directories(catch_main PUBLIC "${CMAKE_CURRENT_BINARY_DIR}")
```

当 Catch 3 发布时，这将需要两次下载，因为现在需要两个文件（但不再需要编写 main.cpp）。`main.cpp` 看起来像这样：

```cpp
#define CATCH_CONFIG_MAIN
#include "catch.hpp"
```

## Vendoring

如果你直接将 Catch 的单个包含版本放入你的项目中，你需要添加 Catch：

```cmake
# Prepare "Catch" library for other executables
set(CATCH_INCLUDE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/extern/catch)
add_library(Catch2::Catch IMPORTED INTERFACE)
set_property(Catch2::Catch PROPERTY INTERFACE_INCLUDE_DIRECTORIES "${CATCH_INCLUDE_DIR}")
```

然后，你会链接到 `Catch2::Catch`。这本来可以作为 INTERFACE 目标，因为你不会导出你的测试。

## 直接包含

如果你使用 `ExternalProject`、`FetchContent` 或 git 子模块添加库，你也可以 `add_subdirectory` Catch（CMake 3.1+）。

Catch 还提供了两个 CMake 模块，你可以使用它们将各个测试注册到 CMake 中。