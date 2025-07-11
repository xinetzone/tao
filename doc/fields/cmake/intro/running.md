# 运行 CMake

在编写 CMake 之前，确保你知道[如何运行](https://cliutils.gitlab.io/modern-cmake/chapters/intro/running.html)它来构建东西。这对于几乎所有 CMake 项目都是真实的，几乎涵盖了所有内容。

## 构建项目

除非另有说明，您应该始终创建构建目录（`build`）并从该目录进行构建。技术上可以执行源码构建，但您必须小心不要覆盖文件或将它们添加到 git 中，所以最好不要这样做。

经典的 CMake 构建流程（TM）：
```bash
~/package $ mkdir build
~/package $ cd build
~/package/build $ cmake ..
~/package/build $ make
```

如果您希望，可以用 `cmake --build .` 替换 `make` 行，它将调用 `make` 或您正在使用的任何构建工具。如果您使用的是较新版本的 CMake（通常您应该使用较新版本，除非您需要检查与旧版 CMake 的兼容性），您可以这样做：

```bash
~/package $ cmake -S. -Bbuild
~/package $ cmake --build build
```

（`-S` 是包含 `CMakeLists.txt` 的源位置， `-B` 是构建目录，将会被创建。）这些命令中的任何一个都可以进行安装：

```bash
# From the build directory (pick one)

~/package/build $ make install
~/package/build $ cmake --build . --target install
~/package/build $ cmake --install . # CMake 3.15+ only

# From the source directory (pick one)

~/package $ make -C build install
~/package $ cmake --build build --target install
~/package $ cmake --install build # CMake 3.15+ only
```

那么你应该使用哪一套方法呢？只要你不忘记将构建目录作为参数输入，从源目录外操作更简洁，而从源目录进行源代码修改更方便。你应该尝试习惯使用 `--build`，这样你就可以不再仅仅使用 `make` 来构建。请注意，从构建目录工作在历史上更为常见，并且某些工具和命令（包括 CTest <3.20）仍然需要从构建目录运行。

为了说明清楚，你可以从构建目录指向源目录，或者从任何地方指向现有的构建目录。

如果你使用 `cmake --build` 而不是直接调用底层构建系统，你可以使用 `-v` 进行详细构建（CMake 3.14+）、 `-j N` 在 N 核心上并行构建（CMake 3.12+），以及 `--target` （任何版本的 CMake）或 `-t` （CMake 3.15+）来选择目标。否则，这些命令在不同构建系统中有所不同，例如 `VERBOSE=1 make` 和 `ninja -v`。你也可以使用环境变量来设置这些，例如 `CMAKE_BUILD_PARALLEL_LEVEL` （CMake 3.12+）和 `VERBOSE` （CMake 3.14+）。

## 选择编译器

选择编译器必须在空目录中的第一次运行时完成。这并非 CMake 语法本身，但你可能不熟悉它。要选择 Clang：
```bash
~/package/build $ CC=clang CXX=clang++ cmake ..
```

这设置了 bash 中的环境变量 CC 和 CXX，CMake 会遵循这些变量。这仅设置当前这一行，但这是你唯一需要使用这些变量的时机；之后 CMake 会继续使用它从这些值中推断出的路径。

## 选择生成器

你可以使用多种工具进行构建； `make` 通常为默认选项。要查看你的系统上 CMake 知晓的所有工具，请运行

```bash
~/package/build $ cmake --help
```

你可以选择一个工具，使用 `-G"My Tool"` （如果工具名包含空格，则只需加引号）。在目录中第一次调用 CMake 时，就像选择编译器一样选择一个工具。你可以创建多个构建目录，例如 build/ 和 buildXcode 。你可以设置环境变量 `CMAKE_GENERATOR` 来控制默认生成器（CMake 3.15+）。请注意，makefiles 仅在你明确指定线程数（例如 make -j2 ）时才会并行运行，而 Ninja 会自动并行运行。在 CMake 的较新版本中，你可以直接向 `cmake --build .` 命令传递并行化选项，例如 `-j2`。

## 设置选项

你使用 `-D` 在 CMake 中设置选项。你可以使用 `-L` 查看选项列表，或使用 `-LH` 查看带人类可读帮助的列表。如果你没有列出源/构建目录，列表将不会重新运行 CMake（使用 `cmake -L` 而不是 `cmake -L .` ）。

## 详细和部分构建

尽管并非所有构建工具都支持，但你可以通过选择以下一项来获取详细构建信息：

```bash
~/package $ cmake --build build --verbose # CMake 3.14+ only
~/package/build $ VERBOSE=1 make
```

实际上，你可以写 `make VERBOSE=1`，make 也会做正确的事情，尽管这是 make 的特性，而不是命令行的一般功能。

你也可以通过指定目标来构建构建的一部分，例如在 CMake 中定义的库或可执行文件的名称，`make` 将会只构建该目标。

## 选项

CMake 支持缓存选项。CMake 中的变量可以被标记为“缓存”，这意味着当它被遇到时，会被写入缓存（构建目录中名为 `CMakeCache.txt` 的文件）。你可以使用 `-D` 在命令行上预设（或更改）缓存选项的值。当 CMake 查找缓存变量时，它会使用现有值，并且不会覆盖它。

### 标准选项

这些是大多数软件包常用的 CMake 选项：

- `-DCMAKE_BUILD_TYPE= `从 Release、RelWithDebInfo、Debug 或有时更多的选项中选择。
- `-DCMAKE_INSTALL_PREFIX=` 安装位置。UNIX 系统安装通常为 `/usr/local` （默认），用户目录通常为 `~/.local`，或者可以选择文件夹。
- `-DBUILD_SHARED_LIBS=` 你可以设置这个 `ON` 或 `OFF` 来控制共享库的默认设置（虽然作者可以明确选择其中一个而不是使用默认设置）
- `-DBUILD_TESTING=` 是常见的启用测试的名称，尽管并非所有软件包都使用它，有时也有充分的理由。

## 调试 CMake 文件

我们已经提到过构建时的详细输出，但你也可以看到详细的 CMake 配置输出。`--trace` 选项会打印 CMake 运行时的每一行。由于这非常详细，CMake 3.7 添加了 `--trace-source="filename"`，它会在运行时打印出你感兴趣文件中执行的每一行。如果你选择要调试的文件名（通常在调试 `CMakeLists.txt` 时通过选择父目录，因为它们都有相同的名称），你只需要看到该文件中运行的行。非常实用！
