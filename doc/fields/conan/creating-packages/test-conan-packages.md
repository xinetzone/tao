# 测试 Conan 包

在教程的所有前面的章节中，使用了 `test_package`。它在构建我们的包并在 `conan create` 命令结束时自动调用，以验证包是否创建正确。在本节中，我们将更详细地解释 `test_package`。

首先克隆源代码以重新创建此项目。你可以在 GitHub 上的 examples2 存储库中找到它们：

```bash
git clone https://github.com/conan-io/examples2.git
cd examples2/tutorial/creating_packages/testing_packages
```

关于 `test_package` 需要记住的一些重要注意事项：

- `test_package` 文件夹与单元测试或集成测试不同。这些测试是“包”测试，用于验证包是否正确创建，以及包的消费者是否能够链接到它并重用它。
- 它本身是小的 Conan 项目，包含自己的 `conanfile.py` 和源代码，包括构建脚本。它依赖于正在创建的包，并构建和执行小型应用程序，该应用程序需要包中的库。
- 它不属于包的一部分。它仅存在于源代码仓库中，而不是在包中。
- `test_package` 文件夹是默认的，但可以通过命令行参数 `--test-folder` 或使用 `test_package_folder` 配方属性定义不同的文件夹。

`hello/1.0` Conan 包的 `test_package` 文件夹包含以下内容：

```bash
test_package
 ├── CMakeLists.txt
 ├── conanfile.py
 └── src
     └── example.cpp
```

看看 `test_package` 中包含的不同文件。首先，`example.cpp` 只是使用我们正在打包的 `libhello` 库的最小示例：

```{code-block} cpp
:caption: test_package/src/example.cpp

#include "hello.h"

int main() {
    hello();
}
```

然后是 `CMakeLists.txt` 文件，用于告诉 CMake 如何构建示例：

```{code-block} cmake
:caption: test_package/CMakeLists.txt

cmake_minimum_required(VERSION 3.15)
project(PackageTest CXX)

find_package(hello CONFIG REQUIRED)

add_executable(example src/example.cpp)
target_link_libraries(example hello::hello)
```

最后，消耗 `hello/1.0` Conan 包的 `test_package` 的 recipe：

```{code-block} python
:caption: test_package/conanfile.py

import os

from conan import ConanFile
from conan.tools.cmake import CMake, cmake_layout
from conan.tools.build import can_run


class helloTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps", "CMakeToolchain"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def layout(self):
        cmake_layout(self)

    def test(self):
        if can_run(self):
            cmd = os.path.join(self.cpp.build.bindir, "example")
            self.run(cmd, env="conanrun")
```

让我们来看看最相关的部分：

- 在 `requirements()` 方法中添加了需求，但在这个案例中我们使用了 Conan 传递给 `test_package` 的 `tested_reference_str` 属性。这是一个方便的属性，用于避免在 `test_package` 中硬编码包名，这样我们就可以用同一个 `test_package` 来测试同一 Conan 包的多个版本。在我们的案例中，这个变量将取 `hello/1.0` 值。
- 定义了 `test()` 方法。这个方法仅在 `test_package` 配置文件中被调用。它会在 `build()` 被调用后立即执行，目的是在二进制文件上运行可执行程序或测试，以证明包已正确创建。关于 `test()` 方法的几点说明：
    - 使用 [`conan.tools.build.cross_building`](https://docs.conan.io/2/reference/tools/build.html#conan-tools-build-can-run) 工具来检查是否可以在当前平台上运行构建的可执行文件。如果设置了 `tools.build.cross_building:can_run` 配置，该工具将返回其值。否则，它将返回我们是否在交叉编译。这是一个非常有用的功能，特别是当您的架构可以运行多个目标时。例如，Mac M1 机器可以同时运行 armv8 和 x86_64。
    - 使用 Conan 放入运行环境中的环境信息来运行 `self.cpp.build.bindir` 文件夹中生成的示例二进制文件。Conan 随后会调用一个包含运行时环境信息的启动器，任何必要的环境信息，以便运行编译的可执行文件和应用程序。

现在已经了解了代码的所有重要部分，让我们尝试我们的 `test_package`。尽管我们已经知道在调用 `conan create` 时会触发 `test_package`，但如果你已经在 Conan 缓存中创建了 `hello/1.0` 包，也可以直接创建 `test_package`。这可以通过 [`conan test`](https://docs.conan.io/2/reference/commands.html#reference-commands) 命令完成：

```{code-block} bash
:linenos:
:emphasize-lines: 18,21

$ conan test test_package hello/1.0

...

-------- test_package: Computing necessary packages --------
Requirements
    fmt/8.1.1#cd132b054cf999f31bd2fd2424053ddc:ff7a496f48fca9a88dc478962881e015f4a5b98f#1d9bb4c015de50bcb4a338c07229b3bc - Cache
    hello/1.0#25e0b5c00ae41ef9fbfbbb1e5ac86e1e:fd7c4113dad406f7d8211b3470c16627b54ff3af#4ff3fd65a1d37b52436bf62ea6eaac04 - Cache
Test requirements
    gtest/1.11.0#d136b3379fdb29bdfe31404b916b29e1:656efb9d626073d4ffa0dda2cc8178bc408b1bee#ee8cbd2bf32d1c89e553bdd9d5606127 - Skip

...

[ 50%] Building CXX object CMakeFiles/example.dir/src/example.cpp.o
[100%] Linking CXX executable example
[100%] Built target example

-------- Testing the package: Running test() --------
hello/1.0 (test package): Running test()
hello/1.0 (test package): RUN: ./example
hello/1.0: Hello World Release! (with color!)
```

如输出所示，`test_package` 构建成功，测试了 `hello/1.0` Conan 包可以无问题地被使用。
