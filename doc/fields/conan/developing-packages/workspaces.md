# 工作区

在上一节中，学习了可编辑包以及如何定义自定义布局。现在介绍工作区的概念以及如何使用它。

## 简介

要启用工作区功能，需要定义环境变量 `CONAN_WORKSPACE_ENABLE=will_break_next`。值 `will_break_next` 用于强调它将在后续版本中更改，并且这项功能仅用于测试，不能用于生产环境。

Conan 工作区让你有机会以 `editable` 模式以协调或整体（也称为超级构建）的方式管理多个包：

- 协调(orchestrated)，指 Conan 逐个构建可编辑包，从应用程序/消费者开始（如果存在）。
- 整体(monolithic)，指可编辑包作为整体构建，为整个工作区生成单一结果（生成器等）。

请注意，添加到工作区的包会自动解析为 `editable` 类型。这些可编辑包被命名为工作区的 `packages`。

## 如何定义工作区

工作空间由 `conanws.yml` 文件和/或 `conanws.py` 文件定义。任何 Conan 工作空间命令都会从当前工作目录向上遍历文件系统，直到文件系统根目录，找到其中一个文件。这将定义“根”工作空间文件夹。`conanws` 文件中的路径旨在相对化，以便必要时可重新定位，或在类似单一代码库的项目中提交到 Git。

通过 `conan workspace` 命令，可以打开、添加和/或从当前工作空间中移除 `packages`。

## 整体构建

Conan 工作空间可以作为单一的整体项目（超级项目）构建，这非常方便。通过例子来看一下：

```bash
$ conan new workspace
$ conan workspace super-install
$ cmake --preset conan-release # use conan-default in Win
$ cmake --build --preset conan-release
```

简单解释一下发生了什么。最初， `conan new workspace` 创建了工作区模板项目，包含一些相关文件和以下结构：

```bash
.
├── CMakeLists.txt
├── app1
│    ├── CMakeLists.txt
│    ├── conanfile.py
│    ├── src
│    │    ├── app1.cpp
│    │    ├── app1.h
│    │    └── main.cpp
│    └── test_package
│        └── conanfile.py
├── conanws.py
├── conanws.yml
├── liba
│    ├── CMakeLists.txt
│    ├── conanfile.py
│    ├── include
│    │    └── liba.h
│    ├── src
│    │    └── liba.cpp
│    └── test_package
│        ├── CMakeLists.txt
│        ├── conanfile.py
│        └── src
│            └── example.cpp
└── libb
    ├── CMakeLists.txt
    ├── conanfile.py
    ├── include
    │    └── libb.h
    ├── src
    │    └── libb.cpp
    └── test_package
        ├── CMakeLists.txt
        ├── conanfile.py
        └── src
            └── example.cpp
```

根 CMakeLists.txt 定义了超项目(super-project)：

```{code-block} cmake
:caption: CMakeLists.txt

cmake_minimum_required(VERSION 3.25)
project(monorepo CXX)

include(FetchContent)

function(add_project SUBFOLDER)
   FetchContent_Declare(
      ${SUBFOLDER}
      SOURCE_DIR ${CMAKE_CURRENT_LIST_DIR}/${SUBFOLDER}
      SYSTEM
      OVERRIDE_FIND_PACKAGE
   )
   FetchContent_MakeAvailable(${SUBFOLDER})
endfunction()

add_project(liba)
# They should be defined in the liba/CMakeLists.txt, but we can fix it here
add_library(liba::liba ALIAS liba)
add_project(libb)
add_library(libb::libb ALIAS libb)
add_project(app1)
```

所以基本上，超级项目使用 `FetchContent` 来添加子文件夹的子项目。为了正确工作，子项目必须是基于 CMake 的子项目，并且有 `CMakeLists.txt`。此外，子项目必须定义正确的目标，就像 `find_package()` 脚本定义的那样，比如 `liba::liba`。如果情况不是这样，总是可以定义一些本地 `ALIAS` 目标。

另一个重要部分是 `conanws.py` 文件：

```{code-block} python
:caption: conanws.py

from conan import Workspace
from conan import ConanFile
from conan.tools.cmake import CMakeDeps, CMakeToolchain, cmake_layout

class MyWs(ConanFile):
   """ This is a special conanfile, used only for workspace definition of layout
   and generators. It shouldn't have requirements, tool_requirements. It shouldn't have
   build() or package() methods
   """
   settings = "os", "compiler", "build_type", "arch"

   def generate(self):
      deps = CMakeDeps(self)
      deps.generate()
      tc = CMakeToolchain(self)
      tc.generate()

   def layout(self):
      cmake_layout(self)

class Ws(Workspace):
   def root_conanfile(self):
      return MyWs  # Note this is the class name
```

`class MyWs(ConanFile)` 内嵌的 `conanfile` 的作用很重要，它定义了超项目所需的生成器和布局。

`conan workspace super-install` 不会单独安装不同的可编辑文件，对于这个命令，可编辑文件不存在，它们只是被视为依赖关系图中的一个单一“节点”，因为它们将是超级项目构建的一部分。因此，只有一个生成的 `conan_toolchain.cmake` 和一个共同的依赖关系 `xxx-config.cmake` 文件集，用于所有超级项目的外部依赖。

上述模板在没有外部依赖的情况下可以正常工作，但有外部依赖时，一切也会以相同的方式运行。这可以通过以下方式测试：

```bash
$ conan new cmake_lib -d name=mymath
$ conan create .
$ conan new workspace -d requires=mymath/0.1
$ conan workspace super-install
$ cmake ...
```

```{note}
当前的 `conan new workspace` 生成基于 CMake 的超级项目。但也可以使用其他构建系统定义超级项目，例如添加不同 `.vcxproj` 子项目的 `MSBuild` 解决方案文件。只要超级项目知道如何聚合和管理子项目，这是可能的。

如果存在某种结构，`conanws.py` 中的 `add()` 方法也可能管理将子项目添加到超级项目中。
```

## 协调构建

Conan 工作空间还可以分别构建不同的 `packages` ，并考虑是否有将其他作为依赖项定义的包。

使用另一种结构来更好地理解它是如何工作的。现在，从零开始创建它，使用 `conan workspace init .` 创建几乎空的 `conanws.py/conanws.yml`，并使用 `conan new cmake_lib/cmake_exe` 基本模板，这些模板创建基于 CMake 的常规 Conan 包：

```bash
$ mkdir myproject && cd myproject
$ conan workspace init .
$ conan new cmake_lib -d name=hello -d version=1.0 -o hello
$ conan new cmake_exe -d name=app -d version=1.0 -d requires=hello/1.0 -o app
```

这些命令创建了如下所示的文件结构：

```bash
.
├── conanws.py
├── conanws.yml
├── app
│    ├── CMakeLists.txt
│    ├── conanfile.py
│    ├── src
│    │    ├── app.cpp
│    │    ├── app.h
│    │    └── main.cpp
│    └── test_package
│        └── conanfile.py
└── hello
     ├── CMakeLists.txt
     ├── conanfile.py
     ├── include
     │    └── hello.h
     ├── src
     │    └── hello.cpp
     └── test_package
         ├── CMakeLists.txt
         ├── conanfile.py
         └── src
             └── example.cpp
```

现在， `conanws.yml` 是空的，而 `conanws.py` 的定义非常简单。将 `app` 应用（消耗 `hello` ）和 `hello` 库作为新的 `packages` 添加到工作区：

```bash
$ conan workspace add hello
Reference 'hello/1.0' added to workspace
$ conan workspace add app
Reference 'app/1.0' added to workspace
```

定义了工作区后，可以构建它们并执行应用程序：

```bash
$ conan workspace build
$ app/build/Release/app
hello/1.0: Hello World Release!
...
app/1.0: Hello World Release!
...
```
