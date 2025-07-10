# 编译标志

CMake 支持多种方式设置编译标志：

- 使用 target_compile_definitions() 函数
- 使用 CMAKE_C_FLAGS 和 CMAKE_CXX_FLAGS 变量。

## 设置目标特定的 C++ 标志

在现代 CMake 中设置 C++ 标志的推荐方式是使用目标标志，这些标志可以通过 `target_compile_definitions()` 函数传递给其他目标。这将填充库的 `INTERFACE_COMPILE_DEFINITIONS`，并根据作用域将定义推送到链接的目标。

```bash
target_compile_definitions(cmake_examples_compile_flags
    PRIVATE EX3
)
```

这会导致编译器在编译目标时添加定义 `-DEX3`。

```bash
如果目标是一个库，并且选择了 PUBLIC 或 INTERFACE 范围，那么定义也会包含在任何链接此目标的可执行文件中。
```

对于编译器选项，您也可以使用 [`target_compile_options()`](https://cmake.org/cmake/help/v3.0/command/target_compile_options.html) 函数。

## 设置默认 C++标志

默认的 `CMAKE_CXX_FLAGS` 要么为空，要么包含适用于构建类型的适当标志。

要设置额外的默认编译标志，可以将以下内容添加到你的顶层 CMakeLists.txt 文件中
```bash
set (CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -DEX2" CACHE STRING "Set C++ Compiler Flags" FORCE)
```
与 CMAKE_CXX_FLAGS 类似，其他选项包括：
- 使用 CMAKE_C_FLAGS 设置 C 编译器标志
- 使用 CMAKE_LINKER_FLAGS 设置链接器标志。

```{note}
上述命令中的 `CACHE STRING "Set C++ Compiler Flags" FORCE` 值用于强制在 CMakeCache.txt 文件中设置此变量。
```

一旦设置了 CMAKE_C_FLAGS 和 CMAKE_CXX_FLAGS，就会为该目录或任何包含的子目录中的所有目标设置一个全局编译器标志/定义。现在不建议使用这种方法，推荐使用 target_compile_definitions 函数。

## 设置 CMake 标志

类似于构建类型，可以使用以下方法设置一个全局 C++编译器标志。

- 使用 ccmake / cmake-gui 等图形工具
- 通过命令行传递给 cmake：`cmake .. -DCMAKE_CXX_FLAGS="-DEX3"`

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
-- Build files have been written to: /home/matrim/workspace/cmake-examples/01-basic/G-compile-flags/build

$ make VERBOSE=1
/usr/bin/cmake -H/home/matrim/workspace/cmake-examples/01-basic/G-compile-flags -B/home/matrim/workspace/cmake-examples/01-basic/G-compile-flags/build --check-build-system CMakeFiles/Makefile.cmake 0
/usr/bin/cmake -E cmake_progress_start /home/matrim/workspace/cmake-examples/01-basic/G-compile-flags/build/CMakeFiles /home/matrim/workspace/cmake-examples/01-basic/G-compile-flags/build/CMakeFiles/progress.marks
make -f CMakeFiles/Makefile2 all
make[1]: Entering directory `/home/matrim/workspace/cmake-examples/01-basic/G-compile-flags/build'
make -f CMakeFiles/cmake_examples_compile_flags.dir/build.make CMakeFiles/cmake_examples_compile_flags.dir/depend
make[2]: Entering directory `/home/matrim/workspace/cmake-examples/01-basic/G-compile-flags/build'
cd /home/matrim/workspace/cmake-examples/01-basic/G-compile-flags/build && /usr/bin/cmake -E cmake_depends "Unix Makefiles" /home/matrim/workspace/cmake-examples/01-basic/G-compile-flags /home/matrim/workspace/cmake-examples/01-basic/G-compile-flags /home/matrim/workspace/cmake-examples/01-basic/G-compile-flags/build /home/matrim/workspace/cmake-examples/01-basic/G-compile-flags/build /home/matrim/workspace/cmake-examples/01-basic/G-compile-flags/build/CMakeFiles/cmake_examples_compile_flags.dir/DependInfo.cmake --color=
Dependee "/home/matrim/workspace/cmake-examples/01-basic/G-compile-flags/build/CMakeFiles/cmake_examples_compile_flags.dir/DependInfo.cmake" is newer than depender "/home/matrim/workspace/cmake-examples/01-basic/G-compile-flags/build/CMakeFiles/cmake_examples_compile_flags.dir/depend.internal".
Dependee "/home/matrim/workspace/cmake-examples/01-basic/G-compile-flags/build/CMakeFiles/CMakeDirectoryInformation.cmake" is newer than depender "/home/matrim/workspace/cmake-examples/01-basic/G-compile-flags/build/CMakeFiles/cmake_examples_compile_flags.dir/depend.internal".
Scanning dependencies of target cmake_examples_compile_flags
make[2]: Leaving directory `/home/matrim/workspace/cmake-examples/01-basic/G-compile-flags/build'
make -f CMakeFiles/cmake_examples_compile_flags.dir/build.make CMakeFiles/cmake_examples_compile_flags.dir/build
make[2]: Entering directory `/home/matrim/workspace/cmake-examples/01-basic/G-compile-flags/build'
/usr/bin/cmake -E cmake_progress_report /home/matrim/workspace/cmake-examples/01-basic/G-compile-flags/build/CMakeFiles 1
[100%] Building CXX object CMakeFiles/cmake_examples_compile_flags.dir/main.cpp.o
/usr/bin/c++    -DEX2   -o CMakeFiles/cmake_examples_compile_flags.dir/main.cpp.o -c /home/matrim/workspace/cmake-examples/01-basic/G-compile-flags/main.cpp
Linking CXX executable cmake_examples_compile_flags
/usr/bin/cmake -E cmake_link_script CMakeFiles/cmake_examples_compile_flags.dir/link.txt --verbose=1
/usr/bin/c++    -DEX2    CMakeFiles/cmake_examples_compile_flags.dir/main.cpp.o  -o cmake_examples_compile_flags -rdynamic
make[2]: Leaving directory `/home/matrim/workspace/cmake-examples/01-basic/G-compile-flags/build'
/usr/bin/cmake -E cmake_progress_report /home/matrim/workspace/cmake-examples/01-basic/G-compile-flags/build/CMakeFiles  1
[100%] Built target cmake_examples_compile_flags
make[1]: Leaving directory `/home/matrim/workspace/cmake-examples/01-basic/G-compile-flags/build'
/usr/bin/cmake -E cmake_progress_start /home/matrim/workspace/cmake-examples/01-basic/G-compile-flags/build/CMakeFiles 0
```
