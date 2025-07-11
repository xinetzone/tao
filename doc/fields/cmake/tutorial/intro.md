# CMake 简介

参考：[intro](https://cmake.org/cmake/help/latest/index.html) & [精通CMake](https://cmake.org/cmake/help/book/mastering-cmake/)

CMake 是一款用于管理源代码构建的工具。最初，CMake 被设计为针对各种不同方言的 Makefile 的生成器，如今，CMake 既可以生成诸如 Ninja 这样的现代构建系统，也能为诸如 Visual Studio 和 Xcode 这类集成开发环境（IDE）生成项目文件。源码：[cmake git 仓库](https://gitlab.kitware.com/cmake/cmake)。

CMake 广泛用于 C 和 C++ 语言，但它也可用于构建其他语言的源代码。

## 源目录和二进制目录

CMake 项目同时具有源目录和二进制目录的概念。源目录是 `CMakeLists.txt` 文件所在的位置，项目的源文件和生成所需的所有其他文件都组织在该位置下。

binary 目录是创建构建生成的所有内容的位置。它通常也称为 `build` 目录。出于后面章节中将明确的原因，CMake 通常使用术语 binary directory，但在开发人员中，术语 build directory 往往更常用。这本书倾向于使用后一个术语，因为它通常更直观。CMake、所选的构建工具（make、Visual Studio 等）、CTest 和 CPack 都将在构建目录及其下面的子目录中创建各种文件。可执行文件、库、测试输出和包都在 build 目录中创建。CMake 还在 build 目录中创建了名为 `CMakeCache.txt` 的特殊文件，用于存储信息以供以后运行时重用。开发人员通常不需要关心 `CMakeCache.txt` 文件，但后面的章节将讨论与此文件相关的情况。构建工具的项目文件（Xcode 或 Visual Studio 项目文件、Makefile 等）也在构建目录中创建，这些项目文件不应置于版本控制之下。`CMakeLists.txt` 文件是项目的规范描述，生成的项目文件应被视为构建输出的一部分。

## 安装 CMake

参考 [Modern CMake 安装](https://cliutils.gitlab.io/modern-cmake/chapters/intro/installing.html)：

```bash
conda install anaconda::cmake
```

或者

```bash
pip install cmake
```

## 基本用法

CMake 以一个或多个 CMakeLists 文件作为输入，并生成用于各种原生开发工具的项目文件或 Makefile。

典型的 CMake 过程如下：

1. 项目定义在一个或多个 CMakeLists 文件中
2. CMake 配置并生成项目
3. 用户使用他们喜欢的本地开发工具构建项目

```{note}
CMakeLists 文件（实际上是指 `CMakeLists.txt`，但通常省略扩展名）是包含 CMake 语言中项目描述的纯文本文件。 `cmake-language` 以一系列注释、命令和变量表示。

您可能会好奇为什么 CMake 决定使用自己的语言，而不是使用 Python、Java 或 Tcl 等现有语言。主要原因在于 CMake 开发者不希望 CMake 运行时依赖额外的工具。如果要求使用这些其他语言，所有 CMake 用户都将需要安装该语言，甚至可能是该语言的特定版本。这还不包括完成部分 CMake 工作所需的语言扩展，这些扩展在性能和能力方面都是必要的。
```

运行 CMake 的最基本方法是通过 `cmake` 命令行实用程序。调用该工具的一种常见方法是将目录更改为 `CMakeLists.txt` 文件所在的位置，然后运行 `cmake`，将 `-G` 选项与生成器类型一起传递，将 `-B` 选项与构建目录一起传递：

```bash
cmake -G "Unix Makefiles" -B build
```

如果 `build` 目录不存在，则会自动创建该目录。如果省略 `-G` 选项，CMake 将根据主机平台选择生成器。在 CMake 3.15 或更高版本中，`CMAKE_GENERATOR` 环境变量可用于指定不同的默认生成器。

当 CMake 完成运行后，它将在 `build` 目录中保存 `CMakeCache.txt` 文件。CMake 使用此文件保存详细信息，以便在再次运行时，它可以重用第一次计算的信息并加快项目生成速度。如后面的章节所述，它还允许在运行之间保存开发人员选项。GUI 应用程序 `cmake-gui` 可用作运行 cmake 命令行工具的替代方法。

## Hello World

首先，考虑最简单的 CMakeLists 文件。从源文件编译可执行文件，CMakeLists 文件将包含三行：

```cmake
cmake_minimum_required(VERSION 3.20)
project(Hello)
add_executable(Hello Hello.c)
```

上面例子中的每一行都执行一个内置的 CMake 命令。参数之间用空格分隔，并且可以拆分为多行：

```cmake
add_executable(MyExe
  main.cpp
  src1.cpp
  src2.cpp
)
```

顶层 CMakeLists 文件的 第一行 应始终为 [`cmake_minimum_required`](https://cmake.org/cmake/help/latest/command/cmake_minimum_required.html#command:cmake_minimum_required)。这允许项目要求特定版本的 CMake，此外还允许 CMake 向后兼容。

任何顶层 CMakeLists 文件的下一行 应为 [`project`](https://cmake.org/cmake/help/latest/command/project.html#command:project) 命令。此命令设置项目名称，并可能指定其他选项，如语言或版本。

对于项目中每个调用 `project` 命令的目录，CMake 会生成一个顶层 `Makefile` 或 IDE 项目文件。项目将包含 `CMakeLists.txt` 文件中的所有目标以及由 [`add_subdirectory`](https://cmake.org/cmake/help/latest/command/add_subdirectory.html#command:add_subdirectory) 命令指定的任何子目录。如果 [`EXCLUDE_FROM_ALL`](https://cmake.org/cmake/help/latest/prop_dir/EXCLUDE_FROM_ALL.html#prop_dir:EXCLUDE_FROM_ALL) 选项在 `add_subdirectory` 命令中使用，生成的项目将不会出现在顶层 Makefile 或 IDE 项目文件中；这对于生成不属于主构建过程的子项目很有用。考虑一个包含多个示例的项目可以使用此功能，通过一次 CMake 运行生成每个示例的构建文件，但示例不会作为正常构建过程的一部分进行构建。

最后，使用 [`add_executable`](https://cmake.org/cmake/help/latest/command/add_executable.html#command:add_executable) 命令通过给定的源文件向项目添加可执行文件。

````{tip}
命令名称也不区分大小写，因此以下内容都是等效的：

```cmake
add_executable(MyExe main.cpp)
ADD_EXECUTABLE(MyExe main.cpp)
Add_Executable(MyExe main.cpp)
```

典型的样式各不相同，但如今公认的惯例是命令名称使用全部小写。这也是内置命令的 CMake 文档遵循的约定。
````