# 修补源代码

在这个[例子](https://docs.conan.io/2/examples/tools/files/patches/patch_sources.html)中，我们将看到如何修补源代码。有时这是必要的，特别是当你为第三方库创建一个包时。如果你需要在构建系统脚本中，甚至是在库的源代码中应用一个安全补丁，可能需要补丁。

请首先克隆源代码以重新创建此项目。你可以在 GitHub 上的 examples2 存储库中找到它们：
```bash
git clone https://github.com/conan-io/examples2.git
cd examples/tools/files/patches
```

## 使用‘replace_in_file’进行修补

修补文件最简单的方法是使用你的配方中的 `replace_in_file` 工具。它在文件中搜索指定的字符串，并用另一个字符串替换它。

### 在 `source()` 方法

`source()` 方法对所有配置（不同的 conan 调用为不同的设置/选项）只调用一次，因此如果更改对所有配置都相同，你只应在 `source()` 方法中修补。

在 `conanfile.py` 中查看 `source()` 方法:
```python
import os
from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.tools.files import get, replace_in_file


class helloRecipe(ConanFile):
    name = "hello"
    version = "1.0"

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    def source(self):
        get(self, "https://github.com/conan-io/libhello/archive/refs/heads/main.zip", strip_root=True)
        replace_in_file(self, os.path.join(self.source_folder, "src", "hello.cpp"), "Hello World", "Hello Friends!")

    ...
```

将 "Hello World" 字符串替换为“Hello Friends!”。可以运行 `conan create .` 并验证替换是否完成：

```bash
$ conan create .
...
-------- Testing the package: Running test() --------
hello/1.0: Hello Friends! Release!
...
```

### 在 `build()` 方法中 

在这种情况下，需要根据配置（`self.settings`, `self.options`…）应用不同的补丁，因此必须在 `build()` 方法中完成。修改配方以引入依赖于 `self.options.shared` 的变更：
```python
class helloRecipe(ConanFile):

    ...

    def source(self):
        get(self, "https://github.com/conan-io/libhello/archive/refs/heads/main.zip", strip_root=True)

    def build(self):
        replace_in_file(self, os.path.join(self.source_folder, "src", "hello.cpp"),
                        "Hello World",
                        "Hello {} Friends!".format("Shared" if self.options.shared else "Static"))
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    ...
```

如果用不同的 `option.shared` 调用 `conan create`，可以检查输出：

```bash
$ conan create .
...
hello/1.0: Hello Static Friends! Release!
...

$ conan create . -o shared=True
...
hello/1.0: Hello Shared Friends! Debug!
...
```

## 使用“patch”工具进行补丁操作

如果你有补丁文件（两个文件版本的差异），你可以使用 `conan.tools.files.patch` 工具来应用它。关于在哪里应用补丁（ `source()` 或 `build()` 方法）的规则是相同的。

我们有补丁文件，其中再次更改消息以显示“Hello Patched World Release！”：
```
--- a/src/hello.cpp
+++ b/src/hello.cpp
@@ -3,9 +3,9 @@

 void hello(){
     #ifdef NDEBUG
-    std::cout << "hello/1.0: Hello World Release!\n";
+    std::cout << "hello/1.0: Hello Patched World Release!\n";
     #else
-    std::cout << "hello/1.0: Hello World Debug!\n";
+    std::cout << "hello/1.0: Hello Patched World Debug!\n";
     #endif

     // ARCHITECTURES
```

将 `conanfile.py` 编辑为：
1. 导入 `patch` 工具。
2. 将 `exports_sources` 添加到补丁文件中，以便在缓存中可以访问它。
3. 调用 `patch` 工具。

```{code-block} python
:emphasize-lines: 4,15,18,19

import os
from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.tools.files import get, replace_in_file, patch


class helloRecipe(ConanFile):
    name = "hello"
    version = "1.0"

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    exports_sources = "*.patch"

    def source(self):
        get(self, "https://github.com/conan-io/libhello/archive/refs/heads/main.zip", strip_root=True)
        patch_file = os.path.join(self.export_sources_folder, "hello_patched.patch")
        patch(self, patch_file=patch_file)

    ...
```

可以运行“conan create”并看到补丁生效了：

```bash
$ conan create .
...
-------- Testing the package: Running test() --------
hello/1.0: Hello Patched World Release!
...
```

也可以使用[教程](https://docs.conan.io/2/tutorial/creating_packages/handle_sources_in_packages.html#creating-packages-handle-sources-in-packages-conandata)中介绍的 `conandata.yml`，这样可以为每个版本声明要应用的补丁：
```yaml
patches:
  "1.0":
    - patch_file: "hello_patched.patch"
```

在 `source()` 方法中引入的变更如下：

```python
def source(self):
    get(self, "https://github.com/conan-io/libhello/archive/refs/heads/main.zip", strip_root=True)
    patches = self.conan_data["patches"][self.version]
    for p in patches:
        patch_file = os.path.join(self.export_sources_folder, p["patch_file"])
        patch(self, patch_file=patch_file)
```

如果运行 `conan create`，补丁也会被应用：
```bash
$ conan create .
...
-------- Testing the package: Running test() --------
hello/1.0: Hello Patched World Release!
...
```

## 使用“apply_conandata_patches”工具进行补丁操作

上面的例子可以工作，但它有点复杂。如果你遵循相同的 yml 结构（查看 [`apply_conandata_patches`](https://docs.conan.io/2/reference/tools/files/patches.html#conan-tools-files-apply-conandata-patches) 以查看完整的支持的 yml），你只需要调用 `apply_conandata_patches`：
```python
from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.tools.files import get, apply_conandata_patches


class helloRecipe(ConanFile):
    name = "hello"
    version = "1.0"

    ...

    def source(self):
        get(self, "https://github.com/conan-io/libhello/archive/refs/heads/main.zip", strip_root=True)
        apply_conandata_patches(self)
```

检查补丁是否也已应用：
```bash
$ conan create .
...
-------- Testing the package: Running test() --------
hello/1.0: Hello Patched World Release!
...
```
