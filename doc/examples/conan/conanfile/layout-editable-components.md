# 使用组件和可编辑包

可以在 `layout()` 方法中定义组件，以支持 `editable` 包的情况。也就是说，如果想把一个包放在 `editable` 模式下，而该包定义了 `components` ，那么必须在 `layout()` 方法中正确地定义组件布局。让我们通过实际例子来看一下。

请首先克隆源代码以重新创建此项目。你可以在 GitHub 的 examples2 仓库中找到它们：
```bash
$ git clone https://github.com/conan-io/examples2.git
$ cd examples2/examples/conanfile/layout/editable_components
```

在那里找到 `greetings` 子文件夹和包，其中包含 2 个库，即 `hello` 库和 `bye` 库。每个库都在包配方内部被建模为 `component` ：

```{code-block} python
:caption:  greetings/conanfile.py

class GreetingsConan(ConanFile):
    name = "greetings"
    version = "0.1"
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps", "CMakeToolchain"
    exports_sources = "src/*"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def layout(self):
        cmake_layout(self, src_folder="src")
        # This "includedirs" starts in the source folder, which is "src"
        # So the components include dirs is the "src" folder (includes are
        # intended to be included as ``#include "hello/hello.h"``)
        self.cpp.source.components["hello"].includedirs = ["."]
        self.cpp.source.components["bye"].includedirs = ["."]
        # compiled libraries "libdirs" will be inside the "build" folder, depending
        # on the platform they will be in "build/Release" or directly in "build" folder
        bt = "." if self.settings.os != "Windows" else str(self.settings.build_type)
        self.cpp.build.components["hello"].libdirs = [bt]
        self.cpp.build.components["bye"].libdirs = [bt]

    def package(self):
        copy(self, "*.h", src=self.source_folder,
             dst=join(self.package_folder, "include"))
        copy(self, "*.lib", src=self.build_folder,
             dst=join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.a", src=self.build_folder,
             dst=join(self.package_folder, "lib"), keep_path=False)

    def package_info(self):
        self.cpp_info.components["hello"].libs = ["hello"]
        self.cpp_info.components["bye"].libs = ["bye"]

        self.cpp_info.set_property("cmake_file_name", "MYG")
        self.cpp_info.set_property("cmake_target_name", "MyGreetings::MyGreetings")
        self.cpp_info.components["hello"].set_property("cmake_target_name", "MyGreetings::MyHello")
        self.cpp_info.components["bye"].set_property("cmake_target_name", "MyGreetings::MyBye")
```

在最终包中， `hello` 和 `bye` 库的位置位于最终的 `lib` 文件夹，因此除了组件的定义外， `package_info()` 方法无需做特殊处理。在这种情况下，还包括了 CMake 生成的文件名和目标的定制，但这对于本示例来说不是必需的。

重要的是 `layout()` 的定义。除了常见的 `cmake_layout` ，还需要定义组件头文件（ `self.cpp.source` ，因为它们是源代码）的位置以及本地构建库的位置。由于库的位置取决于平台，最终的 `self.cpp.build.components["component"].libdirs` 也取决于平台。

通过这个配方，可以将包置于可编辑模式，并使用以下命令本地构建：
```bash
$ conan editable add greetings
$ conan build greetings
# we might want to also build the debug config
```

在 `app` 文件夹中，有一个包配方用于构建 2 个可执行文件，这些文件链接了 `greeting` 包的组件。这里的 `app/conanfile.py` 配方很简单， `build()` 方法构建并运行了用 `CMakeLists.txt` 构建的 `example` 和 `example2` 可执行文件。

```cmake
# Note the MYG file name, not matching the package name,
# because the recipe defined "cmake_file_name"
find_package(MYG)

add_executable(example example.cpp)
# Note the MyGreetings::MyGreetings target name, not matching the package name,
# because the recipe defined "cmake_target_name"
# "example" is linking with the whole package, both "hello" and "bye" components
target_link_libraries(example MyGreetings::MyGreetings)

add_executable(example2 example2.cpp)
# "example2" is only using and linking "hello" component, but not "bye"
target_link_libraries(example2 MyGreetings::MyHello)
```

```bash
$ conan build app
hello: Release!
bye: Release!
```

如果你现在去修改 `bye.cpp` 源文件中的输出消息，然后本地构建 `greetings` 和 `app` ，那么“bye”组件库的最终输出消息应该会发生变化：
```bash
$ conan build greetings
$ conan build app
hello: Release!
adios: Release!
```
