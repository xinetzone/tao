# CMake 基础知识

## 最低版本

[`cmake_minimum_required`](https://cmake.org/cmake/help/latest/command/cmake_minimum_required.html) 是每个 `CMakeLists.txt` 的第一行，这是 CMake 查找的文件所需的名字：

```cmake
cmake_minimum_required(VERSION 3.15)
```

简单介绍一下 CMake 的语法。命令名称 `cmake_minimum_required` 不区分大小写，所以通常的做法是使用小写。`VERSION` 是这个函数的特殊关键字。版本值跟在关键字后面。

这一行很特别！CMake 的版本也会决定策略，这些策略定义了行为变化。所以，如果你将 `minimum_required` 设置为 `VERSION 2.8`，例如在最新的 CMake 版本中，你会在 macOS 上得到错误的链接行为。如果你将其设置为 `3.3` 或更低版本，你将得到错误的隐藏符号行为等。策略和版本的列表可以在 [policies](https://cmake.org/cmake/help/latest/manual/cmake-policies.7.html) 中找到。

从 CMake 3.12 开始，这支持范围语法，例如 `VERSION 3.15...4.0`；这意味着你支持最低到 3.15，但也用新的策略设置测试到了 4.0。这对需要更好设置的用戶来说要友好得多，并且由于语法中的技巧，它与较旧版本的 CMake 向后兼容（尽管实际上运行 CMake 3.1-3.11 只会设置旧版本的策略，因为这些版本没有特别处理这种情况）。新版本的策略对 macOS 和 Windows 用戶来说通常最重要，他们通常也使用最新版本的 CMake。

新项目应该这样做：

```cmake
cmake_minimum_required(VERSION 3.15...4.0)
```

如果你确实需要在这里设置为低值，你可以使用 [`cmake_policy`](https://cmake.org/cmake/help/latest/command/cmake_policy.html) 来有条件地提高策略级别或设置特定策略。

## 设置项目

现在，每个顶层 CMake 文件都会有以下这一行：

```cmake
project(MyProject VERSION 1.0
                  DESCRIPTION "Very nice project"
                  LANGUAGES CXX)
```

字符串被引号括起来，空白字符不重要，项目的名称是第一个参数（位置参数）。这里所有的关键字参数都是可选的。版本号设置了一组变量，如 `MyProject_VERSION` 和 `PROJECT_VERSION`。语言是 `C`、`CXX`、`Fortran`、 `ASM`（CMake 3.8+）、`CUDA`（3.8+）、`CSharp`（CMake 3.15+实验性）。`C` `CXX` 是默认值。在 CMake 3.9 中， `DESCRIPTION` 被添加用于设置项目描述。`project` 的文档可能有帮助。

```{tip}
你可以用 `#` 字符添加[注释](https://cmake.org/cmake/help/latest/manual/cmake-language.7.html#comments)。CMake 也有内联注释语法，但很少使用。
```

[`project`](https://cmake.org/cmake/help/latest/command/project.html#command:project) 命令的文档可能有帮助。

## 创建可执行文件

尽管库要有趣得多，也将把大部分时间花在它们上面，但让我们从简单的可执行文件开始。

```cmake
add_executable(one two.cpp three.h)
```

这里有几个要点需要说明。`one` 既是生成的可执行文件名，也是创建的 CMake 目标名（我保证很快会更多地谈到目标）。接下来是源文件列表，你可以列出任意多个。CMake 很聪明，只会编译源文件扩展名。头文件在大多数情况下会被忽略；唯一列出它们的原因是让它们在 IDE 中显示出来。在许多 IDE 中，目标会显示为文件夹。有关通用构建系统和目标的更多信息，请参阅 [buildsystem](https://cmake.org/cmake/help/latest/manual/cmake-buildsystem.7.html)。

## 创建库

制作库使用 `add_library`，这非常简单：

```bash
add_library(one STATIC two.cpp three.h)
```

你可以选择库的类型，`STATIC`、`SHARED` 或 `MODULE`。如果你不选择这个类型， `BUILD_SHARED_LIBS` 的值将用于在 `STATIC` 和 `SHARED` 之间选择。

在接下来的章节中，你会发现，你经常需要创建虚构的目标，即不需要编译的目标，例如用于头文件库。这被称为 `INTERFACE` 库，是另一种选择；唯一的不同之处在于它后面不能跟文件名。

你也可以使用现有的库来创建 `ALIAS` 库，这仅仅是为目标提供了新名称。这样做的好处是你可以创建名称中包含 `::` 的库（你稍后会看到）。[^1]

[^1]: `::` 语法原本是为 `INTERFACE` `IMPORTED` 库设计的，这些库明确应该是在当前项目外部定义的。但由于这个原因，大多数 `target_*` 命令在 IMPORTED 库上无法使用，使得自行设置变得困难。所以暂时不要使用 `IMPORTED` 关键字，而是使用 `ALIAS` 目标；在开始导出目标之前，这样是没问题的。这个限制在 CMake 3.11 中得到了修复。

## 目标是你朋友

现在已经指定了目标，如何为其添加信息呢？例如，也许它需要包含目录：

```cmake
target_include_directories(one PUBLIC include)
```

[`target_include_directories`](https://cmake.org/cmake/help/latest/command/target_include_directories.html) 为目标添加包含目录。`PUBLIC` 对于可执行文件来说意义不大；对于库来说，它让 CMake 知道任何链接到此目标的任务都必须也需要这个包含目录。其他选项有 `PRIVATE` （只影响当前目标，不影响依赖），和 `INTERFACE` （仅依赖需要）。

然后可以链接目标：

```cmake
add_library(another STATIC another.cpp another.h)
target_link_libraries(another PUBLIC one)
```

[`target_link_libraries`](https://cmake.org/cmake/help/latest/command/target_link_libraries.html) 可能是 CMake 中最实用也最令人困惑的命令。它接受目标（`another`），如果提供了目标，则添加依赖。如果没有该名称（`one`）的目标存在，则会在你的路径上添加名为 `one` 的库的链接（这也是该命令名称的由来）。或者你可以给它库的完整路径。或者链接器标志。为了增加最终的困惑，经典的 CMake 允许你跳过 PUBLIC 等关键字的选择。如果这在目标上完成，如果你在链的下方尝试混合风格，你会得到错误。

专注于在所有地方使用目标，并在所有地方使用关键字，你就能顺利解决问题。

目标可以有包含目录、链接库（或链接目标）、编译选项、编译定义、编译特性（参见 C++11 章节），以及更多。正如你将在两个包含项目章节中看到的，你通常可以得到目标（并且总是创建目标），以表示你使用的所有库。即使是那些不是真正库的东西，比如 OpenMP，也可以用目标来表示。这就是为什么 Modern CMake 如此出色！
