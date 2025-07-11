# 他人使用你的库的方法

允许他人使用你的库有三种好方法和一种坏方法：

## 查找模块（坏方法）

如果你是库的作者，不要创建 `Find<mypackage>.cmake` 脚本！这些是为那些作者不支持 CMake 的库设计的。相反，请按照下面列出的方式使用 `Config<mypackage>.cmake`。

## 添加子项目

一个包可以将你的项目包含在子目录中，然后在子目录上使用 `add_subdirectory`。这对于仅包含头文件和编译速度快的库很有用。请注意，安装命令可能会干扰父项目，因此你可以在 `add_subdirectory` 命令中添加 `EXCLUDE_FROM_ALL`；你明确使用的目标仍然会被构建。

为了作为库的作者支持这一点，请确保你使用 `CMAKE_CURRENT_SOURCE_DIR` 而不是 `PROJECT_SOURCE_DIR` （同样适用于其他变量，如二进制目录）。你可以检查 `CMAKE_PROJECT_NAME STREQUAL PROJECT_NAME` ，只为这个项目添加有意义的选项或默认值。

此外，由于命名空间是个好主意，并且你的库的使用应该与其他下方方法保持一致，你应该添加

```cmake
add_library(MyLib::MyLib ALIAS MyLib)
```

来在所有方法中标准化使用。这个 ALIAS 目标不会被下方导出。

## 导出

第三种方式是 `*Config.cmake` 脚本。

## 安装

见[安装](Installing)