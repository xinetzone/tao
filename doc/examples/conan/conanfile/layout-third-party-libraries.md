# 为第三方库创建包时声明布局

请首先克隆源代码以重新创建此项目。你可以在 GitHub 的 examples2 仓库中找到它们：
```bash
$ git clone https://github.com/conan-io/examples2.git
$ cd examples2/examples/conanfile/layout/third_party_libraries
```

如果有一个项目，旨在为代码位于外部的第三方库创建包：
```bash
.
├── conanfile.py
└── patches
    └── mypatch.patch
```

`conanfile.py` 看起来是这样的：
```python
...

class Pkg(ConanFile):
    name = "hello"
    version = "1.0"
    exports_sources = "patches*"

    ...

    def layout(self):
        cmake_layout(self, src_folder="src")
        # if you are declaring your own layout, just declare:
        # self.folders.source = "src"

    def source(self):
        # we are inside a "src" subfolder, as defined by layout
        # the downloaded soures will be inside the "src" subfolder
        get(self, "https://github.com/conan-io/libhello/archive/refs/heads/main.zip",
            strip_root=True)
        # Please, be aware that using the head of the branch instead of an immutable tag
        # or commit is not a good practice in general as the branch may change the contents

        # patching, replacing, happens here
        patch(self, patch_file=os.path.join(self.export_sources_folder, "patches/mypatch"))

    def build(self):
        # If necessary, the build() method also has access to the export_sources_folder
        # for example if patching happens in build() instead of source()
        #patch(self, patch_file=os.path.join(self.export_sources_folder, "patches/mypatch"))
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
        ...
```

可以看到 `ConanFile.export_sources_folder` 属性可以提供对源代码根文件夹的访问：

在本地，它将是 `conanfile.py` 所在的文件夹

在缓存中，它将是“source”文件夹，该文件夹将包含 `CMakeLists.txt` 和 `patches` 的副本，而“source/src”文件夹将包含实际下载的源代码。

现在可以检查一切是否运行正常：
```bash
$ conan create .
...
Downloading main.zip
hello/1.0: Unzipping 3.7KB
Unzipping 100 %
...
[ 50%] Building CXX object CMakeFiles/hello.dir/src/hello.cpp.o
[100%] Linking CXX static library libhello.a
[100%] Built target hello
...
$ conan list hello/1.0
Local Cache
hello
    hello/1.0
```
