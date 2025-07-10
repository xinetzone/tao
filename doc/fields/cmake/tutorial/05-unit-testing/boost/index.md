# Boost 单元测试框架

使用 CTest 可以生成 make test 目标来运行自动化的单元测试。这个例子展示了如何找到 boost 单元测试框架，创建测试并运行它们。

本教程中的文件如下：

```bash
$ tree
.
├── CMakeLists.txt # 包含你希望运行的 CMake 命令
├── Reverse.h # 用于反转字符串的类
├── Reverse.cpp 
├── Palindrome.h # 用于测试字符串是否为回文的类
├── Palindrome.cpp
├── unit_tests.cpp # 使用 boost 单元测试框架的单元测试
```

此示例需要将 boost 库安装在默认的系统位置。使用的库是 boost unit-test-framework。

## 启用测试

要启用测试，您必须在顶层 CMakeLists.txt 中包含以下行

```cmake
enable_testing()
```

这将启用对当前文件夹及其所有子文件夹的测试。

## 添加测试可执行文件

这一步的要求将取决于你的单元测试框架。以 boost 为例，你可以创建包含所有你想运行的单元测试的二进制文件。

```cmake
add_executable(unit_tests unit_tests.cpp)

target_link_libraries(unit_tests
    example_boost_unit_test
    Boost::unit_test_framework
)

target_compile_definitions(unit_tests
    PRIVATE
        BOOST_TEST_DYN_LINK
)
```

在上述代码中，添加了一个单元测试二进制文件，它链接到 boost unit-test-framework，并包含一个定义，告诉它我们正在使用动态链接。

## 添加测试

要添加测试，你调用 add_test() 函数。这将创建命名的测试，它将运行提供的命令。

```cmake
add_test(test_all unit_tests)
```

在这个例子中，我们创建一个名为 test_all 的测试，它将运行由 unit_tests 可执行文件创建的可执行文件，该可执行文件是由调用 add_executable 创建的。

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
-- Boost version: 1.54.0
-- Found the following Boost libraries:
--   unit_test_framework
-- Configuring done
-- Generating done
-- Build files have been written to: /home/matrim/workspace/cmake-examples/05-unit-testing/boost/build

$ make
Scanning dependencies of target example_boost_unit_test
[ 33%] Building CXX object CMakeFiles/example_boost_unit_test.dir/Reverse.cpp.o
[ 66%] Building CXX object CMakeFiles/example_boost_unit_test.dir/Palindrome.cpp.o
Linking CXX static library libexample_boost_unit_test.a
[ 66%] Built target example_boost_unit_test
Scanning dependencies of target unit_tests
[100%] Building CXX object CMakeFiles/unit_tests.dir/unit_tests.cpp.o
Linking CXX executable unit_tests
[100%] Built target unit_tests

$ make test
Running tests...
Test project /home/matrim/workspace/cmake-examples/05-unit-testing/boost/build
    Start 1: test_all
1/1 Test #1: test_all .........................   Passed    0.00 sec

100% tests passed, 0 tests failed out of 1

Total Test time (real) =   0.01 sec
```

如果代码被更改并导致单元测试产生错误，那么在运行测试时你会看到以下输出。

```bash
$ make test
Running tests...
Test project /home/matrim/workspace/cmake-examples/05-unit-testing/boost/build
    Start 1: test_all
1/1 Test #1: test_all .........................***Failed    0.00 sec

0% tests passed, 1 tests failed out of 1

Total Test time (real) =   0.00 sec

The following tests FAILED:
          1 - test_all (Failed)
Errors while running CTest
make: *** [test] Error 8
```
