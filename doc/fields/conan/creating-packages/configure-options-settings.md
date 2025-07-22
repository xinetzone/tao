# 在配方中配置设置和选项

已经解释了 [Conan 设置和选项](https://docs.conan.io/2/tutorial/consuming_packages/different_configurations.html#settings-and-options-difference)，以及如何使用它们来为不同的配置（如 Debug、Release、静态或共享库等）构建你的项目。在本节中，解释在某个设置或选项不适用于 Conan 包时如何配置这些设置和选项。简要介绍 Conan 如何处理二进制兼容性，以及这与选项和设置的关系。

请首先克隆源代码以重新创建此项目。你可以在 GitHub 上的 examples2 存储库中找到它们：

```bash
git clone https://github.com/conan-io/examples2.git
cd examples2/tutorial/creating_packages/configure_options_settings
```

你会注意到 conanfile.py 文件有一些变化。检查相关部分：

```{code-block} python
:linenos:
:emphasize-lines: 23

class helloRecipe(ConanFile):
    name = "hello"
    version = "1.0"

    ...
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "with_fmt": [True, False]}

    default_options = {"shared": False,
                       "fPIC": True,
                       "with_fmt": True}
    ...

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            # If os=Windows, fPIC will have been removed in config_options()
            # use rm_safe to avoid double delete errors
            self.options.rm_safe("fPIC")
    ...
```

在配方中添加了 [`configure()`](https://docs.conan.io/2/reference/conanfile/methods/configure.html#reference-conanfile-methods-configure) 方法。接下来解释这个方法的目标是什么，以及它与配方中已经定义的 `config_options()` 方法有何不同：
- `configure()`：使用此方法来配置配方的哪些选项或设置是可用的。例如，在这个例子中，删除了 `fPIC` 选项，因为它只有在作为共享库构建时才应为 `True`（实际上，一些构建系统在构建共享库时会自动添加这个标志）。
- `config_options()`：此方法用于在选项取值之前约束包中的可用选项。如果在方法内部删除了某个设置或选项并为其分配了值，Conan 将引发错误。在这个例子中，在 Windows 上删除了 `fPIC` 选项，因为该选项在该操作系统上不存在。请注意，此方法在 `configure()` 方法之前执行。

小心使用 `config_options()` 方法删除选项与使用 `configure()` 方法删除选项的结果不同。在 `config_options()` 中删除选项相当于我们在配方中从未声明过它，这将引发一个异常，提示选项不存在。然而，如果使用 `configure()` 方法删除它，可以传递该选项，但它将没有任何效果。例如，如果你尝试在 Windows 上向 `fPIC` 选项传递值，Conan 将触发异常，提示选项不存在：
::::{card} Windows
^^^
```
$ conan create . --build=missing -o fPIC=True
...
-------- Computing dependency graph --------
ERROR: option 'fPIC' doesn't exist
Possible options are ['shared', 'with_fmt']
```
+++
::::

如你所见，`configure()` 和 `config_options()` 方法在满足特定条件时会删除选项。让我们解释一下我们为什么要这样做以及移除该选项的影响。这与 Conan 如何识别与配置文件中设置的配置二进制兼容的包有关。在下一节中，将介绍 Conan 包 ID 的概念。

## Conan 包的二进制兼容性：包 ID 

在之前的示例中，使用 Conan 为不同的配置（如 Debug 和 Release）进行构建。每次你为这些配置之一创建包时，Conan 都会构建一个新的二进制文件。每个二进制文件都与一个生成的哈希值相关，称为包 ID。包 ID 只是将一组设置、选项和包的需求信息转换为唯一标识符的一种方式。

为 Release 和 Debug 配置构建我们的包，并检查生成的二进制文件的包 ID。

```{code-block} bash
:linenos:
:emphasize-lines: 6,19,29,42

$ conan create . --build=missing -s build_type=Release -tf="" # -tf="" will skip building the test_package
...
[ 50%] Building CXX object CMakeFiles/hello.dir/src/hello.cpp.o
[100%] Linking CXX static library libhello.a
[100%] Built target hello
hello/1.0: Package '738feca714b7251063cc51448da0cf4811424e7c' built
hello/1.0: Build folder /Users/user/.conan2/p/tmp/7fe7f5af0ef27552/b/build/Release
hello/1.0: Generated conaninfo.txt
hello/1.0: Generating the package
hello/1.0: Temporary package folder /Users/user/.conan2/p/tmp/7fe7f5af0ef27552/p
hello/1.0: Calling package()
hello/1.0: CMake command: cmake --install "/Users/user/.conan2/p/tmp/7fe7f5af0ef27552/b/build/Release" --prefix "/Users/user/.conan2/p/tmp/7fe7f5af0ef27552/p"
hello/1.0: RUN: cmake --install "/Users/user/.conan2/p/tmp/7fe7f5af0ef27552/b/build/Release" --prefix "/Users/user/.conan2/p/tmp/7fe7f5af0ef27552/p"
-- Install configuration: "Release"
-- Installing: /Users/user/.conan2/p/tmp/7fe7f5af0ef27552/p/lib/libhello.a
-- Installing: /Users/user/.conan2/p/tmp/7fe7f5af0ef27552/p/include/hello.h
hello/1.0 package(): Packaged 1 '.h' file: hello.h
hello/1.0 package(): Packaged 1 '.a' file: libhello.a
hello/1.0: Package '738feca714b7251063cc51448da0cf4811424e7c' created
hello/1.0: Created package revision 3bd9faedc711cbb4fdf10b295268246e
hello/1.0: Full package reference: hello/1.0#e6b11fb0cb64e3777f8d62f4543cd6b3:738feca714b7251063cc51448da0cf4811424e7c#3bd9faedc711cbb4fdf10b295268246e
hello/1.0: Package folder /Users/user/.conan2/p/5c497cbb5421cbda/p

$ conan create . --build=missing -s build_type=Debug -tf="" # -tf="" will skip building the test_package
...
[ 50%] Building CXX object CMakeFiles/hello.dir/src/hello.cpp.o
[100%] Linking CXX static library libhello.a
[100%] Built target hello
hello/1.0: Package '3d27635e4dd04a258d180fe03cfa07ae1186a828' built
hello/1.0: Build folder /Users/user/.conan2/p/tmp/19a2e552db727a2b/b/build/Debug
hello/1.0: Generated conaninfo.txt
hello/1.0: Generating the package
hello/1.0: Temporary package folder /Users/user/.conan2/p/tmp/19a2e552db727a2b/p
hello/1.0: Calling package()
hello/1.0: CMake command: cmake --install "/Users/user/.conan2/p/tmp/19a2e552db727a2b/b/build/Debug" --prefix "/Users/user/.conan2/p/tmp/19a2e552db727a2b/p"
hello/1.0: RUN: cmake --install "/Users/user/.conan2/p/tmp/19a2e552db727a2b/b/build/Debug" --prefix "/Users/user/.conan2/p/tmp/19a2e552db727a2b/p"
-- Install configuration: "Debug"
-- Installing: /Users/user/.conan2/p/tmp/19a2e552db727a2b/p/lib/libhello.a
-- Installing: /Users/user/.conan2/p/tmp/19a2e552db727a2b/p/include/hello.h
hello/1.0 package(): Packaged 1 '.h' file: hello.h
hello/1.0 package(): Packaged 1 '.a' file: libhello.a
hello/1.0: Package '3d27635e4dd04a258d180fe03cfa07ae1186a828' created
hello/1.0: Created package revision 67b887a0805c2a535b58be404529c1fe
hello/1.0: Full package reference: hello/1.0#e6b11fb0cb64e3777f8d62f4543cd6b3:3d27635e4dd04a258d180fe03cfa07ae1186a828#67b887a0805c2a535b58be404529c1fe
hello/1.0: Package folder /Users/user/.conan2/p/c7796386fcad5369/p
```

如您所见，Conan 生成了两个包 ID：

- 用于发布的包 `738feca714b7251063cc51448da0cf4811424e7c`
- 用于调试的包 `3d27635e4dd04a258d180fe03cfa07ae1186a828`

这两个包 ID 是通过将设置集、选项以及一些关于需求的信息（我们将在文档中稍后解释）进行哈希计算得出的。因此，例如在本例中，它们是下图所示信息的计算结果。

![](https://docs.conan.io/2/_images/conan-package_id.png)

这些包 ID 不同是因为 `build_type` 不同。现在，当你想要安装一个包时，Conan 会：

- 收集应用的设置和选项，以及关于需求的一些信息，并计算对应包 ID 的哈希值。
- 如果该包 ID 与本地 Conan 缓存中存储的某个包匹配，Conan 将使用该包。如果没有匹配，且我们已配置任何 Conan 远程仓库，它将在远程仓库中搜索具有该包 ID 的包。
- 如果计算出的包 ID 既不存在于本地缓存中也不存在于远程仓库中，Conan 将因“缺失二进制文件”错误消息而失败，或者将尝试从源代码构建该包（这取决于 `--build` 参数的值）。这次构建将在本地缓存中生成新的包 ID。

这些步骤已简化，包 ID 的计算远比我们在此解释的复杂得多。配方本身甚至可以调整其包 ID 的计算方式，我们可以有不同版本的配方和包，而且 Conan 中还有一个内置机制，可以配置为声明具有特定包 ID 的某些包彼此兼容。

也许你现在已经直觉到为什么我们在 Conan 配方中删除设置或选项。如果你这样做，这些值将不会包含在包 ID 的计算中，所以即使你定义了它们，生成的包 ID 也会相同。你可以检查这种行为，例如，当我们使用选项 `shared=True` 构建时删除的 `fPIC` 选项。无论你为 `fPIC` 选项传递什么值，对于 `hello/1.0` 二进制文件生成的包 ID 都会相同：

`````{tab-set}
````{tab-item} Windows
```bash
conan create . --build=missing -o shared=True -o fPIC=True -tf=""
```
````
````{tab-item} Linux, macOS
```bash
conan create . --build=missing -o shared=True -o -tf=""
```
````
`````

```bash
...
hello/1.0 package(): Packaged 1 '.h' file: hello.h
hello/1.0 package(): Packaged 1 '.dylib' file: libhello.dylib
hello/1.0: Package '2a899fd0da3125064bf9328b8db681cd82899d56' created
hello/1.0: Created package revision f0d1385f4f90ae465341c15740552d7e
hello/1.0: Full package reference: hello/1.0#e6b11fb0cb64e3777f8d62f4543cd6b3:2a899fd0da3125064bf9328b8db681cd82899d56#f0d1385f4f90ae465341c15740552d7e
hello/1.0: Package folder /Users/user/.conan2/p/8a55286c6595f662/p

$ conan create . --build=missing -o shared=True -o fPIC=False -tf=""
...
-------- Computing dependency graph --------
Graph root
    virtual
Requirements
    fmt/8.1.1#601209640bd378c906638a8de90070f7 - Cache
    hello/1.0#e6b11fb0cb64e3777f8d62f4543cd6b3 - Cache

-------- Computing necessary packages --------
Requirements
    fmt/8.1.1#601209640bd378c906638a8de90070f7:d1b3f3666400710fec06446a697f9eeddd1235aa#24a2edf207deeed4151bd87bca4af51c - Skip
    hello/1.0#e6b11fb0cb64e3777f8d62f4543cd6b3:2a899fd0da3125064bf9328b8db681cd82899d56#f0d1385f4f90ae465341c15740552d7e - Cache

-------- Installing packages --------

-------- Installing (downloading, building) binaries... --------
hello/1.0: Already installed!
```

如您所见，第一次运行创建了 `2a899fd0da3125064bf9328b8db681cd82899d56` 包，而第二次运行，无论 fPIC 选项的值如何不同，都表示我们已经安装了 `2a899fd0da3125064bf9328b8db681cd82899d56` 包。

##  C 库

还有其他典型情况，你可能需要删除某些设置。假设你在打包 C 库。当你构建这个库时，存在一些设置，如编译器 C++ 标准（ `self.settings.compiler.cppstd` ）或使用的标准库（ `self.settings.compiler.libcxx` ），这些设置完全不会影响生成的二进制文件。因此，让它们影响包 ID 的计算是没有意义的，所以典型模式是在 `configure()` 方法中删除它们：

```python
def configure(self):
    self.settings.rm_safe("compiler.cppstd")
    self.settings.rm_safe("compiler.libcxx")
```

请注意，在 `configure()` 方法中删除这些设置不仅会修改包 ID 的计算方式，还会影响工具链和构建系统集成的行为，因为 C++ 设置将不存在。

```{note}
从 Conan 2.4 版本开始，如果定义了 `languages = "C"` 配方属性，则无需上述 `configure()` （实验性功能）。
```

## 仅包含头文件的库

对于打包[仅包含头文件的库的包](https://docs.conan.io/2/tutorial/creating_packages/other_types_of_packages/header_only_packages.html#creating-packages-other-header-only)，情况类似。在这种情况下，不需要链接任何二进制代码，只需将一些头文件添加到项目中。因此，Conan 包的包 ID 不应受设置或选项的影响。为此，有一种更简单的方法来声明生成的包 ID 不应考虑设置、选项或来自需求的信息：在另一个名为 `package_id()` 的配方方法内部调用 `self.info.clear()` 方法。

```python
def package_id(self):
    self.info.clear()
```

将稍后解释 `package_id()` 方法，并说明您如何自定义计算包 ID 的方式。如果您想详细了解此方法的工作原理，也可以查看 [Conanfile 的方法参考](https://docs.conan.io/2/reference/conanfile/methods.html#reference-conanfile-methods)。