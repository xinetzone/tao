# 定义 Conan 包中提供多个库的组件

在教程中关于 [`package_info()` 方法的章节](https://docs.conan.io/2/tutorial/creating_packages/define_package_information.html#tutorial-creating-define-package-info) 里，学习了如何为消费者定义包中的信息，例如库名称或包含和库文件夹。在教程中，创建了只有一个库的包，消费者链接到这个库。然而，在某些情况下，库将其功能分离成不同的组件。这些组件可以独立使用，并且在某些情况下，它们可能需要同一库或其他库的组件。例如，考虑像 OpenSSL 这样的库，它提供 `libcrypto` 和 `libssl`，其中 `libssl` 依赖于 `libcrypto`。

Conan 通过使用 CppInfo 对象的 `components` 属性提供了一种抽象信息的方法，用于定义 Conan 包中每个独立组件的信息。消费者可以选择链接特定的组件，而不是包的其余部分。

以游戏引擎库为例，它提供多个组件，如算法、人工智能、渲染和网络。人工智能和渲染都依赖于算法组件。

请首先克隆源代码以重新创建此项目。你可以在 GitHub 的 examples2 仓库中找到它们：
```bash
$ git clone https://github.com/conan-io/examples2.git
$ cd examples2/examples/conanfile/package_info/components
```

你可以检查项目的具体内容：
```bash
.
├── CMakeLists.txt
├── conanfile.py
├── include
│   ├── ai.h
│   ├── algorithms.h
│   ├── network.h
│   └── rendering.h
├── src
│   ├── ai.cpp
│   ├── algorithms.cpp
│   ├── network.cpp
│   └── rendering.cpp
└── test_package
    ├── CMakeLists.txt
    ├── CMakeUserPresets.json
    ├── conanfile.py
    └── src
        └── example.cpp
```

如你所见，每个组件都有对应的源代码，并且有 `CMakeLists.txt` 文件用于构建它们。还有 `test_package`，将用它来测试游戏引擎包中各个组件的调用。

首先，看看 `conanfile.py` 中的 `package_info()` 方法，以及如何声明要提供给游戏引擎包消费者的每个组件的信息：

```python
...

def package_info(self):
    self.cpp_info.components["algorithms"].libs = ["algorithms"]
    self.cpp_info.components["algorithms"].set_property("cmake_target_name", "algorithms")

    self.cpp_info.components["network"].libs = ["network"]
    self.cpp_info.components["network"].set_property("cmake_target_name", "network")

    self.cpp_info.components["ai"].libs = ["ai"]
    self.cpp_info.components["ai"].requires = ["algorithms"]
    self.cpp_info.components["ai"].set_property("cmake_target_name", "ai")

    self.cpp_info.components["rendering"].libs = ["rendering"]
    self.cpp_info.components["rendering"].requires = ["algorithms"]
    self.cpp_info.components["rendering"].set_property("cmake_target_name", "rendering")
```

有几个相关事项：

- 通过在 `cpp_info.components` 属性中设置信息来声明每个组件生成的库。你可以像为 `self.cpp_info` 对象设置信息一样为每个组件设置相同的信息。组件的 `cpp_info` 有一些默认定义，就像 [`self.cpp_info`](https://docs.conan.io/2/tutorial/creating_packages/define_package_information.html#tutorial-creating-define-package-info) 一样。例如， `cpp_info.components` 对象提供了 `.includedirs` 和 `.libdirs` 属性来定义这些位置，但 Conan 默认将它们的值设置为 `["lib"]` 和 `["include"]` ，因此在这种情况下无需添加它们。
- 还在使用 `.requires` 属性声明组件的依赖关系。通过这个属性，你可以在组件级别声明需求，不仅限于同一配方中的组件，也包括作为 Conan 包依赖声明的其他包中的组件。
- 使用[属性模型](https://docs.conan.io/2/tutorial/creating_packages/define_package_information.html#tutorial-creating-define-package-info-properties)更改组件的默认目标名称。默认情况下，Conan 为组件设置目标名称，如 `<package_name::component_name>` ，但对于本教程，将仅使用组件名称来设置组件目标名称，省略 `::` 。
- 当 `cpp_info` 具有全局构建信息（例如 `cpp_info.defines` ）时，它不会继承给组件。如果你想要将此信息共享给组件，你需要为每个组件显式设置。

你可以通过检查 `test_package` 文件夹来查看消费者部分。首先是 `conanfile.py`：

```python
...

def generate(self):
    deps = CMakeDeps(self)
    deps.check_components_exist = True
    deps.generate()
```

为 CMakeDeps 设置 `check_components_exist` 属性。这并非必需，只是展示如果你希望消费者在组件不存在时失败，应该如何操作。因此，CMakeLists.txt 文件可以像这样编写：

```cmake
cmake_minimum_required(VERSION 3.15)
project(PackageTest CXX)

find_package(game-engine REQUIRED COMPONENTS algorithms network ai rendering)

add_executable(example src/example.cpp)

target_link_libraries(example algorithms
                              network
                              ai
                              rendering)
```

如果任何组件的目标不存在，那么 `find_package()` 的调用将会失败。

运行这个例子：
```bash
$ conan create .
...
game-engine/1.0: RUN: cmake --build "/Users/barbarian/.conan2/p/t/game-d6e361d329116/b/build/Release" -- -j16
[ 12%] Building CXX object CMakeFiles/algorithms.dir/src/algorithms.cpp.o
[ 25%] Building CXX object CMakeFiles/network.dir/src/network.cpp.o
[ 37%] Linking CXX static library libnetwork.a
[ 50%] Linking CXX static library libalgorithms.a
[ 50%] Built target network
[ 50%] Built target algorithms
[ 62%] Building CXX object CMakeFiles/ai.dir/src/ai.cpp.o
[ 75%] Building CXX object CMakeFiles/rendering.dir/src/rendering.cpp.o
[ 87%] Linking CXX static library libai.a
[100%] Linking CXX static library librendering.a
[100%] Built target ai
[100%] Built target rendering
...

======== Launching test_package ========

...
-- Conan: Component target declared 'algorithms'
-- Conan: Component target declared 'network'
-- Conan: Component target declared 'ai'
-- Conan: Component target declared 'rendering'
...
[ 50%] Building CXX object CMakeFiles/example.dir/src/example.cpp.o
[100%] Linking CXX executable example
[100%] Built target example


======== Testing the package: Executing test ========
game-engine/1.0 (test package): Running test()
game-engine/1.0 (test package): RUN: ./example
I am the algorithms component!
I am the network component!
I am the ai component!
└───> I am the algorithms component!
I am the rendering component!
└───> I am the algorithms component!
```

你可以检查要求不存在的组件会引发错误。将不存在的组件添加到 `find_package()` 调用中：

```cmake
cmake_minimum_required(VERSION 3.15)
project(PackageTest CXX)

find_package(game-engine REQUIRED COMPONENTS nonexistent algorithms network ai rendering)

add_executable(example src/example.cpp)

target_link_libraries(example algorithms
                              network
                              ai
                              rendering)
```

再次测试该软件包：

```bash
$ conan test test_package game-engine/1.0

...

Conan: Component 'nonexistent' NOT found in package 'game-engine'
Call Stack (most recent call first):
CMakeLists.txt:4 (find_package)

-- Configuring incomplete, errors occurred!

...

ERROR: game-engine/1.0 (test package): Error in build() method, line 22
        cmake.configure()
        ConanException: Error 1 while executing
```
