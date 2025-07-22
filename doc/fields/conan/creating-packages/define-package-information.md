# 为消费者定义信息：`package_info()` 方法

在之前的教程部分，解释了如何使用 [package 方法](https://docs.conan.io/2/tutorial/creating_packages/package_method.html#creating-packages-package-method)将库的头文件和二进制文件存储在 Conan 包中。依赖该包的消费者将重用这些文件，但我们必须提供一些附加信息，以便 Conan 可以将其传递给构建系统和消费者，从而使用该包。

例如，在示例中，正在构建名为 `hello` 的静态库，它将在 Linux 和 macOS 上生成 `libhello.a` 文件，或在 Windows 上生成 `hello.lib` 文件。此外，还打包了包含库函数声明的头文件 `hello.h`。在 Conan 本地缓存中，Conan 包最终具有以下结构：

```bash
.
├── include
│   └── hello.h
└── lib
    └── libhello.a
```

然后，想要链接到此库的消费者将需要一些信息：

- Conan 本地缓存中包含 `include` 文件夹的位置，用于搜索 `hello.h` 文件。
- 用于链接的库文件名称（`libhello.a` 或 `hello.lib`）
- Conan 本地缓存中 `lib` 文件夹的位置，用于搜索库文件。

Conan 为所有消费者可能需要在 ConanFile 的 [`cpp_info`](https://docs.conan.io/2/reference/conanfile/methods/package_info.html#conan-conanfile-model-cppinfo) 属性中需要的信息提供了抽象。此属性的信息必须在 [`package_info()` 方法](https://docs.conan.io/2/reference/conanfile/methods/package_info.html#reference-conanfile-methods-package-info)中设置。让我们看看我们的 `hello/1.0` Conan 包的 `package_info()` 方法：

```{code-block} python
:caption: conanfile.py

...

class helloRecipe(ConanFile):
    name = "hello"
    version = "1.0"

    ...

    def package_info(self):
        self.cpp_info.libs = ["hello"]
```

以看到几点：

- 将 `hello` 库添加到 `libs` 的 `cpp_info` 属性中，以告诉消费者应该链接该列表中的库。
- 没有添加关于库和头文件打包的 `lib` 或 `include` 文件夹的信息。`cpp_info` 对象提供了 `.includedirs` 和 `.libdirs` 属性来定义这些位置，但 Conan 默认将它们的值设置为 `lib` 和 `include` ，所以在这种情况下不需要添加这些信息。如果你将包文件复制到不同的位置，那么你必须明确设置这些值。Conan 包中的 `package_info` 方法的声明与此处等效：

```{code-block} python
:caption: conanfile.py

...

class helloRecipe(ConanFile):
    name = "hello"
    version = "1.0"

    ...

    def package_info(self):
        self.cpp_info.libs = ["hello"]
        # conan sets libdirs = ["lib"] and includedirs = ["include"] by default
        self.cpp_info.libdirs = ["lib"]
        self.cpp_info.includedirs = ["include"]
```

## 在 `package_info()` 方法中设置信息

除了我们之前解释的可以在 `package_info()` 方法中设置的信息外，还有一些典型的使用场景：

- 根据设置或选项为消费者定义信息
- 自定义生成器提供给消费者的某些信息，例如 CMake 的目标名称或 `pkg-config` 生成的文件名，例如
- 将配置值传播给消费者
- 传播环境信息给消费者
- 定义 Conan 包的组件，这些组件提供多个库

让我们看看这些组件的实际应用。首先，如果你还没有这样做，请克隆项目源代码。你可以在 GitHub 的 examples2 仓库中找到它们：

```bash
git clone https://github.com/conan-io/examples2.git
cd examples2/tutorial/creating_packages/package_information
```

## 定义消费者依赖的设置或选项的信息

对于本教程的这一部分，在库和配方中引入了一些变化。检查相关部分：

### 库源代码中引入的变更

首先，请注意我们使用了 [`libhello` 库的另一个分支](https://github.com/conan-io/libhello/tree/package_info)。检查库的 `CMakeLists.txt`：

`CMakeLists.txt`：
```{code-block}
cmake_minimum_required(VERSION 3.15)
project(hello CXX)

...

add_library(hello src/hello.cpp)

if (BUILD_SHARED_LIBS)
    set_target_properties(hello PROPERTIES OUTPUT_NAME hello-shared)
else()
    set_target_properties(hello PROPERTIES OUTPUT_NAME hello-static)
endif()

...
```

如您所见，根据是否以静态库（`hello-static`）或共享库（`hello-shared`）的形式构建库来设置库的输出名称。现在看看如何将这些更改转换为 Conan 配方。

### 配方引入的变更

为了根据库的 `CMakeLists.txt` 中的变化更新我们的 recipe，需要在 `package_info()` 方法中根据 `self.options.shared` 选项有条件地设置库名称：

```{code-block} python
:caption: conanfile.py
:linenos:
:emphasize-lines: 9,14-17

class helloRecipe(ConanFile):
    ...

    def source(self):
        git = Git(self)
        git.clone(url="https://github.com/conan-io/libhello.git", target=".")
        # Please, be aware that using the head of the branch instead of an immutable tag
        # or commit is not a good practice in general
        git.checkout("package_info")

    ...

    def package_info(self):
        if self.options.shared:
            self.cpp_info.libs = ["hello-shared"]
        else:
            self.cpp_info.libs = ["hello-static"]
```

现在，使用 `shared=False` （这是默认值，因此无需显式设置）创建 Conan 包，并检查我们是否在打包正确的库（`libhello-static.a` 或 `hello-static.lib`），以及是否在 `test_package` 中链接了正确的库。

```{code-block} bash
:emphasize-lines: 4,14,22
:linenos:

$ conan create . --build=missing
...
-- Install configuration: "Release"
-- Installing: /Users/user/.conan2/p/tmp/a311fcf8a63f3206/p/lib/libhello-static.a
-- Installing: /Users/user/.conan2/p/tmp/a311fcf8a63f3206/p/include/hello.h
hello/1.0 package(): Packaged 1 '.h' file: hello.h
hello/1.0 package(): Packaged 1 '.a' file: libhello-static.a
hello/1.0: Package 'fd7c4113dad406f7d8211b3470c16627b54ff3af' created
...
-- Build files have been written to: /Users/user/.conan2/p/tmp/a311fcf8a63f3206/b/build/Release
hello/1.0: CMake command: cmake --build "/Users/user/.conan2/p/tmp/a311fcf8a63f3206/b/build/Release" -- -j16
hello/1.0: RUN: cmake --build "/Users/user/.conan2/p/tmp/a311fcf8a63f3206/b/build/Release" -- -j16
[ 25%] Building CXX object CMakeFiles/hello.dir/src/hello.cpp.o
[ 50%] Linking CXX static library libhello-static.a
[ 50%] Built target hello
[ 75%] Building CXX object tests/CMakeFiles/test_hello.dir/test.cpp.o
[100%] Linking CXX executable test_hello
[100%] Built target test_hello
hello/1.0: RUN: tests/test_hello
...
[ 50%] Building CXX object CMakeFiles/example.dir/src/example.cpp.o
[100%] Linking CXX executable example
[100%] Built target example

-------- Testing the package: Running test() --------
hello/1.0 (test package): Running test()
hello/1.0 (test package): RUN: ./example
hello/1.0: Hello World Release! (with color!)
```

如您所见，针对该库的测试以及链接到 `libhello-static.a` 库的 Conan `test_package` 都成功了。

## 属性模型：为特定生成器设置信息

[`CppInfo`](https://docs.conan.io/2/reference/conanfile/methods/package_info.html#conan-conanfile-model-cppinfo-attributes) 对象提供了 `set_property` 方法来设置针对每个生成器的特定信息。例如，在这个教程中，使用 [CMakeDeps](https://docs.conan.io/2/reference/tools/cmake/cmakedeps.html#conan-tools-cmakedeps) 生成器来生成 CMake 构建需要我们库的项目所需的信息。CMakeDeps ，默认情况下，会使用与 Conan 包相同的名称来设置库的目标名称。如果你查看 `test_package` 中的那个 `CMakeLists.txt` 文件：

```{code-block} cmake
:caption: test_package CMakeLists.txt
:linenos:
:emphasize-lines: 7

cmake_minimum_required(VERSION 3.15)
project(PackageTest CXX)

find_package(hello CONFIG REQUIRED)

add_executable(example src/example.cpp)
target_link_libraries(example hello::hello)
```

可以看到我们链接的是目标名称 `hello::hello` 。Conan 默认设置这个目标名称，但我们可以通过属性模型来更改它。让我们尝试将其更改为名称 `hello::myhello` 。为此，我们需要在我们的 `hello/1.0` Conan 包的 `package_info` 方法中设置属性 `cmake_target_name` 。

```{code-block} python
:caption: conanfile.py
:linenos:
:emphasize-lines: 10

class helloRecipe(ConanFile):
    ...

    def package_info(self):
        if self.options.shared:
            self.cpp_info.libs = ["hello-shared"]
        else:
            self.cpp_info.libs = ["hello-static"]

        self.cpp_info.set_property("cmake_target_name", "hello::myhello")
```

然后，将 `test_package` 文件夹中的 `CMakeLists.txt` 中我们正在使用的目标名称更改为 `hello::myhello`：

```{code-block} cmake
:caption: test_package CMakeLists.txt
:linenos:
:emphasize-lines: 4

cmake_minimum_required(VERSION 3.15)
project(PackageTest CXX)
# ...
target_link_libraries(example hello::myhello)
```

并重新创建包：

```{code-block} bash
:linenos:
:emphasize-lines: 14

$ conan create . --build=missing
Exporting the recipe
hello/1.0: Exporting package recipe
hello/1.0: Using the exported files summary hash as the recipe revision: 44d78a68b16b25c5e6d7e8884b8f58b8
hello/1.0: A new conanfile.py version was exported
hello/1.0: Folder: /Users/user/.conan2/p/a8cb81b31dc10d96/e
hello/1.0: Exported revision: 44d78a68b16b25c5e6d7e8884b8f58b8
...
-------- Testing the package: Building --------
hello/1.0 (test package): Calling build()
...
-- Detecting CXX compile features
-- Detecting CXX compile features - done
-- Conan: Target declared 'hello::myhello'
...
[100%] Linking CXX executable example
[100%] Built target example

-------- Testing the package: Running test() --------
hello/1.0 (test package): Running test()
hello/1.0 (test package): RUN: ./example
hello/1.0: Hello World Release! (with color!)
```

你可以看到 Conan 现在声明目标为 `hello::myhello` 而不是默认的 `hello::hello` ，并且 test_package 构建成功。

目标名称不是你可以在 CMakeDeps 生成器中设置的唯一属性。要获取影响 CMakeDeps 生成器行为的属性完整列表，请查看[参考文档](https://docs.conan.io/2/reference/tools/cmake/cmakedeps.html#cmakedeps-properties)。

## 将环境或配置信息传播给消费者

你可以向消费者提供环境信息。为此，你可以使用 ConanFile 的 [`runenv_info`](https://docs.conan.io/2/reference/conanfile/attributes.html#conan-conanfile-attributes-runenv-info) 和 [`buildenv_info`](https://docs.conan.io/2/reference/conanfile/attributes.html#conan-conanfile-attributes-buildenv-info) 属性：

- [`runenv_info` 环境](https://docs.conan.io/2/reference/tools/env/environment.html#conan-tools-env-environment-model)对象，定义了使用该软件包的消费者在运行时可能需要的环境信息。
- [`buildenv_info` 环境](https://docs.conan.io/2/reference/tools/env/environment.html#conan-tools-env-environment-model)对象，定义了在使用包时，构建者可能需要的环境信息。

请注意，无需将 `cpp_info.bindirs` 添加到 `PATH` 或将 `cpp_info.libdirs` 添加到 `LD_LIBRARY_PATH` ，这些将由 [`VirtualBuildEnv`](https://docs.conan.io/2/reference/tools/env/virtualbuildenv.html#conan-tools-env-virtualbuildenv) 和 [`VirtualRunEnv`](https://docs.conan.io/2/reference/tools/env/virtualrunenv.html#conan-tools-env-virtualrunenv) 自动添加。

您还可以在 `package_info()` 中定义配置值，以便消费者可以使用这些信息。为此，请设置 `ConanFile` 的 [`conf_info`](https://docs.conan.io/2/reference/conanfile/methods/package_info.html#conan-conanfile-model-conf-info) 属性。

要了解更多关于此用例的信息，请查看[相应的示例](https://docs.conan.io/2/examples/conanfile/package_info/package_info_conf_and_env.html#examples-conanfile-package-info-conf-and-env)。

## 定义 Conan 包中提供多个库的组件

在某些情况下，Conan 包可能提供多个库，对于这些情况，您可以使用 [`CppInfo`](https://docs.conan.io/2/reference/conanfile/methods/package_info.html#conan-conanfile-model-cppinfo-attributes) 对象的 `components` 属性为每个库设置单独的信息。

To know more about this use case, please check the components example in the examples section.
要了解更多关于此用例的信息，请查看示例部分中的 [components 示例]((https://docs.conan.io/2/examples/conanfile/package_info/components.html#examples-conanfile-package-info-components))。
