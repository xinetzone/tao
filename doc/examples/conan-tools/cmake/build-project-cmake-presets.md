# CMakeToolchain: 使用 CMakePresets 构建你的项目

在这个[示例](https://docs.conan.io/2/examples/tools/cmake/cmake_toolchain/build_project_cmake_presets.html)中，将了解如何使用 `CMakeToolchain`、预定义的布局如 `cmake_layout` 以及 `CMakePresets` CMake 功能。

以基于模板 `cmake_exe` 的 C++ 项目为例，创建基本项目：

```bash
conan new cmake_exe -d name=foo -d version=1.0
```

## 生成工具链

项目中的配方声明了生成器“CMakeToolchain”。可以调用 `conan install` 来安装 `Release` 和 `Debug` 配置。Conan 将在相应的生成器文件夹中生成 `conan_toolchain.cmake`：

```bash
conan install .
conan install . -s build_type=Debug
```

## 使用 `CMakePresets` 构建项目

在您的 `CMakeLists.txt` 文件相同的文件夹中会生成 `CMakeUserPresets.json` 文件，因此您可以使用来自 `cmake >= 3.23` 的 `--preset` 参数，或者使用支持它的 IDE。

- `CMakeUserPresets.json` 包含位于相应生成器文件夹中的 `CMakePresets.json` 文件。
- `CMakePresets.json` 包含关于 `conan_toolchain.cmake` 位置的信息，甚至可以设置 `binaryDir` 输出目录。

````{attention}
本例中使用 CMake 预设。这需要 `CMake >= 3.23`，因为从 `CMakeUserPresets.json` 到 `CMakePresets.json` 的“include”功能只从该版本开始支持。如果你不想使用预设，可以使用类似：
```bash
cmake <path> -G <CMake generator> -DCMAKE_TOOLCHAIN_FILE=<path to
conan_toolchain.cmake> -DCMAKE_BUILD_TYPE=Release
```

如果你无法使用预设功能，Conan 每次运行 `conan install` 时都会显示确切的 CMake 命令。
````

如果你使用的是多构型生成器(multi-configuration generator)：
```bash
$ cmake --preset conan-default
$ cmake --build --preset conan-debug
$ build\Debug\foo.exe
foo/1.0: Hello World Release!

$ cmake --build --preset conan-release
$ build\Release\foo.exe
foo/1.0: Hello World Release!
```

如果你使用的是单构型生成器(single-configuration generator)：
```bash
$ cmake --preset conan-debug
$ cmake --build --preset conan-debug
$ ./build/Debug/foo
foo/1.0: Hello World Debug!


$ cmake --preset conan-release
$ cmake --build --preset conan-release
$ ./build/Release/foo
foo/1.0: Hello World Release!
```

请注意，不需要像[教程](https://docs.conan.io/2/tutorial/consuming_packages/the_flexibility_of_conanfile_py.html#consuming-packages-flexibility-of-conanfile-py-use-layout)中那样创建 `build/Release` 或 `build/Debug` 文件夹。输出目录由 `cmake_layout()` 声明，并由 CMake `Presets` 功能自动管理。

当你使用 `conan create` 命令在 Conan 缓存中构建包时，这种行为也会由 Conan（配合 `CMake >= 3.15`）自动管理。不需要 `CMake >= 3.23`。