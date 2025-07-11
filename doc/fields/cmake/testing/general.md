# 一般测试信息

在你的主 `CMakeLists.txt` 文件中，需要在根目录下添加以下函数调用：

```cmake
if(CMAKE_PROJECT_NAME STREQUAL PROJECT_NAME)
    include(CTest)
endif()
```

这将启用测试并设置 [BUILD_TESTING](https://cmake.org/cmake/help/v3.20/variable/BUILD_TESTING.html) 选项，以便用户可以开启或关闭测试（同时还能控制其他一些功能）。或者你可以通过直接调用 [enable_testing()](https://gitlab.kitware.com/cmake/cmake/blob/master/Modules/CTest.cmake) 来自行设置。

当你添加测试文件夹时，应该像这样操作：

```cmake
if(CMAKE_PROJECT_NAME STREQUAL PROJECT_NAME AND BUILD_TESTING)
    add_subdirectory(tests)
endif()
```

这样做的理由是，如果其他人包含了你的包，并且他们使用了 `BUILD_TESTING`，他们很可能不希望构建你的测试。在极少数情况下，如果你确实希望同时在这两个包中启用测试，你可以提供一个覆盖设置。

```cmake
if((CMAKE_PROJECT_NAME STREQUAL PROJECT_NAME OR MYPROJECT_BUILD_TESTING) AND BUILD_TESTING)
    add_subdirectory(tests)
endif()
```

上述覆盖的主要用例实际上是在本书自己的示例中，因为主 CMake 项目确实想要运行所有子项目的测试。

您可以使用以下方式注册目标：

```cmake
add_test(NAME TestName COMMAND TargetName)
```

如果在 COMMAND 后面放置除目标名称之外的其他内容，它将注册为要运行的命令行。同样，使用生成器表达式也是有效的：

```cmake
add_test(NAME TestName COMMAND $<TARGET_FILE:${TESTNAME}>)
```

这将使用生成目标的输出位置（因此，可执行文件）。

## 作为测试的一部分构建

如果你想在测试中运行 CMake 来构建一个项目，也可以这样做（事实上，这就是 CMake 自身进行测试的方式）。例如，如果你的主项目名为 MyProject ，并且你有一个可以通过自身构建的 examples/simple 项目，这看起来会像：

```cmake
add_test(
  NAME
    ExampleCMakeBuild
  COMMAND
    "${CMAKE_CTEST_COMMAND}"
             --build-and-test "${My_SOURCE_DIR}/examples/simple"
                              "${CMAKE_CURRENT_BINARY_DIR}/simple"
             --build-generator "${CMAKE_GENERATOR}"
             --test-command "${CMAKE_CTEST_COMMAND}"
)
```

## 测试框架

查看关于流行框架的配方子章节。

- [GoogleTest](https://cliutils.gitlab.io/modern-cmake/chapters/testing/googletest.html)：一个来自 Google 的流行选项。开发可能会有点慢。
- [Catch2](https://cliutils.gitlab.io/modern-cmake/chapters/testing/catch.html)：现代的、类似 PyTest 的框架，带有巧妙的宏。
- [DocTest](https://github.com/onqtam/doctest)：替代 Catch2 的工具，据称编译速度更快且更简洁。参见 Catch2 章节并替换为 DocTest。
