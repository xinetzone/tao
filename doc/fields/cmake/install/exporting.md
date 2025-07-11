# 导出

```{danger}
从 CMake 3.15 开始，导出的默认行为发生了变化。由于更改用户主目录中的文件被认为是“出乎意料的”（而且确实如此，这也是本章存在的原因），因此不再作为默认行为。如果你设置最低或最高 CMake 版本为 3.15 或更高版本，除非你按照以下方式设置 `CMAKE_EXPORT_PACKAGE_REGISTRY`，否则这种情况将不再发生。
```

从另一个项目访问一个项目有三种方法：子目录、导出的构建目录和安装。要在另一个项目中使用一个项目的构建目录，你需要导出目标。为了正确安装，需要导出目标；而允许使用构建目录只需添加两行代码。这通常不是我推荐的工作方式，但对于开发和作为后面讨论的安装过程的准备方式可能很有用。

你应该创建导出集，可能靠近你的主 `CMakeLists.txt` 的末尾。

```cmake
export(TARGETS MyLib1 MyLib2 NAMESPACE MyLib:: FILE MyLibTargets.cmake)
```

这会将你列出的目标放入构建目录中的文件，并可选地为其添加命名空间前缀。现在，为了让 CMake 能够找到这个包，需要将包导出到 `$HOME/.cmake/packages` 文件夹：

```cmake
set(CMAKE_EXPORT_PACKAGE_REGISTRY ON)
export(PACKAGE MyLib)
```

现在，如果你 `find_package(MyLib)`，CMake 就能找到构建目录。查看生成的 `MyLibTargets.cmake` 文件，以帮助你理解具体创建了什么；它只是普通的 CMake 文件，包含了导出的目标。

需要注意的是，存在缺点：如果你有导入的依赖，它们需要在 `find_package` 之前导入。这将在下一个方法中解决。
