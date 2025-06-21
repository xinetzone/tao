# 使用软件包

本节介绍如何使用 Conan 管理依赖项来构建项目。我们将从一个使用 CMake 并依赖于 zlib 库的 C 项目的基本示例开始。该项目将使用一个 conanfile.txt 文件来声明其依赖项。

我们还将介绍如何不仅可以使用 Conan 管理“常规”库，还可以管理构建过程中可能需要的工具：例如 CMake、msys2、MinGW 等。

然后，我们将解释 Conan 的不同概念，如 settings（设置）和 options（选项），以及如何使用它们来构建用于不同配置的项目，例如 Debug（调试）、Release（发布）、静态或共享库等。

此外，我们将解释如何从第一个示例中使用的 conanfile.txt 文件过渡到功能更强大的 conanfile.py 文件。

之后，我们将介绍 Conan 的 build 和 host 配置文件概念，并解释如何使用它们将应用程序交叉编译到不同的平台。

然后，在“版本控制简介”中，我们将学习如何使用不同的版本、定义带有版本范围的需求、修订版（revisions）概念，以及简要介绍 lockfiles（锁定文件）以实现依赖图的可重现性。

```{toctree}
build-simple-cmake-project
use-tools-as-conan-packages
configurations
```
