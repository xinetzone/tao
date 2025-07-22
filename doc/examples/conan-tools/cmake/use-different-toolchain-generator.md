# 使用不同生成器与 CMakeToolchain：Ninja 示例

本指南演示了如何使用 [CMakeToolchain](https://docs.conan.io/2/reference/tools/cmake/cmaketoolchain.html#conan-tools-cmaketoolchain) 与 [Ninja](https://ninja-build.org/) 等预定义生成器一起使用，以及如何配置它以使用不同的生成器。

```{note}
假设您已经在系统上安装了 Ninja。如果您在系统上没有安装 Ninja，可以通过添加 [`tool-requires`](https://docs.conan.io/2/reference/config_files/profiles.html#reference-config-files-profiles-tool-requires) 在您的配置文件（默认或自定义）中使用 [Ninja Conan 包](https://conan.io/center/recipes/ninja)。
```

## 理解 CMake 生成器

[CMake](https://cmake.org/) 客户端提供了多种[生成器](https://cmake.org/cmake/help/latest/manual/cmake-generators.7.html)来创建构建系统文件。如果您想使用 CMake 选择的默认生成器以外的生成器，您可以配置 `tools.cmake.cmaketoolchain:generator` 。

```{note}
请注意，[CMake 客户端](https://cmake.org/)与 [Conan CMake 辅助工具](https://docs.conan.io/2/reference/tools/cmake/cmake.html#conan-tools-cmake-helper)不是同一个。
```

要查看您的系统上有哪些生成器可用，请运行：

```bash
cmake --help
```

您可以在您的[配置文件](https://docs.conan.io/2/reference/config_files/profiles.html#reference-config-files-profiles-conf)中设置此配置，直接在命令行中设置，甚至可以在您的[全局配置](https://docs.conan.io/2/reference/config_files/global_conf.html#reference-config-files-global-conf-patterns)中设置。

## 在配置文件中默认使用 Ninja 生成器

首先，创建配置文件名 `my_custom_profile`，以便可以将 Ninja 生成器设置为使用此配置构建的所有 Conan 包的默认生成器。

```bash
conan profile detect --name=my_custom_profile
```

要在 `my_custom_profile` 配置文件中将 Ninja 生成器设置为默认值，请在文件中添加条目 `[conf]`，其中包含生成器的值：

```bash
[settings]
os=Linux
arch=x86_64
compiler=gcc
compiler.version=13
compiler.libcxx=libstdc++11
compiler.cppstd=20
build_type=Release

[conf]
tools.cmake.cmaketoolchain:generator=Ninja
```

现在，将基于 `cmake_exe` 模板创建基本项目，作为 C++ 项目的示例：

```bash
conan new cmake_exe -d name=foo -d version=0.1.0
```

然后，使用刚刚创建的配置来构建项目：

```bash
conan create . -pr=my_custom_profile
```

此配置将被传递到由 `CMakeToolchain` 生成的 `conan_toolchain.cmake` 文件，然后使用 Ninja 生成器。你应该看到以下输出片段，表明正在使用 Ninja 生成器：

```bash
Profile host:
[settings]
...
[conf]
tools.cmake.cmaketoolchain:generator=Ninja

...
foo/0.1.0: Calling build()
foo/0.1.0: Running CMake.configure()
foo/0.1.0: RUN: cmake -G "Ninja" ...
```

请注意，相同的配置可以传递给默认配置文件，并用于使用该配置文件构建的所有 Conan 软件包。

如果通过命令行传递生成器配置，则相同配置将覆盖配置文件设置。
