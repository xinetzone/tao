# 使用依赖项中的 CMake 宏

当包配方需要通过宏提供 CMake 功能时，可以按以下方式操作。假设有 `pkg` 配方，它将“导出”和“打包” Macros.cmake 文件，该文件包含 `pkg_macro()` CMake 宏：

```{code-block} python
:caption: pkg/conanfile.py

from conan import ConanFile
from conan.tools.files import copy

class Pkg(ConanFile):
    name = "pkg"
    version = "0.1"
    package_type = "static-library"
    # Exporting, as part of the sources
    exports_sources = "*.cmake"

    def package(self):
        # Make sure the Macros.cmake is packaged
        copy(self, "*.cmake", src=self.source_folder, dst=self.package_folder)

    def package_info(self):
        # We need to define that there are "build-directories", in this case
        # the current package root folder, containing build files and scripts
        self.cpp_info.builddirs = ["."]
```

```{code-block} cmake
:caption: pkg/Macros.cmake

function(pkg_macro)
    message(STATUS "PKG MACRO WORKING!!!")
endfunction()
```

当这个包被创建时（ `cd pkg && conan create .` ），它可以为其他包配方所使用，例如这个应用程序：

```{code-block} python
:caption: app/conanfile.py

from conan import ConanFile
from conan.tools.cmake import CMake

class App(ConanFile):
    package_type = "application"
    generators = "CMakeToolchain", "CMakeDeps"
    settings = "os", "compiler", "arch", "build_type"
    requires = "pkg/0.1"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
```

它包含了这个 `CMakeLists.txt` ：

```{code-block} cmake
:caption: app/CMakeLists.txt

cmake_minimum_required(VERSION 3.15)
project(App LANGUAGES NONE)

include(Macros)  # include the file with the macro (note no .cmake extension)
pkg_macro()  # call the macro
```

那么当运行本地构建时，将看到文件是如何被包含以及宏是如何被调用的：

```bash
$ cd app
$ conan build .
PKG MACRO WORKING!!!
```
