# Git 子模块方法

如果你想在同一个服务（GitHub、GitLab、BitBucket 等）上添加一个 Git 仓库，以下是在 extern 目录将其设置为一个子模块的正确 Git 命令：

```bash
$ git submodule add ../../owner/repo.git extern/repo
```

仓库的相对路径很重要；它允许你保持与父仓库相同的访问方式（ssh 或 https）。这种方式在大多数情况下都非常好用。当你在子模块内部时，可以像对待普通仓库一样处理它，而在父仓库中，你可以通过“添加”来改变当前的提交指针。

但传统缺点在于，你必须让你的用户知道 git submodule 命令，这样他们才能 init 和 update 仓库，或者他们必须在首次克隆你的仓库时添加 `--recursive`。CMake 可以提供解决方案：

```cmake
find_package(Git QUIET)
if(GIT_FOUND AND EXISTS "${PROJECT_SOURCE_DIR}/.git")
# Update submodules as needed
    option(GIT_SUBMODULE "Check submodules during build" ON)
    if(GIT_SUBMODULE)
        message(STATUS "Submodule update")
        execute_process(COMMAND ${GIT_EXECUTABLE} submodule update --init --recursive
                        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
                        RESULT_VARIABLE GIT_SUBMOD_RESULT)
        if(NOT GIT_SUBMOD_RESULT EQUAL "0")
            message(FATAL_ERROR "git submodule update --init --recursive failed with ${GIT_SUBMOD_RESULT}, please checkout submodules")
        endif()
    endif()
endif()

if(NOT EXISTS "${PROJECT_SOURCE_DIR}/extern/repo/CMakeLists.txt")
    message(FATAL_ERROR "The submodules were not downloaded! GIT_SUBMODULE was turned off or failed. Please update submodules and try again.")
endif()
```

第一行使用 CMake 的内置 `FindGit.cmake` 检查 Git。然后，如果你在源代码的 git checkout 中，添加一个选项（默认为 `ON` ），允许开发者如果需要可以关闭该功能。接着运行命令获取所有仓库，如果命令失败则失败，并显示友好的错误信息。最后，我们验证仓库是否存在后才继续，无论使用何种方法获取。你可以使用 `OR` 列出多个。

现在，你的用户可以完全不知道子模块的存在，而你仍然可以保持良好的开发实践！唯一需要注意的是开发者；如果你在子模块中开发，每次重新运行 CMake 时都会重置子模块。只需在父级暂存区添加新的提交，你就能正常工作。

然后，你可以包含那些提供良好 CMake 支持的项目：

```cmake
add_subdirectory(extern/repo)
```

或者，如果是一个仅包含头文件的工程，你可以自己构建一个接口库目标。或者，如果支持，你可以使用 `find_package`，可能需要将初始搜索目录设置为已添加的那个（查看文档或你正在使用的 `Find*.cmake` 文件的文件）。你也可以将 CMake 辅助文件目录包含进来，如果你追加到你的 `CMAKE_MODULE_PATH`，例如添加 `pybind11` 的改进版 `FindPython*.cmake` 文件。

## 附加：Git 版本号 

将这部分移至 Git 部分：

```cmake
execute_process(COMMAND ${GIT_EXECUTABLE} rev-parse --short HEAD
                WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}"
                OUTPUT_VARIABLE PACKAGE_GIT_VERSION
                ERROR_QUIET
                OUTPUT_STRIP_TRAILING_WHITESPACE)
```
