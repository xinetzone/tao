# CCache 和工具

在各个版本中，帮助您编写良好代码的常用工具已获得 CMake 的支持。这通常以属性和匹配的 `CMAKE_*` 初始化变量的形式出现。该功能并非旨在与某个特殊程序绑定，而是任何在行为上有所相似的程序。

所有这些都采用 `;` 分隔的值（CMake 中的标准列表），描述您应该在目标源文件上运行的程序和选项。

## CCache

将 `CMAKE_<LANG>_COMPILER_LAUNCHER` 变量或 `<LANG>_COMPILER_LAUNCHER` 属性设置在目标上，使用类似 CCache 的方式来“包装”目标的编译。CCache 的支持在 CMake 的最新版本中不断扩展。实际上，这通常看起来像这样：

```cmake
find_program(CCACHE_PROGRAM ccache)
if(CCACHE_PROGRAM)
    set(CMAKE_CXX_COMPILER_LAUNCHER "${CCACHE_PROGRAM}")
    set(CMAKE_CUDA_COMPILER_LAUNCHER "${CCACHE_PROGRAM}") # CMake 3.9+
endif()
```

## 工具

将以下属性或 `CMAKE_*` 初始化变量设置为工具的命令行。其中大部分仅限于使用 `make` 或 `ninja` 生成器的 C 或 CXX。
```
<LANG>_CLANG_TIDY: CMake 3.6+

<LANG>_CPPCHECK

<LANG>_CPPLINT

<LANG>_INCLUDE_WHAT_YOU_USE
```

## Clang tidy

这是运行 clang-tidy 的命令行，以列表形式（记住，分号分隔的字符串是列表）。

这里是一个使用 Clang-Tidy 的简单示例：

```bash
~/package # cmake -S . -B build-tidy -DCMAKE_CXX_CLANG_TIDY="$(which clang-tidy);-fix"
~/package # cmake --build build -j 1
```

`-fix` 部分是可选的，它会修改你的源文件以尝试修复 tidy 提出的警告。如果你在一个 git 仓库中工作，这相当安全，因为你可以看到发生了什么变化。但是，**请确保不要并行运行你的 `makefile/ninja` 构建**！如果它试图两次修复同一个头文件，这根本不会很好地工作。

如果你希望明确使用目标形式以确保只在本地目标上调用，你可以设置一个变量（比如 `DO_CLANG_TIDY` 这样），而不是使用 `CMAKE_CXX_CLANG_TIDY` 变量，然后在创建目标属性时将其添加到目标属性中。你可以像这样在你的路径中找到 clang-tidy：

```cmake
find_program(
    CLANG_TIDY_EXE
    NAMES "clang-tidy"
    DOC "Path to clang-tidy executable"
)
```

## 包含你所使用的

这是一个使用包含你所使用的示例。首先，你需要拥有这个工具，比如在一个 docker 容器中或使用 brew（macOS）的 brew install include-what-you-use 。然后，你可以将这个传递到你的构建中，而无需修改源代码：

```bash
~/package # cmake -S . -B build-iwyu -DCMAKE_CXX_INCLUDE_WHAT_YOU_USE=include-what-you-use
```

最后，您可以收集输出并（可选地）应用修复：

```bash
~/package # cmake --build build-iwyu 2> iwyu.out
~/package # fix_includes.py < iwyu.out
```

（您应该先检查修复，或在应用后进行修改！）

## 链接您使用的文件 #

有布尔目标属性 `LINK_WHAT_YOU_USE`，它会在链接时检查多余文件。

## Clang-format

不幸的是，Clang-format 并没有与 CMake 真正集成。你可以创建一个自定义目标（参见[这篇帖子](https://github.com/kbenzie/git-cmake-format)），或者手动运行它。有一个我并没有真正尝试过的有趣项目在这里；它添加了一个格式目标，甚至确保你无法提交未格式化的文件。

在 git 仓库中的 bash 里，以下两行命令可以实现这一点（假设你有 `.clang-format` 文件）：

```bash
$ git ls-files -- '*.cpp' '*.h' | xargs clang-format -i -style=file
$ git diff --exit-code --color
```
