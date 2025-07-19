# 构建类型

CMake 具有多种内置的构建配置，可用于编译您的项目。这些配置指定了优化级别以及是否要在二进制文件中包含调试信息。

提供的级别有：

- Release - 向编译器添加 `-O3 -DNDEBUG` 标志
- Debug - 向编译器添加 `-g` 标志
- MinSizeRel - 添加 `-Os -DNDEBUG`
- RelWithDebInfo - 向添加 `-O2 -g -DNDEBUG` 标志

本教程中的文件如下：

```bash
$ tree
.
├── CMakeLists.txt
├── main.cpp
```

## 设置构建类型

可以使用以下方法设置构建类型。

- 使用 ccmake / cmake-gui 等图形工具：![](cmake-gui-build-type.png)
- 通过命令行传递给 cmake：
    ```bash
    cmake .. -DCMAKE_BUILD_TYPE=Release
    ```

## 设置默认构建类型

CMake 提供的默认构建类型是不包含优化编译器标志。对于某些项目，您可能希望设置一个默认构建类型，这样就不必记住每次设置它。

要实现这一点，你可以将以下内容添加到你的顶层 CMakeLists.txt 文件中

```cmake
if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
  message("Setting build type to 'RelWithDebInfo' as none was specified.")
  set(CMAKE_BUILD_TYPE RelWithDebInfo CACHE STRING "Choose the type of build." FORCE)
  # Set the possible values of build type for cmake-gui
  set_property(CACHE CMAKE_BUILD_TYPE PROPERTY STRINGS "Debug" "Release"
    "MinSizeRel" "RelWithDebInfo")
endif()
```

## 构建示例

```bash
$ mkdir build

$ cd build/

$ cmake ..
Setting build type to 'RelWithDebInfo' as none was specified.
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
-- Build files have been written to: /home/matrim/workspace/cmake-examples/01-basic/F-build-type/build

$ make VERBOSE=1
/usr/bin/cmake -H/home/matrim/workspace/cmake-examples/01-basic/F-build-type -B/home/matrim/workspace/cmake-examples/01-basic/F-build-type/build --check-build-system CMakeFiles/Makefile.cmake 0
/usr/bin/cmake -E cmake_progress_start /home/matrim/workspace/cmake-examples/01-basic/F-build-type/build/CMakeFiles /home/matrim/workspace/cmake-examples/01-basic/F-build-type/build/CMakeFiles/progress.marks
make -f CMakeFiles/Makefile2 all
make[1]: Entering directory `/home/matrim/workspace/cmake-examples/01-basic/F-build-type/build'
make -f CMakeFiles/cmake_examples_build_type.dir/build.make CMakeFiles/cmake_examples_build_type.dir/depend
make[2]: Entering directory `/home/matrim/workspace/cmake-examples/01-basic/F-build-type/build'
cd /home/matrim/workspace/cmake-examples/01-basic/F-build-type/build && /usr/bin/cmake -E cmake_depends "Unix Makefiles" /home/matrim/workspace/cmake-examples/01-basic/F-build-type /home/matrim/workspace/cmake-examples/01-basic/F-build-type /home/matrim/workspace/cmake-examples/01-basic/F-build-type/build /home/matrim/workspace/cmake-examples/01-basic/F-build-type/build /home/matrim/workspace/cmake-examples/01-basic/F-build-type/build/CMakeFiles/cmake_examples_build_type.dir/DependInfo.cmake --color=
Dependee "/home/matrim/workspace/cmake-examples/01-basic/F-build-type/build/CMakeFiles/cmake_examples_build_type.dir/DependInfo.cmake" is newer than depender "/home/matrim/workspace/cmake-examples/01-basic/F-build-type/build/CMakeFiles/cmake_examples_build_type.dir/depend.internal".
Dependee "/home/matrim/workspace/cmake-examples/01-basic/F-build-type/build/CMakeFiles/CMakeDirectoryInformation.cmake" is newer than depender "/home/matrim/workspace/cmake-examples/01-basic/F-build-type/build/CMakeFiles/cmake_examples_build_type.dir/depend.internal".
Scanning dependencies of target cmake_examples_build_type
make[2]: Leaving directory `/home/matrim/workspace/cmake-examples/01-basic/F-build-type/build'
make -f CMakeFiles/cmake_examples_build_type.dir/build.make CMakeFiles/cmake_examples_build_type.dir/build
make[2]: Entering directory `/home/matrim/workspace/cmake-examples/01-basic/F-build-type/build'
/usr/bin/cmake -E cmake_progress_report /home/matrim/workspace/cmake-examples/01-basic/F-build-type/build/CMakeFiles 1
[100%] Building CXX object CMakeFiles/cmake_examples_build_type.dir/main.cpp.o
/usr/bin/c++    -O2 -g -DNDEBUG   -o CMakeFiles/cmake_examples_build_type.dir/main.cpp.o -c /home/matrim/workspace/cmake-examples/01-basic/F-build-type/main.cpp
Linking CXX executable cmake_examples_build_type
/usr/bin/cmake -E cmake_link_script CMakeFiles/cmake_examples_build_type.dir/link.txt --verbose=1
/usr/bin/c++   -O2 -g -DNDEBUG    CMakeFiles/cmake_examples_build_type.dir/main.cpp.o  -o cmake_examples_build_type -rdynamic
make[2]: Leaving directory `/home/matrim/workspace/cmake-examples/01-basic/F-build-type/build'
/usr/bin/cmake -E cmake_progress_report /home/matrim/workspace/cmake-examples/01-basic/F-build-type/build/CMakeFiles  1
[100%] Built target cmake_examples_build_type
make[1]: Leaving directory `/home/matrim/workspace/cmake-examples/01-basic/F-build-type/build'
/usr/bin/cmake -E cmake_progress_start /home/matrim/workspace/cmake-examples/01-basic/F-build-type/build/CMakeFiles 0$ mkdir build
$ cd build/
/build$ cmake ..
Setting build type to 'RelWithDebInfo' as none was specified.
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
-- Build files have been written to: /home/matrim/workspace/cmake-examples/01-basic/F-build-type/build
/build$ make VERBOSE=1
/usr/bin/cmake -H/home/matrim/workspace/cmake-examples/01-basic/F-build-type -B/home/matrim/workspace/cmake-examples/01-basic/F-build-type/build --check-build-system CMakeFiles/Makefile.cmake 0
/usr/bin/cmake -E cmake_progress_start /home/matrim/workspace/cmake-examples/01-basic/F-build-type/build/CMakeFiles /home/matrim/workspace/cmake-examples/01-basic/F-build-type/build/CMakeFiles/progress.marks
make -f CMakeFiles/Makefile2 all
make[1]: Entering directory `/home/matrim/workspace/cmake-examples/01-basic/F-build-type/build'
make -f CMakeFiles/cmake_examples_build_type.dir/build.make CMakeFiles/cmake_examples_build_type.dir/depend
make[2]: Entering directory `/home/matrim/workspace/cmake-examples/01-basic/F-build-type/build'
cd /home/matrim/workspace/cmake-examples/01-basic/F-build-type/build && /usr/bin/cmake -E cmake_depends "Unix Makefiles" /home/matrim/workspace/cmake-examples/01-basic/F-build-type /home/matrim/workspace/cmake-examples/01-basic/F-build-type /home/matrim/workspace/cmake-examples/01-basic/F-build-type/build /home/matrim/workspace/cmake-examples/01-basic/F-build-type/build /home/matrim/workspace/cmake-examples/01-basic/F-build-type/build/CMakeFiles/cmake_examples_build_type.dir/DependInfo.cmake --color=
Dependee "/home/matrim/workspace/cmake-examples/01-basic/F-build-type/build/CMakeFiles/cmake_examples_build_type.dir/DependInfo.cmake" is newer than depender "/home/matrim/workspace/cmake-examples/01-basic/F-build-type/build/CMakeFiles/cmake_examples_build_type.dir/depend.internal".
Dependee "/home/matrim/workspace/cmake-examples/01-basic/F-build-type/build/CMakeFiles/CMakeDirectoryInformation.cmake" is newer than depender "/home/matrim/workspace/cmake-examples/01-basic/F-build-type/build/CMakeFiles/cmake_examples_build_type.dir/depend.internal".
Scanning dependencies of target cmake_examples_build_type
make[2]: Leaving directory `/home/matrim/workspace/cmake-examples/01-basic/F-build-type/build'
make -f CMakeFiles/cmake_examples_build_type.dir/build.make CMakeFiles/cmake_examples_build_type.dir/build
make[2]: Entering directory `/home/matrim/workspace/cmake-examples/01-basic/F-build-type/build'
/usr/bin/cmake -E cmake_progress_report /home/matrim/workspace/cmake-examples/01-basic/F-build-type/build/CMakeFiles 1
[100%] Building CXX object CMakeFiles/cmake_examples_build_type.dir/main.cpp.o
/usr/bin/c++    -O2 -g -DNDEBUG   -o CMakeFiles/cmake_examples_build_type.dir/main.cpp.o -c /home/matrim/workspace/cmake-examples/01-basic/F-build-type/main.cpp
Linking CXX executable cmake_examples_build_type
/usr/bin/cmake -E cmake_link_script CMakeFiles/cmake_examples_build_type.dir/link.txt --verbose=1
/usr/bin/c++   -O2 -g -DNDEBUG    CMakeFiles/cmake_examples_build_type.dir/main.cpp.o  -o cmake_examples_build_type -rdynamic
make[2]: Leaving directory `/home/matrim/workspace/cmake-examples/01-basic/F-build-type/build'
/usr/bin/cmake -E cmake_progress_report /home/matrim/workspace/cmake-examples/01-basic/F-build-type/build/CMakeFiles  1
[100%] Built target cmake_examples_build_type
make[1]: Leaving directory `/home/matrim/workspace/cmake-examples/01-basic/F-build-type/build'
/usr/bin/cmake -E cmake_progress_start /home/matrim/workspace/cmake-examples/01-basic/F-build-type/build/CMakeFiles 0
```
