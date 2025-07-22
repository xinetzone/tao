# 预构建二进制包

在某些特定情况下，有必要从现有二进制文件创建包，例如从第三方获取或由未使用 Conan 的另一过程或团队先前构建的二进制文件。在这种情况下，从源代码构建并不是你想要的。

以下是一些可以打包本地文件的场景：
1. 当你本地开发包并希望快速创建包含构建产物的包，但又不希望再次重建（干净副本）你的产物时，你不想调用 `conan create`。如果你使用 IDE，这种方法将保留你的本地项目构建。
2. 当你无法从源代码构建包（只有预构建的二进制文件可用）并且它们存储在本地目录中时。
3. 与 2 相同，但您在远程仓库中有预编译的库。

## 本地构建二进制文件

使用 `conan new` 命令创建“Hello World” C++ 库示例项目：
```bash
conan new cmake_lib -d name=hello -d version=0.1
```

将创建具有以下结构的 Conan 包项目。
```bash
.
├── CMakeLists.txt
├── conanfile.py
├── include
│   └── hello.h
├── src
│   └── hello.cpp
└── test_package
    ├── CMakeLists.txt
    ├── conanfile.py
    └── src
        └── example.cpp
```

在根目录下有 `CMakeLists.txt` 文件，包含 `cpp` 文件的 `src` 文件夹，以及用于头文件的 `include` 文件夹。还有 `test_package/` 文件夹用于测试导出的包是否工作正常。

现在，对于每种不同的配置（不同的编译器、架构、`build_type` 等）：
1. 调用 `conan install` 来生成 `conan_toolchain.cmake` 文件和 `CMakeUserPresets.json` 文件，这些文件可以 IDE 中或调用 CMake（仅 3.23 及以上版本）时使用。
```bash
conan install . -s build_type=Release
```
2. 通过调用 CMake、IDE 等来构建项目：
`````{tab-set}
````{tab-item} Linux, macOS
```bash
$ mkdir -p build/Release
$ cd build/Release
$ cmake ../.. -DCMAKE_BUILD_TYPE=Release -DCMAKE_TOOLCHAIN_FILE=../Release/generators/conan_toolchain.cmake
$ cmake --build .
```
````
````{tab-item} Windows
```bash
$ mkdir -p build/Release
$ cd build/Release
$ cmake ../.. -DCMAKE_BUILD_TYPE=Release -DCMAKE_TOOLCHAIN_FILE=../Release/generators/conan_toolchain.cmake
$ cmake --build .
```
````
`````

```{note}
由于直接使用 IDE 或 CMake 来构建库，配方中的 `build()` 方法永远不会被调用，可以删除。
```

3. 调用 `conan export-pkg` 来打包构建好的工件。

```bash
$ cd ../..
$ conan export-pkg . -s build_type=Release
...
hello/0.1: Calling package()
hello/0.1 package(): Packaged 1 '.h' file: hello.h
hello/0.1 package(): Packaged 1 '.a' file: libhello.a
...
hello/0.1: Package '54a3ab9b777a90a13e500dd311d9cd70316e9d55' created
```

更详细地看一下 `package` 方法。生成的 `package()` 方法使用 `cmake.install()` 将工件从本地文件夹复制到 Conan 包中。

存在一种替代的通用方法，可用于任何构建系统：
```python
def package(self):
    local_include_folder = os.path.join(self.source_folder, self.cpp.source.includedirs[0])
    local_lib_folder = os.path.join(self.build_folder, self.cpp.build.libdirs[0])
    copy(self, "*.h", local_include_folder, os.path.join(self.package_folder, "include"), keep_path=False)
    copy(self, "*.lib", local_lib_folder, os.path.join(self.package_folder, "lib"), keep_path=False)
    copy(self, "*.a", local_lib_folder, os.path.join(self.package_folder, "lib"), keep_path=False)
```

此方法会复制来自以下目录的工件，得益于方法 `layout()`，这些目录将始终指向正确的位置：
- `os.path.join(self.source_folder, self.cpp.source.includedirs[0])` 将始终指向我们的本地包含文件夹。
- `os.path.join(self.build_folder, self.cpp.build.libdirs[0])` 将始终指向库的构建位置，无论使用单配置 CMake 生成器还是多配置生成器。

4. 可以通过调用 `conan test` 来测试构建的包

```bash
$ conan test test_package/conanfile.py hello/0.1 -s build_type=Release

-------- Testing the package: Running test() ----------
hello/0.1 (test package): Running test()
hello/0.1 (test package): RUN: ./example
hello/0.1: Hello World Release!
  hello/0.1: __x86_64__ defined
  hello/0.1: __cplusplus199711
  hello/0.1: __GNUC__4
  hello/0.1: __GNUC_MINOR__2
  hello/0.1: __clang_major__13
  hello/0.1: __clang_minor__1
  hello/0.1: __apple_build_version__13160021
```

现在你可以尝试为 `build_type=Debug` 生成二进制包，方法是执行相同的步骤但更改 `build_type`。你可以针对不同的配置重复此过程任意次数。

## 打包预构建的二进制文件

请首先克隆源代码以重新创建此项目。你可以在 GitHub 上的 examples2 存储库中找到它们：

```bash
git clone https://github.com/conan-io/examples2.git
cd examples2/tutorial/creating_packages/other_packages/prebuilt_binaries
```

这是引言中解释的场景 2 的示例。如果你有包含不同配置二进制的本地文件夹，你可以使用以下方法来打包它们。

这示例的文件，（请注意库文件只是空文件，因此不是有效的库）：

```bash
.
├── conanfile.py
└── vendor_hello_library
    ├── linux
    │   ├── armv8
    │   │   ├── include
    │   │   │   └── hello.h
    │   │   └── libhello.a
    │   └── x86_64
    │       ├── include
    │       │   └── hello.h
    │       └── libhello.a
    ├── macos
    │   ├── armv8
    │   │   ├── include
    │   │   │   └── hello.h
    │   │   └── libhello.a
    │   └── x86_64
    │       ├── include
    │       │   └── hello.h
    │       └── libhello.a
    └── windows
        ├── armv8
        │   ├── hello.lib
        │   └── include
        │       └── hello.h
        └── x86_64
            ├── hello.lib
            └── include
                └── hello.h
```

有对应设置 `os` 和 `arch` 的文件夹和子文件夹。这是示例的配方：

```bash
import os
from conan import ConanFile
from conan.tools.files import copy


class helloRecipe(ConanFile):
    name = "hello"
    version = "0.1"
    settings = "os", "arch"

    def layout(self):
        _os = str(self.settings.os).lower()
        _arch = str(self.settings.arch).lower()
        self.folders.build = os.path.join("vendor_hello_library", _os, _arch)
        self.folders.source = self.folders.build
        self.cpp.source.includedirs = ["include"]
        self.cpp.build.libdirs = ["."]

    def package(self):
        local_include_folder = os.path.join(self.source_folder, self.cpp.source.includedirs[0])
        local_lib_folder = os.path.join(self.build_folder, self.cpp.build.libdirs[0])
        copy(self, "*.h", local_include_folder, os.path.join(self.package_folder, "include"), keep_path=False)
        copy(self, "*.lib", local_lib_folder, os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.a", local_lib_folder, os.path.join(self.package_folder, "lib"), keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["hello"]
```

- 什么也没有在构建，所以 `build` 方法在这里没有用。
- 可以保留上一个示例中的相同 `package` 方法，因为工件的存储位置由 `layout()` 声明。
- 源文件夹（包含头文件）和构建文件夹（包含库文件）都在同一个位置，路径遵循：`vendor_hello_library/{os}/{arch}`
- 头文件位于 `self.source_folder` 的 `include` 子文件夹中（在 `self.cpp.source.includedirs` 中声明它）。
- 库文件位于 `self.build_folder` 文件夹的根目录中（声明 `self.cpp.build.libdirs = ["."]` ）。
- 移除了 `compiler` 和 `build_type`，因为只有根据操作系统和架构不同的库（可能是纯 C 库）。

现在，对于每种不同的配置，都运行 `conan export-pkg` 命令。之后，可以列出二进制文件，以便检查每个预编译库都有一个包。

```bash
$ conan export-pkg . -s os="Linux" -s arch="x86_64"
$ conan export-pkg . -s os="Linux" -s arch="armv8"
$ conan export-pkg . -s os="Macos" -s arch="x86_64"
$ conan export-pkg . -s os="Macos" -s arch="armv8"
$ conan export-pkg . -s os="Windows" -s arch="x86_64"
$ conan export-pkg . -s os="Windows" -s arch="armv8"

$ conan list "hello/0.1#:*"
Local Cache
  hello
    hello/0.1
      revisions
        9c7634dfe0369907f569c4e583f9bc50 (2024-05-10 08:28:31 UTC)
          packages
            522dcea5982a3f8a5b624c16477e47195da2f84f
              info
                settings
                  arch: x86_64
                  os: Windows
            63fead0844576fc02943e16909f08fcdddd6f44b
              info
                settings
                  arch: x86_64
                  os: Linux
            82339cc4d6db7990c1830d274cd12e7c91ab18a1
              info
                settings
                  arch: x86_64
                  os: Macos
            a0cd51c51fe9010370187244af885b0efcc5b69b
              info
                settings
                  arch: armv8
                  os: Windows
            c93719558cf197f1df5a7f1d071093e26f0e44a0
              info
                settings
                  arch: armv8
                  os: Linux
            dcf68e932572755309a5f69f3cee1bede410e907
              info
                settings
                  arch: armv8
                  os: Macos
```

在这个示例中，没有 `test_package/` 文件夹，但你可以像上一个示例那样提供文件夹来测试包。

## 下载和打包预构建二进制文件 

这是引言中解释的情景 3 的示例。如果没有构建库，很可能在某个远程仓库中拥有它们。在这种情况下，创建完整的 Conan 配方，并详细获取二进制文件可能是首选的方法，因为它具有可重复性，而且原始二进制文件可能可以被追溯。

请首先克隆源代码以重新创建此项目。你可以在 GitHub 上的 examples2 存储库中找到它们：

```bash
git clone https://github.com/conan-io/examples2.git
cd examples2/tutorial/creating_packages/other_packages/prebuilt_remote_binaries
```

```{code-block} python
:caption: conanfile.py

import os
from conan.tools.files import get, copy
from conan import ConanFile


class HelloConan(ConanFile):
    name = "hello"
    version = "0.1"
    settings = "os", "arch"

    def build(self):
        base_url = "https://github.com/conan-io/libhello/releases/download/0.0.1/"

        _os = {"Windows": "win", "Linux": "linux", "Macos": "macos"}.get(str(self.settings.os))
        _arch = str(self.settings.arch).lower()
        url = "{}/{}_{}.tgz".format(base_url, _os, _arch)
        get(self, url)

    def package(self):
        copy(self, "*.h", self.build_folder, os.path.join(self.package_folder, "include"))
        copy(self, "*.lib", self.build_folder, os.path.join(self.package_folder, "lib"))
        copy(self, "*.a", self.build_folder, os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.libs = ["hello"]
```

通常，预编译的二进制文件会针对不同的配置，因此 `build()` 方法需要实现的唯一任务就是将 `settings` 映射到不同的 URL。

只需要用不同的设置调用 `conan create` 来生成所需的包：

```bash
$ conan create . -s os="Linux" -s arch="x86_64"
$ conan create . -s os="Linux" -s arch="armv8"
$ conan create . -s os="Macos" -s arch="x86_64"
$ conan create . -s os="Macos" -s arch="armv8"
$ conan create . -s os="Windows" -s arch="x86_64"
$ conan create . -s os="Windows" -s arch="armv8"

$ conan list "hello/0.1#:*"
Local Cache
  hello
    hello/0.1
      revisions
        d8e4debf31f0b7b5ec7ff910f76f1e2a (2024-05-10 09:13:16 UTC)
          packages
            522dcea5982a3f8a5b624c16477e47195da2f84f
              info
                settings
                  arch: x86_64
                  os: Windows
            63fead0844576fc02943e16909f08fcdddd6f44b
              info
                settings
                  arch: x86_64
                  os: Linux
            82339cc4d6db7990c1830d274cd12e7c91ab18a1
              info
                settings
                  arch: x86_64
                  os: Macos
            a0cd51c51fe9010370187244af885b0efcc5b69b
              info
                settings
                  arch: armv8
                  os: Windows
            c93719558cf197f1df5a7f1d071093e26f0e44a0
              info
                settings
                  arch: armv8
                  os: Linux
            dcf68e932572755309a5f69f3cee1bede410e907
              info
                settings
                  arch: armv8
                  os: Macos
```

建议在 `test_package` 文件夹中包含小型消费项目来验证包是否正确构建，然后使用 `conan upload` 将其上传到 Conan 远程。

相同的构建策略适用：如果未创建 Conan 包且未定义 `--build` 参数，则允许 `recipe` 失败。对于这类包，典型的方法可能是定义 `build_policy="missing"`，特别是如果 URL 也由团队控制。如果 URL 是外部的（在互联网上），最好创建包并将其存储在您自己的 Conan 仓库中，这样构建就不会依赖于第三方 URL 的可用性。
