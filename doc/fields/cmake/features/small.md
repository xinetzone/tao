# 添加功能

有很多编译器和链接器设置。当你需要添加一些特殊功能时，你可以先检查 CMake 是否支持它；如果支持，你可以避免明确绑定到特定编译器版本。更棒的是，你可以在你的 CMakeLists 文件中解释你的意图，而不是随意堆砌标志。

## 位置无关代码

[位置无关代码](https://cmake.org/cmake/help/latest/variable/CMAKE_POSITION_INDEPENDENT_CODE.html)通常被称为 `-fPIC` 标志。大多数情况下，你不需要做任何事。CMake 会为 `SHARED` 或 `MODULE` 库包含该标志。如果你确实需要它：

```cmake
set(CMAKE_POSITION_INDEPENDENT_CODE ON)
```

可以全局设置，或者：

```cmake
set_target_properties(lib1 PROPERTIES POSITION_INDEPENDENT_CODE ON)
```


可以显式地为某个目标设置 `ON` （或 `OFF`）。

## 小库

如果你需要链接到 `dl` 库，在 Linux 上使用 `-ldl` ，只需在 `target_link_libraries` 命令中使用内置的 CMake 变量 `${CMAKE_DL_LIBS}`。不需要模块或 `find_package`。 （这会添加所需的所有内容以获取 `dlopen` 和 `dlclose`）

不幸的是，数学库没有那么幸运。如果你需要显式链接到它，你总是可以这样做 `target_link_libraries(MyTarget PUBLIC m)`，但使用 CMake 的通用 [`find_library`](https://cmake.org/cmake/help/latest/command/find_library.html) 会更好：

```cmake
find_library(MATH_LIBRARY m)
if(MATH_LIBRARY)
    target_link_libraries(MyTarget PUBLIC ${MATH_LIBRARY})
endif()
```

你可以通过快速搜索轻松找到 `Find*.cmake` 为此和其他你需要的库；大多数主要软件包都有 CMake 模块的辅助库。有关更多信息，请参阅现有软件包包含章节。

## 跨过程优化

[`INTERPROCEDURAL_OPTIMIZATION`](https://cmake.org/cmake/help/latest/prop-tgt/INTERPROCEDURAL_OPTIMIZATION.html) ，即链接时优化，以及 `-flto` 标志，在最新的 CMake 版本中可用。你可以通过 [`CMAKE_INTERPROCEDURAL_OPTIMIZATION`](https://cmake.org/cmake/help/latest/variable/CMAKE_INTERPROCEDURAL_OPTIMIZATION.html) （仅限 CMake 3.9 及以上版本）或目标的 [`INTERPROCEDURAL_OPTIMIZATION`](https://cmake.org/cmake/help/latest/prop-tgt/INTERPROCEDURAL_OPTIMIZATION.html) 属性来启用此功能。GCC 和 Clang 的支持是在 CMake 3.8 中添加的。如果你设置了 `cmake_minimum_required(VERSION 3.9)` 或更高版本（参见 [`CMP0069`](https://cmake.org/cmake/help/latest/policy/CMP0069.html)，如果编译器不支持，将此值设置为 ON 在目标上是一个错误。你可以使用内置 [`CheckIPOSupported`](https://cmake.org/cmake/help/latest/module/CheckIPOSupported.html) 模块中的 `check_ipo_supported()` 来在操作前查看是否支持。3.9 风格使用的示例：

```cmake
include(CheckIPOSupported)
check_ipo_supported(RESULT result)
if(result)
  set_target_properties(foo PROPERTIES INTERPROCEDURAL_OPTIMIZATION TRUE)
endif()
```
