# 包文件：`package()` 方法

已经在 `hello` 包中使用了 `package()` 方法来调用 CMake 的安装步骤。在这个教程中，将更详细地解释 [`CMake.install()`](https://docs.conan.io/2/reference/tools/cmake/cmake.html#conan-tools-cmake-helper) 的使用方法，以及如何修改这个方法来执行类似以下操作：

- 使用 [`conan.tools.files`](https://docs.conan.io/2/reference/tools/files.html#conan-tools-files) 工具将构建文件夹中生成的工件复制到包文件夹
- 复制包许可证
- 管理符号链接的打包

请首先克隆源代码以重新创建此项目。你可以在 GitHub 上的 examples2 存储库中找到它们：
```bash
git clone https://github.com/conan-io/examples2.git
cd examples2/tutorial/creating_packages/package_method
```

## 在 `package()` 方法中使用 CMake 安装步骤 

当你已经在 `CMakeLists.txt` 中定义了从构建和源文件夹中提取工件（头文件、库、可执行文件）到预定位置的功能，并且可能对这些工件进行一些后处理时，这是最简单的选择。这不需要修改你的 `CMakeLists.txt`，因为 Conan 会将 `CMAKE_INSTALL_PREFIX` CMake 变量设置为指向 recipe 的 [`package_folder`](https://docs.conan.io/2/reference/conanfile/attributes.html#conan-conanfile-properties-package-folder) 属性。然后，在 `CMakeLists.txt` 中对创建的目标调用 `install()` 就足够让 Conan 将构建的工件移动到 Conan 本地缓存的正确位置。

`CMakeLists.txt`:
```
cmake_minimum_required(VERSION 3.15)
project(hello CXX)

add_library(hello src/hello.cpp)
target_include_directories(hello PUBLIC include)
set_target_properties(hello PROPERTIES PUBLIC_HEADER "include/hello.h")

...

install(TARGETS hello)
```

```{code-block} python
:caption: conanfile.py
:emphasize-lines: 3

def package(self):
    cmake = CMake(self)
    cmake.install()
```

再次构建包，并注意与 Conan 本地缓存中文件打包相关的行：

```{code-block} bash
:linenos:
:emphasize-lines: 7-14

$ conan create . --build=missing -tf=""
...
hello/1.0: Build folder /Users/user/.conan2/p/tmp/b5857f2e70d1b2fd/b/build/Release
hello/1.0: Generated conaninfo.txt
hello/1.0: Generating the package
hello/1.0: Temporary package folder /Users/user/.conan2/p/tmp/b5857f2e70d1b2fd/p
hello/1.0: Calling package()
hello/1.0: CMake command: cmake --install "/Users/user/.conan2/p/tmp/b5857f2e70d1b2fd/b/build/Release" --prefix "/Users/user/.conan2/p/tmp/b5857f2e70d1b2fd/p"
hello/1.0: RUN: cmake --install "/Users/user/.conan2/p/tmp/b5857f2e70d1b2fd/b/build/Release" --prefix "/Users/user/.conan2/p/tmp/b5857f2e70d1b2fd/p"
-- Install configuration: "Release"
-- Installing: /Users/user/.conan2/p/tmp/b5857f2e70d1b2fd/p/lib/libhello.a
-- Installing: /Users/user/.conan2/p/tmp/b5857f2e70d1b2fd/p/include/hello.h
hello/1.0 package(): Packaged 1 '.h' file: hello.h
hello/1.0 package(): Packaged 1 '.a' file: libhello.a
hello/1.0: Package 'fd7c4113dad406f7d8211b3470c16627b54ff3af' created
hello/1.0: Created package revision bf7f5b9a3bb2c957742be4be216dfcbb
hello/1.0: Full package reference: hello/1.0#25e0b5c00ae41ef9fbfbbb1e5ac86e1e:fd7c4113dad406f7d8211b3470c16627b54ff3af#bf7f5b9a3bb2c957742be4be216dfcbb
hello/1.0: Package folder /Users/user/.conan2/p/47b4c4c61c8616e5/p
```

如您所见，调用 `cmake.install()` 方法后，包含文件和库文件都被复制到了包文件夹中。

## 在 `package()` 方法中使用 `conan.tools.files.copy()` 进行文件复制和打包许可证 

对于不希望依赖 CMake 的安装功能或使用其他构建系统的场景，Conan 提供了将选定文件复制到 [`package_folder`](https://docs.conan.io/2/reference/conanfile/attributes.html#conan-conanfile-properties-package-folder) 的工具。在这种情况下，您可以使用 [`tools.files.copy`](https://docs.conan.io/2/reference/tools/files/basic.html#conan-tools-files-copy) 函数来执行复制。我们可以用自定义的文件复制步骤替换之前的 `cmake.install()` 步骤，结果将是相同的。

请注意，我们还在许可证文件夹中打包了库源中的 `LICENSE` 文件。这是 Conan 包中的一种常见模式，也可以使用 `cmake.install()` 将其添加到之前的示例中，因为 `CMakeLists.txt` 不会将此文件复制到包文件夹中。

```{code-block} python
:caption: conanfile.py

def package(self):
    copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
    copy(self, pattern="*.h", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))
    copy(self, pattern="*.a", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
    copy(self, pattern="*.so", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
    copy(self, pattern="*.lib", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
    copy(self, pattern="*.dll", src=self.build_folder, dst=os.path.join(self.package_folder, "bin"), keep_path=False)
    copy(self, pattern="*.dylib", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
```

再次构建包，并注意与 Conan 本地缓存文件打包相关的行：

```{code-block} bash
:emphasize-lines: 7-14

$ conan create . --build=missing -tf=""
...
hello/1.0: Build folder /Users/user/.conan2/p/tmp/222db0532bba7cbc/b/build/Release
hello/1.0: Generated conaninfo.txt
hello/1.0: Generating the package
hello/1.0: Temporary package folder /Users/user/.conan2/p/tmp/222db0532bba7cbc/p
hello/1.0: Calling package()
hello/1.0: Copied 1 file: LICENSE
hello/1.0: Copied 1 '.h' file: hello.h
hello/1.0: Copied 1 '.a' file: libhello.a
hello/1.0 package(): Packaged 1 file: LICENSE
hello/1.0 package(): Packaged 1 '.h' file: hello.h
hello/1.0 package(): Packaged 1 '.a' file: libhello.a
hello/1.0: Package 'fd7c4113dad406f7d8211b3470c16627b54ff3af' created
hello/1.0: Created package revision 50f91e204d09b64b24b29df3b87a2f3a
hello/1.0: Full package reference: hello/1.0#96ed9fb1f78bc96708b1abf4841523b0:fd7c4113dad406f7d8211b3470c16627b54ff3af#50f91e204d09b64b24b29df3b87a2f3a
hello/1.0: Package folder /Users/user/.conan2/p/21ec37b931782de8/p
```

检查包含文件和库文件的打包方式。如上所述，`LICENSE` 文件也被复制。

## 在 `package()` 方法中管理符号链接

在包方法中，您还可以控制如何打包符号链接。Conan 默认不会处理符号链接，因此我们提供了几种[工具](https://docs.conan.io/2/reference/tools/files/symlinks.html#id1)来将绝对符号链接转换为相对链接，以及删除外部或损坏的符号链接。

想象一下，在上一例打包的文件中，有些是符号链接，它们指向 Conan 缓存内的绝对位置。那么，调用 `conan.tools.files.symlinks.absolute_to_relative_symlinks()` 会将这些绝对链接转换为相对路径，使包可重定位。

```{code-block} python
:caption: conanfile.py

from conan.tools.files.symlinks import absolute_to_relative_symlinks

def package(self):
    copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
    copy(self, pattern="*.h", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))
    copy(self, pattern="*.a", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
    ...

    absolute_to_relative_symlinks(self, self.package_folder)
```