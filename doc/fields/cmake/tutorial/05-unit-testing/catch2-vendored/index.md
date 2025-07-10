# Catch2 单元测试框架

使用 [CTest](https://cmake.org/Wiki/CMake/Testing_With_CTest) 可以生成 make test 目标来运行自动化的单元测试。本示例展示了如何查找 [catch2 框架](https://github.com/catchorg/Catch2)、创建测试并运行它们。

本教程中的文件如下：

```bash
$ tree
.
├── 3rd_party
│   └── catch2
│       ├── catch2
│       │   └── catch.hpp
│       └── CMakeLists.txt
├── CMakeLists.txt
├── Reverse.h
├── Reverse.cpp
├── Palindrome.h
├── Palindrome.cpp
├── unit_tests.cpp
```

- `3rd_party/catch2/catch2/catch.hpp` - catch2 单头文件版本的授权副本
- `3rd_party/catch2/CMakeLists.txt` - 使 Catch2 作为库可用的 CMake 文件
- `CMakeLists.txt` - 包含你希望运行的 CMake 命令
- `Reverse.h / .cpp` - 用于反转字符串的类
- `Palindrome.h / .cpp` - 用于测试字符串是否为回文的类
- `unit_test.cpp` - 使用 catch2 单元测试框架的单元测试

## Vendoring catch2

由于 catch2 以单个头文件的形式提供，我已经下载并将其提交到我的仓库中。这意味着在构建我的项目时没有任何外部依赖。这是使用 Catch2 最简单的方法之一。

## Catch2 接口库

catch2 目录中的 CMakeLists.txt 文件创建了一个 INTERFACE 库和一个 ALIAS 库，以便轻松地将 Catch2 添加到您的可执行文件中。

```cmake
add_library(Catch2 INTERFACE)
add_library(Catch2::Test ALIAS Catch2)
target_include_directories(Catch2 INTERFACE ${CMAKE_CURRENT_SOURCE_DIR})
```

## 使用 C++11 构建

由于 Catch2 需要 C11 来构建，我使用了`CMAKE_CXX_STANDARD`来设置 C11。正如之前的示例中所描述的，你可以使用其他方法来设置这个标准。

## 启用测试

要启用测试，您必须在您的顶层 CMakeLists.txt 中包含以下行

```cmake
enable_testing()
```

这将启用对当前文件夹及其所有子文件夹的测试。

## 添加测试可执行文件

这一步的需求将取决于你的单元测试框架。在 catch2 的示例中，你可以创建包含所有你想运行的单元测试的二进制文件。

```cmake
add_executable(unit_tests unit_tests.cpp)

target_link_libraries(unit_tests
    example_unit_test
    Catch2::Test
)
```

在上述代码中，添加了一个单元测试二进制文件，它链接了先前创建的 catch2 ALIAS 目标。

## 添加测试

要添加测试，你调用 add_test() 函数。这将创建一个命名的测试，它将运行提供的命令。

```cmake
add_test(test_all unit_tests)
```

在这个例子中，我们创建一个名为 test_all 的测试，它将运行由 unit_tests 可执行文件创建的可执行文件，该可执行文件是由调用 add_executable 创建的。

## 示例

```bash
$ mkdir build

$ cd build/

$ cmake ..
-- The C compiler identification is GNU 5.4.0
-- The CXX compiler identification is GNU 5.4.0
-- Check for working C compiler: /usr/bin/cc
-- Check for working C compiler: /usr/bin/cc -- works
-- Detecting C compiler ABI info
-- Detecting C compiler ABI info - done
-- Detecting C compile features
-- Detecting C compile features - done
-- Check for working CXX compiler: /usr/bin/c++
-- Check for working CXX compiler: /usr/bin/c++ -- works
-- Detecting CXX compiler ABI info
-- Detecting CXX compiler ABI info - done
-- Detecting CXX compile features
-- Detecting CXX compile features - done
-- Configuring done
-- Generating done
-- Build files have been written to: /data/code/cmake-examples/05-unit-testing/catch2-vendored/build


$ make
Scanning dependencies of target example_unit_test
[ 20%] Building CXX object CMakeFiles/example_unit_test.dir/Reverse.cpp.o
[ 40%] Building CXX object CMakeFiles/example_unit_test.dir/Palindrome.cpp.o
[ 60%] Linking CXX static library libexample_unit_test.a
[ 60%] Built target example_unit_test
Scanning dependencies of target unit_tests
[ 80%] Building CXX object CMakeFiles/unit_tests.dir/unit_tests.cpp.o
[100%] Linking CXX executable unit_tests
[100%] Built target unit_tests


$ make test
Running tests...
Test project /data/code/cmake-examples/05-unit-testing/catch2-vendored/build
    Start 1: test_all
1/1 Test #1: test_all .........................   Passed    0.00 sec

100% tests passed, 0 tests failed out of 1

Total Test time (real) =   0.00 sec
```

如果代码被更改并导致单元测试产生错误，那么在运行测试时你会看到以下输出。

```bash
Running tests...
Test project /data/code/cmake-examples/05-unit-testing/catch2-vendored/build
    Start 1: test_all
1/1 Test #1: test_all .........................***Failed    0.00 sec

0% tests passed, 1 tests failed out of 1

Total Test time (real) =   0.00 sec

The following tests FAILED:
    1 - test_all (Failed)
Errors while running CTest
Makefile:61: recipe for target 'test' failed
make: *** [test] Error 8
```
