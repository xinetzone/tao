# 构建软件包：`build()` 方法

已经使用了包含 [`build()`](https://docs.conan.io/2/reference/conanfile/methods/build.html#reference-conanfile-methods-build) 方法的 Conan 配方，并学习了如何使用它来调用构建系统并构建我们的软件包。在这个教程中，我们将修改这个方法，并解释你可以如何使用它来执行以下操作：

- 构建和运行测试
- 按条件对源代码进行补丁处理
- 根据条件选择要使用的构建系统

请首先克隆源代码以重新创建此项目。你可以在 GitHub 上的 examples2 存储库中找到它们：

```bash
git clone https://github.com/conan-io/examples2.git
cd examples2/tutorial/creating_packages/build_method
```

## 为您的项目构建和运行测试

你会注意到 conanfile.py 文件有一些变化。检查相关部分：

### 配方引入的变更

```{code-block} python
:caption: conanfile.py
:linenos:
:emphasize-lines: 12,19,33-34

class helloRecipe(ConanFile):
    name = "hello"
    version = "1.0"

    ...

    def source(self):
        git = Git(self)
        git.clone(url="https://github.com/conan-io/libhello.git", target=".")
        # Please, be aware that using the head of the branch instead of an immutable tag
        # or commit is not a good practice in general
        git.checkout("with_tests")

    ...

    def requirements(self):
        if self.options.with_fmt:
            self.requires("fmt/8.1.1")
        self.test_requires("gtest/1.11.0")

    ...

    def generate(self):
        tc = CMakeToolchain(self)
        if self.options.with_fmt:
            tc.variables["WITH_FMT"] = True
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
        if not self.conf.get("tools.build:skip_test", default=False):
            test_folder = os.path.join("tests")
            if self.settings.os == "Windows":
                test_folder = os.path.join("tests", str(self.settings.build_type))
            self.run(os.path.join(test_folder, "test_hello"))

    ...
```

- 将 `gtest/1.11.0` 要求添加到配方中作为 `test_requires()` 。这是一种用于测试库（如 Catch2 或 gtest）的要求类型。
- 使用 `tools.build:skip_test` 配置（默认为 `False` ），来告诉 CMake 是否要构建和运行测试。有几点需要注意：
- 如果将 `tools.build:skip_test` 配置设置为 `True` ，Conan 将自动将 `BUILD_TESTING` 变量注入 CMake 并设置为 `OFF` 。在下一节中，我们会看到我们使用这个变量在 `CMakeLists.txt` 中决定是否构建测试。
- 在 `build()` 方法中使用 `tools.build:skip_test` 配置，在构建包和测试之后，来决定是否要运行测试。
- 在这种情况下，使用 `gtest` 进行测试，并且必须检查构建方法是否要运行测试。此配置也会影响如果你使用 `CTest` 和 `Meson.test()` for Meson 时 `CMake.test()` 的执行。

### 库源代码中引入的变更

首先请注意，使用了 `libhello` 库的[另一个分支](https://github.com/conan-io/libhello/tree/with_tests)。这个分支在库方面有两个新特性：

- 在[库源代码](https://github.com/conan-io/libhello/blob/with_tests/src/hello.cpp#L9-L12)中添加了名为 `compose_message()` 的新函数，以便可以为此函数添加一些单元测试。这个函数只是根据传入的参数创建一条输出消息。
- 正如我们在上一节中提到的，[库的 `CMakeLists.txt` 文件](https://github.com/conan-io/libhello/blob/with_tests/CMakeLists.txt#L15-L17)使用了 `BUILD_TESTING` CMake 变量，该变量有条件地添加了测试目录。

`CMakeLists.txt`：
```
cmake_minimum_required(VERSION 3.15)
project(hello CXX)

...

if (NOT BUILD_TESTING STREQUAL OFF)
    add_subdirectory(tests)
endif()

...
```

`BUILD_TESTING` [CMake 变量](https://cmake.org/cmake/help/latest/module/CTest.html)由 Conan 声明并设置为 `OFF` （如果尚未定义），每当 `tools.build:skip_test` 配置设置为值 `True` 时。此变量通常在您使用 CTest 时由 CMake 声明，但使用 `tools.build:skip_test` 配置时，即使您使用其他测试框架，也可以在您的 `CMakeLists.txt` 中使用它。

在[测试文件夹](https://github.com/conan-io/libhello/blob/with_tests/tests/CMakeLists.txt)中有使用 [googletest](https://github.com/google/googletest) 进行测试的 `CMakeLists.txt`：

```{code-block} cmake
:caption: tests/CMakeLists.txt

cmake_minimum_required(VERSION 3.15)
project(PackageTest CXX)

find_package(GTest REQUIRED CONFIG)

add_executable(test_hello test.cpp)
target_link_libraries(test_hello GTest::gtest GTest::gtest_main hello)
```

对 `compose_message()` 函数的功能进行基本测试：

```{code-block} cpp
:caption: tests/test.cpp

#include "../include/hello.h"
#include "gtest/gtest.h"

namespace {
    TEST(HelloTest, ComposeMessages) {
      EXPECT_EQ(std::string("hello/1.0: Hello World Release! (with color!)\n"), compose_message("Release", "with color!"));
      ...
    }
}
```

现在已经回顾了代码中的所有变化，试试这些改动：

```{code-block} bash
:linenos:
:emphasize-lines: 6-23

$ conan create . --build=missing -tf=""
...
[ 25%] Building CXX object CMakeFiles/hello.dir/src/hello.cpp.o
[ 50%] Linking CXX static library libhello.a
[ 50%] Built target hello
[ 75%] Building CXX object tests/CMakeFiles/test_hello.dir/test.cpp.o
[100%] Linking CXX executable test_hello
[100%] Built target test_hello
hello/1.0: RUN: ./tests/test_hello
Capturing current environment in /Users/user/.conan2/p/tmp/c51d80ef47661865/b/build/generators/deactivate_conanbuildenv-release-x86_64.sh
Configuring environment variables
Running main() from /Users/user/.conan2/p/tmp/3ad4c6873a47059c/b/googletest/src/gtest_main.cc
[==========] Running 1 test from 1 test suite.
[----------] Global test environment set-up.
[----------] 1 test from HelloTest
[ RUN      ] HelloTest.ComposeMessages
[       OK ] HelloTest.ComposeMessages (0 ms)
[----------] 1 test from HelloTest (0 ms total)

[----------] Global test environment tear-down
[==========] 1 test from 1 test suite ran. (0 ms total)
[  PASSED  ] 1 test.
hello/1.0: Package '82b6c0c858e739929f74f59c25c187b927d514f3' built
...
```

如您所见，测试已被构建并运行。现在使用命令行中的 `tools.build:skip_test` 配置来跳过测试的构建和运行：

```bash
$ conan create . -c tools.build:skip_test=True -tf=""
...
[ 50%] Building CXX object CMakeFiles/hello.dir/src/hello.cpp.o
[100%] Linking CXX static library libhello.a
[100%] Built target hello
hello/1.0: Package '82b6c0c858e739929f74f59c25c187b927d514f3' built
...
```

现在你可以看到，只构建了库目标，没有构建或运行任何测试

## 条件性地修补源代码 

如果您需要修补源代码，推荐的方法是在 `source()` 方法中执行。有时，如果该补丁依赖于设置或选项，您必须在启动构建之前使用 `build()` 方法将补丁应用于源代码。Conan 提供了[几种实现这一功能的方法](https://docs.conan.io/2/examples/tools/files/patches/patch_sources.html#examples-tools-files-patches)。其中一种方法是使用 [`replace_in_file`](https://docs.conan.io/2/reference/tools/files/basic.html#conan-tools-files-replace-in-file) 工具：

```python
import os
from conan import ConanFile
from conan.tools.files import replace_in_file


class helloRecipe(ConanFile):
    name = "hello"
    version = "1.0"

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    def build(self):
        replace_in_file(self, os.path.join(self.source_folder, "src", "hello.cpp"),
                        "Hello World",
                        "Hello {} Friends".format("Shared" if self.options.shared else "Static"))
```

请注意，在 `build()` 中应尽量避免打补丁，仅在非常特殊的情况下才进行，因为这会使您在本地开发包时更加困难（我们将在后面的[本地开发流程](https://docs.conan.io/2/tutorial/developing_packages/local_package_development_flow.html#local-package-development-flow)部分对此进行更详细的解释）。

## 有条件地选择构建系统 

在构建过程中，有些包需要根据不同的平台选择不同的构建系统，这种情况并不少见。例如，`hello` 库可以在 Windows 上使用 CMake 构建，在 Linux 和 macOS 上使用 Autotools 构建。这可以很容易地在 `build()` 方法中这样处理：

```python
...

class helloRecipe(ConanFile):
    name = "hello"
    version = "1.0"

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    ...

    def generate(self):
        if self.settings.os == "Windows":
            tc = CMakeToolchain(self)
            tc.generate()
            deps = CMakeDeps(self)
            deps.generate()
        else:
            tc = AutotoolsToolchain(self)
            tc.generate()
            deps = PkgConfigDeps(self)
            deps.generate()

    ...

    def build(self):
        if self.settings.os == "Windows":
            cmake = CMake(self)
            cmake.configure()
            cmake.build()
        else:
            autotools = Autotools(self)
            autotools.autoreconf()
            autotools.configure()
            autotools.make()

    ...
```
