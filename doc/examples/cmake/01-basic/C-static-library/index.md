# 包含静态库

演示如何创建并链接静态库的hello world示例。该示例将库文件和可执行文件放在同一目录，实际项目中建议使用[子项目结构](../../02-sub-projects/index)。

项目文件结构：

```
. 
├── CMakeLists.txt
├── include
│   └── static
│       └── Hello.h
└── src
    ├── Hello.cpp
    └── main.cpp
```

**关键文件**：
- `CMakeLists.txt`: 包含CMake构建指令
- `include/static/Hello.h`: 头文件
- `src/Hello.cpp`: 库源文件
- `src/main.cpp`: 主程序文件

## 核心概念

### 创建静态库

使用`add_library`命令创建静态库：

```cmake
add_library(hello_library STATIC
    src/Hello.cpp
)
```

这会生成`libhello_library.a`静态库文件。现代CMake推荐直接指定源文件路径。

### 包含目录配置

使用`target_include_directories`设置公共包含目录：

```cmake
target_include_directories(hello_library
    PUBLIC
        ${PROJECT_SOURCE_DIR}/include
)
```

作用域说明：
- **PRIVATE**: 仅当前目标使用
- **INTERFACE**: 仅链接本库的目标使用
- **PUBLIC**: 同时适用于当前目标和链接目标

**最佳实践**：建议采用命名空间目录结构（如`include/static/`），源文件包含时使用：

```cpp
#include "static/Hello.h"
```

### 链接库文件

使用`target_link_libraries`链接库到可执行文件：

```cmake
add_executable(hello_binary
    src/main.cpp
)

target_link_libraries(hello_binary
    PRIVATE
        hello_library
)
```

这会自动传播PUBLIC/INTERFACE包含目录。编译器实际执行的链接命令示例：

```
/usr/bin/c++ CMakeFiles/hello_binary.dir/src/main.cpp.o -o hello_binary -rdynamic libhello_library.a
```

## 构建流程

```bash
$ mkdir build

$ cd build

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
-- Build files have been written to: /home/matrim/workspace/cmake-examples/01-basic/C-static-library/build

$ make
Scanning dependencies of target hello_library
[ 50%] Building CXX object CMakeFiles/hello_library.dir/src/Hello.cpp.o
Linking CXX static library libhello_library.a
[ 50%] Built target hello_library
Scanning dependencies of target hello_binary
[100%] Building CXX object CMakeFiles/hello_binary.dir/src/main.cpp.o
Linking CXX executable hello_binary
[100%] Built target hello_binary

$ ls
CMakeCache.txt  CMakeFiles  cmake_install.cmake  hello_binary  libhello_library.a  Makefile

$ ./hello_binary
Hello Static Library!
```