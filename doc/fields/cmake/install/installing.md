# 安装

安装命令会在你 `make install` 时将文件或目标“安装”到安装树中。你的基本目标安装命令如下：

```cmake
install(TARGETS MyLib
        EXPORT MyLibTargets
        LIBRARY DESTINATION lib
        ARCHIVE DESTINATION lib
        RUNTIME DESTINATION bin
        INCLUDES DESTINATION include
        )
```

各种目的地只有在你要安装库、静态库或程序时才需要。包含目录是特殊的；因为目标不会安装包含文件。它只在导出的目标上设置包含目录（这通常已经由 `target_include_directories` 设置，所以如果你想要干净的 cmake 文件，请检查 `MyLibTargets` 文件并确保你不包含两次包含目录）。

通常来说，让 CMake 能够访问版本信息是个好主意，这样 `find_package` 就可以指定版本。这看起来是这样的：

```cmake
include(CMakePackageConfigHelpers)
write_basic_package_version_file(
    MyLibConfigVersion.cmake
    VERSION ${PACKAGE_VERSION}
    COMPATIBILITY AnyNewerVersion
    )
```

接下来你有两个选择。你需要创建 `MyLibConfig.cmake`，但你可以直接将目标导出到它，或者手动编写它，然后包含目标文件。如果你有任何依赖项，即使是 OpenMP，也需要使用后一种选项，所以我将说明这种方法。

首先，创建安装目标文件（与你在构建目录中创建的那个非常相似）：

```cmake
install(EXPORT MyLibTargets
        FILE MyLibTargets.cmake
        NAMESPACE MyLib::
        DESTINATION lib/cmake/MyLib
         )
```

这个文件将把你导出的目标放入文件中。如果你没有依赖项，这里就使用 `MyLibConfig.cmake` 而不是 `MyLibTargets.cmake`。然后在你的源代码树中的某个地方编写一个自定义的 `MyLibConfig.cmake` 文件。如果你想要捕获配置时的变量，可以使用 `.in` 文件，并且你将需要使用 `@var@` 语法。内容看起来是这样的：

```cmake
include(CMakeFindDependencyMacro)

# Capturing values from configure (optional)
set(my-config-var @my-config-var@)

# Same syntax as find_package
find_dependency(MYDEP REQUIRED)

# Any extra setup

# Add the targets file
include("${CMAKE_CURRENT_LIST_DIR}/MyLibTargets.cmake")
```

现在，你可以使用配置文件（如果你使用了 `.in` 文件），然后安装生成的文件。因已经创建了 `ConfigVersion` 文件，这也是安装它的好地方。

```cmake
configure_file(MyLibConfig.cmake.in MyLibConfig.cmake @ONLY)
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/MyLibConfig.cmake"
              "${CMAKE_CURRENT_BINARY_DIR}/MyLibConfigVersion.cmake"
        DESTINATION lib/cmake/MyLib
        )
```

就这样！现在一旦你安装了一个包，`lib/cmake/MyLib` 中就会有 CMake 会搜索的文件（具体来说，是 `MyLibConfig.cmake` 和 `MyLibConfigVersion.cmake` ），而且 `config` 使用的目标文件也应该在那里。

当 CMake 搜索一个包时，它会在当前安装前缀和几个标准位置查找。你也可以手动将 `MyLib_PATH` 添加到搜索路径中，如果配置文件未找到，CMake 会给出友好的帮助输出。

上面提到的 [CMakePackageConfigHelpers](https://cmake.org/cmake/help/latest/module/CMakePackageConfigHelpers.html) 模块有额外的工具来帮助编写更可移植的 Config.cmake 文件。参考 CMake 文档中的 [configure_package_config_file](https://cmake.org/cmake/help/latest/module/CMakePackageConfigHelpers.html#command:configure_package_config_file)（用于替代 `configure_file` ）和 `@PACKAGE_INIT@` 替换字符串来获取

- 一组自动定义的 `PACKAGE_<var>` 变量（用于 `<var>` 的相对路径版本）和
- 一个 `set_and_check()` 的 `set()` 替代方案，用于自动检查路径是否存在。