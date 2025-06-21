# 理解使用 conanfile.py 与 conanfile.txt 的灵活性

在之前的示例中，在 `conanfile.txt` 文件中声明了依赖项（Zlib 和 CMake）。让我们看看那个文件

```{code-block} ini
:caption: conanfile.txt

[requires]
zlib/1.2.11

[tool_requires]
cmake/3.22.6

[generators]
CMakeDeps
CMakeToolchain
```

对于简单情况，使用 `conanfile.txt` 构建项目已经足够，但如果您需要更大的灵活性，则应该使用 `conanfile.py` 文件，您可以在其中使用 Python 代码来动态添加需求、根据其他选项更改选项或为您的需求设置选项。让我们来看如何迁移到 `conanfile.py` 并使用其中一些功能的示例。

请先克隆源码以重新创建此项目。您可以在 GitHub 的 [examples2](https://github.com/conan-io/examples2) 仓库中找到它们

```bash
git clone https://github.com/conan-io/examples2.git
cd examples2/tutorial/consuming_packages/conanfile_py
```

检查文件夹内容，注意内容与之前的示例相同，只是用 `conanfile.py` 替换了 `conanfile.txt`。

```
.
├── CMakeLists.txt
├── conanfile.py
└── src
    └── main.c
```

我们将相同的信息转换为 `conanfile.py`。这个文件通常被称为 **“Conan recipe”**。它可以用于消费包（如本例所示），也可以用于[创建包](../creating-packages/index)。对于当前情况，它将定义我们的需求（库和构建工具）以及修改选项和设置如何消费这些包的逻辑。在使用此文件创建包的情况下，它可以定义（除其他外）如何下载包的源代码、如何从源代码构建二进制文件、如何打包二进制文件，以及有关未来消费者如何消费该包的信息。稍后我们将在 创建包 部分解释如何使用 Conan recipe 创建包。

以 Conan recipe 形式表示的等效内容如下所示：

```python
from conan import ConanFile


class CompressorRecipe(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeToolchain", "CMakeDeps"

    def requirements(self):
        self.requires("zlib/1.2.11")

    def build_requirements(self):
        self.tool_requires("cmake/3.22.6")
```

要创建 Conan recipe，声明了继承自 `ConanFile` 类的类。这个类有不同的类属性和方法：

- `settings` 类属性定义了项目范围的变量，例如编译器、其版本或操作系统本身，这些变量在构建项目时可能会改变。这与 Conan 如何管理二进制兼容性有关，因为这些值会影响 Conan 包的 **package ID** 的值。我们稍后将解释 Conan 如何使用此值来管理二进制兼容性。
- `generators` 类属性指定在调用 `conan install` 命令时将运行哪些 Conan generator。在本例中，添加了 `CMakeToolchain` 和 `CMakeDeps`，就像在 `conanfile.txt` 中一样。
- 在 `requirements()` 方法中，使用 `self.requires()` 方法声明 `zlib/1.2.11` 依赖项。
- 在 `build_requirements()` 方法中，使用 `self.tool_requires()` 方法声明 `cmake/3.22.6` 依赖项。

```{attention} 
将工具的依赖项添加到 `build_requirements()` 中并非绝对必要，因为理论上该方法中的所有内容都可以在 `requirements()` 方法中完成。但是，`build_requirements()` 提供了一个专门的位置来定义 `tool_requires` 和 `test_requires`，这有助于保持结构清晰和有组织性。更多信息请查阅 [`requirements()`](https://docs.conan.org.cn/2/reference/conanfile/methods/requirements.html#reference-conanfile-methods-requirements) 和 [`build_requirements()`](https://docs.conan.org.cn/2/reference/conanfile/methods/build_requirements.html#reference-conanfile-methods-build-requirements) 文档。
```

您可以检查，运行与之前示例相同的命令将得到与之前相同的结果。

## 使用 `layout()` 方法

在之前的示例中，每次执行 `conan install` 命令时，都必须使用 `--output-folder` 参数来定义想要创建 Conan 生成文件的位置。有一个更整洁的方法可以决定 Conan 应该在哪里生成构建系统的文件，这将允许我们决定，例如，是否根据使用的 CMake generator 类型设置不同的输出文件夹。您可以在 `conanfile.py` 文件内部的 `layout()` 方法中直接定义这一点，使其适用于所有平台，而无需添加更多更改。

```{code-block} python
:caption: conanfile.py
:linenos:

import os

from conan import ConanFile


class CompressorRecipe(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeToolchain", "CMakeDeps"

    def requirements(self):
        self.requires("zlib/1.2.11")
        if self.settings.os == "Windows":
            self.requires("base64/0.4.0")

    def build_requirements(self):
        if self.settings.os != "Windows":
            self.tool_requires("cmake/3.22.6")

    def layout(self):
        # We make the assumption that if the compiler is msvc the
        # CMake generator is multi-config
        multi = True if self.settings.get_safe("compiler") == "msvc" else False
        if multi:
            self.folders.generators = os.path.join("build", "generators")
            self.folders.build = "build"
        else:
            self.folders.generators = os.path.join("build", str(self.settings.build_type), "generators")
            self.folders.build = os.path.join("build", str(self.settings.build_type))
```

如您所见，在 `layout()` 方法中定义了 `self.folders.generators` 属性。这是 Conan 生成所有辅助文件（CMake toolchain 和 cmake dependencies 文件）的文件夹。

请注意，对于 `multi-config` generator（如 Visual Studio）和 `single-config` generator（如 Unix Makefiles），文件夹的定义是不同的。对于前者，无论构建类型如何，文件夹都是相同的，构建系统将在该文件夹内管理不同的构建类型。但 `single-config` generator（如 Unix Makefiles）必须为每种配置（作为不同的 `build_type` Release/Debug）使用不同的文件夹。在这种情况下，我们添加了一个简单的逻辑来考虑如果编译器名称是 msvc，则为 `multi-config`。

无需始终在 `conanfile.py` 中编写此逻辑。有一些预定义的布局您可以导入并直接在您的 `recipe` 中使用。例如，对于 CMake 情况，Conan 中已经定义了 `cmake_layout()`。

```{code-block} python
:caption: conanfile.py
:linenos:

from conan import ConanFile
from conan.tools.cmake import cmake_layout


class CompressorRecipe(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeToolchain", "CMakeDeps"

    def requirements(self):
        self.requires("zlib/1.2.11")

    def build_requirements(self):
        self.tool_requires("cmake/3.22.6")

    def layout(self):
        cmake_layout(self)
```

## 使用 `validate()` 方法为不支持的配置引发错误

`validate()` 方法 在 Conan 加载 conanfile.py 时进行评估，您可以使用它来检查输入的设置。例如，如果您的项目在 macOS 上不支持 armv8 架构，则可以引发 `ConanInvalidConfiguration` 异常，使 Conan 返回一个特殊错误码。这将表明用于 `setting` 或 `option` 的配置不受支持。

```{code-block} python
:caption: conanfile.py
:linenos:

...
from conan.errors import ConanInvalidConfiguration

class CompressorRecipe(ConanFile):
    ...

    def validate(self):
        if self.settings.os == "Macos" and self.settings.arch == "armv8":
            raise ConanInvalidConfiguration("ARM v8 not supported in Macos")
```

## 使用 `conanfile.py` 的条件需求

您可以向 `requirements()` 方法 添加一些逻辑来有条件地添加或移除需求。例如，想象一下您想在 Windows 上添加额外的依赖项，或者想使用系统的 CMake 安装而不是使用 Conan 的 `tool_requires`：

```{code-block} python
:caption: conanfile.py
:linenos:
from conan import ConanFile


class CompressorRecipe(ConanFile):
    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeToolchain", "CMakeDeps"

    def requirements(self):
        self.requires("zlib/1.2.11")

        # Add base64 dependency for Windows
        if self.settings.os == "Windows":
            self.requires("base64/0.4.0")

    def build_requirements(self):
        # Use the system's CMake for Windows
        if self.settings.os != "Windows":
            self.tool_requires("cmake/3.22.6")
```

## 使用 `generate()` 方法从包中复制资源

在某些场景下，Conan 包包含对消费其打包的库有用甚至必要的文件。这些文件可以是配置文件、资源文件，甚至是项目正确构建或运行所需的特定文件。使用 `generate()` 方法，您可以将这些文件从 Conan 缓存复制到您的项目文件夹中，确保所有必需的资源都可直接使用。

这是一个示例，展示了如何将依赖项的 `resdirs` 目录中的所有资源复制到项目内的 `assets` 目录：

```python
import os
from conan import ConanFile
from conan.tools.files import copy

class MyProject(ConanFile):

    ...

    def generate(self):
        # Copy all resources from the dependency's resource directory
        # to the "assets" folder in the source directory of your project
        dep = self.dependencies["dep_name"]
        copy(self, "*", dep.cpp_info.resdirs[0], os.path.join(self.source_folder, "assets"))
```

然后，在 `conan install` 步骤之后，所有这些资源文件将被本地复制，允许您在项目的构建过程中使用它们。有关如何在 `generate()` 方法中导入包文件的完整示例，您可以参考 [关于使用 Dear ImGui 库的博客文章](https://blog.conan.org.cn/2019/06/26/An-introduction-to-the-Dear-ImGui-library.html)，其中演示了如何根据图形 API 导入库的绑定。

```{attention}
需要澄清的是，复制库（无论是静态库还是共享库）并不是必需的。Conan 的设计宗旨是使用 [`generators`](https://docs.conan.org.cn/2/reference/tools.html#conan-tools) 和 [`environment tools`](https://docs.conan.org.cn/2/reference/tools/env/virtualrunenv.html#conan-tools-env-virtualrunenv) 从 Conan 本地缓存中的位置使用库，而无需将它们复制到本地文件夹。
```
