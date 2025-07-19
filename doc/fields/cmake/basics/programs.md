# 运行其他程序

## 在配置时运行命令

在配置时运行命令相对容易。使用 `execute_process` 来运行进程并获取结果。通常建议避免在 CMake 中硬编码程序路径；你可以使用 `${CMAKE_COMMAND}`、 `find_package(Git)` 或 `find_program` 来获取运行命令的路径。使用 `RESULT_VARIABLE` 来检查返回码，使用 `OUTPUT_VARIABLE` 来获取输出。

更新所有 git 子模块的示例：

```cmake
find_package(Git QUIET)

if(GIT_FOUND AND EXISTS "${PROJECT_SOURCE_DIR}/.git")
    execute_process(COMMAND ${GIT_EXECUTABLE} submodule update --init --recursive
                    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
                    RESULT_VARIABLE GIT_SUBMOD_RESULT)
    if(NOT GIT_SUBMOD_RESULT EQUAL "0")
        message(FATAL_ERROR "git submodule update --init --recursive failed with ${GIT_SUBMOD_RESULT}, please checkout submodules")
    endif()
endif()
```

## 在构建时运行命令

构建时命令稍微有点棘手。主要复杂之处在于目标系统；你想在什么时候运行你的命令？它是否会产生另一个目标需要的输出？考虑到这一点，这里有一个调用 Python 脚本生成头文件的示例：

```cmake
find_package(PythonInterp REQUIRED)
add_custom_command(OUTPUT "${CMAKE_CURRENT_BINARY_DIR}/include/Generated.hpp"
    COMMAND "${PYTHON_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/scripts/GenerateHeader.py" --argument
    DEPENDS some_target)

add_custom_target(generate_header ALL
    DEPENDS "${CMAKE_CURRENT_BINARY_DIR}/include/Generated.hpp")

install(FILES ${CMAKE_CURRENT_BINARY_DIR}/include/Generated.hpp DESTINATION include)
```

在这里，生成过程发生在 `some_target` 完成后，并且在你运行不带目标的 `make` 时（ `ALL` ）发生。如果你将这个作为另一个目标的依赖项使用 `add_dependencies`，你可以避免使用 `ALL` 关键字。或者，你可以要求用户在构建时显式地构建 `generate_header` 目标。

## 包含常见工具

在编写跨平台工作的 CMake 构建时，有用的工具是 `cmake -E <mode>` （在 CMake 文件中显示为 `${CMAKE_COMMAND} -E` ）。这种模式允许 CMake 在不显式调用系统工具的情况下执行各种操作，如 `copy` 、 `make_directory` 和 `remove` 。它主要用于构建时命令。请注意，非常有用的 `create_symlink` 模式以前仅限于 Unix，但在 CMake 3.13 中为 Windows 添加了该模式。请参阅[文档](https://cmake.org/cmake/help/latest/manual/cmake.1.html#command-line-tool-mode)。