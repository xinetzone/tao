# 代码管理

管理代码是指将第三方代码包含在您的仓库中，并将其作为项目的一部分进行构建。这是一种确保构建项目所需的所有文件都是开发环境一部分的方法。

## 包含第三方代码

通常，这可能以 3rd_party 或 vendor 目录的形式出现，你可以在其中复制你想要包含的库的源代码。例如，你可以做类似的事情：

```bash
$ tree
.
├── 3rd_party
│   └── catch2
│       ├── catch2
│       │   └── catch.hpp
│       └── CMakeLists.txt
├── CMakeLists.txt
├── src
│   └── example.cpp
```

如果这些项目直接支持 CMake，那么可能可以在库文件夹上执行 add_subdirectory() 操作，并让该项目构建，从而让你的代码可以使用它。

如果第三方代码不支持 CMake，您可能需要在项目上创建 "shim" 层，以使其能够通过 CMake 进行构建和发现。

## 使用 git 来管理代码

包含第三方代码的一种稍微不同的方法可以是使用您的版本控制软件来管理整个过程。

对于 git，您可以使用 [git 子模块](https://git-scm.com/book/en/v2/Git-Tools-Submodules)或 [git 子树](https://git-scm.com/book/en/v1/Git-Tools-Subtree-Merging)。这些可以在初始化/更新时将正确的第三方代码版本拉入您的仓库。

## 示例

在 [catch2 测试](../../05-unit-testing/catch2-vendored/index)教程中，已经可以看到简单的代码管理示例。