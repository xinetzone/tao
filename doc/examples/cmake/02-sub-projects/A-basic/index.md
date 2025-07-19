# 基本子项目

这个示例展示了如何设置包含子项目的 CMake 项目。顶层 CMakeLists.txt 调用子目录中的 CMakeLists.txt 来创建以下内容：

- sublibrary1 - 一个静态库
- sublibrary2 - 一个仅包含头文件的库
- subbinary - 一个可执行文件

本示例包含的文件有：

```
$ tree
.
├── CMakeLists.txt # 顶层 CMakeLists.txt
├── subbinary
│   ├── CMakeLists.txt # 用于生成可执行文件
│   └── main.cpp # 可执行文件的源代码
├── sublibrary1
│   ├── CMakeLists.txt # 用于创建静态库
│   ├── include
│   │   └── sublib1
│   │       └── sublib1.h
│   └── src
│       └── sublib1.cpp
└── sublibrary2 
    ├── CMakeLists.txt # 用于设置头文件库
    └── include
        └── sublib2
            └── sublib2.h
```

在这个例子中，我将头文件移动到了每个项目的 include 目录下的子文件夹中，而将目标 include 保留为根 include 文件夹。这是一个好主意，可以防止文件名冲突，因为你必须像下面这样包含文件：

```cpp
#include "sublib1/sublib1.h"
```

这也意味着，如果你为其他用户安装你的库，默认的安装位置将是 `/usr/local/include/sublib1/sublib1.h`。

## 添加子目录

一个 CMakeLists.txt 文件可以包含并调用包含 CMakeLists.txt 文件的子目录。

```cmake
add_subdirectory(sublibrary1)
add_subdirectory(sublibrary2)
add_subdirectory(subbinary)
```

## 引用子项目目录

当使用 project() 命令创建项目时，CMake 会自动创建一些变量，这些变量可用于引用项目详情。然后这些变量可以被其他子项目或主项目使用。例如，要引用不同项目的源目录，你可以使用。

```
${sublibrary1_SOURCE_DIR}
${sublibrary2_SOURCE_DIR}
```

CMake 创建的变量包括：

| 变量名                  | 描述                                                                 |
|-------------------------|----------------------------------------------------------------------|
| `PROJECT_NAME`          | 当前`project()`命令设置的项目名称称                                    |
| `CMAKE_PROJECT_NAME`    | 顶层项目名称，即第一个`project()`设置的项目名                       |
| `PROJECT_SOURCE_DIR`    | 当前项目源码目录                                                    |
| `PROJECT_BINARY_DIR`    | 当前项目构建目录                                                    |
| `<name>_SOURCE_DIR`     | 名为"<name>"项目的源码目录（注意替换实际项目名）在这个例子中，创建的源目录将是 sublibrary1_SOURCE_DIR 、 sublibrary2_SOURCE_DIR 和 subbinary_SOURCE_DIR 。 |

## 纯头文件库

如果你有作为纯头文件库创建的库，CMake 支持 INTERFACE 目标来允许创建没有任何构建输出的目标。更多详情可以在[这里](https://cmake.org/cmake/help/v3.4/command/add_library.html#interface-libraries)找到

```bash
add_library(${PROJECT_NAME} INTERFACE)
```

在创建目标时，您也可以使用 INTERFACE 作用域包含该目标的相关目录。INTERFACE 作用域用于定义目标的需求，这些需求被任何链接此目标的库使用，但不在目标本身的编译中使用。

```
target_include_directories(${PROJECT_NAME}
    INTERFACE
        ${PROJECT_SOURCE_DIR}/include
)
```

## 从子项目引用库

如果子项目创建了库，其他项目可以通过在 target_link_libraries() 命令中调用目标名称来引用它。这意味着你不必引用新库的完整路径，它会被添加为依赖项。

```
target_link_libraries(subbinary
    PUBLIC
        sublibrary1
)
```

或者，你可以创建一个别名目标，它允许你在只读上下文中引用该目标。

要创建一个别名目标，请运行：

```cmake
add_library(sublibrary2)
add_library(sub::lib2 ALIAS sublibrary2)
```

要引用别名，只需按照以下方式引用即可：

```cmake
target_link_libraries(subbinary
    sub::lib2
)
```

## 包含子项目的目录

在添加子项目的库时，从 cmake v3 开始，无需在调用这些库的二进制文件的包含目录中添加项目的包含目录。

这是由在创建库时 `target_include_directories()` 命令中的作用域控制的。在这个例子中，因为子二进制可执行文件链接了 sublibrary1 和 sublibrary2，它将自动包含 `${sublibrary1_SOURCE_DIR}/include` 和 `${sublibrary2_SOURCE_DIR}/include` 文件夹，因为它们是以库的 PUBLIC 和 INTERFACE 作用域导出的。

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
-- Build files have been written to: /home/matrim/workspace/cmake-examples/02-sub-projects/A-basic/build

$ make
Scanning dependencies of target sublibrary1
[ 50%] Building CXX object sublibrary1/CMakeFiles/sublibrary1.dir/src/sublib1.cpp.o
Linking CXX static library libsublibrary1.a
[ 50%] Built target sublibrary1
Scanning dependencies of target subbinary
[100%] Building CXX object subbinary/CMakeFiles/subbinary.dir/main.cpp.o
Linking CXX executable subbinary
[100%] Built target subbinary
```