# CMakeToolchain: 将任意 CMake 变量注入依赖项

您可以在 GitHub 的 examples2 仓库中找到重新创建此项目的源代码：

```bash
$ git clone https://github.com/conan-io/examples2.git
$ cd examples2/examples/tools/cmake/cmake_toolchain/user_toolchain_profile
```

在一般情况下，Conan 软件包配方通过设置、配置文件和选项提供必要的抽象，以控制构建的不同方面。许多配方定义 `options` 来激活或停用功能、可选依赖项或二进制特性。可以使用 `tools.build:cxxflags` 之类的配置来注入任意 C++ 编译标志。

在某些特殊情况下，可能需要将 CMake 变量直接注入执行 CMake 构建的依赖项。当这些依赖项使用 `CMakeToolchain` 集成时，这是可行的。让我们在这个简单的示例中查看它。

如果有以下包配方，其中包含简单的 `conanfile.py` 和打印变量的 `CMakeLists.txt`：

```{code-block} python
:caption: conanfile.py

from conan import ConanFile
from conan.tools.cmake import CMake

class AppConan(ConanFile):
    name = "foo"
    version = "1.0"
    settings = "os", "compiler", "build_type", "arch"
    exports_sources = "CMakeLists.txt"

    generators = "CMakeToolchain"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
```

```{code-block} cmake
:caption: CMakeLists.txt

cmake_minimum_required(VERSION 3.15)
project(foo LANGUAGES NONE)
message(STATUS "MYVAR1 ${MY_USER_VAR1}!!")
```

可以像下面这样定义配置文件和 `myvars.cmake` 文件（两者位于同一文件夹中）：

```{code-block} ini
:caption: myprofile

include(default)
[conf]
tools.cmake.cmaketoolchain:user_toolchain+={{profile_dir}}/myvars.cmake
```

请注意， `{{profile_dir}}` 是 `jinja` 模板表达式，它计算当前配置文件夹，从而允许计算到 `myvars.cmake` 文件的必要路径。 `tools.cmake.cmaketoolchain:user_toolchain` 是要注入到生成的 `conan_toolchain.cmake` 中的文件列表，因此使用 `+=` 运算符将其追加到其中。

`myvars.cmake` 可以定义想要的任意数量的变量：

```{code-block} cmake
:caption: myvars.cmake

set(MY_USER_VAR1 "MYVALUE1")
```

应用此配置文件，可以看到 CMake 构建包有效地使用了外部 `myvars.cmake` 文件中提供的变量：

```bash
$ conan create . -pr=myprofile
...
-- MY_USER_VAR1 MYVALUE1
```

请注意，在为 `tools.cmake.cmaketoolchain:system_name` 等配置定义值时使用 `user_toolchain` 是受支持的。

此外，`user_toolchain` 文件可以定义用于交叉编译的变量，例如 `CMAKE_SYSTEM_NAME`、 `CMAKE_SYSTEM_VERSION` 和 `CMAKE_SYSTEM_PROCESSOR`。如果这些变量在用户工具链文件中定义，则会尊重这些定义，而 Conan 自动推导的 `conan_toolchain.cmake` 不会覆盖用户定义的变量。如果这些变量未在用户工具链文件中定义，则 Conan 将使用自动推导的变量。

`tools.cmake.cmaketoolchain:user_toolchain` 的值也可以通过命令行的 `-c` 参数传递，但 `myvars.cmake` 的位置需要是绝对路径才能被找到，因为 Jinja 替换不会在命令行中发生。
