# 当 Conanfile 位于子文件夹中时声明布局

请首先克隆源代码以重新创建此项目。你可以在 GitHub 的 examples2 仓库中找到它们：
```bash
$ git clone https://github.com/conan-io/examples2.git
$ cd examples2/examples/conanfile/layout/conanfile_in_subfolder
```

如果有一个项目，旨在打包与 `conanfile.py` 位于同一代码库中的代码，但 `conanfile.py` 不在项目的根目录中：
```bash
.
├── CMakeLists.txt
├── conan
│   └── conanfile.py
├── include
│   └── say.h
└── src
    └── say.cpp
```
你可以在 `conanfile.py` 中声明布局：
```python
import os
from conan import ConanFile
from conan.tools.files import load, copy
from conan.tools.cmake import CMake


class PkgSay(ConanFile):
    name = "say"
    version = "1.0"
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeToolchain"

    def layout(self):
        # The root of the project is one level above
        self.folders.root = ".."
        # The source of the project (the root CMakeLists.txt) is the source folder
        self.folders.source = "."
        self.folders.build = "build"

    def export_sources(self):
        # The path of the CMakeLists.txt and sources we want to export are one level above
        folder = os.path.join(self.recipe_folder, "..")
        copy(self, "*.txt", folder, self.export_sources_folder)
        copy(self, "src/*.cpp", folder, self.export_sources_folder)
        copy(self, "include/*.h", folder, self.export_sources_folder)

    def source(self):
        # Check that we can see that the CMakeLists.txt is inside the source folder
        cmake_file = load(self, "CMakeLists.txt")

    def build(self):
        # Check that the build() method can also access the CMakeLists.txt in the source folder
        path = os.path.join(self.source_folder, "CMakeLists.txt")
        cmake_file = load(self, path)

        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
```

你可以尝试创建 `say` 包：
```bash
$ cd conan
$ conan create .
```
