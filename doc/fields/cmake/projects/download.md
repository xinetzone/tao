# 下载项目

## 下载方法：构建时 

直到 CMake 3.11，包的主要下载方法是在构建时进行的。这会导致几个问题；其中最重要的是 add_subdirectory 在还不存在的文件上无法工作！为此，内置工具 ExternalProject 必须通过自己进行构建来解决这个问题。（然而，它也可以构建非 CMake 包）。

```{note}
请注意，ExternalData 是用于非包数据的工具。
```

## 下载方式：配置时

如果你更喜欢配置时，请查看 [Crascit/DownloadProject](https://github.com/Crascit/DownloadProject) 仓库，那里有一个即插即用的解决方案。子模块虽然效果很好，但我已停止大多数像 GoogleTest 这样的下载，并将它们迁移到了子模块中。如果没有网络连接，自动下载很难模拟，而且它们通常在构建目录中实现，如果你有多个构建目录，这会浪费时间和空间。