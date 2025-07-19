# 调试代码

你可能需要调试你的 CMake 构建，或者调试你的 C++ 代码。这里都涵盖了。

## CMake 调试

首先，让我们看看如何调试 CMakeLists 或其他 CMake 文件。

### 打印变量

在 CMake 中，传统的打印语句方法如下：

```cmake
message(STATUS "MY_VARIABLE=${MY_VARIABLE}")
```

然而，内置模块使这更加简单：

```cmake
include(CMakePrintHelpers)
cmake_print_variables(MY_VARIABLE)
```

如果你想要打印出某个属性，这样要好用得多！你不需要逐个获取每个目标的属性（或其他具有属性的项，例如 `SOURCES`、 `DIRECTORIES`、 `TESTS` 或 `CACHE_ENTRIES` ——某些原因下全局属性似乎缺失了），你只需直接列出它们并打印出来：

```cmake
cmake_print_properties(
    TARGETS my_target
    PROPERTIES POSITION_INDEPENDENT_CODE
)
```

### 跟踪运行情况

你是否想要精确地查看你的 CMake 文件中发生了什么，以及何时发生的？ `--trace-source="filename"` 功能非常棒。你提供的文件中运行的每一行都会在运行时被回显到屏幕上，让你能够精确地跟踪发生的情况。此外还有相关的选项，但它们往往会让你被大量的输出淹没。

例如：

```bash
cmake -S . -B build --trace-source=CMakeLists.txt
```

如果你添加 `--trace-expand`，变量将被展开为其值。

## 在调试模式下构建

对于单配置生成器，你可以使用 `-DCMAKE_BUILD_TYPE=Debug` 来构建你的代码以获取调试标志。在多配置生成器（如许多 IDE）中，你可以在 IDE 中选择配置。这种模式有独特的标志（以 `_DEBUG` 结尾的变量与 `_RELEASE` 不同），以及生成器表达式值 `CONFIG:Debug` 或 `CONFIG:Release`。

一旦你进行了调试构建，你可以在其上运行调试器，例如 `gdb` 或 `lldb`。