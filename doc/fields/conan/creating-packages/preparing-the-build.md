# 准备构建

在[上一节的教程](https://docs.conan.io/2/tutorial/creating_packages/add_dependencies_to_packages.html#creating-packages-add-dependencies-to-packages)中，将 [`fmt`](https://conan.io/center/fmt) 需求添加到 Conan 包中，以便为“Hello World” C++ 库提供彩色输出。在本节中，关注配方（recipe）的 `generate()` 方法。此方法的目的是在运行构建步骤时生成所有可能需要的信息。这意味着包括：

- ``写入用于构建步骤的文件，例如注入环境变量的[脚本](https://docs.conan.io/2/reference/tools/env/environment.html#conan-tools-env-environment-model)、传递给构建系统的文件等。
- 配置工具链，根据设置和选项提供额外信息，或从 Conan 默认生成的工具链中移除可能不适用于某些情况的信息。

基于上一教程部分，解释如何使用这个方法的简单示例。在 recipe 中添加 `with_fmt` 选项，根据其值决定是否需要 `fmt` 库。使用 `generate()` 方法修改工具链，使其向 CMake 传递变量，这样就可以根据条件添加该库，并在源代码中使用 `fmt` 或不使用 `fmt`。

请首先克隆源代码以重新创建此项目。你可以在 GitHub 上的 examples2 存储库中找到它们：

```bash
git clone https://github.com/conan-io/examples2.git
cd examples2/tutorial/creating_packages/preparing_the_build
```

你会注意到 recipe 中的 `conanfile.py` 文件有一些变化。检查相关部分：

```{code-block} python
:emphasize-lines: 12,16,20,29,32,37

...
from conan.tools.build import check_max_cppstd, check_min_cppstd
...

class helloRecipe(ConanFile):
    name = "hello"
    version = "1.0"

    ...
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "with_fmt": [True, False]}

    default_options = {"shared": False,
                       "fPIC": True,
                       "with_fmt": True}
    ...

    def validate(self):
        if self.options.with_fmt:
            check_min_cppstd(self, "11")
            check_max_cppstd(self, "14")

    def source(self):
        git = Git(self)
        git.clone(url="https://github.com/conan-io/libhello.git", target=".")
        # Please, be aware that using the head of the branch instead of an immutable tag
        # or commit is not a good practice in general
        git.checkout("optional_fmt")

    def requirements(self):
        if self.options.with_fmt:
            self.requires("fmt/8.1.1")

    def generate(self):
        tc = CMakeToolchain(self)
        if self.options.with_fmt:
            tc.variables["WITH_FMT"] = True
        tc.generate()

    ...
```

如您所见：

- 声明了新的 `with_fmt` 选项，默认值设置为 `True`。
- 根据 `with_fmt` 选项的值：
- 条件性地安装 `fmt/8.1.1` Conan 包。
- 条件性地要求最小和最大的 C++ 标准，因为 `fmt` 库至少需要 C++11，如果尝试使用高于 C++14 的标准，它将无法编译（只是一个例子，实际上 `fmt` 可以用更现代的标准来构建）。
- 条件性地将 `WITH_FMT` 变量注入 `CMakeToolchain`，值为 `True` ，以便可以在 `hello` 库的 `CMakeLists.txt` 中使用它来添加 CMake `fmt::fmt` 目标。
- 正在克隆库的另一个分支。`optional_fmt` 分支包含一些代码更改。

看看 CMake 方面有哪些变化：

```{code-block} cmake
:caption: CMakeLists.txt
:emphasize-lines: 8-12

cmake_minimum_required(VERSION 3.15)
project(hello CXX)

add_library(hello src/hello.cpp)
target_include_directories(hello PUBLIC include)
set_target_properties(hello PROPERTIES PUBLIC_HEADER "include/hello.h")

if (WITH_FMT)
    find_package(fmt)
    target_link_libraries(hello fmt::fmt)
    target_compile_definitions(hello PRIVATE USING_FMT=1)
endif()

install(TARGETS hello)
```

如您所见，使用了在 CMakeToolchain 中注入的 `WITH_FMT` 。根据值的不同，我将尝试查找 `fmt` 库，并将我们的 `hello` 库与之链接。此外，请检查是否添加了 `USING_FMT=1` 编译定义，该定义根据我们是否选择添加对 `fmt` 的支持而在源代码中使用。

```{code-block} cpp
:caption: hello.cpp
:emphasize-lines: 4,9

#include <iostream>
#include "hello.h"

#if USING_FMT == 1
#include <fmt/color.h>
#endif

void hello(){
    #if USING_FMT == 1
        #ifdef NDEBUG
        fmt::print(fg(fmt::color::crimson) | fmt::emphasis::bold, "hello/1.0: Hello World Release! (with color!)\n");
        #else
        fmt::print(fg(fmt::color::crimson) | fmt::emphasis::bold, "hello/1.0: Hello World Debug! (with color!)\n");
        #endif
    #else
        #ifdef NDEBUG
        std::cout << "hello/1.0: Hello World Release! (without color)" << std::endl;
        #else
        std::cout << "hello/1.0: Hello World Debug! (without color)" << std::endl;
        #endif
    #endif
}
```

先使用 `with_fmt=True` 从源代码构建软件包，然后使用 `with_fmt=False` 。当 `test_package` 运行时，它会根据选项的值显示不同的消息。

```bash
$ conan create . --build=missing -o with_fmt=True
-------- Exporting the recipe ----------
...

-------- Testing the package: Running test() ----------
hello/1.0 (test package): Running test()
hello/1.0 (test package): RUN: ./example
hello/1.0: Hello World Release! (with color!)

$ conan create . --build=missing -o with_fmt=False
-------- Exporting the recipe ----------
...

-------- Testing the package: Running test() ----------
hello/1.0 (test package): Running test()
hello/1.0 (test package): RUN: ./example
hello/1.0: Hello World Release! (without color)
```

这只是使用 `generate()` 方法根据选项的值来定制工具链的简单示例，但在 `generate()` 方法中你可以做很多其他的事情，例如：

- 根据您的需求创建完整的自定义工具链，用于构建。
- 访问有关包依赖的某些信息，例如：
    - 通过 [`conf_info`](https://docs.conan.io/2/reference/conanfile/methods/package_info.html#conan-conanfile-model-conf-info) 进行配置。
    - 依赖项的选项。
    - 使用[复制工具](https://docs.conan.io/2/reference/tools/files/basic.html#conan-tools-files-copy)从依赖项导入文件。您也可以导入文件以创建包的清单，收集所有依赖项的版本和许可证。
- 使用[环境工具](https://docs.conan.io/2/reference/tools/env/environment.html#conan-tools-env-environment-model)生成系统环境信息。
- 除了 Release 和 Debug 之外，添加自定义配置，考虑设置，如 ReleaseShared 或 DebugShared。
