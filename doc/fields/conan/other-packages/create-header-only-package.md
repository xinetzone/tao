# 仅包含头文件的包

在本节中，将学习如何为仅包含头文件的库创建配方。

请首先克隆源代码以重新创建此项目。你可以在 GitHub 上的 examples2 存储库中找到它们：

```bash
git clone https://github.com/conan-io/examples2.git
cd examples2/tutorial/creating_packages/other_packages/header_only
```

仅包含头文件的库仅由头文件组成。这意味着消费者不需要链接任何库，只需包含头文件，因此只需要二进制配置即可用于仅包含头文件的库。

在“[创建 Conan 包](https://docs.conan.io/2/tutorial/creating_packages/create_your_first_package.html#creating-packages-create-your-first-conan-package)”部分，学习了设置的概念，以及如何通过应用不同的 `build_type` （发布/调试）来构建食谱，从而生成新的二进制包。

由于只需要二进制包，因此不需要声明设置属性。仅包含头文件的食谱的基本示例：

```{code-block} python
:caption: conanfile.py

from conan import ConanFile
 from conan.tools.files import copy


 class SumConan(ConanFile):
     name = "sum"
     version = "0.1"
     # No settings/options are necessary, this is header only
     exports_sources = "include/*"
     # We can avoid copying the sources to the build folder in the cache
     no_copy_source = True
     # Important, define the package_type
     package_type = "header-library"

     def package(self):
         # This will also copy the "include" folder
         copy(self, "*.h", self.source_folder, self.package_folder)

     def package_info(self):
         # For header-only packages, libdirs and bindirs are not used
         # so it's necessary to set those as empty.
         self.cpp_info.bindirs = []
         self.cpp_info.libdirs = []
```

请注意，将 `cpp_info.bindirs` 和 `cpp_info.libdirs` 设置为 `[]`，因为仅包含头文件的库没有编译好的库或二进制文件，而它们默认为 `["bin"]` 和 `["lib"]` ，因此需要覆盖这些默认值。

同时请确认已将 [`no_copy_source`](https://docs.conan.io/2/reference/conanfile/attributes.html#conan-conanfile-properties-no-copy-source) 属性设置为 `True`，这样源代码就不会从 `source_folder` 复制到 `build_folder`。这是仅包含头文件的库的典型优化方式，以避免额外的复制操作。

头文件库就是简单的函数，用于求两个数的和：
```{code-block} c++
:caption: include/sum.h

inline int sum(int a, int b){
    return a + b;
}
```

在克隆的项目中的 `examples2/tutorial/creating_packages/other_packages/header_only` 文件夹里包含 `test_package` 文件夹，里面有使用头文件库的应用示例。因此可以运行 `conan create .` 命令来构建包并测试包：

```bash
$ conan create .
...
[ 50%] Building CXX object CMakeFiles/example.dir/src/example.cpp.o
[100%] Linking CXX executable example
[100%] Built target example

-------- Testing the package: Running test() ----------
sum/0.1 (test package): Running test()
sum/0.1 (test package): RUN: ./example
1 + 3 = 4
```

运行 `conan create` 后，会为头文件库创建新的二进制包，可以看到 `test_package` 项目如何正确地使用它。

可以通过运行这个命令来列出创建的二进制包：

```bash
$ conan list "sum/0.1#:*"
Local Cache
  sum
    sum/0.1
      revisions
        c1a714a086933b067bcbf12002fb0780 (2024-05-09 15:28:51 UTC)
          packages
            da39a3ee5e6b4b0d3255bfef95601890afd80709
              info
```

得到具有包 ID `da39a3ee5e6b4b0d3255bfef95601890afd80709` 的包。看看如果我们运行 `conan create` 并指定 `-s build_type=Debug` 会发生什么：

```bash
$ conan create . -s build_type=Debug
$ conan list "sum/0.1#:*"
Local Cache
  sum
    sum/0.1
      revisions
        c1a714a086933b067bcbf12002fb0780 (2024-05-09 15:28:51 UTC)
          packages
            da39a3ee5e6b4b0d3255bfef95601890afd80709
              info
```

即使 `test_package` 可执行文件是针对 Debug 构建的，得到的头文件库的二进制包也是相同的。这是因为在配方中没有指定 `settings` 属性，因此输入设置（ `-s build_type=Debug` ）中的更改不会影响配方，因此生成的二进制包始终是相同的。

## 仅包含头文件的库，带测试

在之前的示例中，看到了为什么仅包含头文件的库的配方不应该声明 `settings` 属性，但有时配方需要它们来构建某些可执行文件，例如用于测试库。尽管如此，仅包含头文件的库的二进制包仍然应该是唯一的，因此将回顾如何实现这一点。

请首先克隆源代码以重新创建此项目。你可以在 GitHub 上的 examples2 存储库中找到它们：

```bash
git clone https://github.com/conan-io/examples2.git
cd examples2/tutorial/creating_packages/other_packages/header_only_gtest
```

有用于求两个数之和的头文件库，但现在有这个配方：

```{code-block} python
:caption: conanfile.py

import os
from conan import ConanFile
from conan.tools.files import copy
from conan.tools.cmake import cmake_layout, CMake


class SumConan(ConanFile):
    name = "sum"
    version = "0.1"
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = "include/*", "test/*"
    no_copy_source = True
    generators = "CMakeToolchain", "CMakeDeps"
    # Important, define the package_type
    package_type = "header-library"

    def requirements(self):
        self.test_requires("gtest/1.11.0")

    def validate(self):
        check_min_cppstd(self, 11)

    def layout(self):
        cmake_layout(self)

    def build(self):
        if not self.conf.get("tools.build:skip_test", default=False):
            cmake = CMake(self)
            cmake.configure(build_script_folder="test")
            cmake.build()
            self.run(os.path.join(self.cpp.build.bindir, "test_sum"))

    def package(self):
        # This will also copy the "include" folder
        copy(self, "*.h", self.source_folder, self.package_folder)

    def package_info(self):
        # For header-only packages, libdirs and bindirs are not used
        # so it's necessary to set those as empty.
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

    def package_id(self):
        self.info.clear()
```

这些是食谱中引入的变更：

- 引入了从 `test_require` 到 `gtest/1.11.0` 的 `test_require` 。`test_require` 类似于常规需求，但它不会传播给消费者，也不会产生冲突。
- `gtest` 至少需要 C++11 来构建。因此引入了调用 `check_min_cppstd 的 validate()` 方法。
- 由于使用 CMake 构建 `gtest` 示例，使用了生成器 CMakeToolchain 和 CMakeDeps ，并声明 `cmake_layout()` 具有已知的/标准的目录结构。
- 有 `build()` 方法，构建测试，但仅当标准配置 `tools.build:skip_test` 不是 `True` 时。使用该配置作为启用/禁用测试的标准方式。它被像 CMake 这样的辅助工具使用，以在我们在 CMake 中实现测试时跳过 `cmake.test()` 。
- 有 `package_id()` 方法调用 `self.info.clear()`。这是在内部从 `package_id` 计算中移除所有信息（设置、选项、要求），因此只为头文件库生成配置。

可以调用 `conan create` 来构建和测试我们的软件包。

```bash
$ conan create . -s compiler.cppstd=14 --build missing
...
Running main() from /Users/luism/.conan2/p/tmp/9bf83ef65d5ff0d6/b/googletest/src/gtest_main.cc
[==========] Running 1 test from 1 test suite.
[----------] Global test environment set-up.
[----------] 1 test from SumTest
[ RUN      ] SumTest.BasicSum
[       OK ] SumTest.BasicSum (0 ms)
[----------] 1 test from SumTest (0 ms total)

[----------] Global test environment tear-down
[==========] 1 test from 1 test suite ran. (0 ms total)
[  PASSED  ] 1 test.
sum/0.1: Package 'da39a3ee5e6b4b0d3255bfef95601890afd80709' built
...
```

可以再次运行 `conan create` ，指定不同的 `compiler.cppstd` ，构建的软件包将是相同的：

```bash
$ conan create . -s compiler.cppstd=17
...
sum/0.1: RUN: ./test_sum
Running main() from /Users/luism/.conan2/p/tmp/9bf83ef65d5ff0d6/b/googletest/src/gtest_main.cc
[==========] Running 1 test from 1 test suite.
[----------] Global test environment set-up.
[----------] 1 test from SumTest
[ RUN      ] SumTest.BasicSum
[       OK ] SumTest.BasicSum (0 ms)
[----------] 1 test from SumTest (0 ms total)

[----------] Global test environment tear-down
[==========] 1 test from 1 test suite ran. (0 ms total)
[  PASSED  ] 1 test.
sum/0.1: Package 'da39a3ee5e6b4b0d3255bfef95601890afd80709' built
```

```{note}
一旦获得了 `sum/0.1` 二进制包（在服务器上，通过 `conan upload` 后，或在本地缓存中），即使我们没有指定 `os` 、 `arch` 、… 等输入值，也可以安装它。这是 Conan 2.X 的新功能。

    可以使用空配置文件调用 `conan install --require sum/0.1` ，从服务器获取二进制包。但如果丢失了二进制包，需要重新构建包，由于缺少配置，它将失败。
```
