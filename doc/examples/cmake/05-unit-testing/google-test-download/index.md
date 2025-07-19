# Google 测试单元测试框架

使用 [CTest](https://cmake.org/Wiki/CMake/Testing_With_CTest)，你可以生成 make test 目标来运行自动化的单元测试。本示例展示了如何下载和构建[谷歌测试库](https://github.com/google/googletest)，创建测试并运行它们。

本教程中的文件如下：
```bash
$ tree
.
├── 3rd_party
│   └── google-test
│       ├── CMakeLists.txt
│       └── CMakeLists.txt.in
├── CMakeLists.txt
├── Reverse.h
├── Reverse.cpp
├── Palindrome.h
├── Palindrome.cpp
├── unit_tests.cpp
```

- `3rd_party/google-test/CMakeLists.txt` - 构建和准备谷歌测试库的 CMake 命令
- `3rd_party/google-test/CMakeLists.txt.in` - 用于下载谷歌测试的辅助脚本
- `CMakeLists.txt` - 包含你希望运行的 CMake 命令
- `Reverse.h / .cpp` - 用于反转字符串的类
- `Palindrome.h / .cpp` - 用于测试字符串是否为回文的类
- `unit_test.cpp` - 使用 google test 单元测试框架的单元测试

## 下载并构建 Google Test

```cmake
add_subdirectory(3rd_party/google-test)
```

这将添加用于下载和构建 Google Test 的 CMake 文件。这是添加 Google Test 的推荐方法，[Google Test 的 readme](https://github.com/google/googletest/blob/master/googletest/README.md) 文件和这里都有更多详细信息。

## 启用测试

要启用测试，您必须在您的顶层 CMakeLists.txt 中包含以下行

```cmake
enable_testing()
```

这将启用对当前文件夹及其所有子文件夹的测试。

## 添加测试可执行文件

这一步的要求将取决于你的单元测试框架。在谷歌测试的示例中，你可以创建包含所有你想运行的单元测试的二进制文件。

```cmake
add_executable(unit_tests unit_tests.cpp)

target_link_libraries(unit_tests
    example_google_test
    GTest::GTest
    GTest::main
)
```

在上述代码中，添加了一个单元测试二进制文件，它通过在[下载和构建](https://github.com/ttroy50/cmake-examples/blob/master/05-unit-testing/google-test-download/3rd_party/google-test/CMakeLists.txt) GTest 期间设置的 ALIAS 目标链接到谷歌测试单元测试框架。

## 添加测试

要添加一个测试，你调用 add_test() 函数。这将创建一个命名的测试，它将运行提供的命令。
```cmake
add_test(test_all unit_tests)
```

在这个例子中，我们创建一个名为 test_all 的测试，它将运行由 unit_tests 可执行文件创建的可执行文件，该可执行文件是由调用 add_executable 创建的。

## 构建示例

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
-- Build files have been written to: /data/data/code/cmake-examples/05-unit-testing/google-test-download/build/3rd_party/google-test/googletest-download
Scanning dependencies of target googletest
[ 11%] Creating directories for 'googletest'
[ 22%] Performing download step (download, verify and extract) for 'googletest'
-- downloading...
     src='https://github.com/google/googletest/archive/bfc0ffc8a698072c794ae7299db9cb6866f4c0bc.tar.gz'
     dst='/data/data/code/cmake-examples/05-unit-testing/google-test-download/build/3rd_party/google-test/googletest-download/googletest-prefix/src/bfc0ffc8a698072c794ae7299db9cb6866f4c0bc.tar.gz'
     timeout='none'
-- downloading... done
-- verifying file...
     file='/data/data/code/cmake-examples/05-unit-testing/google-test-download/build/3rd_party/google-test/googletest-download/googletest-prefix/src/bfc0ffc8a698072c794ae7299db9cb6866f4c0bc.tar.gz'
-- verifying file... warning: did not verify file - no URL_HASH specified?
-- extracting...
     src='/data/code/cmake-examples/05-unit-testing/google-test-download/build/3rd_party/google-test/googletest-download/googletest-prefix/src/bfc0ffc8a698072c794ae7299db9cb6866f4c0bc.tar.gz'
     dst='/data/code/cmake-examples/05-unit-testing/google-test-download/build/3rd_party/google-test/googletest-src'
-- extracting... [tar xfz]
-- extracting... [analysis]
-- extracting... [rename]
-- extracting... [clean up]
-- extracting... done
[ 33%] No patch step for 'googletest'
[ 44%] No update step for 'googletest'
[ 55%] No configure step for 'googletest'
[ 66%] No build step for 'googletest'
[ 77%] No install step for 'googletest'
[ 88%] No test step for 'googletest'
[100%] Completed 'googletest'
[100%] Built target googletest
-- Found PythonInterp: /usr/bin/python (found version "2.7.12")
-- Looking for pthread.h
-- Looking for pthread.h - found
-- Looking for pthread_create
-- Looking for pthread_create - not found
-- Check if compiler accepts -pthread
-- Check if compiler accepts -pthread - yes
-- Found Threads: TRUE
-- Configuring done
-- Generating done
-- Build files have been written to: /data/code/cmake-examples/05-unit-testing/google-test-download/build

$ make
Scanning dependencies of target example_google_test
[  6%] Building CXX object CMakeFiles/example_google_test.dir/Reverse.cpp.o
[ 12%] Building CXX object CMakeFiles/example_google_test.dir/Palindrome.cpp.o
[ 18%] Linking CXX static library libexample_google_test.a
[ 18%] Built target example_google_test
Scanning dependencies of target gtest
[ 25%] Building CXX object 3rd_party/google-test/googletest-build/googlemock/gtest/CMakeFiles/gtest.dir/src/gtest-all.cc.o
[ 31%] Linking CXX static library libgtest.a
[ 31%] Built target gtest
Scanning dependencies of target gtest_main
[ 37%] Building CXX object 3rd_party/google-test/googletest-build/googlemock/gtest/CMakeFiles/gtest_main.dir/src/gtest_main.cc.o
[ 43%] Linking CXX static library libgtest_main.a
[ 43%] Built target gtest_main
Scanning dependencies of target unit_tests
[ 50%] Building CXX object CMakeFiles/unit_tests.dir/unit_tests.cpp.o
[ 56%] Linking CXX executable unit_tests
[ 56%] Built target unit_tests
Scanning dependencies of target gmock_main
[ 62%] Building CXX object 3rd_party/google-test/googletest-build/googlemock/CMakeFiles/gmock_main.dir/__/googletest/src/gtest-all.cc.o
[ 68%] Building CXX object 3rd_party/google-test/googletest-build/googlemock/CMakeFiles/gmock_main.dir/src/gmock-all.cc.o
[ 75%] Building CXX object 3rd_party/google-test/googletest-build/googlemock/CMakeFiles/gmock_main.dir/src/gmock_main.cc.o
[ 81%] Linking CXX static library libgmock_main.a
[ 81%] Built target gmock_main
Scanning dependencies of target gmock
[ 87%] Building CXX object 3rd_party/google-test/googletest-build/googlemock/CMakeFiles/gmock.dir/__/googletest/src/gtest-all.cc.o
[ 93%] Building CXX object 3rd_party/google-test/googletest-build/googlemock/CMakeFiles/gmock.dir/src/gmock-all.cc.o
[100%] Linking CXX static library libgmock.a
[100%] Built target gmock

$ make test
Running tests...
Test project /data/code/cmake-examples/05-unit-testing/google-test-download/build
    Start 1: test_all
1/1 Test #1: test_all .........................   Passed    0.00 sec

100% tests passed, 0 tests failed out of 1

Total Test time (real) =   0.00 sec
```

如果代码被更改并导致单元测试产生错误，那么在运行测试时你会看到以下输出。

```bash
$ make test
Running tests...
Test project /data/code/cmake-examples/05-unit-testing/google-test-download/build
    Start 1: test_all
1/1 Test #1: test_all .........................***Failed    0.00 sec

0% tests passed, 1 tests failed out of 1

Total Test time (real) =   0.00 sec

The following tests FAILED:
    1 - test_all (Failed)
Errors while running CTest
Makefile:72: recipe for target 'test' failed
make: *** [test] Error 8
```
