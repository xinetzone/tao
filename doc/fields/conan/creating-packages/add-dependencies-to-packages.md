# 为包添加依赖项

在[之前的教程](https://docs.conan.io/2/tutorial/creating_packages.html#tutorial-creating-packages)部分，为“Hello World”C++库创建了 Conan 包。使用了 [`conan.tools.scm.Git()`](https://docs.conan.io/2/reference.html#reference) 工具从 git 仓库获取源代码。到目前为止，该包还没有对其他 Conan 包的依赖。解释如何像在[消费包](https://docs.conan.io/2/tutorial/consuming_packages/the_flexibility_of_conanfile_py.html#consuming-packages-flexibility-of-conanfile-py)部分一样，非常相似地添加依赖项。将使用 [`fmt`](https://conan.io/center/fmt) 库为“Hello World”库添加一些花哨的彩色输出。

请首先克隆源代码以重新创建此项目。你可以在 GitHub 上的 examples2 存储库中找到它们：

```bash
git clone https://github.com/conan-io/examples2.git
cd examples2/tutorial/creating_packages/add_requires
```

你会注意到 `previous recipe` 中的 `conanfile.py` 文件有一些变化。检查相关部分：

```python
...
from conan.tools.build import check_max_cppstd, check_min_cppstd
...

class helloRecipe(ConanFile):
    name = "hello"
    version = "1.0"

    ...
    generators = "CMakeDeps"
    ...

    def validate(self):
        check_min_cppstd(self, "11")
        check_max_cppstd(self, "20")

    def requirements(self):
        self.requires("fmt/8.1.1")

    def source(self):
        git = Git(self)
        git.clone(url="https://github.com/conan-io/libhello.git", target=".")
        # Please, be aware that using the head of the branch instead of an immutable tag
        # or commit is not a good practice in general
        git.checkout("require_fmt")
```

- 首先，设置 `generators` 类属性，使 Conan 调用 `CMakeDeps` 生成器。在之前的配方中不需要这样做，因为没有依赖项。[`CMakeDeps`](https://docs.conan.io/2/reference/tools/cmake/cmakedeps.html#conan-tools-cmakedeps) 将生成所有 CMake 需要找到 `fmt` 库的配置文件。
- 接下来，使用 [`requires()`](https://docs.conan.io/2/reference/conanfile/methods.html#reference-conanfile-methods) 方法将 [`fmt`](https://conan.io/center/fmt) 依赖项添加到我们的包中。
- 注意在 [`source()`](https://docs.conan.io/2/reference/conanfile/methods.html#reference-conanfile-methods) 方法中添加了一行。使用 `Git().checkout()` 方法在 [`require_fmt`](https://github.com/conan-io/libhello/tree/require_fmt) 分支中检出源代码。这个分支包含了添加到库消息中的源代码更改，以及在 `CMakeLists.txt` 中声明正在使用 `fmt` 库。
- 最后，注意在配方中添加了 [`validate()`](https://docs.conan.io/2/reference/conanfile/methods.html#reference-conanfile-methods) 方法。在[消费包](https://docs.conan.io/2/tutorial/consuming_packages/the_flexibility_of_conanfile_py.html#consuming-packages-flexibility-of-conanfile-py)部分已经使用过这个方法来对不支持的配置抛出错误。在这里，调用 [`check_min_cppstd()`](https://docs.conan.io/2/reference/tools/build.html#conan-tools-build-check-min-cppstd) 和 [`check_max_cppstd()`](https://docs.conan.io/2/reference/tools/build.html#conan-tools-build-check-max-cppstd) 函数来验证在设置中至少使用 C++11 且最多使用 C++20 标准。

你可以使用 [`require_fmt`](https://github.com/conan-io/libhello/tree/require_fmt) 分支中的 `fmt` 库来检查新源代码。你会发现 [`hello.cpp`](https://github.com/conan-io/libhello/blob/require_fmt/src/hello.cpp) 文件为输出消息添加了颜色：

```cpp
#include <fmt/color.h>

#include "hello.h"

void hello(){
    #ifdef NDEBUG
    fmt::print(fg(fmt::color::crimson) | fmt::emphasis::bold, "hello/1.0: Hello World Release!\n");
    #else
    fmt::print(fg(fmt::color::crimson) | fmt::emphasis::bold, "hello/1.0: Hello World Debug!\n");
    #endif
    ...
```

使用当前的默认配置从源代码构建包，然后让 `test_package` 文件夹测试包。现在你应该看到带颜色的输出消息：

```bash
$ conan create . --build=missing
-------- Exporting the recipe ----------
...
-------- Testing the package: Running test() ----------
hello/1.0 (test package): Running test()
hello/1.0 (test package): RUN: ./example
hello/1.0: Hello World Release!
  hello/1.0: __x86_64__ defined
  hello/1.0: __cplusplus 201103
  hello/1.0: __GNUC__ 4
  hello/1.0: __GNUC_MINOR__ 2
  hello/1.0: __clang_major__ 13
  hello/1.0: __clang_minor__ 1
  hello/1.0: __apple_build_version__ 13160021
```

## 依赖项的传递性

默认情况下，Conan 假定所需的依赖项头文件是当前包的实现细节，以促进低耦合和封装等良好的软件工程实践。在上述示例中， `fmt` 是 `hello/1.0` 包中的纯实现细节。`hello/1.0` 的使用者不会知道任何关于 `fmt` 的信息，也无法访问其头文件；如果 `hello/1.0` 的使用者尝试添加 `#include <fmt/color.h>`，它将失败，因为无法找到这些头文件。

但如果 `hello/1.0` 包的公共头文件包含 `#include` 到 `fmt` 的头文件，这意味着这些头文件必须向下传递，以允许 `hello/1.0` 的使用者成功编译。由于这不是默认的预期行为，配方必须声明如下：

```python
class helloRecipe(ConanFile):
    name = "hello"
    version = "1.0"

    def requirements(self):
        self.requires("fmt/8.1.1", transitive_headers=True)
```

这将把必要的编译标志和头文件 `includedirs` 传播给 `hello/1.0` 的使用者。

```{admonition} 最佳实践
如果 `hello/1.0` 的使用者直接包含了 `fmt` 头文件，例如 `#include <fmt/color.h>` ，那么，这样的使用者应该声明自己的 `self.requires("fmt/8.1.1")` 依赖，因为这是直接依赖的。换句话说，即使从该使用者中移除了对 `hello/1.0` 的依赖，它仍然会依赖于 `fmt` ，因此它不能滥用来自 `hello` 的 `fmt` 头文件的传递性，而是应该明确声明它们。
```
