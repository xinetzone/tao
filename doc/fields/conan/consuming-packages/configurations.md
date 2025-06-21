# 构建多种配置：Release、Debug、静态和共享

克隆源代码以重新创建此项目：

```bash
git clone https://github.com/conan-io/examples2.git
cd examples2/tutorial/consuming_packages/different_configurations
```

到目前为止，构建了依赖于 zlib 库的简单 CMake 项目，并了解了 `tool_requires`，这是一种用于像 CMake 这样的构建工具的特殊类型的 `requirements`。在这两种情况下，都没有指定想要以 Release 或 Debug 模式构建应用程序，也没有指定想要链接到静态或共享库。这是因为 Conan，如果没有特别指示，将使用在“默认配置文件”中声明的默认配置。这个默认配置文件是在运行 `conan profile detect` 命令的第一个示例中创建的。Conan 将此文件存储在 Conan 用户主目录中的 `/profiles` 文件夹中。您可以通过运行 `conan config home` 命令获取 Conan 用户主目录的位置，然后查看 `/profiles` 文件夹中的默认配置文件内容来检查默认配置文件的内容。

```bash
$ conan config home
Current Conan home: /Users/tutorial_user/.conan2

# output the file contents
$ cat /Users/tutorial_user/.conan2/profiles/default
[settings]
os=Macos
arch=x86_64
compiler=apple-clang
compiler.version=14.0
compiler.libcxx=libc++
compiler.cppstd=gnu11
build_type=Release
[options]
[tool_requires]
[env]

# The default profile can also be checked with the command "conan profile show"
```

如您所见，配置文件有不同的部分。`[settings]` 部分包含关于操作系统、架构、编译器和构建配置等信息。

当您调用设置了 `--profile` 参数的 Conan 命令时，Conan 将从配置文件中获取所有信息并将其应用于您想要构建或安装的软件包。如果您不指定该参数，则等同于使用 `--profile=default` 调用它。这两个命令的行为相同。

```bash
$ conan install . --build=missing
$ conan install . --build=missing --profile=default
```

您可以存储不同的配置文件，并使用它们为不同的设置进行构建。例如，使用 `build_type=Debug`，或者为您使用该配置文件构建的所有软件包添加 `tool_requires`。创建 `debug` 配置文件来尝试使用不同的配置进行构建。

```{code-block} ini
:caption: <conan home>/profiles/debug
:emphasize-lines: 8

[settings]
os=Macos
arch=x86_64
compiler=apple-clang
compiler.version=14.0
compiler.libcxx=libc++
compiler.cppstd=gnu11
build_type=Debug
```

## 修改设置：对应用程序及其依赖项使用 Debug 配置

使用配置文件并不是设置所需配置的唯一方法。您还可以在 Conan 命令中使用 `--settings` 参数覆盖配置文件设置。例如，您可以以 Debug 配置而不是 Release 配置构建之前示例中的项目。

在构建之前，请检查是否修改了之前示例中的源代码，以显示构建源代码时使用的构建配置。

```{code-block} c
:linenos:
:emphasize-lines: 6-10

#include <stdlib.h>
...

int main(void) {
    ...
    #ifdef NDEBUG
    printf("Release configuration!\n");
    #else
    printf("Debug configuration!\n");
    #endif

    return EXIT_SUCCESS;
}
```

以 Debug 配置构建项目

```bash
conan install . --output-folder=build --build=missing --settings=build_type=Debug
```

正如我上面解释的，这相当于拥有 `debug` 配置文件，并使用 `--profile=debug` 参数而不是 `--settings=build_type=Debug` 参数来运行这些命令。

这个 `conan install` 命令将检查是否在本地缓存中已拥有 Debug 配置所需的库（Zlib），如果没有则获取。它还将更新 `CMakeToolchain` 生成器创建的 `conan_toolchain.cmake` 和 `CMakePresets.json` 文件中的构建配置，以便我们在构建应用程序时它以 Debug 配置构建。现在，像之前的示例一样构建您的项目，并在输出中检查它是如何以 Debug 配置构建的。

:::::{tab-set}
::::{tab-item} Windows
```{code-block} bash
:emphasize-lines: 9

# assuming Visual Studio 15 2017 is your VS version and that it matches your default profile
$ cd build
$ cmake .. -G "Visual Studio 15 2017" -DCMAKE_TOOLCHAIN_FILE=conan_toolchain.cmake
$ cmake --build . --config Debug
$ Debug\compressor.exe
Uncompressed size is: 233
Compressed size is: 147
ZLIB VERSION: 1.2.11
Debug configuration!
```
::::
::::{tab-item} Linux, macOS
```{code-block} bash
:emphasize-lines: 8

$ cd build
$ cmake .. -DCMAKE_TOOLCHAIN_FILE=conan_toolchain.cmake -DCMAKE_BUILD_TYPE=Debug
$ cmake --build .
$ ./compressor
Uncompressed size is: 233
Compressed size is: 147
ZLIB VERSION: 1.2.11
Debug configuration!
```
::::
:::::

## 修改选项：将应用程序依赖项链接为共享库

到目前为止，一直在应用程序中静态链接 Zlib。这是因为在 Zlib 的 Conan 软件包中有一个属性默认为在该模式下构建。可以通过使用 `--options` 参数将 `shared` 选项设置为 `True` 来从静态链接改为共享链接。为此，请运行：

```bash
conan install . --output-folder=build --build=missing --options=zlib/1.2.11:shared=True
```

这样做，Conan 将安装 Zlib 共享库，生成用于与其一起构建的文件，以及在运行应用程序时定位这些动态库所需的文件。

```{attention}
选项是按软件包定义的。在这种情况下，定义的是我们想要特定版本的 `zlib/1.2.11` 作为共享库。如果我们有其他依赖项，并且我们希望所有依赖项（只要可能）都作为共享库，我们将使用 `-o *:shared=True`，其中 `*` 模式匹配所有软件包引用。
```

配置应用程序以链接 Zlib 作为共享库后，再次构建应用程序。

:::::{tab-set}
::::{tab-item} Windows
```bash
$ cd build
# assuming Visual Studio 15 2017 is your VS version and that it matches your default profile
$ cmake .. -G "Visual Studio 15 2017" -DCMAKE_TOOLCHAIN_FILE=conan_toolchain.cmake
$ cmake --build . --config Release
...
[100%] Built target compressor
```
::::
::::{tab-item} Linux, macOS
```bash
$ cd build
$ cmake .. -DCMAKE_TOOLCHAIN_FILE=conan_toolchain.cmake -DCMAKE_BUILD_TYPE=Release
$ cmake --build .
...
[100%] Built target compressor
```
::::
:::::


现在，如果您尝试运行编译后的可执行文件，您将看到错误，因为可执行文件找不到我们刚刚安装的 Zlib 共享库。

:::::{tab-set}
::::{tab-item} Windows
```bash
$ Release\compressor.exe
(on a pop-up window) The code execution cannot proceed because zlib1.dll was not found. Reinstalling the program may fix this problem.
# This error depends on the console being used and may not always pop up.
# It could run correctly if the console gets the zlib dll from a different path.
```
::::
::::{tab-item} Linux
```bash
$ ./compressor
./compressor: error while loading shared libraries: libz.so.1: cannot open shared object file: No such file or directory
```
::::
::::{tab-item} Macos
```bash
$ ./compressor
./compressor: dyld[41259]: Library not loaded: @rpath/libz.1.dylib
```
::::
:::::

这是因为共享库（Windows 中是 `.dll`，macOS 中是 `.dylib`，Linux 中是 `.so`）是在运行时加载的。这意味着应用程序可执行文件在运行时需要知道所需共享库的位置。在 Windows 上，动态链接器将搜索同一目录，然后在 `PATH` 目录中搜索。在 macOS 上，它将在 `DYLD_LIBRARY_PATH` 中声明的目录中搜索，在 Linux 上将使用 `LD_LIBRARY_PATH`。

Conan 提供了一种机制来定义这些变量，并使可执行文件能够找到和加载这些共享库。这种机制就是 VirtualRunEnv 生成器。如果您检查输出文件夹，您将看到 Conan 生成了名为 `conanrun.sh/bat` 的新文件。这是我们在执行` conan install` 时激活 `shared` 选项后，自动调用 VirtualRunEnv 生成器的结果。这个生成的脚本将设置 `PATH`、`LD_LIBRARY_PATH`、`DYLD_LIBRARY_PATH` 和 `DYLD_FRAMEWORK_PATH` 环境变量，以便可执行文件可以找到共享库。

:::::{tab-set}
::::{tab-item} Windows
```bash
$ conanrun.bat
$ Release\compressor.exe
Uncompressed size is: 233
Compressed size is: 147
...
```
::::
::::{tab-item} Linux, macOS
```bash
$ source conanrun.sh
$ ./compressor
Uncompressed size is: 233
Compressed size is: 147
...
```
::::
:::::

就像之前使用 VirtualBuildEnv 生成器的示例一样，当我们运行 `conanrun.sh/bat` 脚本时，会创建一个名为 `deactivate_conanrun.sh/bat` 的停用脚本，以恢复环境。源化或运行它即可。

:::::{tab-set}
::::{tab-item} Windows
```bash
$ deactivate_conanrun.bat
```
::::
::::{tab-item} Linux, macOS
```bash
source deactivate_conanrun.sh
```
::::
:::::

## `settings` 和 `options` 的区别

您可能已经注意到，要更改 Debug 和 Release 配置，使用了 Conan 的 `setting`，但当为可执行文件设置 `shared` 模式时，使用了 Conan 的 `options`。请注意 `settings` 和 `options` 之间的区别。

- `settings` 通常是客户端机器定义的项目范围配置。例如操作系统、架构、编译器或构建配置等，它们对多个 Conan 软件包通用，并且仅为其中一个软件包定义一个默认值没有意义。例如，Conan 软件包声明“Visual Studio”作为默认编译器没有意义，因为这是由最终用户定义的，如果在 Linux 环境中工作，这样做可能毫无意义。
- `options` 用于软件包特定的配置，可以在配方中设置默认值。例如，一个软件包可以定义其默认链接方式是静态，并且如果消费者没有另外指定，则应使用此链接方式。

## 引入 Package ID 的概念

当使用不同的 `settings` 和 `options` 使用像 Zlib 这样的软件包时，您可能想知道 Conan 如何确定从远程仓库中检索哪个二进制文件。答案在于 `package_id` 的概念。

`package_id` 是 Conan 用于确定包的二进制兼容性的标识符。它是根据多个因素计算得出的，包括包的设置、选项和依赖项。当你修改这些因素中的任何一个时，Conan 会计算新的 `package_id` 来引用相应的二进制文件。

以下是流程分解：

- 确定 Settings 和 Options：Conan 首先检索用户的输入设置和选项。这些可以来自命令行或配置文件，例如 `–settings=build_type=Debug` 或 `–profile=debug`。
- 计算 Package ID：根据 `settings`、`options` 和依赖项的当前值，Conan 计算哈希值。这个哈希值就是 `package_id`，代表二进制软件包的唯一身份。
- 获取二进制文件：Conan 然后在其缓存或指定的远程仓库中检查是否存在具有计算出的 `package_id` 的二进制软件包。如果找到匹配项，它将检索该二进制文件。如果找不到，Conan 可以从源代码构建软件包或指示二进制文件缺失。

在本教程中，当您使用不同的 `settings` 和 `options` 使用 Zlib 时，Conan 使用 `package_id` 来确保它获取与我们指定配置匹配的正确二进制文件。
