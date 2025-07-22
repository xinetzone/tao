# CMakeToolchain: 使用 Conan 生成的预设扩展你的 CMakePresets 

在这个[示例](https://docs.conan.io/2/examples/tools/cmake/cmake_toolchain/extend_own_cmake_presets.html)中，将看到如何扩展你自己的 `CMakePresets` 以包含 Conan 生成的预设。

请首先克隆源代码以重新创建此项目。你可以在 GitHub 的 examples2 仓库中找到它们：

```bash
git clone https://github.com/conan-io/examples2.git
cd examples2/examples/tools/cmake/cmake_toolchain/extend_own_cmake_presets
```

请打开 `conanfile.py` 并查看它是如何设置 `tc.user_presets_path = 'ConanPresets.json'` 的。通过修改 `CMakeToolchain` 的这个属性，你可以更改生成的预设的默认文件名。

```python
def generate(self):
    tc = CMakeToolchain(self)
    tc.user_presets_path = 'ConanPresets.json'
    tc.generate()
    ...
```

现在你可以提供你自己的 `CMakePresets.json`，除了 `CMakeLists.txt`：

```{code-block} json
:caption: CMakePresets.json

{
"version": 4,
"include": ["./ConanPresets.json"],
"configurePresets": [
    {
        "name": "default",
        "displayName": "multi config",
        "inherits": "conan-default"
    },
    {
        "name": "release",
        "displayName": "release single config",
        "inherits": "conan-release"
    },
    {
        "name": "debug",
        "displayName": "debug single config",
        "inherits": "conan-debug"
    }
],
"buildPresets": [
    {
        "name": "multi-release",
        "configurePreset": "default",
        "configuration": "Release",
        "inherits": "conan-release"
    },
    {
        "name": "multi-debug",
        "configurePreset": "default",
        "configuration": "Debug",
        "inherits": "conan-debug"
    },
    {
        "name": "release",
        "configurePreset": "release",
        "configuration": "Release",
        "inherits": "conan-release"
    },
    {
        "name": "debug",
        "configurePreset": "debug",
        "configuration": "Debug",
        "inherits": "conan-debug"
    }
]
}
```

注意 `"include": ["./ConanPresets.json"]`, 和每个预设 `inherits` 都是 Conan 生成的。

现在可以为 `Release` 和 `Debug`（以及其他配置，如果需要的话，借助 `build_folder_vars` ）进行安装：

```bash
$ conan install .
$ conan install . -s build_type=Debug
```

并使用自己的、扩展了 Conan 生成预设的配置来构建和运行应用程序：

```bash
# Linux (single-config, 2 configure, 2 builds)
$ cmake --preset debug
$ cmake --build --preset debug
$ ./build/Debug/foo
> Hello World Debug!

$ cmake --preset release
$ cmake --build --preset release
$ ./build/Release/foo
> Hello World Release!

# Windows VS (Multi-config, 1 configure 2 builds)
$ cmake --preset default

$ cmake --build --preset multi-debug
$ build\\Debug\\foo
> Hello World Debug!

$ cmake --build --preset multi-release
$ build\\Release\\foo
> Hello World Release!
```
