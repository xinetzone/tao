# 在 `tool_requires` 中透明地使用 cmake 模块

当想要重用位于另一个 Conan 包内的 `.cmake` 脚本时，有几种可能的场景，例如如果 `.cmake` 脚本位于常规的 `requires` 或 `tool_requires` 中。

此外，还可能想要采用两种不同的方法：

- 脚本的使用者可以在他们的 `CMakeLists.txt` 中进行显式的 `include(MyScript)`。这种方法非常明确，设置起来也更简单，只需在配方中定义 `self.cpp_info.builddirs` ，具有 `CMakeToolchain` 的使用者将自动能够进行 `include()` 并使用该功能。这里有[示例](https://docs.conan.io/2/examples/graph/requires/consume_cmake_macro.html#consume-cmake-macro)。
- 消费者希望在执行 `find_package()` 时自动加载 `cmake` 模块依赖。当前示例实现了这种情况。

假设有一个包，打算用作 `tool_require` ，其 recipe 如下：

```{code-block} python
:caption: myfunctions/conanfile.py

import os
from conan import ConanFile
from conan.tools.files import copy

class Conan(ConanFile):
    name = "myfunctions"
    version = "1.0"
    exports_sources = ["*.cmake"]

    def package(self):
        copy(self, "*.cmake", self.source_folder, self.package_folder)

    def package_info(self):
        self.cpp_info.set_property("cmake_build_modules", ["myfunction.cmake"])
```

以及位于 `myfunction.cmake` 文件：

```{code-block} cmake
:caption: myfunctions/myfunction.cmake

function(myfunction)
    message("Hello myfunction!!!!")
endfunction()
```

可以执行 `cd myfunctions && conan create .` ，这将创建包含 `cmake` 脚本的 `myfunctions/1.0` 包。

然后，消费者包将如下所示：

```{code-block} python
:caption: consumer/conanfile.py

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain

class Conan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    tool_requires = "myfunctions/1.0"

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

        deps = CMakeDeps(self)
        # By default 'myfunctions-config.cmake' is not created for tool_requires
        # we need to explicitly activate it
        deps.build_context_activated = ["myfunctions"]
        # and we need to tell to automatically load 'myfunctions' modules
        deps.build_context_build_modules = ["myfunctions"]
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
```

`CMakeLists.txt`：

```{code-block} cmake
:caption: consumer/CMakeLists.txt

cmake_minimum_required(VERSION 3.0)
project(test)
find_package(myfunctions CONFIG REQUIRED)
myfunction()
```

然后，消费者将能够从依赖模块中自动调用 `myfunction()`：

```bash
$ conan build .
...
Hello myfunction!!!!
```

如果由于某种原因消费者想要强制将 `tool_requires()` 作为 CMake 模块使用，消费者可以执行 `deps.set_property("myfunctions", "cmake_find_mode", "module", build_context=True)` ，然后 `find_package(myfunctions MODULE REQUIRED)` 将会起作用。
