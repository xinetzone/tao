# 有用模块 #

CMake 的[模块](https://cmake.org/cmake/help/latest/manual/cmake-modules.7.html)集合中有许多有用的模块；但其中一些比其他模块更有用。以下是一些亮点。

## CMakeDependentOption

[CMakeDependentOption](https://cmake.org/cmake/help/latest/module/CMakeDependentOption.html)添加了命令 `cmake_dependent_option`，它根据另一组变量的真值来设置一个选项。它看起来是这样的：

```cmake
include(CMakeDependentOption)
cmake_dependent_option(BUILD_TESTS "Build your tests" ON "VAL1;VAL2" OFF)
```

这只是简写，相当于这个：

```cmake
if(VAL1 AND VAL2)
    set(BUILD_TESTS_DEFAULT ON)
else()
    set(BUILD_TESTS_DEFAULT OFF)
endif()

option(BUILD_TESTS "Build your tests" ${BUILD_TESTS_DEFAULT})

if(NOT BUILD_TESTS_DEFAULT)
    mark_as_advanced(BUILD_TESTS)
endif()
```

请注意，如果你使用 `include(CTest)`， `BUILD_TESTING` 是一种更好的检查测试是否启用的方法，因为它是为你定义好的。这只是 `CMakeDependentOption` 的示例。

## CMakePrintHelpers

[CMakePrintHelpers](https://cmake.org/cmake/help/latest/module/CMakePrintHelpers.html)模块有几个方便的输出函数。`cmake_print_properties` 可以让你轻松打印属性。而 `cmake_print_variables` 会打印你给它的任何变量的名称和值。

## CheckCXXCompilerFlag

[CheckCXXCompilerFlag](https://cmake.org/cmake/help/latest/module/CheckCXXCompilerFlag.html) 这个函数用于检查标志是否受支持。例如：

```cmake
include(CheckCXXCompilerFlag)
check_cxx_compiler_flag(-someflag OUTPUT_VARIABLE)
```

请注意 `OUTPUT_VARIABLE` 也会出现在配置打印输出中，所以选择一个好名字。

这只是许多类似模块中的一个，例如 `CheckIncludeFileCXX`、`CheckStructHasMember`、`TestBigEndian` 和 `CheckTypeSize`，这些模块允许你检查系统信息（你可以将这些信息传递给你的源代码）。

## try_compile/try_run

[try_compile](https://cmake.org/cmake/help/latest/command/try_compile.html)/[try_run](https://cmake.org/cmake/help/latest/command/try_run.html)并非一个模块，但对上述许多模块至关重要。你可以在配置时尝试编译（并可能运行）一小段代码。这可以让你获取关于你系统功能的信息。基本语法是：

```cmake
try_compile(
  RESULT_VAR
    bindir
  SOURCES
    source.cpp
)
```

你可以添加许多选项，例如 `COMPILE_DEFINITIONS`。在 CMake 3.8 及更高版本中，这将遵循 CMake C/C++/CUDA 标准设置。如果你使用 `try_run`，它将运行生成的程序，并在 `RUN_OUTPUT_VARIABLE` 中给出输出。

## FeatureSummary

[FeatureSummary](https://cmake.org/cmake/help/latest/module/FeatureSummary.html) 是相当有用但颇为古怪的模块。它允许你打印出搜索过的包列表，以及任何你明确标记的选项。它与 [`find_package`](https://cmake.org/cmake/help/latest/command/find_package.html) 部分关联但并不完全依赖。你首先包含这个模块，一如既往：

```cmake
include(FeatureSummary)
```

然后，对于你已经运行或将要运行的任何 find_package 命令，你可以扩展默认信息：

```cmake
set_package_properties(OpenMP PROPERTIES
    URL "http://www.openmp.org"
    DESCRIPTION "Parallel compiler directives"
    PURPOSE "This is what it does in my package")
```

你也可以将包的类型设置为 `RUNTIME` 、`OPTIONAL` 、`RECOMMENDED` 或 `REQUIRED`；然而，你不能降低包的类型；如果你已经通过 `find_package` 基于某个选项添加了一个 `REQUIRED` 包，你会看到它被列为 `REQUIRED`。

此外，你可以将任何选项标记为特性摘要的一部分。如果你选择与某个包相同的名称，它们会相互交互。

```cmake
add_feature_info(WITH_OPENMP OpenMP_CXX_FOUND "OpenMP (Thread safe FCNs only)")
```

然后，你可以将功能摘要打印到屏幕或日志文件中：

```cmake
if(CMAKE_PROJECT_NAME STREQUAL PROJECT_NAME)
    feature_summary(WHAT ENABLED_FEATURES DISABLED_FEATURES PACKAGES_FOUND)
    feature_summary(FILENAME ${CMAKE_CURRENT_BINARY_DIR}/features.log WHAT ALL)
endif()
```

你可以构建任何你喜欢的 `WHAT` 项目集合，或者直接使用 `ALL`。