# CMakeToolchain: 在包内使用 xxx-config.cmake 文件

Conan 通常依赖于 `package_info()` 抽象，以允许使用任何构建系统构建的包被任何使用其他构建系统构建的包使用。在 CMake 的情况下，Conan 依赖于 `CMakeDeps` 生成器为每个依赖项生成 `xxxx-config.cmake` 文件，即使这些依赖项没有生成文件或根本没有使用 CMake 构建。

ConanCenter 使用这种抽象，而不是打包 `xxx-config.cmake` 文件，而是使用 `package_info()` 中的信息。这对于尽可能提供与构建系统无关的包，并对不同的构建系统、供应商和用户公平非常重要。例如，许多 Conan 用户很高兴地使用本地的 MSBuild（VS）项目，而完全不需要 CMake。如果 ConanCenter 的包仅使用包内的 `config.cmake` 文件构建，这将是不可能的。

但 ConanCenter 这样做并不意味着这是不可能或不必要的。完全可以使用包内的 `xxx-config.cmake` 文件，而放弃使用 CMakeDeps 生成器。

你可以在 GitHub 的 examples2 仓库中找到重现这个示例的源代码：

```bash
git clone https://github.com/conan-io/examples2.git
cd examples2/examples/tools/cmake/pkg_config_files
```

如果看一下 `conanfile.py` ：
```{code-block} python
:caption: conanfile.py

class pkgRecipe(ConanFile):
    name = "pkg"
    version = "0.1"
    ...

    def package_info(self):
        # No information provided, only the in-package .cmake is used here
        # Other build systems or CMake via CMakeDeps will fail
        self.cpp_info.builddirs = ["pkg/cmake"]
        self.cpp_info.set_property("cmake_find_mode", "none")
```

这是非常典型的配方，主要区别在于 `package_info()` 方法。有三个重要的注意事项：
- 它没有定义像 `self.cpp_info.libs = ["mypkg"]` 这样的字段。Conan 不会将此信息传播给消费者，这些信息唯一存在的地方是在包内的 `xxx-config.cmake` 文件中
- 万一仍有用户在使用 `CMakeDeps`，它将禁用客户端生成的 `xxx-config.cmake` 文件，使用 `set_property("cmake_find_mode", "none")`
- 它将定义该文件夹将包含构建脚本（如 `xxx-config.cmake` 包），供消费者定位。

因此，定义包详细信息的责任已转移到包含以下内容的 `CMakeLists.txt`：

```cmake
add_library(mylib src/pkg.cpp)  # Use a different name than the package, to make sure

set_target_properties(mylib PROPERTIES PUBLIC_HEADER "include/pkg.h")
target_include_directories(mylib PUBLIC
        $<BUILD_INTERFACE:${PROJECT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
    )

# Use non default mypkgConfig name
install(TARGETS mylib EXPORT mypkgConfig)
export(TARGETS mylib
    NAMESPACE mypkg::  # to simulate a different name and see it works
    FILE "${CMAKE_CURRENT_BINARY_DIR}/mypkgConfig.cmake"
)
install(EXPORT mypkgConfig
    DESTINATION "${CMAKE_INSTALL_PREFIX}/pkg/cmake"
    NAMESPACE mypkg::
)
```

有了这些信息，当执行 conan create 时：

- `build()` 方法将构建该包
- `package()` 方法将调用 `cmake install` ，这将创建 `mypkgConfig.cmake` 文件
- 它将在包文件夹的 `pkg/cmake/mypkgConfig.cmake` 文件中创建
- 它将包含足够的信息用于头文件，并创建 `mypkg::mylib` 目标

请注意，Conan 也无法知道配置文件名、命名空间和目标的具体细节，因此这也是消费者构建脚本需要了解的内容。

这就足以让包含内部 `mypkgConfig.cmake` 文件的包供消费者使用。在这个示例代码中，消费者只是 `test_package/conanfile.py`，但同样的规则适用于任何任意的消费者。

消费者 `conanfile.py` 完全不需要使用 `CMakeDeps` ，只需要 `generators = "CMakeToolchain"` 。请注意， `CMakeToolchain` 生成器仍然是必要的，因为 `mypkgConfig.cmake` 需要从 Conan 缓存中找到。生成的 `CMakeToolchain` 文件 `conan_toolchain.cmake` 包含了这些路径的定义。

消费者 `CMakeLists.txt` 将遵循标准：

```cmake
find_package(mypkg CONFIG REQUIRED)

add_executable(example src/example.cpp)
target_link_libraries(example mypkg::mylib)
```

您可以通过以下方式验证其是否正常工作：

```bash
$ conan create .

======== Testing the package: Executing test ========
pkg/0.1 (test package): Running test()
pkg/0.1 (test package): RUN: Release\example
pkg/0.1: Hello World Release!
pkg/0.1: _M_X64 defined
pkg/0.1: MSVC runtime: MultiThreadedDLL
pkg/0.1: _MSC_VER1939
pkg/0.1: _MSVC_LANG201402
pkg/0.1: __cplusplus199711
pkg/0.1 test_package
```

## 重要注意事项

所提出的方法有一个局限性，它不适用于多配置 IDE。实现这种方法将无法让开发人员直接在 Visual Studio 等 IDE 中从发布版本切换到调试版本，反之亦然，并且需要 `conan install` 进行更改。对于单配置设置来说，这根本不是问题，但对于 Visual Studio 开发人员来说可能会有些不便。团队正在开发 VS 插件，这可能有助于缓解这个问题。原因在于 CMake 的限制， `find_package()` 只能找到一个配置，而 CMakeDeps 在这里被移除，Conan 无法避免这个限制。

需要了解的是，正确管理对其他依赖项的传递性也是包作者和包 `CMakeLists.txt` 的责任，在某些情况下这并不简单。如果处理不当，可能会导致包内的 `xxx-config.cmake` 文件将其传递依赖项定位到其他地方，比如系统，而不是传递的 Conan 包依赖项中。

最后，请记住这些包不会对除 CMake 以外的其他构建系统可用。
