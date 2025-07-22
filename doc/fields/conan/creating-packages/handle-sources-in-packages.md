# 处理包中的源代码

在[上一节的教程](https://docs.conan.io/2/tutorial/creating_packages/create_your_first_package.html#creating-packages-create-your-first-conan-package)中，为“Hello World” C++库创建了 Conan 包。使用 `Conanfile` 的 `exports_sources` 属性来声明库的源代码位置。当源文件与 `Conanfile` 位于同一文件夹时，这是定义源文件位置的最简单方法。然而，有时源文件存储在远程仓库或远程服务器上的文件中，而不是与 `Conanfile` 位于同一位置。在本节中，将通过添加 `source()` 方法来修改之前创建的配方，并解释如何：

- 从远程仓库中存储的 zip 文件中获取源代码。
- 从 git 仓库的分支中获取源代码。

请首先克隆源代码以重新创建此项目。你可以在 GitHub 上的 examples2 存储库中找到它们：
```bash
git clone https://github.com/conan-io/examples2.git
cd examples2/tutorial/creating_packages/handle_sources
```

项目的结构与前一个示例相同，但省略了库源代码：
```bash
.
├── CMakeLists.txt
├── conanfile.py
└── test_package
    ├── CMakeLists.txt
    ├── conanfile.py
    └── src
        └── example.cpp
```

从远程仓库中的 zip 文件获取源代码

看看 `conanfile.py` 中的变化：

```python
from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.tools.files import get


class helloRecipe(ConanFile):
    name = "hello"
    version = "1.0"

    ...

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    def source(self):
        # Please, be aware that using the head of the branch instead of an immutable tag
        # or commit is a bad practice and not allowed by Conan
        get(self, "https://github.com/conan-io/libhello/archive/refs/heads/main.zip",
                  strip_root=True)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        cmake_layout(self)

    def generate(self):
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

如您所见，配方相同，但不再像之前那样声明 `exports_sources` 属性，即

```python
exports_sources = "CMakeLists.txt", "src/*", "include/*"
```

用这些信息声明 `source()` 方法：

```python
def source(self):
    # Please, be aware that using the head of the branch instead of an immutable tag
    # or commit is strongly discouraged, unsupported by Conan and likely to cause issues
    get(self, "https://github.com/conan-io/libhello/archive/refs/heads/main.zip",
              strip_root=True)
```

使用了 [`conan.tools.files.get()`](https://docs.conan.io/2/reference/tools/files/downloads.html#conan-tools-files-get) 工具，它会首先从作为参数传递的 URL 下载 zip 文件，然后解压它。请注意，我们传递了 `strip_root=True` 参数，以便如果所有解压的内容都在一个文件夹中，所有内容都会被移动到父文件夹（有关更多详细信息，请查看 [`conan.tools.files.unzip()`](https://docs.conan.io/2/reference/tools/files/basic.html#conan-tools-files-unzip) 参考）。

```{warning}
预计未来获取源码会产生相同的结果。强烈不建议使用可变源码来源，例如 git 中的移动引用（如 HEAD 分支），或指向可能随时间变化的文件内容的 URL，这也不受支持。不遵循这一做法会导致未定义行为，很可能导致程序中断。
```

zip 文件的内容与之前在 Conan 配方旁边拥有的源代码相同，所以如果你执行 `conan create`，结果将与之前相同。

```{code-block} bash
:emphasize-lines: 8-13

$ conan create .

...

-------- Installing packages ----------

Installing (downloading, building) binaries...
hello/1.0: Calling source() in /Users/user/.conan2/p/0fcb5ffd11025446/s/.
Downloading update_source.zip

hello/1.0: Unzipping 3.7KB
Unzipping 100 %
hello/1.0: Copying sources to build folder
hello/1.0: Building your package in /Users/user/.conan2/p/tmp/369786d0fb355069/b

...

-------- Testing the package: Running test() ----------
hello/1.0 (test package): Running test()
hello/1.0 (test package): RUN: ./example
hello/1.0: Hello World Release!
hello/1.0: __x86_64__ defined
hello/1.0: __cplusplus199711
hello/1.0: __GNUC__4
hello/1.0: __GNUC_MINOR__2
hello/1.0: __clang_major__13
hello/1.0: __clang_minor__1
hello/1.0: __apple_build_version__13160021
```

请检查带有下载和解压操作消息的高亮行。

## 来自 git 仓库分支的源代码

现在，修改 `source()` 方法，从 git 仓库获取源代码，而不是从 zip 文件获取。只展示相关部分：

```python
...

from conan.tools.scm import Git


class helloRecipe(ConanFile):
    name = "hello"
    version = "1.0"

    ...

    def source(self):
        git = Git(self)
        git.clone(url="https://github.com/conan-io/libhello.git", target=".")

    ...
```

在这里，使用 [`conan.tools.scm.Git()`](https://docs.conan.io/2/reference.html#reference) 工具。Git 类实现了多种方法来与 git 仓库进行交互。在这种情况下调用 `clone()` 方法来克隆 `https://github.com/conan-io/libhello.git` 仓库的默认分支，并使用相同的文件夹来克隆源代码而不是子文件夹（传递 `target="."` 参数）。

```{warning}
如上所述，这只是简单的示例。` Git()` 的 source origin 也必须是不可变的。必须检出不可变的标签或特定的提交来保证正确的行为。使用仓库的 `HEAD` 是不被允许的，并且可能导致未定义的行为和破坏。
```

要在仓库中检出提交或标签，使用 Git 工具的 `checkout()` 方法：

```python
def source(self):
    git = Git(self)
    git.clone(url="https://github.com/conan-io/libhello.git", target=".")
    git.checkout("<tag> or <commit hash>")
```

关于 Git 类方法的更多信息，请查阅 `conan.tools.scm.Git()` 的[参考文档](https://docs.conan.io/2/reference.html#reference)。

请注意，也可以通过调用 `self.run()` 方法来运行其他命令。

## 使用 `conandata.yml` 文件

可以在与 `conanfile.py` 相同的文件夹中编写名为 `conandata.yml` 的文件。这个文件将被 Conan 自动导出并解析，可以从配方中读取这些信息。例如，这很方便用来提取外部源存储库的 URL、zip 文件等。这是 `conandata.yml` 的示例：

```yaml
sources:
  "1.0":
    url: "https://github.com/conan-io/libhello/archive/refs/heads/main.zip"
    sha256: "7bc71c682895758a996ccf33b70b91611f51252832b01ef3b4675371510ee466"
    strip_root: true
  "1.1":
    url: ...
    sha256: ...
```

这个配方不需要为代码的每个版本进行修改。可以将指定版本的 `keys` （ `url` 、 `sha256` 和 `strip_root` ）作为参数传递给 `get` 函数，这个函数在这种情况下允许我们验证下载的 zip 文件是否具有正确的 `sha256` 。因此，可以将源方法修改为这样：

```python
def source(self):
    get(self, **self.conan_data["sources"][self.version])
    # Equivalent to:
    # data = self.conan_data["sources"][self.version]
    # get(self, data["url"], sha256=data["sha256"], strip_root=data["strip_root"])
```
