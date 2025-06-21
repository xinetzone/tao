# 创建 Conan 包

在前面的章节中，使用了 Conan 包（例如 Zlib），首先使用 `conanfile.txt`，然后使用 `conanfile.py`。但是 `conanfile.py` recipe 文件不仅用于使用其他包，它也可以用来创建自己的包。在本节中，我们将解释如何使用 `conanfile.py` recipe 创建简单的 Conan 包，以及如何使用 Conan 命令从源代码构建这些包。

使用 `conan new` 命令创建 “Hello World” C++ 库示例项目

```bash
conan new cmake_lib -d name=hello -d version=1.0 -o .temp
```

这将创建具有以下结构的 Conan 包项目

```
.temp
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

生成的文件是：

- `conanfile.py`：在根文件夹中，有 `conanfile.py`，它是主要的 `recipe` 文件，负责定义如何构建和使用包。
- `CMakeLists.txt`：简单的通用 `CMakeLists.txt`，其中没有任何与 Conan 相关的内容。
- `src` 和 `include` 文件夹：包含简单 C++ “hello” 库的文件夹。
- `test_package` 文件夹：包含示例应用程序，该应用程序将依赖并链接到创建的包。这不是强制性的，但它有助于检查包是否正确创建。
```python
from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps


class helloRecipe(ConanFile):
    name = "hello"
    version = "1.0"
    package_type = "library"

    # Optional metadata
    license = "<Put the package license here>"
    author = "<Put your name here> <And your email here>"
    url = "<Package recipe repository url here, for issues about the package>"
    description = "<Description of hello package here>"
    topics = ("<Put some tag here>", "<here>", "<and here>")

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    # Sources are located in the same place as this recipe, copy them to the recipe
    exports_sources = "CMakeLists.txt", "src/*", "include/*"

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self)
    
    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["hello"]
```
简要解释下 `recipe` 的不同部分

首先，您可以看到定义的 Conan 包的名称和版本

- `name`：字符串，最少 2 个字符，最多 100 个小写字符，用于定义包名称。它应该以字母数字字符或下划线开头，可以包含字母数字、下划线、`+`、`.`、`-` 字符。
- `version`：字符串，可以取任何值，与 `name` 属性的约束相同。如果版本遵循语义版本控制形式 `X.Y.Z-pre1+build2`，该值可能用于通过版本范围而不是精确版本来要求此包。

接下来您可以看到一些定义元数据的属性。这些属性是可选的但推荐使用，它们定义了包的简短 `description`、打包库的 `author`、`license`、包仓库的 `url` 以及与包相关的 `topics` 等信息。
之后，有一个与二进制配置相关的部分。此部分定义了包的有效 `settings` 和 `options`。

- `settings` 是项目范围的配置，不能在 `recipes` 中设置默认值。例如操作系统、编译器或构建配置，这些将是多个 Conan 包共有的。
- `options` 是包特定的配置，可以在 `recipes` 中设置默认值。在本例中，我们有将包创建为共享库或静态库的选项，其中静态库是默认值。
之后，设置 `exports_sources` 属性来定义哪些源文件属于 Conan 包。这些是您想要打包的库的源文件。在本例中，“hello” 库的源文件。
接下来，声明了几个方法

- `config_options()` 方法（与 `configure()` 方法一起）允许对二进制配置模型进行微调。例如，在 Windows 上没有 fPIC 选项，因此可以将其移除。
- `layout()` 方法声明了期望找到源文件以及构建过程中生成文件的目标位置。例如，生成二进制文件的目标文件夹以及 Conan generator 在 `generate()` 方法中创建的所有文件。在本例中，由于项目使用 CMake 作为构建系统，调用 `cmake_layout()`。调用此函数将为 CMake 项目设置预期的位置。
- `generate()` 方法准备从源代码构建包。在本例中，可以将其简化为属性 `generators = "CMakeToolchain"`，但此处保留是为了展示这个重要方法。在这种情况下，执行 CMakeToolchain `generate()` 方法将创建 `conan_toolchain.cmake` 文件，该文件将 Conan 的 `settings` 和 `options` 转换为 CMake 语法。CMakeDeps `generator` 为了完整性而添加，但在 `recipe` 中添加 `requires` 之前并非严格必需。
- `build()` 方法使用 CMake wrapper 调用 CMake 命令。它是一个薄层，在本例中将传递 `-DCMAKE_TOOLCHAIN_FILE=conan_toolchain.cmake` 参数。它将配置项目并从源代码构建。
- `package()` 方法将 `artifacts`（头文件、库文件）从构建文件夹复制到最终的包文件夹。这可以使用简单的“copy”命令完成，但在本例中，它利用了 CMake 已有的 `install` 功能。如果 `CMakeLists.txt` 没有实现此功能，则很容易在 `package()` 方法中使用 `copy()` 工具 编写等效的实现。
- 最后，`package_info()` 方法定义了当使用者使用此包时，必须链接 “hello” 库。也可以定义其他信息，例如 `include` 或 `lib` 路径。此信息用于 `generator` （如 CMakeDeps）创建的文件，供使用者使用。这是关于当前包的通用信息，无论使用者使用何种构建系统，也无论我们在 `build()` 方法中使用了何种构建系统，此信息都对使用者可用。
`test_package` 文件夹对于现在理解如何创建包并非关键。重要的部分是

- `test_package` 文件夹不同于单元测试或集成测试。这些测试是“包”测试，用于验证包是否正确创建，以及包使用者是否能够链接并重用它。
- 它本身就是一个小的 Conan 项目。它包含自己的 `conanfile.py` 及其源代码（包括构建脚本），它依赖于正在创建的包，并构建和执行需要包中库的小应用程序。
- 它不属于包。它仅存在于源代码仓库中，而不是在包中。
使用当前默认配置从源代码构建包，然后让 `test_package` 文件夹测试该包
```bash
$ conan create .

======== Exporting recipe to the cache ========
hello/1.0: Exporting package recipe
...
hello/1.0: Exported: hello/1.0#dcbfe21e5250264b26595d151796be70 (2024-03-04 17:52:39 UTC)

======== Installing packages ========
-------- Installing package hello/1.0 (1 of 1) --------
hello/1.0: Building from source
hello/1.0: Calling build()
...
hello/1.0: Package '9bdee485ef71c14ac5f8a657202632bdb8b4482b' built

======== Testing the package: Building ========
...
[ 50%] Building CXX object CMakeFiles/example.dir/src/example.cpp.o
[100%] Linking CXX executable example
[100%] Built target example

======== Testing the package: Executing test ========
hello/1.0 (test package): Running test()
hello/1.0 (test package): RUN: ./example
hello/1.0: Hello World Release!
  hello/1.0: __aarch64__ defined
  hello/1.0: __cplusplus201703
  hello/1.0: __GNUC__4
  hello/1.0: __GNUC_MINOR__2
  hello/1.0: __clang_major__15
  hello/1.0: __apple_build_version__15000309
...
```
如果显示“Hello world Release!”，则表示成功了。这是发生的事情

- `conanfile.py` 和 `src` 文件夹的内容一起被复制（在 Conan 术语中称为 导出）到本地 Conan 缓存中。
- `hello/1.0` 包的新的从源代码构建过程开始，调用 `generate()`、`build()` 和 `package()` 方法。这会在 Conan 缓存中创建二进制包。
- Conan 然后进入 `test_package` 文件夹并执行 `conan install + conan build + test()` 方法，以检查包是否正确创建
可以验证 `recipe` 和包的二进制文件是否在缓存中
```bash
$ conan list hello
Local Cache
  hello
    hello/1.0
```
`conan create` 命令接收与 `conan install` 相同的参数，因此您可以向其传递相同的 `settings` 和 `options`。如果执行以下命令，将为 Debug 配置创建新的包二进制文件，并将 `hello` 库构建为共享库
```bash
$ conan create . -s build_type=Debug
...
hello/1.0: Hello World Debug!

$ conan create . -o hello/1.0:shared=True
...
hello/1.0: Hello World Release!
```
这些新的包二进制文件也将存储在 Conan 缓存中，可供此计算机上的任何项目使用。可以通过以下命令查看它们
```bash
# list all the binaries built for the hello/1.0 package in the cache
$ conan list "hello/1.0:*"
Local Cache
  hello
    hello/1.0
      revisions
        dcbfe21e5250264b26595d151796be70 (2024-05-10 09:40:15 UTC)
          packages
            2505f7ebb5a4cca156b2d6b8534f415a4a48b5c9
              info
                settings
                  arch: armv8
                  build_type: Release
                  compiler: apple-clang
                  compiler.cppstd: gnu17
                  compiler.libcxx: libc++
                  compiler.version: 15
                  os: Macos
                options
                  shared: True
            39f48664f195e0847f59889d8a4cdfc6bca84bf1
              info
                settings
                  arch: armv8
                  build_type: Release
                  compiler: apple-clang
                  compiler.cppstd: gnu17
                  compiler.libcxx: libc++
                  compiler.version: 15
                  os: Macos
                options
                  fPIC: True
                  shared: False
            814ddaac84bc84f3595aa076660133b88e49fb11
              info
                settings
                  arch: armv8
                  build_type: Debug
                  compiler: apple-clang
                  compiler.cppstd: gnu17
                  compiler.libcxx: libc++
                  compiler.version: 15
                  os: Macos
                options
                  fPIC: True
                  shared: False
```
现在已经创建了简单的 Conan 包，接下来将更详细地解释 Conanfile 的每个方法。您将学习如何修改这些方法来实现从外部仓库获取源代码、向我们的包添加依赖项、自定义工具链等等。
## 关于 Conan 缓存的注意事项

当您执行 `conan create` 命令时，您的包构建并非发生在您的本地文件夹中，而是在 Conan 缓存内的另一个文件夹中。此缓存位于用户主文件夹下的 `.conan2` 文件夹中。Conan 将使用 `~/.conan2` 文件夹存储构建好的包以及不同的配置文件。您已经使用过 `conan list` 命令来列出存储在本地缓存中的 `recipes` 和 `binaries`。

重要提示：Conan 缓存是 Conan 客户端私有的 - 修改、添加、删除或更改 Conan 缓存内的文件是未定义行为，很可能导致损坏。