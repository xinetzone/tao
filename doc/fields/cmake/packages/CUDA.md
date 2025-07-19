# CUDA

CUDA 支持有两种方式。新方法在 CMake 3.8（Windows 为 3.9）中引入，应强烈优先于旧方法——我提及旧方法是因为某个旧包很可能包含它。与旧语言不同，CUDA 支持正在快速发展，而构建 CUDA 很困难，因此我建议您要求使用非常新的 CMake 版本！CMake 3.17 和 3.18 针对 CUDA 有很多直接改进。

关于 CUDA 和现代 CMake 的一个好资源是 CMake 开发者 Robert Maynard [在 GTC 2017 上的演讲](http://on-demand.gputechconf.com/gtc/2017/presentation/S7438-robert-maynard-build-systems-combining-cuda-and-machine-learning.pdf)。

## 添加 CUDA 语言

启用 CUDA 支持有两种方法。如果 CUDA 不是可选的：

```cmake
project(MY_PROJECT LANGUAGES CUDA CXX)
```

您可能还想在这里列出 CXX 。如果 CUDA 是可选的，您需要将这个条件性地放在某处：

```cmake
enable_language(CUDA)
```

您可以通过检查 `CMAKE_CUDA_COMPILER` （在 CMake 3.11 之前缺失）来查看 CUDA 是否存在。

您可以检查像 `CMAKE_CUDA_COMPILER_ID` （对于 `nvcc`，这是 "NVIDIA" ，Clang 在 CMake 3.18 中添加）这样的变量。您可以使用 `CMAKE_CUDA_COMPILER_VERSION` 来检查版本。

## CUDA 相关变量

许多名称中带有 CXX 的变量都有以 CUDA 代替的 CUDA 版本。例如，要设置 CUDA 所需的 C++标准，

```cmake
if(NOT DEFINED CMAKE_CUDA_STANDARD)
    set(CMAKE_CUDA_STANDARD 11)
    set(CMAKE_CUDA_STANDARD_REQUIRED ON)
endif()
```

如果你在寻找 CUDA 的标准级别，在 CMake 3.17 中增加了一系列新的编译器特性，比如 `cuda_std_11`。这些特性与 cxx 版本一样，能为你带来同样的好处。

### 添加库/可执行文件

这部分很简单；只要你对 CUDA 文件使用 `.cu`，你就可以像平时一样直接添加库。

你也可以使用可分离编译：

```cmake
set_target_properties(mylib PROPERTIES
                            CUDA_SEPARABLE_COMPILATION ON)
```

你也可以直接使用 `CUDA_PTX_COMPILATION` 属性来创建 PTX 文件。

### 针对架构

当你构建 CUDA 代码时，通常应该针对某个架构。如果你不这样做，你会为最低支持的架构编译 PTX，这提供了基本指令，但在运行时编译，可能导致加载速度明显变慢。

所有显卡都有一个架构级别，比如“7.2”。你有两个选择；第一个是代码级别；这会向正在编译的代码报告一个版本，比如“5.0”，并且会利用到 5.0 版本的所有功能，但不会超过（假设代码写得很好/标准库）。然后是目标架构，它必须等于或大于代码架构。它需要与你的目标显卡的主版本号相同，并且要等于或小于目标显卡。所以 7.0 是我们 7.2 显卡的一个常见选择。最后，你也可以生成 PTX；这将在所有未来的显卡上工作，但会即时编译。

在 CMake 3.18 中，目标架构的设置变得非常简单。如果你的版本范围包含 3.18 或更高版本，你将使用 CMAKE_CUDA_ARCHITECTURES 变量和目标上的 CUDA_ARCHITECTURES 属性。你可以列出值（不包括 . ），例如 50 代表架构 5.0。这将为真实（SASS）和虚拟架构（PTX）生成代码。传递 '50-real' 值将仅生成 SASS，而传递 '50-virtual' 值将仅生成 PTX。如果设置为 OFF，则不会传递架构。

在 CMake 3.24 中，架构值已扩展以支持用户友好的值 'native'、'all' 和 'all-major'。

### 与目标工作

使用目标应该与 CXX 类似，但存在一个问题。如果你包含一个包含编译器选项（标志）的目标，大多数情况下，这些选项不会被正确的包含保护（而且它们具有正确 CUDA 封装的几率更小）。以下是正确的编译器选项行的示例：

```cmake
set(opt "$<$<BUILD_INTERFACE:$<COMPILE_LANGUAGE:CXX>>:-fopenmp>$<$<BUILD_INTERFACE:$<COMPILE_LANGUAGE:CUDA>>:-Xcompiler=-fopenmp>")
```

然而，如果你使用几乎任何 find_package，并且使用 Modern CMake 的 target 和继承方法，一切都会崩溃。我是吃一堑长一智。

目前，这里有一个相当合理的解决方案，只要你知道未别名化的目标名称。这是一个函数，通过使用 CUDA 编译器来包装标志，以修复仅针对 C++的目标：

```cmake
function(CUDA_CONVERT_FLAGS EXISTING_TARGET)
    get_property(old_flags TARGET ${EXISTING_TARGET} PROPERTY INTERFACE_COMPILE_OPTIONS)
    if(NOT "${old_flags}" STREQUAL "")
        string(REPLACE ";" "," CUDA_flags "${old_flags}")
        set_property(TARGET ${EXISTING_TARGET} PROPERTY INTERFACE_COMPILE_OPTIONS
            "$<$<BUILD_INTERFACE:$<COMPILE_LANGUAGE:CXX>>:${old_flags}>$<$<BUILD_INTERFACE:$<COMPILE_LANGUAGE:CUDA>>:-Xcompiler=${CUDA_flags}>"
            )
    endif()
endfunction()
```

### 有用的变量 

即使不启用 CUDA 语言，您也可以使用 FindCUDAToolkit 来查找各种有用的目标和变量。

```cmake
cmake_minimum_required(VERSION 3.17)
project(example LANGUAGES CXX)

find_package(CUDAToolkit REQUIRED)
add_executable(uses_cublas source.cpp)
target_link_libraries(uses_cublas PRIVATE CUDA::cublas)
```

使用 `find_package(CUDAToolkit)` 提供的变量：

- `CUDAToolkit_BIN_DIR`: 存放 nvcc 可执行文件的目录
- `CUDAToolkit_INCLUDE_DIRS`: 包含内置 Thrust 等头文件的目录列表
- `CUDAToolkit_LIBRARY_DIR`: 存放 CUDA 运行时库的目录

启用 CUDA 语言提供的变量：

- `CMAKE_CUDA_COMPILER`: 带位置的 NVCC
- `CMAKE_CUDA_TOOLKIT_INCLUDE_DIRECTORIES`: 内置 Thrust 等的位置

````{note}
请注意 FindCUDA 已弃用，但对于 CMake < 3.18 的版本，以下函数需要 FindCUDA：
- CUDA 版本检查 / 选择版本
- 架构检测（注意：3.12 版本部分修复了这个问题）
- 从非 `-.cu` 文件链接 CUDA 库
````

## 经典 FindCUDA [警告：不建议使用] （仅作参考用）

如果你需要支持较旧版本的 CMake，我建议至少将 CMake 3.9 版本中的 FindCUDA 包含到你的 cmake 文件夹中（可以查看 CLIUtils github 组织的 [git 仓库](https://github.com/CLIUtils/cuda_support)）。你需要两个新增加的功能： CUDA_LINK_LIBRARIES_KEYWORD 和 cuda_select_nvcc_arch_flags ，以及更新的架构和 CUDA 版本。

要使用旧的 CUDA 支持，你使用 find_package :

```cmake
find_package(CUDA 7.0 REQUIRED)
message(STATUS "Found CUDA ${CUDA_VERSION_STRING} at ${CUDA_TOOLKIT_ROOT_DIR}")
```

你可以通过 CUDA_NVCC_FLAGS （列表追加）控制 CUDA 标志，并通过 CUDA_SEPARABLE_COMPILATION 控制可分离编译。你还需要确保 CUDA 能良好运行，并向目标添加关键字（CMake 3.9+）：

```cmake
set(CUDA_LINK_LIBRARIES_KEYWORD PUBLIC)
```

你可能还想允许用户检查其当前硬件的架构标志：

```cmake
cuda_select_nvcc_arch_flags(ARCH_FLAGS) # optional argument for arch to add
```
