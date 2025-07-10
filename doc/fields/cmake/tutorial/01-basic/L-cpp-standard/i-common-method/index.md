# C++标准常见方法

本示例展示了一种设置 C++标准的常见方法。这适用于大多数版本的 CMake。然而，如果你要针对较新版本的 CMake，则有一些更方便的方法可用。

## 检查编译标志

CMake 支持尝试使用你传递给函数 CMAKE_CXX_COMPILER_FLAG 的任何标志来编译程序。结果会存储在你传入的变量中。

例如：
```
include(CheckCXXCompilerFlag)
CHECK_CXX_COMPILER_FLAG("-std=c++11" COMPILER_SUPPORTS_CXX11)
```

这个示例将尝试使用标志 `-std=c++11` 编译程序，并将结果存储在变量 COMPILER_SUPPORTS_CXX11 中。

`include(CheckCXXCompilerFlag)` 行告诉 CMake 包含这个函数，以便可以使用它。

## 添加标志

一旦确定编译是否支持该标志，你就可以使用标准的 cmake 方法将该标志添加到目标中。在这个示例中，我们使用 CMAKE_CXX_FLAGS 将标志传递给所有目标。

```bash
if(COMPILER_SUPPORTS_CXX11)#
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")
elseif(COMPILER_SUPPORTS_CXX0X)#
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++0x")
else()
    message(STATUS "The compiler ${CMAKE_CXX_COMPILER} has no C++11 support. Please use a different C++ compiler.")
endif()
```

上述示例仅检查编译标志的 gcc 版本，并支持从 C++11 回退到预标准化 C++0x 标志。在实际使用中，您可能需要检查 C14，或添加对不同设置编译方法的支持，例如`-std=gnu11`。

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
-- Performing Test COMPILER_SUPPORTS_CXX11
-- Performing Test COMPILER_SUPPORTS_CXX11 - Success
-- Performing Test COMPILER_SUPPORTS_CXX0X
-- Performing Test COMPILER_SUPPORTS_CXX0X - Success
-- Configuring done
-- Generating done
-- Build files have been written to: /data/code/01-basic/L-cpp-standard/i-common-method/build

$ make VERBOSE=1
/usr/bin/cmake -H/data/code/01-basic/L-cpp-standard/i-common-method -B/data/code/01-basic/L-cpp-standard/i-common-method/build --check-build-system CMakeFiles/Makefile.cmake 0
/usr/bin/cmake -E cmake_progress_start /data/code/01-basic/L-cpp-standard/i-common-method/build/CMakeFiles /data/code/01-basic/L-cpp-standard/i-common-method/build/CMakeFiles/progress.marks
make -f CMakeFiles/Makefile2 all
make[1]: Entering directory `/data/code/01-basic/L-cpp-standard/i-common-method/build'
make -f CMakeFiles/hello_cpp11.dir/build.make CMakeFiles/hello_cpp11.dir/depend
make[2]: Entering directory `/data/code/01-basic/L-cpp-standard/i-common-method/build'
cd /data/code/01-basic/L-cpp-standard/i-common-method/build && /usr/bin/cmake -E cmake_depends "Unix Makefiles" /data/code/01-basic/L-cpp-standard/i-common-method /data/code/01-basic/L-cpp-standard/i-common-method /data/code/01-basic/L-cpp-standard/i-common-method/build /data/code/01-basic/L-cpp-standard/i-common-method/build /data/code/01-basic/L-cpp-standard/i-common-method/build/CMakeFiles/hello_cpp11.dir/DependInfo.cmake --color=
Dependee "/data/code/01-basic/L-cpp-standard/i-common-method/build/CMakeFiles/hello_cpp11.dir/DependInfo.cmake" is newer than depender "/data/code/01-basic/L-cpp-standard/i-common-method/build/CMakeFiles/hello_cpp11.dir/depend.internal".
Dependee "/data/code/01-basic/L-cpp-standard/i-common-method/build/CMakeFiles/CMakeDirectoryInformation.cmake" is newer than depender "/data/code/01-basic/L-cpp-standard/i-common-method/build/CMakeFiles/hello_cpp11.dir/depend.internal".
Scanning dependencies of target hello_cpp11
make[2]: Leaving directory `/data/code/01-basic/L-cpp-standard/i-common-method/build'
make -f CMakeFiles/hello_cpp11.dir/build.make CMakeFiles/hello_cpp11.dir/build
make[2]: Entering directory `/data/code/01-basic/L-cpp-standard/i-common-method/build'
/usr/bin/cmake -E cmake_progress_report /data/code/01-basic/L-cpp-standard/i-common-method/build/CMakeFiles 1
[100%] Building CXX object CMakeFiles/hello_cpp11.dir/main.cpp.o
/usr/bin/c++    -std=c++11   -o CMakeFiles/hello_cpp11.dir/main.cpp.o -c /data/code/01-basic/L-cpp-standard/i-common-method/main.cpp
Linking CXX executable hello_cpp11
/usr/bin/cmake -E cmake_link_script CMakeFiles/hello_cpp11.dir/link.txt --verbose=1
/usr/bin/c++    -std=c++11    CMakeFiles/hello_cpp11.dir/main.cpp.o  -o hello_cpp11 -rdynamic
make[2]: Leaving directory `/data/code/01-basic/L-cpp-standard/i-common-method/build'
/usr/bin/cmake -E cmake_progress_report /data/code/01-basic/L-cpp-standard/i-common-method/build/CMakeFiles  1
[100%] Built target hello_cpp11
make[1]: Leaving directory `/data/code/01-basic/L-cpp-standard/i-common-method/build'
/usr/bin/cmake -E cmake_progress_start /data/code/01-basic/L-cpp-standard/i-common-method/build/CMakeFiles 0
```
