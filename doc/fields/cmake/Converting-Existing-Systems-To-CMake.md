# 转换现有系统到 CMake

参考：
- [将现有系统转换为 CMake](https://cmake.org/cmake/help/book/mastering-cmake/chapter/Converting%20Existing%20Systems%20To%20CMake.html)

对于许多人来说，与 CMake 打交道的第一件事就是将现有的项目从使用旧的构建系统转换为使用 CMake。这个过程可能相当简单，但有几个问题需要考虑。本节将探讨这些问题，并提供一些将项目有效转换为 CMake 的建议。在转换为 CMake 时需要考虑的第一个问题是项目的目录结构。

## 源代码目录结构

大多数小型项目将源代码放在顶层目录或名为 `src` 或 `source` 的目录中。即使所有源代码都在子目录中，也强烈建议为顶层目录创建 `CMakeLists` 文件。原因有两个。首先，对于某些人来说，必须在项目的子目录上运行 CMake，而不是主目录上，这可能会让人感到困惑。其次，你可能希望从其他目录安装文档或其他支持文件。通过在项目的顶层放置 `CMakeLists` 文件，你可以使用 `add_subdirectory` 命令进入文档目录，其 `CMakeLists` 文件可以安装文档（你可以为文档目录创建没有目标或源代码的 `CMakeLists` 文件）。

对于源代码分布在多个目录中的项目，有几个选项。许多基于 `Makefile` 的项目使用的选项是在顶层目录中有单一的 `Makefile`，列出要编译的所有源文件。例如：

```
SOURCES=\
  subdir1/foo.cxx \
  subdir1/foo2.cxx \
  subdir2/gah.cxx \
  subdir2/bar.cxx
```

这种方法使用 CMake 时，使用类似的语法也同样有效：

```cmake
set(SOURCES
  subdir1/foo.cxx
  subdir1/foo2.cxx
  subdir1/gah.cxx
  subdir2/bar.cxx
  )
```

另一种选择是让每个子目录构建一个库或多个库，然后可以将这些库链接到可执行文件中。在这种情况下，每个子目录会定义自己的源文件列表，并添加相应的目标。第三种选择是前两种的结合；每个子目录可以有一个 `CMakeLists` 文件来列出其源文件，但顶层 `CMakeLists` 文件不会使用 `add_subdirectory` 命令进入子目录。相反，顶层 `CMakeLists` 文件将使用 `include` 命令包含每个子目录的 `CMakeLists` 文件。例如，顶层的 CMakeLists 文件可能包含以下代码

```cmake
# collect the files for subdir1
include(subdir1/CMakeLists.txt)
foreach(FILE ${FILES})
  set(subdir1Files ${subdir1Files} subdir1/${FILE})
endforeach()

# collect the files for subdir2
include(subdir2/CMakeLists.txt)
foreach(FILE ${FILES})
  set(subdir2Files ${subdir2Files} subdir2/${FILE})
endforeach()

# add the source files to the executable
add_executable(foo ${subdir1Files} ${subdir2Files})
```

而子目录中的 `CMakeLists` 文件可能如下所示：

```cmake
# list the source files for this directory
set(FILES
  foo1.cxx
  foo2.cxx
  )
```

你使用哪种方法完全取决于你。对于大型项目，当进行更改时，拥有多个共享库确实可以显著提高构建时间。对于小型项目，其他两种方法也有其优势。这里的主要建议是选择一种策略并坚持下去。

## 构建目录

接下来需要考虑的是将生成的目标文件、库和可执行文件放在哪里。有几种不同的常用方法，其中一些方法与 CMake 配合得更好。推荐策略是将二进制文件放在与源代码树具有相同结构的独立树中。例如，如果源代码树如下所示：

```bash
foo/
  subdir1
  subdir2
```

二进制树可能看起来像这样：

```bash
foobin/
  subdir1
  subdir2
```

对于某些 Windows 生成器，如 Visual Studio，构建文件实际上会保存在与所选配置匹配的子目录中；例如 debug、release 等。

如果你需要从同一个源代码树支持多种架构，强烈推荐使用如下所示的目录结构：

```bash
projectfoo/
  foo/
    subdir1
    subdir2
  foo-linux/
    subdir1
    subdir2
  foo-osx/
    subdir1
    subdir2
  foo-solaris/
    subdir1
    subdir2
```

那样，每种架构都有自己的构建目录，并且不会与其他架构相互干扰。请记住，不仅对象文件保存在二进制目录中，而且任何配置文件通常也会写入二进制树中。在 UNIX 项目中主要发现的另一种树结构是，不同架构的二进制文件保存在源树的子目录中（见下文）。CMake 在这种结构下工作效果不佳，因此我们建议切换到上面所示的独立构建树结构。

```bash
foo/
  subdir1/
    linux
    solaris
    hpux
  subdir2/
    linux
    solaris
    hpux
```

CMake 提供了三个变量用于控制二进制目标文件的输出位置。它们分别是 [CMAKE_RUNTIME_OUTPUT_DIRECTORY](https://cmake.org/cmake/help/latest/variable/CMAKE_RUNTIME_OUTPUT_DIRECTORY.html#variable:CMAKE_RUNTIME_OUTPUT_DIRECTORY) 、 [CMAKE_LIBRARY_OUTPUT_DIRECTORY](https://cmake.org/cmake/help/latest/variable/CMAKE_LIBRARY_OUTPUT_DIRECTORY.html#variable:CMAKE_LIBRARY_OUTPUT_DIRECTORY) 和 [CMAKE_ARCHIVE_OUTPUT_DIRECTORY](https://cmake.org/cmake/help/latest/variable/CMAKE_ARCHIVE_OUTPUT_DIRECTORY.html#variable:CMAKE_ARCHIVE_OUTPUT_DIRECTORY) 变量。这些变量用于初始化库和可执行文件的属性，以控制它们的输出位置。设置这些变量可以使项目将所有库和可执行文件放置在同一个目录中。对于包含许多子目录的项目，这可以节省大量时间。下面是典型的实现示例：

```bash
# Setup output directories.
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/bin)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/lib)
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/lib)
```

在这个示例中，所有的“runtime”可执行文件将被写入项目二进制树中的 bin 子目录，包括所有平台上的可执行文件和 Windows 上的 DLL 文件。其他可执行文件将被写入 lib 目录。这种方法对于使用共享库（DLL）的项目非常实用，因为它将所有的共享库集中在一个目录中。如果可执行文件放在同一个目录中，那么它们在 Windows 上运行时可以更容易地找到所需的共享库。

关于目录结构的最后一点说明：使用 CMake 时，项目内部包含项目是完全可行的。例如，在 Visualization Toolkit 的源代码树中，有包含 `zlib` 压缩库完整副本的目录。在为该库编写 CMakeLists 文件时，使用 `project` 命令创建名为 `VTKZLIB` 的项目，尽管它位于 VTK 源代码树和项目中。这对 VTK 没有实际影响，但它允许我们独立于 VTK 构建 `zlib`，而无需修改其 CMakeLists 文件。

## 转换项目时有用的 CMake 命令 

有一些 CMake 命令可以简化并加快将现有项目转换的工作。使用 [`file`](https://cmake.org/cmake/help/latest/command/file.html#command:file) 命令和 `GLOB` 参数，你可以快速设置包含所有匹配 `glob` 表达式的文件列表的变量。例如：
```cmake
# collect up the source files
file(GLOB SRC_FILES "*.cxx")

# create the executable
add_executable(foo ${SRC_FILES})
```

将 `SRC_FILES` 变量设置为当前源目录中所有 `.cxx` 文件的列表。然后，它将使用这些源文件创建可执行文件。Windows 开发者应注意，`glob` 匹配是区分大小写的。

## 将 UNIX Makefiles 转换为 CMake

如果你的项目目前基于标准 UNIX Makefiles，那么将其转换为 CMake 应该相对简单。基本上，对于你的项目中每个包含 Makefile 的目录，你将创建一个匹配的 CMakeLists 文件。你如何处理目录中的多个 Makefile 取决于它们的功能。如果额外的 Makefile（或 Makefile 类型文件）只是包含在主 Makefile 中，你可以创建匹配的 CMake 输入文件（.cmake），并以类似的方式将它们包含到你的主 CMakeLists 文件中。如果不同的 Makefile 需要为不同的情况在命令行中调用，可以考虑创建一个主 CMakeLists 文件，该文件使用一些逻辑来根据 CMake 选项选择要 include 的 Makefile。

通常 Makefile 中会包含要编译的目标文件列表。这些可以按照以下方式转换为 CMake 变量：

```
OBJS= \
  foo1.o \
  foo2.o \
  foo3.o
```

变成
```cmake
set(SOURCES
  foo1.c
  foo2.c
  foo3.c
)
```

虽然对象文件通常列在 Makefile 中，但在 CMake 中，重点在于源文件。如果你在 Makefile 中使用了条件语句，它们可以转换成 CMake 的 if 命令。由于 CMake 处理依赖关系的生成，大多数依赖关系或生成依赖关系的规则都可以消除。在需要构建库或可执行文件的地方，用 `add_library` 或 `add_executable` 命令替换这些规则。

一些 UNIX 构建系统（和源代码）大量使用系统架构来确定编译哪些文件或使用什么标志。通常这些信息存储在 Makefile 变量 ARCH 或 UNAME 中。在这种情况下，首选是用更通用的测试替换特定于架构的代码。对于某些软件包，由于架构特定代码太多，这种改变可能并不合理，或者你可能出于其他原因需要基于架构做决策。在这些情况下，你可以使用变量 [`CMAKE_SYSTEM_NAME`](https://cmake.org/cmake/help/latest/variable/CMAKE_SYSTEM_NAME.html#variable:CMAKE_SYSTEM_NAME) 和 [`CMAKE_SYSTEM_VERSION`](https://cmake.org/cmake/help/latest/variable/CMAKE_SYSTEM_VERSION.html#variable:CMAKE_SYSTEM_VERSION) 。它们提供了关于主机计算机操作系统和版本的相当详细的信息。
