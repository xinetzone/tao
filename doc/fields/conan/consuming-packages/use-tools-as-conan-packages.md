# 将构建工具作为 Conan 包使用

```{topic} 典型应用场景
:class: border-bottom

- 指定特定版本的构建工具（如 CMake 3.27.1）
- 隔离不同项目的工具链环境
- 确保 CI/CD 流水线工具版本一致性
```

获取示例项目（建议指定分支版本）：

```bash
git clone -b v1.0.0 https://github.com/conan-io/examples2.git
cd examples2/tutorial/consuming_packages/tool_requires
```

项目结构说明：

```
.
├── CMakeLists.txt    # CMake 构建脚本
└── src/
    └── main.c        # 示例源代码
```

该项目包含基本的 `CMakeLists.txt`，其中包含了 `zlib` 依赖项以及位于 `main.c` 中的字符串压缩程序源代码。

:::::{tab-set}
::::{tab-item} CMakeLists.txt
```{code-block} cmake
:emphasize-lines: 6

cmake_minimum_required(VERSION 3.15)
project(compressor C)

find_package(ZLIB REQUIRED)

message("Building with CMake version: ${CMAKE_VERSION}")

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
::::
:::::

```{code-block} ini
:emphasize-lines: 4,5
:caption: conanfile.txt

[requires]
zlib/1.2.11

[tool_requires]
cmake/3.22.6

[generators]
CMakeDeps
CMakeToolchain
```

```{note}
请注意，此 `conanfile.txt` 将分别安装 `zlib/1.2.11` 和 `cmake/3.22.6`。然而，如果 Conan 在 Conan Center 中找不到 Zlib 的二进制文件，并且需要从源代码构建，则您的系统上必须已经存在 CMake 安装，因为在您的 `conanfile.txt` 中声明的 `cmake/3.22.6` 仅适用于您的当前项目，而不适用于所有依赖项。如果您想在必要时安装 Zlib 时，也使用该 `cmake/3.22.6` 来构建 Zlib，您可以将 `[tool_requires]` 部分添加到您正在使用的配置文件中。有关更多信息，请查阅 [配置文件文档](https://docs.conan.org.cn/2/reference/config_files/profiles.html#reference-config-files-profiles)。
```

使用 Conan 安装 Zlib 和 CMake 3.22.6，并生成找到它们的文件。将在 `build` 文件夹中生成这些文件。为此，只需运行

```bash
conan install . --output-folder=build --build=missing
```

````{tip} 
PowerShell 用户需要在上一个命令中添加 `--conf=tools.env.virtualenv:powershell=<executable>` （例如，`powershell.exe` 或 `pwsh`），以便生成 `.ps1` 文件而不是 `.bat` 文件。从 Conan 2.11.0 起，将此配置设置为 `True` 或 `False` 已被弃用。

为避免每次都添加此行，建议在配置文件的 `[conf]` 部分进行配置。有关详细信息，请参阅 [配置文件部分](https://docs.conan.org.cn/2/reference/config_files/profiles.html#reference-config-files-profiles)。
````

会看到 Conan 生成了名为 `conanbuild.sh/bat` 的新文件。这是在声明 `conanfile.txt` 中的 `tool_requires` 时自动调用 `VirtualBuildEnv` 生成器的结果。此文件设置了一些环境变量，例如新的 `PATH`，可以使用它将 `CMake v3.22.6` 的位置注入到环境中。

激活虚拟环境，并运行 `cmake --version` 来检查您是否已将新的 `CMake` 版本安装到路径中。

:::::{tab-set} 
::::{tab-item} Windows
```bash
$ cd build
$ conanbuild.bat
# conanbuild.ps1 if using Powershell
```
::::
::::{tab-item} Linux, macOS
```bash
$ cd build
$ source conanbuild.sh
Capturing current environment in deactivate_conanbuildenv-release-x86_64.sh
Configuring environment variables
```
::::
:::::

运行 `cmake` 并检查版本
```bash
$ cmake --version
cmake version 3.22.6
...
```

如您所见，激活环境后，CMake v3.22.6 二进制文件夹已添加到路径中，现在是当前活动版本。现在您可以像之前一样构建您的项目，但这次 Conan 将使用 CMake 3.22.6 来构建它

:::::{tab-set} 
::::{tab-item} Windows
```bash
# assuming Visual Studio 15 2017 is your VS version and that it matches your default profile
$ cmake .. -G "Visual Studio 15 2017" -DCMAKE_TOOLCHAIN_FILE=conan_toolchain.cmake
$ cmake --build . --config Release
...
Building with CMake version: 3.22.6
...
[100%] Built target compressor
$ Release\compressor.exe
Uncompressed size is: 233
Compressed size is: 147
ZLIB VERSION: 1.2.11
```
::::
::::{tab-item} Linux, macOS
```bash
$ cmake .. -DCMAKE_TOOLCHAIN_FILE=conan_toolchain.cmake -DCMAKE_BUILD_TYPE=Release
$ cmake --build .
...
Building with CMake version: 3.22.6
...
[100%] Built target compressor
$ ./compressor
Uncompressed size is: 233
Compressed size is: 147
ZLIB VERSION: 1.2.11
```
::::
:::::

请注意，当激活环境时，在同一文件夹中创建了名为 `deactivate_conanbuild.sh/bat` 的新文件。如果您 `source` 此文件，可以将环境恢复到之前状态。

:::::{tab-set} 
::::{tab-item} Windows
```bash
$ deactivate_conanbuild.bat
```
::::
::::{tab-item} Linux, macOS
```bash
$ source deactivate_conanbuild.sh
Restoring environment
```
::::
:::::

```{admonition} 最佳实践
`tool_requires` 和工具包适用于可执行应用程序，例如 `cmake` 或 `ninja`。请勿使用 `tool_requires` 来依赖库或类似库的依赖项。
```
