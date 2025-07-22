# 包开发流程

本节介绍了 Conan 本地开发流程，该流程允许您直接在本地项目目录中处理包，而无需先将包内容导出到 Conan 缓存中。

这种本地工作流程鼓励用户在其配方相关的本地子目录中尝试错误，这与开发人员通常使用其他构建工具测试构建其项目的方式类似。该策略是在此阶段单独测试 `conanfile.py` 方法。

使用[creating_packages](https://docs.conan.io/2/tutorial/creating_packages.html#tutorial-creating-packages)中创建的 hello 包来使用这个流程。

请克隆源代码以重新创建此项目。您可以在 GitHub 上的 examples2.0 存储库中找到它们：
```bash
git clone https://github.com/conan-io/examples2.git
cd examples2/tutorial/developing_packages/local_package_development_flow
```

检查该文件夹的内容：

```bash
.
├── conanfile.py
└── test_package
    ├── CMakeLists.txt
    ├── conanfile.py
    └── src
        └── example.cpp
```

## `conan source`

通常情况下，你需要从 `conan source` 命令开始。这里的策略是隔离测试你的源方法，并将文件下载到相对于 `conanfile.py` 的临时子文件夹中。这个相对文件夹由 `self.folders.source` 方法中的 `layout()` 属性定义。在这种情况下，由于使用的是预定义的 `cmake_layout`，可通过 `src_folder` 参数设置该值。

```{caution}
在这个例子中，从远程仓库打包第三方库。如果你在同一个仓库中与配方一起存放你的源代码，大多数情况下运行 `conan source` 是不必要的。
```

看看配方的 `source()` 和 `layout()` 方法：
```python
...

def source(self):
    # Please be aware that using the head of the branch instead of an immutable tag
    # or commit is not a good practice in general.
    get(self, "https://github.com/conan-io/libhello/archive/refs/heads/main.zip",
        strip_root=True)

def layout(self):
    cmake_layout(self, src_folder="src")

...
```

运行 `conan source` 命令并检查结果：
```bash
$ conan source .
conanfile.py (hello/1.0): Calling source() in /Users/.../local_package_development_flow/src
Downloading main.zip
conanfile.py (hello/1.0): Unzipping 3.7KB
Unzipping 100%
```

你可以看到出现了新的 `src` 文件夹，其中包含所有 `hello` 库的源代码。

```{code-block} bash
:emphasize-lines: 3-10

.
├── conanfile.py
├── src
│   ├── CMakeLists.txt
│   ├── LICENSE
│   ├── README.md
│   ├── include
│   │   └── hello.h
│   └── src
│       └── hello.cpp
└── test_package
    ├── CMakeLists.txt
    ├── conanfile.py
    └── src
        └── example.cpp
```

现在可以方便地检查源代码并验证它们。一旦你的源代码方法正确，并且包含你期望的文件，你就可以继续测试与下载依赖相关的各种属性和方法。

## `conan install`

运行 `conan source` 命令后，可以运行 `conan install` 命令。该命令将在需要时安装所有配方要求，并通过运行 `generate()` 方法准备所有构建所需的文件。

可以检查配方中参与此步骤的所有部分：

```python
...

class helloRecipe(ConanFile):

    ...

    generators = "CMakeDeps"

    ...

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    ...
```

现在运行 `conan install` 命令并检查结果：
```bash
$ conan install .
...
-------- Finalizing install (deploy, generators) --------
conanfile.py (hello/1.0): Writing generators to ...
conanfile.py (hello/1.0): Generator 'CMakeDeps' calling 'generate()'
conanfile.py (hello/1.0): Calling generate()
...
conanfile.py (hello/1.0): Generating aggregated env files
```

你可以看到出现了新的构建文件夹，里面包含了 Conan 构建库所需的所有文件，比如 CMake 的工具链和几个环境配置文件。

```{code-block} bash
:emphasize-lines: 3-10

.
├── build
│   └── Release
│       └── generators
│           ├── CMakePresets.json
│           ├── cmakedeps_macros.cmake
│           ├── conan_toolchain.cmake
│           ├── conanbuild.sh
│           ├── conanbuildenv-release-x86_64.sh
│           ├── conanrun.sh
│           ├── conanrunenv-release-x86_64.sh
│           ├── deactivate_conanbuild.sh
│           └── deactivate_conanrun.sh
├── conanfile.py
├── src
│   ├── CMakeLists.txt
│   ├── CMakeUserPresets.json
│   ├── LICENSE
│   ├── README.md
│   ├── include
│   │   └── hello.h
│   └── src
│       └── hello.cpp
└── test_package
    ├── CMakeLists.txt
    ├── conanfile.py
    └── src
        └── example.cpp
```

现在所有构建所需的文件都已生成，您可以继续测试 `build()` 方法。

## `conan build`

运行 `conan build` 命令将调用 `build()` 方法：
```python
...

class helloRecipe(ConanFile):

    ...

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    ...
```

运行 `conan build`:
```bash
$ conan build .
...
-- Conan toolchain: C++ Standard 11 with extensions ON
-- Conan toolchain: Setting BUILD_SHARED_LIBS = OFF
-- Configuring done
-- Generating done
-- Build files have been ...
conanfile.py (hello/1.0): CMake command: cmake --build ...
conanfile.py (hello/1.0): RUN: cmake --build ...
[100%] Built target hello
```

对于大多数配方， `build()` 方法应该非常简单，你也可以直接调用构建系统，而无需调用 Conan，因为你已经拥有所有构建所需的文件。如果你检查 `src` 文件夹的内容，你会发现 `CMakeUserPresets.json` 文件，你可以使用它来配置和构建 `conan-release` 预设。试试看：
```bash
$ cd src
$ cmake --preset conan-release
...
-- Configuring done
-- Generating done

$ cmake --build --preset conan-release
...
[100%] Built target hello
```

你可以检查直接调用 CMake 的结果与使用 `conan build` 命令得到的结果是相同的。

````{note}
本例中使用 CMake 预设。这需要 `CMake >= 3.23`，因为从 `CMakeUserPresets.json` 到 `CMakePresets.json` 的“include”功能只从该版本开始支持。如果你不想使用预设，可以使用类似：
```bash
cmake <path> -G <CMake generator> -DCMAKE_TOOLCHAIN_FILE=<path to
conan_toolchain.cmake> -DCMAKE_BUILD_TYPE=Release
```
如果你无法使用预设功能，Conan 每次运行 `conan install` 时都会显示确切的 CMake 命令。
````

## `conan export-pkg`

现在已经本地构建了包二进制文件，也可以使用 `conan export-pkg` 命令将这些工件打包到 Conan 本地缓存中。请注意，此命令将在 Conan 缓存中创建包，并在运行 `test_package` 后进行测试。

```bash
$ conan export-pkg .
conanfile.py (hello/1.0) package(): Packaged 1 '.h' file: hello.h
conanfile.py (hello/1.0) package(): Packaged 1 '.a' file: libhello.a
conanfile.py (hello/1.0): Package 'b1d267f77ddd5d10d06d2ecf5a6bc433fbb7eeed' created
conanfile.py (hello/1.0): Created package revision f09ef573c22f3919ba26ee91ae444eaa
...
conanfile.py (hello/1.0): Package folder /Users/...
conanfile.py (hello/1.0): Exported package binary
...
[ 50%] Building CXX object CMakeFiles/example.dir/src/example.cpp.o
[100%] Linking CXX executable example
[100%] Built target example

-------- Testing the package: Running test() --------
hello/1.0 (test package): Running test()
hello/1.0 (test package): RUN: ./example
hello/1.0: Hello World Release!
hello/1.0: __x86_64__ defined
hello/1.0: __cplusplus201103
hello/1.0: __GNUC__4
hello/1.0: __GNUC_MINOR__2
hello/1.0: __clang_major__14
hello/1.0: __apple_build_version__14000029
```

现在您可以列出本地缓存中的包，并检查 `hello/1.0` 包是否已创建：

```bash
$ conan list hello/1.0
Local Cache
  hello
    hello/1.0
```

