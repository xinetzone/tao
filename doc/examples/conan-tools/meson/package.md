# 使用 Meson 创建 Conan 包

在"[创建 Conan 包](https://docs.conan.io/2/tutorial/creating_packages/create_your_first_package.html#creating-packages-create-your-first-conan-package)"教程中，CMake 被用作构建系统。如果你还没有阅读那部分内容，请先阅读以熟悉 `conanfile.py` 和 `test_package` 的概念，然后再回来阅读关于 Meson 包创建的特定内容。

使用 `conan new` 命令创建“Hello World” C++ 库示例项目：

```bash
conan new meson_lib -d name=hello -d version=1.0
```

这将创建具有以下结构的 Conan 包项目
```bash
├── conanfile.py
├── meson.build
├── hello.vcxproj
├── src
│   ├── hello.h
│   └── hello.cpp
└── test_package
    ├── conanfile.py
    ├── meson.build
    └── src
        └── example.cpp
```

结构和文件与之前的 CMake 示例非常相似：
- conanfile.py：在根文件夹中有 conanfile.py，它是主要的配方文件，负责定义包的构建和消费方式。
- `meson.build`：Meson 构建脚本。该脚本不需要包含任何 Conan 特定的内容，它对 Conan 完全透明，因为集成是透明的。
- src 文件夹：包含简单的 C++ hello”库的文件夹。
- `test_package` 文件夹：包含一个示例应用程序，该程序将需要并链接到创建的包。在这种情况下， test_package 也包含 meson.build ，但也可以使用其他构建系统（如 CMake）来包含 `test_package`，如果需要的话。`test_package `不一定要使用与包相同的构建系统。

让我们看一下包配方 `conanfile.py` （仅显示相关的新部分）：

```python
exports_sources = "meson.build", "src/*"

def layout(self):
    basic_layout(self)

def generate(self):
    tc = MesonToolchain(self)
    tc.generate()

def build(self):
    meson = Meson(self)
    meson.configure()
    meson.build()

def package(self):
    meson = Meson(self)
    meson.install()
```

简要解释一下配方的不同部分：
- `layout()` 定义了 `basic_layout()` ，这比 CMake 的定义要灵活度低，因此它不允许任何参数化。
- `generate()` 方法调用 `MesonToolchain`，该调用可以生成用于交叉编译的 `conan_meson_native.ini` 和 `conan_meson_cross.ini` Meson 工具链文件。如果项目有与 Conan requires 相关的依赖，也应该添加 `PkgConfigDeps` 。
- `build()` 方法使用 `Meson()` 辅助工具来驱动构建
- `package()` 方法使用 Meson 安装功能来定义并将最终产物复制到包文件夹中。

`test_package` 文件夹还包含 `meson.build` 文件，该文件声明了对测试包的依赖，并链接了应用程序，以验证包是否正确创建并包含该库：

```{code-block} meson
:caption: test_package/meson.build

project('Testhello', 'cpp')
hello = dependency('hello', version : '>=0.1')
executable('example', 'src/example.cpp', dependencies: hello)
```

请注意 `test_package/conanfile.py` 还包含 `generators = "PkgConfigDeps", "MesonToolchain"`，因为 `test_package` 将“hello”包作为依赖，而 `PkgConfigDeps` 是定位它的必要条件。

````{note}
本示例假设系统已安装 Meson、Ninja 和 PkgConfig，但这并不总是成立。如果未安装，您可以使用以下方式创建 `myprofile` 配置文件：
```ini
include(default)

[tool_requires]
meson/[*]
pkgconf/[*]
```
````

在配置文件中添加了 Meson 和 pkg-config 作为工具需求。通过执行 `conan create . -pr=myprofile`，这些工具将被安装并在软件包的构建过程中可用。

使用当前的默认配置从源代码构建包，然后让 `test_package` 文件夹测试该包：

```bash
$ conan create .

...
======== Testing the package: Executing test ========
hello/1.0 (test package): Running test()
hello/1.0 (test package): RUN: .\example
hello/1.0: Hello World Release!
  hello/1.0: _M_X64 defined
  hello/1.0: MSVC runtime: MultiThreadedDLL
  hello/1.0: _MSC_VER1939
  hello/1.0: _MSVC_LANG201402
  hello/1.0: __cplusplus201402
hello/1.0 test_package
```

可以验证配方和包的二进制文件是否在缓存中：

```bash
$ conan list "hello/1.0:*"
Local Cache:
  hello
    hello/1.0
      revisions
        856c535669f78da11502a119b7d8a6c9 (2024-03-04 17:52:39 UTC)
          packages
            c13a22a41ecd72caf9e556f68b406569547e0861
              info
                settings
                  arch: x86_64
                  build_type: Release
                  compiler: msvc
                  compiler.cppstd: 14
                  compiler.runtime: dynamic
                  compiler.runtime_type: Release
                  compiler.version: 193
                  os: Windows
```
