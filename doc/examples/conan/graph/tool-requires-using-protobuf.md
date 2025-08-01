# 使用相同的依赖作为 `requires` 和 `tool_requires` 

有些库可以同时作为库和工具依赖使用，例如 [`protobuf`](https://github.com/conan-io/conan-center-index/tree/master/recipes/protobuf)。这些库通常包含库本身的头文件/源文件，或许还有一些额外的工具（编译器、shell 脚本等）。这两部分在不同的上下文中使用，以 `protobuf` 为例来考虑这种情况：

- 我想创建包含编译后的 `protobuf` 消息的库。在构建时需要调用 `protobuf` 编译器（构建上下文），而包含编译后的 `.pb.cc` 文件的库需要与 `protobuf` 库链接（宿主上下文）。

基于这一点，应该能够在同一个 Conan 配方中在构建/宿主上下文中使用 `protobuf`。基本上，你的包配方应该看起来像这样：

```python
def requirements(self):
    self.requires("protobuf/3.18.1")

def build_requirements(self):
    self.tool_requires("protobuf/<host_version>")
```

```{note}
`protobuf/<host_version>` 表达式确保在两个上下文中使用相同版本的库。更多内容可以在[这里](https://docs.conan.io/2/reference/conanfile/methods/build_requirements.html#reference-conanfile-build-requirements-host-version)阅读。
```

这是处理在两个上下文中使用的任何其他库的方法。

请首先克隆源代码以重新创建此项目。你可以在 GitHub 上的 examples2 存储库中找到它们：
```bash
git clone https://github.com/conan-io/examples2.git
cd examples2/examples/graph/tool_requires/using_protobuf/myaddresser
```

项目的结构如下：

```bash
./
├── conanfile.py
├── CMakeLists.txt
├── addressbook.proto
├── apple-arch-armv8
├── apple-arch-x86_64
└── src
   └── myaddresser.cpp
└── include
   └── myaddresser.h
└── test_package
   ├── conanfile.py
   ├── CMakeLists.txt
   └── src
       └── example.cpp
```

`conanfile.py` 看起来像：

```{code-block} python
:caption: ./conanfile.py

from conan import ConanFile
from conan.tools.cmake import CMake, cmake_layout


class myaddresserRecipe(ConanFile):
    name = "myaddresser"
    version = "1.0"
    package_type = "library"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    generators = "CMakeDeps", "CMakeToolchain"
    # Sources are located in the same place as this recipe, copy them to the recipe
    exports_sources = "CMakeLists.txt", "src/*", "include/*", "addressbook.proto"

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def requirements(self):
        self.requires("protobuf/3.18.1")

    def build_requirements(self):
        self.tool_requires("protobuf/<host_version>")

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["myaddresser"]
        self.cpp_info.requires = ["protobuf::libprotobuf"]
```

如您所见，在不同的上下文中同时使用 `protobuf`。

`CMakeLists.txt` 展示了此示例如何使用 `protobuf` 编译器和库：
```{code-block} cmake
:caption: ./CMakeLists.txt

cmake_minimum_required(VERSION 3.15)
project(myaddresser LANGUAGES CXX)

find_package(protobuf CONFIG REQUIRED)

protobuf_generate_cpp(PROTO_SRCS PROTO_HDRS addressbook.proto)

add_library(myaddresser src/myaddresser.cpp ${PROTO_SRCS})
target_include_directories(myaddresser PUBLIC include)

target_include_directories(myaddresser PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<BUILD_INTERFACE:${CMAKE_CURRENT_BINARY_DIR}>
  $<INSTALL_INTERFACE:include>
)

target_link_libraries(myaddresser PUBLIC protobuf::libprotobuf)

set_target_properties(myaddresser PROPERTIES PUBLIC_HEADER "include/myaddresser.h;${PROTO_HDRS}")
install(TARGETS myaddresser)
```

在库本身定义了简单的 `myaddresser.cpp`，该文件使用生成的 `addressbook.pb.h` 头文件：

```{code-block} cpp
:caption: ./src/myaddresser.cpp

#include <iostream>
#include <fstream>
#include <string>
#include "addressbook.pb.h"
#include "myaddresser.h"

void myaddresser(){
  // Testing header generated by protobuf
  GOOGLE_PROTOBUF_VERIFY_VERSION;

  tutorial::AddressBook address_book;
  auto * person = address_book.add_people();
  person->set_id(1337);
  std::cout << "myaddresser(): created a person with id 1337\n";
  // Optional:  Delete all global objects allocated by libprotobuf.
  google::protobuf::ShutdownProtobufLibrary();
}
```

最后，`test_package` 示例简单地调用 `myaddresser()` 函数来检查一切是否正常工作：

```{code-block} cpp
:caption: ./test_package/src/example.cpp

#include <iostream>
#include <fstream>
#include <string>
#include "myaddresser.h"


int main(int argc, char* argv[]) {
  myaddresser();
  return 0;
}
```

那么，看看它是否运行良好：

```bash
$ conan create . --build missing
...

Requirements
    myaddresser/1.0#71305099cc4dc0b08bb532d4f9196ac1:c4e35584cc696eb5dd8370a2a6d920fb2a156438 - Build
    protobuf/3.18.1#ac69396cd9fbb796b5b1fc16473ca354:e60fa1e7fc3000cc7be2a50a507800815e3f45e0#0af7d905b0df3225a3a56243841e041b - Cache
    zlib/1.2.13#13c96f538b52e1600c40b88994de240f:d0599452a426a161e02a297c6e0c5070f99b4909#69b9ece1cce8bc302b69159b4d437acd - Cache
Build requirements
    protobuf/3.18.1#ac69396cd9fbb796b5b1fc16473ca354:e60fa1e7fc3000cc7be2a50a507800815e3f45e0#0af7d905b0df3225a3a56243841e041b - Cache
...

-- Install configuration: "Release"
-- Installing: /Users/myuser/.conan2/p/b/myser03f790a5a5533/p/lib/libmyaddresser.a
-- Installing: /Users/myuser/.conan2/p/b/myser03f790a5a5533/p/include/myaddresser.h
-- Installing: /Users/myuser/.conan2/p/b/myser03f790a5a5533/p/include/addressbook.pb.h

myaddresser/1.0: package(): Packaged 2 '.h' files: myaddresser.h, addressbook.pb.h
myaddresser/1.0: package(): Packaged 1 '.a' file: libmyaddresser.a
....

======== Testing the package: Executing test ========
myaddresser/1.0 (test package): Running test()
myaddresser/1.0 (test package): RUN: ./example
myaddresser(): created a person with id 1337
```

确认运行正常后，尝试使用交叉编译。请注意，这部分内容基于 MacOS Intel 系统，进行 MacOS ARM 系统的交叉编译，但当然你可以根据需要使用自己的配置文件。

````{note}
运行示例的这一部分需要 MacOS 系统。
```bash
$ conan create . --build missing -pr:b apple-arch-x86_64 -pr:h apple-arch-armv8
...

-- Install configuration: "Release"
-- Installing: /Users/myuser/.conan2/p/b/myser03f790a5a5533/p/lib/libmyaddresser.a
-- Installing: /Users/myuser/.conan2/p/b/myser03f790a5a5533/p/include/myaddresser.h
-- Installing: /Users/myuser/.conan2/p/b/myser03f790a5a5533/p/include/addressbook.pb.h

myaddresser/1.0: package(): Packaged 2 '.h' files: myaddresser.h, addressbook.pb.h
myaddresser/1.0: package(): Packaged 1 '.a' file: libmyaddresser.a
....

======== Testing the package: Executing test ========
myaddresser/1.0 (test package): Running test()
```

现在，由于主机架构，无法看到示例运行。如果想检查示例可执行文件是否为正确的构建：
```bash
$ file test_package/build/apple-clang-13.0-armv8-gnu17-release/example
test_package/build/apple-clang-13.0-armv8-gnu17-release/example: Mach-O 64-bit executable arm64
```

一切按预期工作，可执行文件是为 `arm64` 架构构建的 64 位可执行文件。
````
