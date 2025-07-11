# 打包

有两种方法可以指示 CMake 构建您的软件包；一种是通过使用 `CPackConfig.cmake` 文件，另一种是将 `CPack` 变量集成到您的 `CMakeLists.txt` 文件中。由于您希望将主构建中的变量包含进来，比如版本号，如果您选择这种方式，就需要创建一个配置文件。我将向您展示集成版本：

```cmake
# Packaging support
set(CPACK_PACKAGE_VENDOR "Vendor name")
set(CPACK_PACKAGE_DESCRIPTION_SUMMARY "Some summary")
set(CPACK_PACKAGE_VERSION_MAJOR ${PROJECT_VERSION_MAJOR})
set(CPACK_PACKAGE_VERSION_MINOR ${PROJECT_VERSION_MINOR})
set(CPACK_PACKAGE_VERSION_PATCH ${PROJECT_VERSION_PATCH})
set(CPACK_RESOURCE_FILE_LICENSE "${CMAKE_CURRENT_SOURCE_DIR}/LICENSE")
set(CPACK_RESOURCE_FILE_README "${CMAKE_CURRENT_SOURCE_DIR}/README.md")
```

这是制作二进制软件包时最常用的变量。二进制软件包使用 CMake 的安装机制，因此任何安装的内容都会包含在内。

您也可以制作源代码软件包。您应该将 `CPACK_SOURCE_IGNORE_FILES` 设置为正则表达式，以确保不会选择任何额外的文件（如构建目录或 git 详细信息）；否则 `make package_source` 会将源代码目录中的所有内容原封不动地打包在一起。您还可以设置源代码生成器，以使源代码软件包生成您喜欢的文件类型：

```cmake
set(CPACK_SOURCE_GENERATOR "TGZ;ZIP")
set(CPACK_SOURCE_IGNORE_FILES
    /.git
    /dist
    /.*build.*
    /\\\\.DS_Store
)
```

请注意，这种方法在 Windows 上不起作用，但生成的源代码软件包在 Windows 上可以正常工作。

最后，您需要包含 CPack 模块：

```cmake
include(CPack)
```
