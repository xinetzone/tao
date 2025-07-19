# CMake 核心概念

参考：[CMake 核心概念](https://cmake.org/cmake/help/book/mastering-cmake/chapter/Key%20Concepts.html)

许多 CMake 对象，如目标、目录和源文件，都与属性相关联。属性是附加到特定对象上的键值对。访问属性最通用的方式是通过 [`set_property`](https://cmake.org/cmake/help/latest/command/set_property.html#command:set_property) 和 [`get_property`](https://cmake.org/cmake/help/latest/command/get_property.html#command:get_property) 命令。这些命令允许您从任何具有属性的 CMake 对象中设置或获取属性。请参阅 [cmake-properties 手册](https://cmake.org/cmake/help/latest/manual/cmake-properties.7.html#manual:cmake-properties(7))以获取支持的属性列表。从命令行运行 cmake 命令并使用 `--help-property-list` 选项，可以获得 CMake 支持的属性完整列表。

## CMake 目标 

可能最重要的项目是目标(targets)。目标代表由 CMake 构建的可执行文件、库和实用工具。每个 [`add_library`](https://cmake.org/cmake/help/latest/command/add_library.html#command:add_library)、 [`add_executable`](https://cmake.org/cmake/help/latest/command/add_executable.html#command:add_executable) 和 [`add_custom_target`](https://cmake.org/cmake/help/latest/command/add_custom_target.html#command:add_custom_target) 命令都会创建目标。例如，以下命令将创建名为“foo”的目标，它是静态库，`foo1.c` 和 `foo2.c` 作为源文件。

```cmake
add_library(foo STATIC foo1.c foo2.c)
```

名称“foo”现在可以在项目的其他地方用作库名称，并且 CMake 会在需要时知道如何将名称扩展为库。库可以声明为特定类型，如 `STATIC`、 `SHARED`、 `MODULE`，或者不声明。`STATIC` 表示库必须作为静态库构建。同样，`SHARED` 表示它必须作为共享库构建。`MODULE` 表示库必须创建，以便可以动态加载到可执行文件中。模块库在许多平台上实现为共享库，但并非所有平台。因此，CMake 不允许其他目标链接到模块。如果未指定这些选项，则表示库可以构建为共享或静态。在这种情况下，CMake 使用变量 [`BUILD_SHARED_LIBS`](https://cmake.org/cmake/help/latest/variable/BUILD_SHARED_LIBS.html#variable:BUILD_SHARED_LIBS) 的设置来确定库应该是 `SHARED` 还是 `STATIC`。如果未设置，则 CMake 默认构建静态库。

同样，可执行文件也有一些选项。默认情况下，可执行文件将是传统的控制台应用程序，具有 `main` 入口点。可以通过指定 `WIN32` 选项来请求 Windows 系统上的 WinMain 入口点，同时在非 Windows 系统上保留 `main`。

除了存储类型，目标还跟踪通用属性。这些属性可以使用 [`set_target_properties`](https://cmake.org/cmake/help/latest/command/set_target_properties.html#command:set_target_properties) 和 [`get_target_property`](https://cmake.org/cmake/help/latest/command/get_target_property.html#command:get_target_property) 命令，或更通用的 [`set_property`](https://cmake.org/cmake/help/latest/command/set_property.html#command:set_property) 和 [`get_property`](https://cmake.org/cmake/help/latest/command/get_property.html#command:get_property) 命令来设置和检索。有用的属性是 [`LINK_FLAGS`](https://cmake.org/cmake/help/latest/prop_tgt/LINK_FLAGS.html#prop_tgt:LINK_FLAGS)，用于为特定目标指定额外的链接标志。目标存储它们链接的库列表，该列表使用 [`target_link_libraries`](https://cmake.org/cmake/help/latest/command/target_link_libraries.html#command:target_link_libraries) 命令设置。传递到此命令的名称可以是库、库的完整路径，或来自 [`add_library`](https://cmake.org/cmake/help/latest/command/add_library.html#command:add_library) 命令的库名称。目标还存储链接时使用的链接目录，以及构建后要执行的定制命令。

## 使用要求

CMake 还会从链接的库目标中传播“使用要求”。使用要求会影响 `<target>` 中源代码的编译。它们由链接目标上定义的属性指定。

例如，要指定链接到库时所需的包含目录，您可以执行以下操作：

```cmake
add_library(foo foo.cxx)
target_include_directories(foo PUBLIC
                           "${CMAKE_CURRENT_BINARY_DIR}"
                           "${CMAKE_CURRENT_SOURCE_DIR}"
                           )
```

现在任何链接到目标 `foo` 的内容都会自动将 `foo` 的二进制文件和源文件作为包含目录。通过“使用要求”引入的包含目录的顺序将与 [`target_link_libraries`](https://cmake.org/cmake/help/latest/command/target_link_libraries.html#command:target_link_libraries) 调用中目标的顺序相匹配。

对于 CMake 创建的每个库或可执行文件，它都会使用 `target_link_libraries` 命令跟踪该目标所依赖的所有库。例如：

```cmake
add_library(foo foo.cxx)
target_link_libraries(foo bar)

add_executable(foobar foobar.cxx)
target_link_libraries(foobar foo)
```

即使只对“foobar”显式指定了“foo”，它也会将库“foo”和“bar”链接到可执行文件“foobar”中。

## 使用目标指定优化或调试库

在 Windows 平台上，用户通常需要将调试库与调试库链接，优化库与优化库链接。CMake 通过 `target_link_libraries` 命令帮助满足这一要求，该命令接受可选的标记为 `debug` 或 `optimized` 的标志。如果库前面有 `debug` 或 `optimized`，那么该库将仅与适当的配置类型链接。例如：

```cmake
add_executable(foo foo.c)
target_link_libraries(foo debug libdebug optimized libopt)
```

在这种情况下，如果选择了调试构建，`foo` 将链接到 `libdebug`；如果选择了优化构建，则链接到 `libopt`。

## 对象库

大型项目通常将源文件组织成不同的组，可能位于不同的子目录中，每个组需要不同的包含目录和预处理器定义。为此用例，CMake 开发了对象库的概念。

对象库是一组源文件编译成的对象文件集合，这些对象文件不会被链接到库文件或制作成归档文件。相反，由 `add_library` 或 `add_executable` 创建的其他目标可以通过形如 `$<TARGET_OBJECTS:name>` 的表达式作为源来引用这些对象，其中`“name”`是由 `add_library` 调用创建的目标。例如：

```cmake
add_library(A OBJECT a.cpp)
add_library(B OBJECT b.cpp)
add_library(Combined $<TARGET_OBJECTS:A> $<TARGET_OBJECTS:B>)
```

将包含 `A` 和 `B` 对象文件到名为 `Combined` 的库中。对象库只能包含编译成对象文件的源文件（和头文件）。

## 源文件

源文件结构与目标类似。它存储文件名、扩展名以及与源文件相关的若干通用属性。与目标一样，你可以使用 [`set_source_files_properties`](https://cmake.org/cmake/help/latest/command/set_source_files_properties.html#command:set_source_files_properties) 和 [`get_source_file_property`](https://cmake.org/cmake/help/latest/command/get_source_file_property.html#command:get_source_file_property) 或更通用的版本来设置和获取属性。

## 目录、测试和属性

除了目标和源文件，你可能会偶尔处理其他对象，例如目录和测试。通常，这些交互表现为从这些对象中设置或获取属性（例如 [`set_directory_properties`](https://cmake.org/cmake/help/latest/command/set_directory_properties.html#command:set_directory_properties) 或 [`set_tests_properties`](https://cmake.org/cmake/help/latest/command/set_tests_properties.html#command:set_tests_properties) ）。
