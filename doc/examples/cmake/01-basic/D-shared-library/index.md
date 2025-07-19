# 创建并链接共享库

展示 "hello world" 示例，首先创建并链接共享库。还展示了如何创建[别名目标](https://cmake.org/cmake/help/v3.0/manual/cmake-buildsystem.7.html#alias-targets)。

文件如下
```
$ tree
.
├── CMakeLists.txt
├── include
│   └── shared
│       └── Hello.h
└── src
    ├── Hello.cpp
    └── main.cpp
```

- CMakeLists.txt - 包含你希望运行的 CMake 命令
- include/shared/Hello.h - 要包含的头文件
- src/Hello.cpp - 要编译的源文件
- src/main.cpp - 含有 main 的源文件

## 添加共享库

与之前静态库的示例一样，add_library() 函数也用于从一些源文件创建共享库。其调用方式如下：

```cmake
add_library(hello_library SHARED
    src/Hello.cpp
)
```

这将用于创建名为 `libhello_library.so` 的共享库，其源文件通过 add_library() 函数传递。

## 别名目标

顾名思义，别名目标是目标的替代名称，在只读上下文中可以用来代替真实的目标名称。

```cmake
add_library(hello::library ALIAS hello_library)
```

如下所示，这允许您在将其他目标链接到它时使用别名名称来引用该目标。

## 链接共享库

链接共享库与链接静态库相同。在创建可执行文件时，使用 target_link_library()函数指向你的库

```cmake
add_executable(hello_binary
    src/main.cpp
)

target_link_libraries(hello_binary
    PRIVATE
        hello::library
)
```

这告诉 CMake 使用别名目标名称将 hello_library 链接到 hello_binary 可执行文件。

一个被链接器调用的例子是
```bash
/usr/bin/c++ CMakeFiles/hello_binary.dir/src/main.cpp.o -o hello_binary -rdynamic libhello_library.so -Wl,-rpath,/home/matrim/workspace/cmake-examples/01-basic/D-shared-library/build
```

## 构建示例

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
-- Build files have been written to: /home/matrim/workspace/cmake-examples/01-basic/D-shared-library/build

$ make
Scanning dependencies of target hello_library
[ 50%] Building CXX object CMakeFiles/hello_library.dir/src/Hello.cpp.o
Linking CXX shared library libhello_library.so
[ 50%] Built target hello_library
Scanning dependencies of target hello_binary
[100%] Building CXX object CMakeFiles/hello_binary.dir/src/main.cpp.o
Linking CXX executable hello_binary
[100%] Built target hello_binary

$ ls
CMakeCache.txt  CMakeFiles  cmake_install.cmake  hello_binary  libhello_library.so  Makefile

$ ./hello_binary
Hello Shared Library!
```
