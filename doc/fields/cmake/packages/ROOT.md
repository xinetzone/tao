# ROOT

ROOT 是一种用于高能物理的 C++ 工具包。它非常庞大。虽然你可能会发现很多（或大多数）示例都是错误的，但在 CMake 中使用它的方法确实有很多。以下是建议。

最重要的是，在较新的 ROOT 版本中，CMake 支持有了很多改进——使用 6.16 及以上版本会容易得多！如果你真的必须支持 6.14 或更早版本，请查看文末的部分。此外，6.20 版本也有进一步的改进，它表现得更像一个标准的 CMake 项目，并为目标等导出了 C++ 标准功能。

## 查找 ROOT

ROOT 6.10+ 支持配置文件发现，因此你可以直接执行：

```cmake
find_package(ROOT 6.16 CONFIG REQUIRED)
```

尝试查找 ROOT。如果你没有设置路径，可以将 `-DROOT_DIR=$ROOTSYS/cmake` 传递给查找 ROOT。 （但，实际上，你应该使用 `thisroot.sh` ）。

## 正确的方法（目标）

ROOT 6.12 及更早版本不会为导入的目标添加包含目录。ROOT 6.14+ 已经修正了这个错误，所需目标属性也在不断改进。这种方法正变得越来越容易使用（有关旧版 ROOT 的详细信息，请参阅本页末尾的示例）。

要链接，只需选择您想要使用的库：

```cmake
add_executable(RootSimpleExample SimpleExample.cxx)
target_link_libraries(RootSimpleExample PUBLIC ROOT::Physics)
```

如果您想查看默认列表，请在命令行上运行 `root-config --libs`。

## 旧的全局方式

ROOT 提供了设置 ROOT [项目的工具](https://root.cern.ch/how/integrate-root-my-project-cmake)，您可以使用 `include("${ROOT_USE_FILE}")` 激活它。这将自动为您创建难看的目录级别和全局变量。它将节省您一些设置时间，但如果您尝试做一些复杂的事情，它将浪费大量时间。只要您不是在制作库，对于简单的脚本来说可能就可以了。包含和标志是全局设置的，但您仍然需要自己链接到 `${ROOT_LIBRARIES}` ，以及可能还需要 `ROOT_EXE_LINKER_FLAGS` （在链接之前，您必须先 `separate_arguments` ，否则如果存在多个标志（如在 macOS 上）将会出现错误）。此外，在 6.16 之前，您必须手动修复一个关于空格的 bug。

这会是什么样子：

```cmake
# Sets up global settings
include("${ROOT_USE_FILE}")

# This is required for ROOT < 6.16
# string(REPLACE "-L " "-L" ROOT_EXE_LINKER_FLAGS "${ROOT_EXE_LINKER_FLAGS}")

# This is required on if there is more than one flag (like on macOS)
separate_arguments(ROOT_EXE_LINKER_FLAGS)

add_executable(RootUseFileExample SimpleExample.cxx)
target_link_libraries(RootUseFileExample PUBLIC ${ROOT_LIBRARIES}
                                                ${ROOT_EXE_LINKER_FLAGS})
```

## 组件

Find ROOT 允许你指定组件。它会将你列出的任何内容添加到 `${ROOT_LIBRARIES}` 中，因此你可能想使用那个来构建自己的目标，以避免两次列出组件。这并没有解决依赖关系；如果列出了 `RooFit` 但没有列出 `RooFitCore` ，这是一个错误。如果你链接到 `ROOT::RooFit` 而不是 `${ROOT_LIBRARIES}` ，那么 `RooFitCore` 就不是必需的。

## 字典生成

字典生成是 ROOT 在 C++中缺少反射功能时的一种解决方案。它允许 ROOT 学习你的类的详细信息，以便能够保存它、在 Cling 解释器中显示方法等。为了支持字典生成，你的源代码需要进行以下修改：
- 你的类定义应以 `ClassDef(MyClassName, 1)` 结尾
- 你的类实现中应该包含 `ClassImp(MyClassName)`

ROOT 提供 `rootcling` 和 `genreflex` （一个 `rootcling` 的遗留接口）二进制文件，这些文件生成构建字典所需的源文件。它还定义了 `root_generate_dictionary` ，一个 CMake 函数，用于在构建过程中调用 `rootcling` 。

要加载这个函数，首先包含 ROOT 宏：

```cmake
include("${ROOT_DIR}/modules/RootNewMacros.cmake")
# For ROOT versions than 6.16, things break
# if nothing is in the global include list!
if (${ROOT_VERSION} VERSION_LESS "6.16")
    include_directories(ROOT_NONEXISTENT_DIRECTORY_HACK)
endif()
```

添加 `if(...)` 条件是为了修复 `NewMacros` 文件中的一个错误，该错误会导致如果没有至少一个全局包含目录或 `inc` 文件夹，字典生成会失败。我这里包含了一个不存在的目录只是为了让它能工作。没有 `ROOT_NONEXISTENT_DIRECTORY_HACK` 目录。

rootcling 使用特殊的头文件，通过[特定的格式](https://root.cern.ch/selecting-dictionary-entries-linkdefh)来确定要为哪些部分生成字典。这个文件的名字可以有任意的前缀，但必须以 LinkDef.h 结尾。一旦你写好了这个头文件，就可以调用字典生成函数。

## 手动构建字典

有时，你可能希望让 ROOT 生成字典，然后自己将源文件添加到你的库目标中。你可以调用 `root_generate_dictionary` ，传入字典的名称，例如 `G__Example` ，任何需要的头文件，最后是特殊的 `LinkDef.h` 文件，列在 `LINKDEF` 之后：

```cmake
root_generate_dictionary(G__Example Example.h LINKDEF ExampleLinkDef.h)
```

这个命令将创建三个文件：

- `${NAME}.cxx` ：当你构建库时，这个文件应该包含在你的源文件中。
- `lib{NAME}.rootmap` （移除了 `G__` 前缀）：纯文本格式的 `rootmap` 文件
- `lib{NAME}_rdict.pcm` (已移除 `G__` 前缀): 一个 [ROOT 预编译模块文件](https://inspirehep.net/literature/1413967) 目标名称（ `${NAME}` ）由字典名称决定；如果字典名称以 `G__` 开头，则会被移除。否则，直接使用该名称。

最后两个输出文件必须与库输出文件相邻。这是通过检查 `CMAKE_LIBRARY_OUTPUT_DIRECTORY` 实现的（它不会获取本地目标设置）。如果你设置了 `libdir` 但没有设置（全局）安装位置，你还需要将 `ARG_NOINSTALL` 设置为 `TRUE`。

### 使用现有目标构建字典

无需手动将生成的添加到库源文件中，您可以通过传递 `MODULE` 参数让 ROOT 帮您完成。该参数应指定一个现有构建目标的名称：

```cmake
add_library(Example)
root_generate_dictionary(G__Example Example.h MODULE Example LINKDEF ExampleLinkDef.h)
```

字典的完整名称（例如 `G__Example` ）不应与 `MODULE` 参数完全相同。

## 使用旧版 ROOT 

如果你真的不得不使用旧版 ROOT，你需要类似这样：

```cmake
# ROOT targets are missing includes and flags in ROOT 6.10 and 6.12
set_property(TARGET ROOT::Core PROPERTY
    INTERFACE_INCLUDE_DIRECTORIES "${ROOT_INCLUDE_DIRS}")

# Early ROOT does not include the flags required on targets
add_library(ROOT::Flags_CXX IMPORTED INTERFACE)


# ROOT 6.14 and earlier have a spacing bug in the linker flags
string(REPLACE "-L " "-L" ROOT_EXE_LINKER_FLAGS "${ROOT_EXE_LINKER_FLAGS}")

# Fix for ROOT_CXX_FLAGS not actually being a CMake list
separate_arguments(ROOT_CXX_FLAGS)
set_property(TARGET ROOT::Flags_CXX APPEND PROPERTY
    INTERFACE_COMPILE_OPTIONS ${ROOT_CXX_FLAGS})

# Add definitions
separate_arguments(ROOT_DEFINITIONS)
foreach(_flag ${ROOT_EXE_LINKER_FLAG_LIST})
    # Remove -D or /D if present
    string(REGEX REPLACE [=[^[-//]D]=] "" _flag ${_flag})
    set_property(TARGET ROOT::Flags APPEND PROPERTY INTERFACE_LINK_LIBRARIES ${_flag})
endforeach()

# This also fixes a bug in the linker flags
separate_arguments(ROOT_EXE_LINKER_FLAGS)
set_property(TARGET ROOT::Flags_CXX APPEND PROPERTY
    INTERFACE_LINK_LIBRARIES ${ROOT_EXE_LINKER_FLAGS})

# Make sure you link with ROOT::Flags_CXX too!
```
