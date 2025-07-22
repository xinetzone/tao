# 理解 Conan 包布局

在上一节中，介绍了可编辑包的概念，并提到它们在可编辑模式下能够立即工作的原因是当前 `layout()` 方法中信息的定义。本篇详细地探讨这一特性。

在[本教程](https://docs.conan.io/2/tutorial/developing_packages/package_layout.html)中，将继续使用 `say/1.0` 包和[可编辑包教程](./editable-packages)中使用的 `hello/1.0` 消费者。

首先，请克隆源代码以重新创建此项目。您可以在 GitHub 的 examples2 仓库中找到它们：

```bash
git clone https://github.com/conan-io/examples2.git
cd examples2/tutorial/developing_packages/package_layout
```

如您所见，主文件夹结构是相同的：

```bash
.
├── hello
│   ├── CMakeLists.txt
│   ├── conanfile.py
│   └── src
│       └── hello.cpp
└── say
    ├── CMakeLists.txt
    ├── conanfile.py
    ├── include
    │   └── say.h
    └── src
        └── say.cpp
```

这里的 主要区别在于，在 `say/1.0` ConanFile 中没有使用预定义的 [`cmake_layout()`](https://docs.conan.io/2/reference/tools/cmake/cmake_layout.html#cmake-layout)，而是声明了自己的自定义布局。让我们看看我们如何在 layout() 方法中描述信息，以便在 Conan 本地缓存中创建包以及包处于可编辑模式时都能正常工作。

```{code-block} python
:caption: say/conanfile.py

import os
from conan import ConanFile
from conan.tools.cmake import CMake


class SayConan(ConanFile):
    name = "say"
    version = "1.0"

    exports_sources = "CMakeLists.txt", "src/*", "include/*"

    ...

    def layout(self):

        ## define project folder structure

        self.folders.source = "."
        self.folders.build = os.path.join("build", str(self.settings.build_type))
        self.folders.generators = os.path.join(self.folders.build, "generators")

        ## cpp.package information is for consumers to find the package contents in the Conan cache

        self.cpp.package.libs = ["say"]
        self.cpp.package.includedirs = ["include"] # includedirs is already set to 'include' by
                                                   # default, but declared for completion
        self.cpp.package.libdirs = ["lib"]         # libdirs is already set to 'lib' by
                                                   # default, but declared for completion

        ## cpp.source and cpp.build information is specifically designed for editable packages:

        # this information is relative to the source folder that is '.'
        self.cpp.source.includedirs = ["include"] # maps to ./include

        # this information is relative to the build folder that is './build/<build_type>', so it will
        self.cpp.build.libdirs = ["."]  # map to ./build/<build_type> for libdirs

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
```

回顾 `layout()` 方法。可以看到正在为 `self.folders` 和 `self.cpp` 设置值。解释这些值的作用。

## `self.folders`

定义了 `say` 项目的源代码结构，以及由 Conan 生成的文件和构建产物存放的文件夹。这种结构与包是否处于可编辑模式或导出到 Conan 本地缓存中并构建无关。定义 `say` 包的文件夹结构：

```bash
say
 ├── CMakeLists.txt
 ├── conanfile.py
 ├── include
 │   └── say.h
 ├── src
 │   └── say.cpp
 └── build
     ├── Debug            --> Built artifacts for Debug
     │   └── generators   --> Conan generated files for Debug config
     └── Release          --> Built artifacts for Release
         └── generators   --> Conan generated files for Release config
```

- 由于 CMakeLists.txt 位于 `.` 文件夹中，`self.folders.source` 被设置为 `.`。
- 将 `self.folders.build` 设置为 `./build/Release` 或 `./build/Debug`，具体取决于 `build_type` 的设置。这些是希望构建的二进制文件存放的文件夹。
- `self.folders.generators` 文件夹为所有由 Conan 生成器创建的文件设置的位置。在这种情况下，所有由 CMakeToolchain 生成器生成的文件都将存储在那里。

```{note}
请注意，上述值适用于单配置 CMake 生成器。为了支持多配置生成器，例如 Visual Studio，您需要对此布局进行一些更改。要查看同时支持单配置和多配置的完整布局，请查阅 Conan 文档中的 [`cmake_layout()`](https://docs.conan.io/2/reference/tools/cmake/cmake_layout.html#cmake-layout)。
```

## `self.cpp`

这个属性用于定义消费者将如何找到包的内容（头文件、库等），具体取决于包是否处于可编辑模式。

## `cpp.package`

- 首先，设置 `cpp.package` 的信息。这定义了包的内容及其相对于本地缓存中存储包的文件夹的位置。请注意，定义这些信息等同于在 `package_info()` 方法中定义 `self.cpp_info`。这是我们定义的信息：
- `self.cpp.package.libs`：添加 `say` 库，以便消费者知道应该链接它。这等同于在 `package_info()` 方法中声明 `self.cpp_info.libs`。
- `self.cpp.package.libdirs`: 添加 `lib` 文件夹，以便消费者知道他们应该在那里搜索库。这相当于在 `package_info()` 方法中声明 `self.cpp_info.libdirs`。请注意，在 `cpp_info` 和 `cpp.package` 中 `libdirs` 的默认值都是 `["lib"]`，因此可以省略该声明。
- `self.cpp.package.includedirs`: 添加 `include` 文件夹，以便消费者知道他们应该在那里搜索库头文件。这相当于在 `package_info()` 方法中声明 `self.cpp_info.includedirs`。请注意，在 `cpp_info` 和 `cpp.package` 中 `includedirs` 的默认值都是 `["include"]`，因此可以省略该声明。

为了检查这些信息如何影响消费者，我们将首先对 `say` 包执行 `conan create` 操作：

```bash
cd say
conan create . -s build_type=Release
```

当调用 `conan create` 时，Conan 会将 `recipe` 中声明的 `recipe` 和 `sources` 移动到本地缓存中的 `recipe` 文件夹，然后创建单独的 `package` 文件夹来构建二进制文件并存储实际的 `package` 内容。如果你检查 [`YOUR_CONAN_HOME]/p` 文件夹，你会发现两个类似这些的新文件夹：

```{tip}
可以使用 `conan cache` 命令或检查 `conan create` 命令的输出来获取这些文件夹的确切位置。
```

```{code-block} bash
:emphasize-lines: 14-18

<YOUR_CONAN_HOME>/p
├── sayb3ea744527a91      --> folder for sources
│   └── ...
│
└── say830097e941e10      --> folder for building and storing the package binaries
    ├── b
    │   ├── build
    │   │   └── Release
    │   ├── include
    │   │   └── say.h
    │   └── src
    │       ├── hello.cpp
    │       └── say.cpp
    └── p
        ├── include       --> defined in cpp.package.includedirs
        │   └── say.h
        └── lib           --> defined in cpp.package.libdirs
            └── libsay.a  --> defined in self.cpp.package.libs
```

可以在那里识别出在 `layout()` 方法中定义的结构。如果你现在构建 `hello` 消费项目，它将在本地缓存中搜索 `say` 在该文件夹中的所有头文件和库，搜索位置由 `cpp.package` 定义：

```{code-block} bash
:emphasize-lines: 11,13

$ cd ../hello
$ conan install . -s build_type=Release

# Linux, MacOS
$ cmake --preset conan-release --log-level=VERBOSE
# Windows
$ cmake --preset conan-default --log-level=VERBOSE

...
-- Conan: Target declared 'say::say'
-- Conan: Library say found <YOUR_CONAN_HOME>p/say8938ceae216fc/p/lib/libsay.a
-- Created target CONAN_LIB::say_say_RELEASE STATIC IMPORTED
-- Conan: Found: <YOUR_CONAN_HOME>p/p/say8938ceae216fc/p/lib/libsay.a
-- Configuring done
...

$ cmake --build --preset conan-release
[ 50%] Building CXX object CMakeFiles/hello.dir/src/hello.cpp.o
[100%] Linking CXX executable hello
[100%] Built target hello
```

## `cpp.source` 和 `cpp.build`

还定义了配方中的 `cpp.source` 和 `cpp.build` 属性。这些属性仅在包处于可编辑模式下使用，并指向消费者用来查找头文件和可执行文件的路径。定义了：

- `self.cpp.source.includedirs` 设置为 `["include"]`。此路径相对于定义为 `self.folders.source` 的 `.`。对于可编辑包，此路径将是项目所在的本地文件夹。
- `self.cpp.build.libdirs` 设置为 `["."]`。此路径相对于定义为 `./build/` 的 `self.folders.build`。对于可编辑包，此路径将指向 `/build/`。

请注意，还有其他 `cpp.source` 和 `cpp.build` 的定义，它们具有不同的含义和用途。例如：

- `self.cpp.source.libdirs` 和 `self.cpp.source.libs` 可以在我们有预编译库在源代码仓库中，例如提交到 git 中时使用。它们不是构建的产物，而是源代码的一部分。
- `self.cpp.build.includedirs` 可以用于包含在构建时生成的头文件所在的文件夹，因为通常情况下，在开始编译项目之前，一些代码生成器会被构建过程调用。

为了检查这些信息如何影响消费者，将首先将 `say` 包设置为可编辑模式，并在本地进行构建。

```bash
$ cd ../say
$ conan editable add . --name=say --version=1.0
$ conan install . -s build_type=Release
$ cmake --preset conan-release
$ cmake --build --preset conan-release
```

如果你现在检查 `say` 项目文件夹的内容，可以看到输出文件夹与用 `self.folders` 定义的那些相匹配：

```{code-block} bash
:emphasize-lines: 5,11,13

.
├── CMakeLists.txt
├── CMakeUserPresets.json
├── build
│   └── Release       --> defined in cpp.build.libdirs
│       ├── ...
│       ├── generators
│       │   ├── CMakePresets.json
│       │   ├── ...
│       │   └── deactivate_conanrun.sh
│       └── libsay.a  --> no need to define
├── conanfile.py
├── include           --> defined in cpp.source.includedirs
│   └── say.h
└── src
    ├── hello.cpp
    └── say.cpp
```

既然已经将 `say` 包置于可编辑模式，如果构建 `hello` 消费者项目，它将搜索 `say` 的所有头文件和库，这些文件和库位于 `cpp.source` 和 `cpp.build` 定义的文件夹中：

```{code-block} bash
:emphasize-lines: 11,12

$ cd ../hello
$ conan install . -s build_type=Release

# Linux, MacOS
$ cmake --preset conan-release --log-level=VERBOSE
# Windows
$ cmake --preset conan-default --log-level=VERBOSE

...
-- Conan: Target declared 'say::say'
-- Conan: Library say found <local_folder>/examples2/tutorial/developing_packages/package_layout/say/build/Release/libsay.a
-- Conan: Found: <local_folder>/examples2/tutorial/developing_packages/package_layout/say/build/Release/libsay.a
-- Configuring done
...

$ cmake --build --preset conan-release
[ 50%] Building CXX object CMakeFiles/hello.dir/src/hello.cpp.o
[100%] Linking CXX executable hello
[100%] Built target hello

$ conan editable remove --refs=say/1.0
```

```{note}
请注意，没有定义 `self.cpp.build.libs = ["say"]` 。这是因为 `self.cpp.source` 和 `self.cpp.build` 中设置的信息将与 `self.cpp.package` 中的信息合并，因此您只需定义可编辑包中会发生变化的内容。出于同样的原因，您也可以省略设置 `self.cpp.source.includedirs = ["include"]` ，但保留它以展示 `cpp.source` 的使用方法。
```
