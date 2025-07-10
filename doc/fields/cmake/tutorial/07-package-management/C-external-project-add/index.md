# 外部项目

CMake 支持使用 External Project 命令下载和构建外部项目。通过在代码中添加 ExternalProject_Add，你可以让 CMake 自动从 HTTP 或源代码管理系统（例如 git）下载源文件。

配置完成后，外部项目将生成一个自定义目标，该目标可用于控制外部项目的下载、更新、构建、测试和安装阶段。

## 标准

外部项目的简单示例如下：

```cmake
include(ExternalProject)
ExternalProject_Add(googletest
  URL    https://github.com/google/googletest/archive/bfc0ffc8a698072c794ae7299db9cb6866f4c0bc.tar.gz_
)
```

添加后，你将获得目标 googletest ，它会在你构建项目时尝试下载、构建和安装 Google Test。

```{note}
这会尝试将 Google Test 安装到你的标准位置，例如 /usr/ ，如果你不是 root 用户，可能会失败。要跳过安装步骤，你可以添加一行 `INSTALL_COMMAND ""`
```

默认情况下，项目假定通过 CMake 工作，外部项目将知道如何使用标准的 CMake 命令进行构建。如果外部项目使用不同的构建系统，你可以使用 INSTALL_COMMAND、CONFIGURE_COMMAND、BUILD_COMMAND 等来设置各种命令。

## 替代方法

安装包的另一种方法是在 CMake 配置时运行 ExternalProject 命令。这会导致下载在配置步骤发生，然后你可以使用 add_subdirectory 将项目添加到你的代码中（假设它使用 CMake）。一个示例可以在 [google-test-download 教程](../../05-unit-testing/google-test-download/index)中找到。

更通用的下载代码版本可以在[这里](https://github.com/Crascit/DownloadProject)找到。