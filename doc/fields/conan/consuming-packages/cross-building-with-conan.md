# 如何使用 Conan 进行应用程序交叉编译：主机和构建上下文

请先克隆源代码以重现此项目。您可以在 GitHub 上的 examples2 仓库 中找到它们。

```bash
git clone https://github.com/conan-io/examples2.git
cd examples2/tutorial/consuming_packages/cross_building
```

在之前的示例中，学习了如何使用 `conanfile.py` 或 `conanfile.txt` 来构建使用 Zlib 和 CMake Conan 包压缩字符串的应用程序。此外，解释了您可以在称为 Conan 配置文件的文件中设置操作系统、编译器或构建配置等信息。您可以使用该配置文件作为参数 (`--profile`) 来调用 `conan install` 命令。还解释了不指定该配置文件等同于使用 `--profile=default` 参数。

在所有这些示例中，使用相同的平台来构建和运行应用程序。但是，如果您想在运行 Ubuntu Linux 的机器上构建应用程序，然后将其运行在像树莓派这样的另一个平台上怎么办？Conan 可以使用两个不同的配置文件来模拟这种情况，一个用于 构建 应用程序的机器（Ubuntu Linux），另一个用于 运行 应用程序的机器（树莓派）。将在下一节解释这种“双配置文件”方法。

## Conan 双配置文件模型：构建配置文件和主机配置文件

即使您在调用 Conan 时只指定一个 --profile 参数，Conan 在内部也会使用两个配置文件。一个用于 构建 二进制文件的机器（称为 构建 配置文件），另一个用于 运行 这些二进制文件的机器（称为 主机 配置文件）。调用此命令

```bash
conan install . --build=missing --profile=someprofile
```

等同于

```bash
conan install . --build=missing --profile:host=someprofile --profile:build=default
```

如您所见，使用了两个新参数
- `profile:host`: 这是定义构建的二进制文件将在哪个平台运行的配置文件。对于我们的字符串压缩器应用程序，此配置文件将应用于将在 树莓派 上运行的 Zlib 库。
- `profile:build`: 这是定义二进制文件将在哪个平台构建的配置文件。对于我们的字符串压缩器应用程序，此配置文件将由用于在 Ubuntu Linux 机器上编译它的 CMake 工具使用。

请注意，当您只使用一个配置文件参数 `--profile` 时，它等同于 `--profile:host`。如果您未指定 `--profile:build` 参数，Conan 将在内部使用 `default` 配置文件。

因此，如果想在 Ubuntu Linux 机器上构建压缩器应用程序，但在树莓派上运行它，则应使用两个不同的配置文件。对于 构建 机器，可以使用默认配置文件，在我们的例子中看起来像这样

```{code-block} ini
:caption: <conan home>/profiles/default

[settings]
os=Linux
arch=x86_64
build_type=Release
compiler=gcc
compiler.cppstd=gnu14
compiler.libcxx=libstdc++11
compiler.version=9
```

以及树莓派（即 主机）的配置文件

```{code-block} ini
:caption: <conan home>/profiles/raspberrypi
:emphasize-lines: 8-12

[settings]
os=Linux
arch=armv7hf
compiler=gcc
build_type=Release
compiler.cppstd=gnu14
compiler.libcxx=libstdc++11
compiler.version=9
[buildenv]
CC=arm-linux-gnueabihf-gcc-9
CXX=arm-linux-gnueabihf-g++-9
LD=arm-linux-gnueabihf-ld
```

```{important}
请注意，为了成功构建此示例，您应该安装一个工具链，其中包含为适当架构构建应用程序所需的编译器和所有工具。在本例中，主机是安装了 `armv7hf` 架构操作系统的树莓派 3，并且我们在 Ubuntu 机器上安装了 `arm-linux-gnueabihf` 工具链。
```

如果您查看 raspberry 配置文件，会有一个名为 `[buildenv]` 的部分。此部分用于设置构建应用程序所需的环境变量。在本例中，我们声明了 `CC`、`CXX` 和 `LD` 变量，它们分别指向交叉构建工具链的编译器和链接器。将此部分添加到配置文件中，每次执行 `conan install` 时都会调用 VirtualBuildEnv 生成器。此生成器会将该环境信息添加到 `conanbuild.sh` 脚本中，我们将在使用 CMake 构建之前 `source` 该脚本，以便它可以使用交叉构建工具链。

```{tip}
在某些情况下，您的构建平台上没有可用的工具链。对于这些情况，您可以使用交叉编译器的 Conan 包，并将其添加到配置文件的 `[tool_requires]` 部分。有关使用工具链包进行交叉构建的示例，请查看 [此示例](https://docs.conan.org.cn/2/examples/cross_build/toolchain_packages.html#example-cross-build-toolchain-package-use)。
```

## 构建和主机上下文

现在我们已经准备好了两个配置文件，来看一下 `conanfile.py`

```{code-block} python
:caption: conanfile.py
:linenos:

from conan import ConanFile
from conan.tools.cmake import cmake_layout

class CompressorRecipe(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeToolchain", "CMakeDeps"

    def requirements(self):
        self.requires("zlib/1.2.11")

    def build_requirements(self):
        self.tool_requires("cmake/3.22.6")

    def layout(self):
        cmake_layout(self)
```

如您所见，这几乎与我们在[之前的示例](https://docs.conan.org.cn/2/tutorial/consuming_packages/the_flexibility_of_conanfile_py.html#consuming-packages-flexibility-of-conanfile-py)中使用的 `conanfile.py` 相同。我们将需要 `zlib/1.2.11` 作为常规依赖项，并需要 `cmake/3.22.6` 作为构建应用程序所需的工具。

我们需要应用程序使用交叉构建工具链为树莓派构建，并链接为同一平台构建的 `zlib/1.2.11` 库。另一方面，我们需要 `cmake/3.22.6` 二进制文件在 Ubuntu Linux 上运行。Conan 在依赖图中内部管理这一点，区分我们称之为“构建上下文”和“主机上下文”的内容。

- **主机上下文** 由根包（在 `conan install` 或 `conan create` 命令中指定的那个）及其通过 self.requires() 添加的所有依赖项填充。在本例中，这包括压缩器应用程序和 `zlib/1.2.11` 依赖项。
- **构建上下文** 包含在构建机器上使用的工具依赖项。此类别通常包括所有开发工具，如 CMake、编译器和链接器。在本例中，这包括 `cmake/3.22.6` 工具。

这些上下文定义了 Conan 如何管理每个依赖项。例如，由于 `zlib/1.2.11` 属于 主机上下文，我们在 raspberry 配置文件（主机配置文件）中定义的 `[buildenv]` 构建环境仅在构建时应用于 `zlib/1.2.11` 库，并且不会影响属于 构建上下文 的任何内容，例如 `cmake/3.22.6` 依赖项。

现在，让我们构建应用程序。首先，使用构建和主机平台的配置文件调用 `conan install`。这将安装为 `armv7hf` 架构构建的 `zlib/1.2.11` 依赖项，以及可在 64 位架构上运行的 `cmake/3.22.6` 版本。

```bash
conan install . --build missing -pr:b=default -pr:h=./profiles/raspberry
```

然后，调用 CMake 构建应用程序。正如我们在之前的示例中所做的那样，我们必须通过运行 `source Release/generators/conanbuild.sh` 来激活 构建环境。这将设置定位交叉构建工具链和构建应用程序所需的环境变量。

```bash
$ cd build
$ source Release/generators/conanbuild.sh
Capturing current environment in deactivate_conanbuildenv-release-armv7hf.sh
Configuring environment variables
$ cmake .. -DCMAKE_TOOLCHAIN_FILE=Release/generators/conan_toolchain.cmake -DCMAKE_BUILD_TYPE=Release
$ cmake --build .
...
-- Conan toolchain: C++ Standard 14 with extensions ON
-- The C compiler identification is GNU 9.4.0
-- Detecting C compiler ABI info
-- Detecting C compiler ABI info - done
-- Check for working C compiler: /usr/bin/arm-linux-gnueabihf-gcc-9 - skipped
-- Detecting C compile features
-- Detecting C compile features - done    [100%] Built target compressor
...
$ source Release/generators/deactivate_conanbuild.sh
```

您可以通过运行 Linux 工具 `file` 来检查我们是否为正确的架构构建了应用程序

```{code-block} bash
:emphasize-lines: 2

$ file compressor
compressor: ELF 32-bit LSB shared object, ARM, EABI5 version 1 (SYSV), dynamically
linked, interpreter /lib/ld-linux-armhf.so.3,
BuildID[sha1]=2a216076864a1b1f30211debf297ac37a9195196, for GNU/Linux 3.2.0, not
stripped
```