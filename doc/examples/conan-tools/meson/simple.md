# 使用 Conan 构建简单的 Meson 项目

在这个[示例](https://docs.conan.io/2/examples/tools/meson/build_simple_meson_project.html)中，将创建使用最流行的 C++ 库之一：[Zlib](https://zlib.net/) 的字符串压缩应用程序。

```{note}
这个示例基于主要的“[使用 Conan 构建简单的 CMake 项目](https://docs.conan.io/2/tutorial/consuming_packages/build_simple_cmake_project.html#consuming-packages-build-simple-cmake-project)”教程。因此，在尝试这个示例之前，强烈建议您先阅读它。
```

使用 Meson 作为构建系统，并使用 [pkg-config](../../../fields/pkg-config/pkgconfiglite) 作为辅助工具，因此在进行这个示例之前，您应该先安装它们。

请首先克隆源代码以重新创建此项目。你可以在 GitHub 的 examples2 仓库中找到它们：

```bash
git clone https://github.com/conan-io/examples2.git
cd examples2/examples/tools/meson/mesontoolchain/simple_meson_project
```

从非常简单的 C 语言项目开始，其结构如下：

```bash
.
├── meson.build
└── src
    └── main.c
```

项目包含基本的 `meson.build`，其中包括 `zlib` 依赖和字符串压缩程序在 `main.c` 中的源代码。


```{code-block} c
:caption: main.c

#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include <zlib.h>

int main(void) {
    char buffer_in [256] = {"Conan is a MIT-licensed, Open Source package manager for C and C++ development "
                            "for C and C++ development, allowing development teams to easily and efficiently "
                            "manage their packages and dependencies across platforms and build systems."};
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
    printf("Compressed size is: %lu\n", strlen(buffer_out));

    printf("ZLIB VERSION: %s\n", zlibVersion());

    return EXIT_SUCCESS;
}
```

```{code-block} meson
:caption: meson.build

project('tutorial', 'c')
zlib = dependency('zlib', version : '1.2.11')
executable('compressor', 'src/main.c', dependencies: zlib)
```

创建包含以下内容的 `conanfile.txt` 来安装 Zlib：

```ini
[requires]
zlib/1.3.1

[generators]
PkgConfigDeps
MesonToolchain
```

在这种情况下，将使用 [`PkgConfigDeps`](https://docs.conan.io/2/reference/tools/gnu/pkgconfigdeps.html#id1) 来生成关于 Zlib 库文件安装位置的信息，这得益于 `*.pc` 文件，并使用 [`MesonToolchain`](https://docs.conan.io/2/reference/tools/meson/mesontoolchain.html#id1) 通过 `conan_meson_[native|cross].ini` 文件将构建信息传递给 `Meson`，该文件描述了本机/交叉编译环境，在本例中是 `conan_meson_native.ini` 文件。

使用 Conan 来安装 Zlib 并生成 Meson 需要找到此库并构建我们项目的文件。将这些文件生成在 `build` 文件夹中。为此，请运行：

```bash
conan install . --output-folder=build --build=missing
```

构建并运行压缩器应用程序：

`````{tab-set} 
````{tab-item} Windows
```bash
$ cd build
$ meson setup --native-file conan_meson_native.ini .. meson-src
$ meson compile -C meson-src
$ meson-src\compressor.exe
Uncompressed size is: 233
Compressed size is: 147
ZLIB VERSION: 1.2.11
```
````
````{tab-item} Linux, macOS
```bash
$ cd build
$ meson setup --native-file conan_meson_native.ini .. meson-src
$ meson compile -C meson-src
$ ./meson-src/compressor
Uncompressed size is: 233
Compressed size is: 147
ZLIB VERSION: 1.2.11
```
````
`````