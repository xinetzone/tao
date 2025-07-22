# 工具需求包

在“[将构建工具作为 Conan 包使用](https://docs.conan.io/2/tutorial/consuming_packages/use_tools_as_conan_packages.html#consuming-packages-tool-requires)”部分，学习了如何使用工具需求来构建（或协助构建）项目或 Conan 包。在本节中，将学习如何为工具需求创建配方。

```{admonition} 最佳实践
:class: tip

`tool_requires` 和 tool packages 适用于可执行应用程序，例如 `cmake` 或 `ninja`，这些可以作为 `tool_requires("cmake/[>=3.25]")` 被其他包使用，以将它们放置在它们的路径中。它们不适用于库式的依赖项（为它们使用 `requires`），测试框架（使用 `test_requires` ）或通常属于最终应用程序“主机”上下文中的任何内容。不要滥用 `tool_requires` 用于其他目的。
```

请首先克隆源代码以重新创建此项目。你可以在 GitHub 上的 examples2 存储库中找到它们：

```bash
git clone https://github.com/conan-io/examples2.git
cd examples2/tutorial/creating_packages/other_packages/tool_requires/tool
```

## 简单的工具需求配方

这是（假的）应用程序的配方，该应用程序接收路径，如果路径是安全的则返回 `0`。可以检查以下简单的配方如何涵盖了大多数 `tool-require` 使用案例：

```{code-block} python
:caption: conanfile.py

import os
from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.tools.files import copy


class secure_scannerRecipe(ConanFile):
    name = "secure_scanner"
    version = "1.0"
    package_type = "application"

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"

    # Sources are located in the same place as this recipe, copy them to the recipe
    exports_sources = "CMakeLists.txt", "src/*"

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        extension = ".exe" if self.settings_build.os == "Windows" else ""
        copy(self, "*secure_scanner{}".format(extension),
             self.build_folder, os.path.join(self.package_folder, "bin"), keep_path=False)

    def package_info(self):
        self.buildenv_info.define("MY_VAR", "23")
```

这个配方中有几个相关事项：

- 它声明了 `package_type = "application"`。这是可选的但方便，它将告诉 Conan 当前包不包含要链接的头文件或库。消费者将知道这个包是应用程序。
- `package()` 方法将可执行文件打包到 `bin/` 文件夹中，该文件夹默认声明为 `bindir： self.cpp_info.bindirs = ["bin"]`。
- 在 `package_info()` 方法中，使用 `self.buildenv_info` 来定义环境变量 `MY_VAR`，该变量也将对消费者可用。

为 `tool_require` 创建二进制包：

```bash
$ conan create .
...
secure_scanner/1.0: Calling package()
secure_scanner/1.0: Copied 1 file: secure_scanner
secure_scanner/1.0 package(): Packaged 1 file: secure_scanner
...
Security Scanner: The path 'mypath' is secure!
```

回顾一下 `test_package/conanfile.py`：

```python
from conan import ConanFile


class secure_scannerTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def test(self):
        extension = ".exe" if self.settings_build.os == "Windows" else ""
        self.run("secure_scanner{} mypath".format(extension))
```

要求使用 `secure_scanner` 包，因为 `tool_require` 正在执行 `self.tool_requires(self.tested_reference_str)`。在 `test()` 方法中，运行应用程序，因为它是 `PATH` 中的可用程序。在下一个示例中，将看到为什么来自 `tool_require` 的可执行文件对消费者是可用的。

创建消费者配方来测试是否可以运行 `tool_require` 的 `secure_scanner` 应用程序并读取环境变量。前往 `examples2/tutorial/creating_packages/other_packages/tool_requires/consumer` 文件夹：

```{code-block} python
:caption: conanfile.py

from conan import ConanFile

class MyConsumer(ConanFile):
    name = "my_consumer"
    version = "1.0"
    settings = "os", "arch", "compiler", "build_type"
    tool_requires = "secure_scanner/1.0"

    def build(self):
        extension = ".exe" if self.settings_build.os == "Windows" else ""
        self.run("secure_scanner{} {}".format(extension, self.build_folder))
        if self.settings_build.os != "Windows":
            self.run("echo MY_VAR=$MY_VAR")
        else:
            self.run("set MY_VAR")
```

在这个简单的配方中，声明了从 `tool_require` 到 `secure_scanner/1.0` 的范围，并在 `build()` 方法中直接调用了打包的应用程序 `secure_scanner` ，同时打印了 `MY_VAR` 环境变量的值。

如果构建消费者：
```bash
$ conan build .

-------- Installing (downloading, building) binaries... --------
secure_scanner/1.0: Already installed!

-------- Finalizing install (deploy, generators) --------
...
conanfile.py (my_consumer/1.0): RUN: secure_scanner /Users/luism/workspace/examples2/tutorial/creating_packages/other_packages/tool_requires/consumer
...
Security Scanner: The path '/Users/luism/workspace/examples2/tutorial/creating_packages/other_packages/tool_requires/consumer' is secure!
...
MY_VAR=23
```

可以看到可执行文件返回了 `0`（因为文件夹是安全的），并且输出了 `Security Scanner: The path is secure!` 消息。它还输出了分配给 `MY_VAR` 的“23”值，但是，为什么这些会自动可用呢？

- 生成器 `VirtualBuildEnv` 和 `VirtualRunEnv` 会自动使用。
- `VirtualRunEnv` 正在读取 `tool-requires` ，并创建像 `conanbuildenv-release-x86_64.sh` 的启动器，将所有 `cpp_info.bindirs` 追加到 `PATH` ，将所有 `cpp_info.libdirs` 追加到 `LD_LIBRARY_PATH` 环境变量，并声明每个 `self.buildenv_info` 变量。
- 每次 conan 执行 `self.run` 时，默认情况下，在调用任何命令之前会激活 `conanbuild.sh` 文件。`conanbuild.sh` 包含了 `conanbuildenv-release-x86_64.sh` ，所以应用程序在 `PATH` 中，环境变量“`MYVAR`”具有 `tool-require` 中声明的值。

## 在 `package_id()` 中移除设置

通过之前的配方，如果我们使用不同的设置调用 `conan create`，比如不同的编译器版本，我们会得到具有不同 `package ID` 的二进制包。这可能便于，例如，更好地追踪我们的工具。在这种情况下，兼容性插件可以帮助我们在 Conan 找不到我们特定编译器版本的二进制文件时定位最佳匹配的二进制文件。

但在某些情况下，可能只想生成二进制文件，只考虑 `os` ， `arch`，或者最多添加 `build_type` 来知道应用程序是构建为 `Debug` 还是 `Release`。可以添加 `package_id()` 方法来移除它们：

```{code-block} python
:caption: conanfile.py

import os
from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.tools.files import copy


class secure_scannerRecipe(ConanFile):
    name = "secure_scanner"
    version = "1.0"
    settings = "os", "compiler", "build_type", "arch"
    ...

    def package_id(self):
        del self.info.settings.compiler
        del self.info.settings.build_type
```

所以，如果用不同的 `build_type` 调用 `conan create`，会得到完全相同的 `package_id`。

```bash
$ conan create .
...
Package '82339cc4d6db7990c1830d274cd12e7c91ab18a1' created

$ conan create . -s build_type=Debug
...
Package '82339cc4d6db7990c1830d274cd12e7c91ab18a1' created
```

得到了相同的二进制文件 `package_id` 。第二个命令 `conan create . -s build_type=Debug` 创建并覆盖了之前的 `Release` 二进制文件（它创建了一个更新的包版本），因为它们具有相同的 `package_id` 标识符。通常只需要创建 `Release` ，如果出于任何原因需要管理 `Debug` 和 `Release` 二进制文件，那么方法就是不移除 `del self.info.settings.build_type` 。
