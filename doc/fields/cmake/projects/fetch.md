# FetchContent (CMake 3.11+)

通常，您希望在配置阶段而不是构建阶段进行数据或包的下载。这一功能在第三方模块中多次被发明，但最终作为 [FetchContent](https://cmake.org/cmake/help/latest/module/FetchContent.html) 模块被添加到 CMake 3.11 中。

FetchContent 模块拥有出色的文档，我不会尝试重复。关键点包括：
- 使用 `FetchContent_Declare(MyName)` 获取数据或包。您可以设置 URL、Git 仓库等。
- 在第一步中您选择的名字上使用 `FetchContent_GetProperties(MyName)` 获取 `MyName_*` 变量。
- 检查 `MyName_POPULATED`，如果未填充，则使用 `FetchContent_Populate(MyName)` （如果是包，则使用 `add_subdirectory("${MyName_SOURCE_DIR}" "${MyName_BINARY_DIR}")` ）

例如，下载 Catch2：

```cmake
FetchContent_Declare(
  catch
  GIT_REPOSITORY https://github.com/catchorg/Catch2.git
  GIT_TAG        v2.13.6
)

# CMake 3.14+
FetchContent_MakeAvailable(catch)
```

如果你无法使用 CMake 3.14+，准备代码的经典方式是：

```cmake
# CMake 3.11+
FetchContent_GetProperties(catch)
if(NOT catch_POPULATED)
  FetchContent_Populate(catch)
  add_subdirectory(${catch_SOURCE_DIR} ${catch_BINARY_DIR})
endif()
```

当然，你可以将这个内容打包成宏：

```cmake
if(${CMAKE_VERSION} VERSION_LESS 3.14)
    macro(FetchContent_MakeAvailable NAME)
        FetchContent_GetProperties(${NAME})
        if(NOT ${NAME}_POPULATED)
    	    FetchContent_Populate(${NAME})
    	    add_subdirectory(${${NAME}_SOURCE_DIR} ${${NAME}_BINARY_DIR})
        endif()
    endmacro()
endif()
```

现在你可以在 CMake 3.11+中使用 CMake 3.14+的语法。

这里有[示例](https://gitlab.com/CLIUtils/modern-cmake/-/tree/master/examples/fetch)。