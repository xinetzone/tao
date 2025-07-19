# 配置文件生成

使用 CMake 的 configure_file 函数注入 CMake 变量。

在调用 cmake 时，可以创建使用 CMakeLists.txt 和 cmake 缓存中变量的文件。在 CMake 生成过程中，文件会被复制到新位置，并且任何 cmake 变量都会被替换。

本教程中的文件如下：

```bash
$ tree
.
├── CMakeLists.txt # 包含你希望运行的 CMake 命令
├── main.cpp  # 主源文件
├── path.h.in # 包含构建目录路径的文件
├── ver.h.in # 包含项目版本的文件
```

## 配置文件

要在文件中执行变量替换，您可以在 CMake 中使用 configure_file() 函数。此函数的核心参数是源文件和目标文件。

```cmake
configure_file(ver.h.in ${PROJECT_BINARY_DIR}/ver.h)

configure_file(path.h.in ${PROJECT_BINARY_DIR}/path.h @ONLY)
```

上述第一个示例，允许使用 `${}` 语法或 `@@` 在 `ver.h.in` 文件中定义变量。生成后，`PROJECT_BINARY_DIR` 中将出现新的文件 `ver.h`。

```cpp
const char* ver = "${cf_example_VERSION}";
```

第二个示例，仅允许在 `path.h.in` 文件中使用 `@@` 语法定义变量。生成后，`PROJECT_BINARY_DIR` 中将出新的文件 `path.h`。

```cpp
const char* path = "@CMAKE_SOURCE_DIR@";
```

## 构建示例

```bash
$ mkdir build

$ cd build/

$ cmake ..
-- The C compiler identification is GNU 4.8.4
-- The CXX compiler identification is GNU 4.8.4
-- Check for working C compiler: /usr/bin/cc
-- Check for working C compiler: /usr/bin/cc -- works
-- Detecting C compiler ABI info
-- Detecting C compiler ABI info - done
-- Check for working CXX compiler: /usr/bin/c++
-- Check for working CXX compiler: /usr/bin/c++ -- works
-- Detecting CXX compiler ABI info
-- Detecting CXX compiler ABI info - done
-- Configuring done
-- Generating done
-- Build files have been written to: /home/matrim/workspace/cmake-examples/03-code-generation/configure-files/build

$ ls
CMakeCache.txt  CMakeFiles  cmake_install.cmake  Makefile  path.h  ver.h

$ cat path.h
#ifndef __PATH_H__
#define __PATH_H__

// version variable that will be substituted by cmake
// This shows an example using the @ variable type
const char* path = "/home/matrim/workspace/cmake-examples/03-code-generation/configure-files";

#endif

$ cat ver.h
#ifndef __VER_H__
#define __VER_H__

// version variable that will be substituted by cmake
// This shows an example using the $ variable type
const char* ver = "0.2.1";

#endif

$ make
Scanning dependencies of target cf_example
[100%] Building CXX object CMakeFiles/cf_example.dir/main.cpp.o
Linking CXX executable cf_example
[100%] Built target cf_example

$ ./cf_example
Hello Version 0.2.1!
Path is /home/matrim/workspace/cmake-examples/03-code-generation/configure-files
```
