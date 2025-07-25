# 为开发者创建与 Conan 无关的依赖部署

使用 `full_deploy` 部署器，可以创建与 Conan 无关的依赖副本，开发者即使在没有在他们的计算机上安装 Conan 的情况下也可以使用。

对于大多数情况，常见的推荐流程是直接从 Conan 缓存使用 Conan 包：

![](https://docs.conan.io/2/_images/packages_from_cache.png)

然而，在某些情况下，将依赖部署到用户文件夹中可能很有用，这样依赖就可以位于该位置而不是 Conan 缓存中。这可以使用 Conan 部署器来实现。

通过例子来看。所有源代码都在 `examples2.0 Github` 仓库中
```bash
git clone https://github.com/conan-io/examples2.git
cd examples2/examples/extensions/deployers/development_deploy
```

在文件夹中我们可以找到以下 `conanfile.txt` :

```ini
[requires]
zlib/1.2.13

[tool_requires]
cmake/3.25.3

[generators]
CMakeDeps
CMakeToolchain

[layout]
cmake_layout
```

该文件夹还包含标准的 `CMakeLists.txt` 和 `main.cpp` 源文件，该文件可以创建链接 `zlib` 库的可执行文件。

可以安装 Debug 和 Release 依赖项，并使用以下命令部署本地包副本：
```bash
$ conan install . --deployer=full_deploy --build=missing
$ conan install . --deployer=full_deploy -s build_type=Debug --build=missing
```
这将创建以下文件夹：
```bash
├──src
├──build
│   ├──generators
|         └── ZLibConfig.cmake
├──full_deploy
│   ├──build
│   │   └──cmake
│   │       └──3.25.3
│   │           └──x86_64
│   │               ├──bin
│   │
│   └──host
│       └──zlib
│           └──1.2.13
│               ├──Debug
│               │   └──x86_64
│               │       ├──include
│               │       ├──lib
│               └──Release
│                   └──x86_64
│                       ├──include
│                       ├──lib
```

（请注意，您可以使用 `--deployer-folder` 参数来更改部署器的输出基础文件夹路径）

这个文件夹是完全自包含的。它包含必要的工具（如 `cmake` 可执行文件）、 `zlib` 的头文件和编译库，以及 `build/generators` 文件夹中的必要文件（如 `ZLibConfig.cmake` ），这些文件通过相对路径指向 `full_deploy` 中的二进制文件。

![](https://docs.conan.io/2/_images/independent_dependencies_deploy.png)

Conan 缓存可以被删除，甚至 Conan 可以被卸载，然后该文件夹可以移动到计算机的其他位置或复制到另一台计算机，前提是它具有相同的操作系统、编译器等配置。
```bash
$ cd ..
$ cp -R development_deploy /some/other/place
$ cd /some/other/place
```

文件可以被开发者使用，例如：

`````{tab-set}
````{tab-item} Windows
```bash
$ cd build
# Activate the environment to use CMake 3.25
$ generators\conanbuild.bat
$ cmake --version
cmake version 3.25.3
# Configure, should match the settings used at install
$ cmake .. -G \"Visual Studio 17 2022\" -DCMAKE_TOOLCHAIN_FILE=generators/conan_toolchain.cmake
$ cmake --build . --config Release
$ Release\compressor.exe
ZLIB VERSION: 1.2.13
```
````
````{tab-item} Linux
Linux 和 OSX 中的环境脚本不可重定位，因为它们包含绝对路径，而 sh shell [没有任何方法来为被调用的文件提供当前脚本目录的访问](https://stackoverflow.com/questions/29832037/how-to-get-script-directory-in-posix-sh/29835459#29835459)。

这不应该是一个大的阻碍，因为通过在生成器文件夹中使用“搜索和替换” sed 可以解决这个问题：
```bash
$ cd build/Release/generators
# Fix folders in Linux
$ sed -i 's,{old_folder},{new_folder},g' *
# Fix folders in MacOS
$ sed -i '' 's,{old_folder},{new_folder},g' *
$ source conanbuild.sh
$ cd ..
$ cmake --version
cmake version 3.25.3
$ cmake ../.. -DCMAKE_TOOLCHAIN_FILE=generators/conan_toolchain.cmake -DCMAKE_BUILD_TYPE=Release
$ cmake --build .
$ ./compressor
ZLIB VERSION: 1.2.13
```
````
`````

```{admonition} 最佳实践
这一流程是可行的，但这并不意味着它适用于大多数情况。它存在一些限制：

- 效率较低，需要额外复制依赖项
- 目前只有 `CMakeDeps` 和 `CMakeToolchain` 可以重定位。对于其他构建系统集成，请在 Github 上创建工单
- Linux 和 OSX 的 shell 脚本不能重定位，需要手动 sed
- 二进制可变性仅限于 Release/Debug。生成的文件专用于当前配置，更改其他设置（操作系统、编译器、架构）将需要不同的部署

一般情况下，建议正常使用缓存。这种“可移植开发部署”可能适用于分发看起来像 SDK 的最终产品，给未使用 Conan 的项目消费者。
```