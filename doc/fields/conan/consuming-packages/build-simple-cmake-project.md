# 基于 Conan 的 CMake 项目构建

```{topic} 项目目标
:class: border-bottom

- 实现基于 Zlib 1.3.1 的字符串压缩功能
- 演示 Conan 与 CMake 的集成流程
- 展示多平台构建配置方法
```

使用 CMake 作为构建系统，但请记住 **Conan 兼容任何构建系统**，不仅限于 CMake。

克隆源代码以重新创建此项目：

```bash
git clone https://github.com/conan-io/examples2.git
cd examples2/tutorial/consuming_packages/simple_cmake_project
```

从非常简单的 C 语言项目开始，其结构如下
```
.
├── CMakeLists.txt
└── src
    └── main.c
```

该项目包含基本的 `CMakeLists.txt`，其中包含了 `zlib` 依赖项以及位于 `main.c` 中的字符串压缩程序源代码。
:::::{tab-set}
::::{tab-item} CMakeLists.txt
```cmake
cmake_minimum_required(VERSION 3.15)
project(compressor C)

find_package(ZLIB REQUIRED)

add_executable(${PROJECT_NAME} src/main.c)
target_link_libraries(${PROJECT_NAME} ZLIB::ZLIB)
```
::::
::::{tab-item} main.c
```cpp
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include <zlib.h>

int main(void) {
    char buffer_in [256] = {"Conan is a MIT-licensed, Open Source package manager for C and C++ development, "
                            "allowing development teams to easily and efficiently manage their packages and "
                            "dependencies across platforms and build systems."};
    char buffer_out [256] = {0};

    z_stream defstream;
    defstream.zalloc = Z_NULL;
    defstream.zfree = Z_NULL;
    defstream.opaque = Z_NULL;
    defstream.avail_in = (uInt) strlen(buffer_in);
    defstream.next_in = (Bytef *) buffer_in;
    defstream.avail_out = (uInt) sizeof(buffer_out);
    defstream.next_out = (Bytef *) buffer_out;

    deflateInit(&defstream, Z_BEST_COMPRESSION);
    deflate(&defstream, Z_FINISH);
    deflateEnd(&defstream);

    printf("Uncompressed size is: %lu\n", strlen(buffer_in));
    printf("Compressed size is: %lu\n", defstream.total_out);

    printf("ZLIB VERSION: %s\n", zlibVersion());

    return EXIT_SUCCESS;
}
```
::::
:::::

应用程序依赖于 Zlib 库。默认情况下，Conan 会尝试从名为 ConanCenter 的远程服务器安装库。您可以在那里搜索库并查看可用版本。在本例中，在查看了 Zlib 的可用版本后，择使用最新的版本之一：`zlib/1.3.1`。

使用 Conan 安装 Zlib 库并在项目中找到它的最简单方法是使用 `conanfile.txt` 文件。内容如下：

````{eval-rst}
.. code-block:: ini
    :caption: conanfile.txt

    [requires]
    zlib/1.3.1

    [generators]
    CMakeDeps
    CMakeToolchain
````

- `[requires]` 部分声明要在项目中使用的库的地方，在本例中是 `zlib/1.3.1`。
- `[generators]` 部分告诉 Conan 生成编译器或构建系统将用于查找依赖项和构建项目的文件。在本例中，由于项目基于 CMake，将使用 [CMakeDeps](https://docs.conan.org.cn/2/reference/tools/cmake/cmakedeps.html#conan-tools-cmakedeps) 来生成关于 Zlib 库文件安装位置的信息，并使用 [CMakeToolchain](https://docs.conan.org.cn/2/reference/tools/cmake/cmaketoolchain.html#conan-tools-cmaketoolchain) 通过 CMake 工具链文件将构建信息传递给 CMake。

除了 `conanfile.txt`，还需要 Conan profile 来构建项目。Conan profile 允许用户定义一套配置，例如编译器、构建配置、架构、共享或静态库等。默认情况下，Conan 不会自动检测 profile，因此需要创建。要让 Conan 根据当前操作系统和已安装的工具尝试猜测 profile，请运行：

```bash
conan profile detect --force
```

这将根据环境检测操作系统、构建架构和编译器设置。默认情况下，它还会将构建配置设置为 `Release`。生成的 `profile` 将存储在 Conan 主文件夹中，名称为 `default`，并且除非通过命令行指定了另一个 `profile`，否则 Conan 在所有命令中默认使用它。

以下是此命令在 Ubuntu 上的输出示例：

```bash
$ conan profile detect --force
```

输出：

```bash
detect_api: CC and CXX: /media/pc/data/lxw/envs/anaconda3a/envs/py313/bin/x86_64-conda-linux-gnu-cc, /media/pc/data/lxw/envs/anaconda3a/envs/py313/bin/x86_64-conda-linux-gnu-c++ 
detect_api: Found gcc 12.4
detect_api: gcc>=5, using the major as version
detect_api: gcc C++ standard library: libstdc++11

Detected profile:
[settings]
arch=x86_64
build_type=Release
compiler=gcc
compiler.cppstd=gnu17
compiler.libcxx=libstdc++11
compiler.version=12
os=Linux

WARN: This profile is a guess of your environment, please check it.
WARN: The output of this command is not guaranteed to be stable and can change in future Conan versions.
WARN: Use your own profile files for stability.
Saving detected profile to /home/ai/.conan2/profiles/default
```

````{admonition} 关于 Conan 检测到的 C++ 标准的说明
Conan 总是将默认的 C++ 标准设置为检测到的编译器版本默认使用的标准，使用 `apple-clang` 的 macOS 除外。在这种情况下，对于 `apple-clang >= 11`，它将 `compiler.cppstd=gnu17`。如果您想使用不同的 C++ 标准，可以直接编辑默认的 profile 文件。首先，使用以下命令获取默认 profile 的位置：

```bash
$ conan profile path default
/Users/user/.conan2/profiles/default
```

然后打开并编辑该文件，将 `compiler.cppstd` 设置为您想使用的 C++ 标准。
````

````{admonition} 自定义编译器配置
:class: tip

如果您想修改 Conan profile 以使用非默认的编译器，您需要更改 compiler 设置，并使用 [`tools.build:compiler_executables` 配置](https://docs.conan.org.cn/2/reference/tools/cmake/cmaketoolchain.html#conan-cmake-toolchain-conf) 明确告诉 Conan 在哪里找到它。
````

使用 Conan 来安装 Zlib 并生成 CMake 需要用于查找此库和构建项目的文件。将在 `build` 文件夹中生成这些文件。为此，请运行：
```bash
conan install . --output-folder=build --build=missing
```

从输出中您可以看到，发生了几件事：

1. Conan 从远程服务器安装了 Zlib 库，如果该库可用，默认情况下应该是 Conan Center 服务器。该服务器存储 Conan 配方（定义库如何构建的文件）以及可以重用的二进制文件，这样就无需每次都从源代码构建。
2. Conan 在 `build` 文件夹下生成了几个文件。这些文件是由在 `conanfile.txt` 中设置的 `CMakeToolchain` 和 `CMakeDeps` 生成器生成的。`CMakeDeps` 生成文件，以便 CMake 找到刚刚下载的 Zlib 库。另一方面，`CMakeToolchain` 为 `CMake` 生成工具链文件，以便可以使用为默认 profile 检测到的相同设置透明地使用 `CMake` 构建的项目。

## 多平台构建指南

:::::{tab-set}
::::{tab-item} Windows
```powershell
cd build
cmake .. -G "Visual Studio 17 2022" ^
  -DCMAKE_TOOLCHAIN_FILE=conan_toolchain.cmake ^
  -DCMAKE_BUILD_TYPE=Release
cmake --build . --config Release
./compressor.exe
```
:::: 

::::{tab-item} Linux/macOS
```bash
cd build
cmake .. \
  -DCMAKE_TOOLCHAIN_FILE=conan_toolchain.cmake \
  -DCMAKE_BUILD_TYPE=Release
cmake --build . -j$(nproc)
./compressor
```
::::
:::::

```{list-table} 构建结果验证
:header-rows: 1
:widths: 30 70

* - 指标
  - 预期值
* - 未压缩大小
  - 207 bytes
* - 压缩后大小
  - 149 bytes
* - Zlib 版本
  - 1.3.1
```

请注意，`CMakeToolchain` 可能会生成 `CMake` `preset` 文件，这允许使用现代 `CMake (>=3.23)` 的用户使用 `cmake --preset` 而不是传递工具链文件参数。请参见 使用 [CMake preset 构建](https://docs.conan.org.cn/2/examples/tools/cmake/cmake_toolchain/build_project_cmake_presets.html#examples-tools-cmake-toolchain-build-project-presets)。
