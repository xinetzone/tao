# 当有多个子项目时声明布局

请首先克隆源代码以重新创建此项目。你可以在 GitHub 的 examples2 仓库中找到它们：
```bash
git clone https://github.com/conan-io/examples2.git
cd examples2/examples/conanfile/layout/multiple_subprojects
```

假设有一个包含两个子项目：`hello` 和 `bye` 的项目，它们需要访问同一级别的某些信息（兄弟文件夹）。每个子项目将是一个 Conan 包。结构可能类似于以下内容：

```bash
.
├── bye
│   ├── CMakeLists.txt
│   ├── bye.cpp        # contains an #include "../common/myheader.h"
│   └── conanfile.py   # contains include(../common/myutils.cmake)
├── common
│   ├── myheader.h
│   └── myutils.cmake
└── hello
    ├── CMakeLists.txt # contains include(../common/myutils.cmake)
    ├── conanfile.py
    └── hello.cpp      # contains an #include "../common/myheader.h"
```

`hello` 和 `bye` 子项目都需要使用位于` common` 文件夹内的某些文件（这些文件也可能被其他子项目使用和共享），并通过它们的相对位置进行引用。请注意 `common` 并不打算成为一个 Conan 包。它只是将被复制到不同子项目包中的通用代码。

可以使用 `self.folders.root = ".."` 布局指定符来定位项目的根目录，然后使用 `self.folders.subproject = "subprojectfolder"` 将大部分布局重新定位到当前子项目文件夹，因为这将包含构建脚本、源代码等，因此其他辅助工具如 `cmake_layout()` 仍然可以正常工作。看看 `hello` 的 `conanfile.py` 可能看起来像什么：

```{code-block} python
:caption: ./hello/conanfile.py

import os
from conan import ConanFile
from conan.tools.cmake import cmake_layout, CMake
from conan.tools.files import copy


class hello(ConanFile):
    name = "hello"
    version = "1.0"

    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeToolchain"

    def layout(self):
        self.folders.root = ".."
        self.folders.subproject = "hello"
        cmake_layout(self)

    def export_sources(self):
        source_folder = os.path.join(self.recipe_folder, "..")
        copy(self, "hello/conanfile.py", source_folder, self.export_sources_folder)
        copy(self, "hello/CMakeLists.txt", source_folder, self.export_sources_folder)
        copy(self, "hello/hello.cpp", source_folder, self.export_sources_folder)
        copy(self, "common*", source_folder, self.export_sources_folder)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
        self.run(os.path.join(self.cpp.build.bindirs[0], "hello"))
```

构建 `hello`，并使用 `common` 文件夹的内容检查其是否正确构建。

```bash
$ conan install hello
$ conan build hello
...
[100%] Built target hello
conanfile.py (hello/1.0): RUN: ./hello
hello WORLD
```

你也可以运行 `conan create`，并检查它是否工作正常：
```bash
$ conan create hello
...
[100%] Built target hello
conanfile.py (hello/1.0): RUN: ./hello
hello WORLD
```

```{note}
注意 `export_sources()` 方法的重要性，它能够保持 `hello` 和 `common` 文件夹的相同相对布局，无论是在当前文件夹中的本地开发者流程中，还是在这些源代码被复制到 Conan 缓存中时，使用 `conan create` 或 `conan install --build=hello` 在那里进行构建。这是 `layout()` 设计原则之一，事物在用户文件夹和缓存中的相对位置必须保持一致。
```
