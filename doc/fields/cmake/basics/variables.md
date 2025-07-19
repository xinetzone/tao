# 变量和缓存

## 局部变量

局部变量是这样设置的：

```cmake
set(MY_VARIABLE "value")
```

变量的名称通常是全大写，后面跟着值。通过使用 `${}` 访问变量，例如 `${MY_VARIABLE}`。CMake 有作用域的概念；只要你在同一个作用域内，就可以访问设置变量的值。如果你离开一个函数或子目录中的文件，变量将不再被定义。你可以使用 `PARENT_SCOPE` 在当前作用域的上一级作用域中设置变量。

列表在你设置它们时就是值的序列：

```bash
set(MY_LIST "one" "two")
```

它们在内部变成 `;` 分隔的值。所以这是相同的语句：

```bash
set(MY_VARIABLE "one;two")
```

`list(` 命令有用于处理列表的工具， `separate_arguments` 会将空格分隔的字符串转换为列表（就地）。请注意，如果 CMake 中的值没有空格，那么未加引号的值与加引号的值相同；这允许你在处理你知道不可能包含空格的值时跳过引号的大部分时间。

当使用 `${}` 语法展开变量时，所有关于空格的规则都适用。在路径方面要特别小心；路径可以随时包含空格，并且当它是变量时应该始终加引号（永远不要写 `${MY_PATH}`，应该始终写 `"${MY_PATH}"`）。

## 缓存变量

如果你想从命令行设置变量，CMake 提供了变量缓存。一些变量已经在这里了，比如 `CMAKE_BUILD_TYPE`。声明变量并在它尚未设置时设置的语法是：

```cmake
set(MY_CACHE_VARIABLE "VALUE" CACHE STRING "Description")
```

这不会替换现有的值。这是为了让你可以在命令行上设置这些变量，并且在 CMake 文件执行时不会被覆盖。如果你想将这些变量用作临时的全局变量，那么你可以这样做：

```cmake
set(MY_CACHE_VARIABLE "VALUE" CACHE STRING "" FORCE)
mark_as_advanced(MY_CACHE_VARIABLE)
```

第一行将强制设置值，无论什么情况，而第二行将防止变量在运行 `cmake -L ..` 或使用 GUI 时出现在变量列表中。这种情况非常常见，你也可以使用 `INTERNAL` 类型来实现相同的功能（尽管从技术上讲它强制使用 `STRING` 类型，但这不会影响任何依赖于该变量的 CMake 代码）：

```cmake
set(MY_CACHE_VARIABLE "VALUE" CACHE INTERNAL "")
```

由于 `BOOL` 是一种非常常见的变量类型，你可以使用快捷方式更简洁地设置它：

```cmake
option(MY_OPTION "This is settable from the command line" OFF)
```

对于 `BOOL` 数据类型， `ON` 和 `OFF` 有几种不同的表述方式。

参见 [cmake-variables](https://cmake.org/cmake/help/latest/manual/cmake-variables.7.html) 了解 CMake 中已知的变量列表。

## 环境变量

你也可以 `set(ENV{variable_name} value)` 获取 `$ENV{variable_name}` 环境变量，尽管通常最好避免这样做。

## 缓存

缓存实际上只是文本文件 `CMakeCache.txt`，当你在运行 CMake 时会在构建目录中创建。这就是 CMake 记住你设置的任何内容的方式，因此你不必每次重新运行 CMake 时都重新列出你的选项。

## 属性

CMake 存储信息的另一种方式是使用属性。这类似于变量，但它附加到某个其他项目上，比如目录或目标。全局属性可以是有用的未缓存的全局变量。许多目标属性是从带有前缀 `CMAKE_` 的匹配变量初始化的。所以设置 `CMAKE_CXX_STANDARD`，例如，将意味着所有新创建的目标在创建时 `CXX_STANDARD` 会被设置为那个值。设置属性有两种方式：

```bash
set_property(TARGET TargetName
             PROPERTY CXX_STANDARD 11)

set_target_properties(TargetName PROPERTIES
                      CXX_STANDARD 11)
```

第一种形式更通用，可以一次性设置多个目标/文件/测试，并且具有有用的选项。第二种是快捷方式，用于在一个目标上设置多个属性。你也可以类似地获取属性：

```cmake
get_property(ResultVariable TARGET TargetName PROPERTY CXX_STANDARD)
```

参见 [cmake-properties](https://cmake.org/cmake/help/latest/manual/cmake-properties.7.html) 获取所有已知属性的列表。在某些情况下，你也可以创建自己的属性。