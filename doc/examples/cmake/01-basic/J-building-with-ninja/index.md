# 使用 ninja 构建

如前所述，CMake 元构建系统，可用于为许多其他构建工具创建构建文件。本例展示了如何让 CMake 使用 [ninja](../../../../fields/ninja/index) 构建工具。

## 生成器

CMake 生成器负责为底层构建系统编写输入文件（例如 Makefiles）。运行 `cmake --help` 将显示可用的生成器。

### 命令行构建工具生成器

这些生成器用于命令行构建工具，如 Make 和 Ninja。在用 CMake 生成构建系统之前，必须配置所选的工具链。

支持的生成器包括：
```
Borland Makefiles

MSYS Makefiles

MinGW Makefiles

NMake Makefiles

NMake Makefiles JOM

Ninja

Unix Makefiles

Watcom WMake
```

### IDE 构建工具生成器

这些生成器是为包含自己编译器的集成开发环境设计的。例如，Visual Studio 和 Xcode 都原生包含编译器。

支持的生成器包括：
```
Visual Studio 6

Visual Studio 7

Visual Studio 7 .NET 2003

Visual Studio 8 2005

Visual Studio 9 2008

Visual Studio 10 2010
Visual Studio 2010

Visual Studio 11 2012
Visual Studio 2012

Visual Studio 12 2013

Xcode
```

### 其他生成器

这些生成器创建用于与替代 IDE 工具工作的配置，并且必须与 IDE 或命令行生成器一起使用。

支持的生成器包括：
```
CodeBlocks

CodeLite

Eclipse CDT4

KDevelop3

Kate

Sublime Text 2
```

## 调用生成器

要调用 CMake 生成器，您可以使用 `-G` 命令行开关，例如：

```bash
cmake .. -G Ninja
```

完成上述步骤后，CMake 将生成所需的 Ninja 构建文件，这些文件可以通过 ninja 命令运行。

```bash
$ cmake .. -G Ninja

$ ls
build.ninja  CMakeCache.txt  CMakeFiles  cmake_install.cmake  rules.ninja
```

## 构建示例

```bash
$ mkdir build.ninja

$ cd build.ninja/

$ cmake .. -G Ninja
-- The C compiler identification is GNU 4.8.4
-- The CXX compiler identification is GNU 4.8.4
-- Check for working C compiler using: Ninja
-- Check for working C compiler using: Ninja -- works
-- Detecting C compiler ABI info
-- Detecting C compiler ABI info - done
-- Check for working CXX compiler using: Ninja
-- Check for working CXX compiler using: Ninja -- works
-- Detecting CXX compiler ABI info
-- Detecting CXX compiler ABI info - done
-- Configuring done
-- Generating done
-- Build files have been written to: /home/matrim/workspace/cmake-examples/01-basic/J-building-with-ninja/build.ninja

$ ninja -v
[1/2] /usr/bin/c++     -MMD -MT CMakeFiles/hello_cmake.dir/main.cpp.o -MF "CMakeFiles/hello_cmake.dir/main.cpp.o.d" -o CMakeFiles/hello_cmake.dir/main.cpp.o -c ../main.cpp
[2/2] : && /usr/bin/c++      CMakeFiles/hello_cmake.dir/main.cpp.o  -o hello_cmake  -rdynamic && :

$ ls
build.ninja  CMakeCache.txt  CMakeFiles  cmake_install.cmake  hello_cmake  rules.ninja

$ ./hello_cmake
Hello CMake!
```
