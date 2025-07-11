# GoogleTest

GoogleTest 和 GoogleMock 是经典选项；我个人推荐使用 Catch2，因为 GoogleTest 严格遵循 Google 的开发哲学；它很快就会放弃旧编译器，它假设用户想要生活在 HEAD 上等等。添加 GoogleMock 也常常令人痛苦——而且你需要 GoogleMock 才能获得 matchers，而 matchers 是 Catch2 的默认功能（但不是 doctest 的）。

## 子模块方法（首选）

要使用这种方法，只需将 GoogleTest 作为子模块检出：

```bash
git submodule add --branch=release-1.8.0 ../../google/googletest.git extern/googletest
```

然后在你的主 `CMakeLists.txt` 中：

```cmake
option(PACKAGE_TESTS "Build the tests" ON)
if(PACKAGE_TESTS)
    enable_testing()
    include(GoogleTest)
    add_subdirectory(tests)
endif()
```

推荐使用 `PROJECT_NAME STREQUAL CMAKE_PROJECT_NAME` 来设置 `PACKAGE_TESTS` 选项的默认值，因为只有当这是当前项目时，它才应该默认构建。如前所述，你必须在你的主 `CMakeLists` 文件中做 `enable_testing`。

现在，在你的测试目录中：

```cmake
add_subdirectory("${PROJECT_SOURCE_DIR}/extern/googletest" "extern/googletest")
```

如果你在主 CMakeLists 文件中这样做，你可以使用普通的 add_subdirectory ；这里的额外路径是需要的，以纠正构建路径，因为我们是从子目录中调用它的。

下一行是可选的，但可以使你的 CACHE 更干净：

```cmake
mark_as_advanced(
    BUILD_GMOCK BUILD_GTEST BUILD_SHARED_LIBS
    gmock_build_tests gtest_build_samples gtest_build_tests
    gtest_disable_pthreads gtest_force_shared_crt gtest_hide_internal_symbols
)
```

如果你对保持支持文件夹的 IDE 干净感兴趣，我也会添加这些行：

```cmake
set_target_properties(gtest PROPERTIES FOLDER extern)
set_target_properties(gtest_main PROPERTIES FOLDER extern)
set_target_properties(gmock PROPERTIES FOLDER extern)
set_target_properties(gmock_main PROPERTIES FOLDER extern)
```

然后，要添加测试，推荐使用以下宏：

```cmake
macro(package_add_test TESTNAME)
    # create an executable in which the tests will be stored
    add_executable(${TESTNAME} ${ARGN})
    # link the Google test infrastructure, mocking library, and a default main function to
    # the test executable.  Remove g_test_main if writing your own main function.
    target_link_libraries(${TESTNAME} gtest gmock gtest_main)
    # gtest_discover_tests replaces gtest_add_tests,
    # see https://cmake.org/cmake/help/v3.10/module/GoogleTest.html for more options to pass to it
    gtest_discover_tests(${TESTNAME}
        # set a working directory so your project root so that you can find test data via paths relative to the project root
        WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}
        PROPERTIES VS_DEBUGGER_WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}"
    )
    set_target_properties(${TESTNAME} PROPERTIES FOLDER tests)
endmacro()

package_add_test(test1 test1.cpp)
```

这将允许你快速简单地添加测试。你可以根据需要调整。如果你之前没见过， ARGN 表示“列出的参数之后的每个参数”。修改宏以满足你的需求。例如，如果你在测试库，并且需要为不同的测试链接不同的库，你可以使用这个：

```cmake
macro(package_add_test_with_libraries TESTNAME FILES LIBRARIES TEST_WORKING_DIRECTORY)
    add_executable(${TESTNAME} ${FILES})
    target_link_libraries(${TESTNAME} gtest gmock gtest_main ${LIBRARIES})
    gtest_discover_tests(${TESTNAME}
        WORKING_DIRECTORY ${TEST_WORKING_DIRECTORY}
        PROPERTIES VS_DEBUGGER_WORKING_DIRECTORY "${TEST_WORKING_DIRECTORY}"
    )
    set_target_properties(${TESTNAME} PROPERTIES FOLDER tests)
endmacro()

package_add_test_with_libraries(test1 test1.cpp lib_to_test "${PROJECT_DIR}/european-test-data/")
```

## 下载方法

你可以使用 [CMake 辅助仓库](https://github.com/CLIUtils/cmake)中的下载器，通过 CMake 的 include 命令来使用。

这是一个基于优秀的 [DownloadProject](https://github.com/Crascit/DownloadProject) 工具的 [GoogleTest 下载器](https://github.com/google/googletest)。为每个项目下载一份副本是使用 GoogleTest 的推荐方式（事实上，他们已经禁用了自动 CMake 安装目标），所以这种方式尊重了这一设计决策。这个方法在配置时下载项目，以便 IDE 正确找到库。使用它很简单：

```cmake
cmake_minimum_required(VERSION 3.15)
project(MyProject CXX)
list(APPEND CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake)

enable_testing() # Must be in main file

include(AddGoogleTest) # Could be in /tests/CMakeLists.txt
add_executable(SimpleTest SimpleTest.cu)
add_gtest(SimpleTest)
```

````{note}
注意： `add_gtest` 只是一个宏，它添加 `gtest` 、 `gmock` 和 `gtest_main` ，然后运行 `add_test` 来创建同名的测试：
```cmake
target_link_libraries(SimpleTest gtest gmock gtest_main)
add_test(SimpleTest SimpleTest)
```
````

## FetchContent: CMake 3.11

FetchContent 模块的示例是 GoogleTest：

```cmake
include(FetchContent)

FetchContent_Declare(
  googletest
  GIT_REPOSITORY https://github.com/google/googletest.git
  GIT_TAG        release-1.8.0
)

FetchContent_GetProperties(googletest)
if(NOT googletest_POPULATED)
  FetchContent_Populate(googletest)
  add_subdirectory(${googletest_SOURCE_DIR} ${googletest_BINARY_DIR})
endif()
```
