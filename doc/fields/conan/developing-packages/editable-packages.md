# 可编辑模式下的包 

使用 Conan 包的常规方式是运行 `conan create` 或 `conan export-pkg` 将它们存储在本地缓存中，以便消费者使用缓存中的包。在某些情况下，当你希望在开发过程中使用这些包时，每次修改包时都需要运行 `conan create` 会显得很繁琐。对于这些情况，你可以将你的包置于可编辑模式，消费者将能够在本地工作目录中找到你的头文件和工件，从而无需进行打包。

让我们看看如何将包置于可编辑模式，并从本地工作目录中消费它。

首先，请克隆源代码以重新创建此项目。您可以在 GitHub 的 examples2 仓库中找到它们：

```bash
git clone https://github.com/conan-io/examples2.git
cd examples2/tutorial/developing_packages/editable_packages
```

这个项目中包含两个文件夹：

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

- 包含完整包的“say”文件夹，包括其 `conanfile.py` 及其源代码。
- 包含简单消费者项目的“hello”文件夹，包括 `conanfile.py` 及其源代码，该项目依赖于 `say/1.0` 需求。

将 `say/1.0` 置于可编辑模式，并展示 `hello` 消费者如何在其本地工作目录中找到 `say/1.0` 头文件和可执行文件。

## 将 `say/1.0` 包置于可编辑模式

为了避免每次更改都在缓存中创建包 `say/1.0`，将该包设置为可编辑模式，从缓存中的引用创建链接到本地工作目录：

```bash
$ conan editable add say
$ conan editable list
say/1.0
    Path: /Users/.../examples2/tutorial/developing_packages/editable_packages/say/conanfile.py
```

从现在开始，任何其他 Conans 包或项目使用 `say/1.0` 都将被重定向到 `/Users/.../examples2/tutorial/developing_packages/editable_packages/say/conanfile.py` 用户文件夹，而不是从 Conans 缓存中使用该包。

请注意，可编辑包的关键在于正确定义包的 `layout()`。阅读[包的 layout() 部分](https://docs.conan.io/2/reference/conanfile/methods/layout.html#reference-conanfile-methods-layout)以了解更多关于此方法的信息。

在这个示例中，`say conanfile.py` 食谱使用预定义的 `cmake_layout()`，该定义定义了典型的 CMake 项目布局，具体布局可能因平台和使用的生成器而异。

现在 `say/1.0` 包处于可编辑模式，让我们在本地构建它：

```bash
$ cd say

# Windows: we will build two configurations to show multi-config
$ conan install . -s build_type=Release
$ conan install . -s build_type=Debug
$ cmake --preset conan-default
$ cmake --build --preset conan-release
$ cmake --build --preset conan-debug

# Linux, macOS: we will build only one configuration
$ conan install .
$ cmake --preset conan-release
$ cmake --build --preset conan-release
```

## 使用 `say/1.0` 包的可编辑模式

在可编辑模式下使用软件包对使用者来说是透明的。在这种情况下，可以像往常一样构建 hello 应用程序：

```bash
$ cd ../hello

# Windows: we will build two configurations to show multi-config
$ conan install . -s build_type=Release
$ conan install . -s build_type=Debug
$ cmake --preset conan-default
$ cmake --build --preset conan-release
$ cmake --build --preset conan-debug
$ build\Release\hello.exe
say/1.0: Hello World Release!
...
$ build\Debug\hello.exe
say/1.0: Hello World Debug!
...

# Linux, macOS: we will only build one configuration
$ conan install .
$ cmake --preset conan-release
$ cmake --build --preset conan-release
$ ./build/Release/hello
say/1.0: Hello World Release!
```

如您所见， `hello` 可以成功找到 `say/1.0` 包的头文件和库文件。

## 使用可编辑的包

完成上述步骤后，您可以在不涉及 Conan 的情况下，通过构建系统或 IDE 对可编辑的包进行修改。所做的任何更改将直接应用于消费者。通过修改 say 源代码来看看它是如何工作的：

```bash
$ cd ../say
# Edit src/say.cpp and change the error message from "Hello" to "Bye"

# Windows: we will build two configurations to show multi-config
$ cmake --build --preset conan-release
$ cmake --build --preset conan-debug

# Linux, macOS: we will only build one configuration
$ cmake --build --preset conan-release
```

然后构建并运行“hello”项目：
```bash
$ cd ../hello

# Windows
$ cd build
$ cmake --build --preset conan-release
$ cmake --build --preset conan-debug
$ Release\hello.exe
say/1.0: Bye World Release!
$ Debug\hello.exe
say/1.0: Bye World Debug!

# Linux, macOS
$ cmake --build --preset conan-release
$ ./build/Release/hello
say/1.0: Bye World Release!
```

通过这种方式，你可以在不执行任何 Conan 命令的情况下同时开发 `say` 库和 `hello` 应用。如果你在 IDE 中同时打开了它们，可以简单地依次构建。

## 构建可编辑依赖项

如果可编辑的依赖项很多，逐一按正确顺序构建可能会很麻烦。可以使用 `--build` 参数进行有序构建可编辑的依赖项。

先清理之前的本地可执行文件：

```bash
git clean -xdf
```

使用之前尚未真正使用的 `build()` 方法（因为一直直接调用 `cmake` 进行构建，而不是通过调用 `conan build` 命令），只需：

```bash
conan build hello
```

请注意，为了完整构建这个项目，我们只需要执行这两个命令。在不同的文件夹中从零开始：

```bash
$ git clone https://github.com/conan-io/examples2.git
$ cd examples2/tutorial/developing_packages/editable_packages
$ conan editable add say
$ conan build hello --build=editable
```

请注意，如果我们没有将 `--build=editable` 传递给 `conan build hello`，处于可编辑模式下的 `say/0.1` 的二进制文件将不可用，并且会失败。使用 `--build=editable` 时，首先会在本地对 `say` 的二进制文件进行本地增量构建，然后会对 `hello` 进行另一个增量构建。所有操作仍然会在本地进行，缓存中不会构建任何包。如果有多个 `editable` 依赖项，并且存在嵌套的传递依赖项，Conan 将按正确的顺序构建它们。

如果可编辑的包在 Conan 缓存中有依赖项，可以通过使用 `--build=editable --build=cascade` 强制从源代码重新构建缓存依赖项。通常应避免这样做。如果需要重新构建这些依赖项，建议也将它们置于可编辑模式。

请注意，可以使用自己的 `test_package` 文件夹来构建和测试可编辑模式的包。如果将包置于可编辑模式，并且它包含 `test_package` 文件夹，`conan create` 命令仍然会进行当前包的本地构建。

## 撤销编辑模式

要禁用包的可编辑模式，只需使用以下方式移除链接：

```bash
conan editable remove --refs=say/1.0
```

它将移除链接（本地目录不会受到影响），所有使用该依赖的包将再次从缓存中获取。

```{warning}
在消耗上游可编辑包时构建的包可能会生成与可编辑包发布版本不兼容的二进制文件和包。避免在不使用缓存中所有库的版本重新创建这些包的情况下上传它们。
```
