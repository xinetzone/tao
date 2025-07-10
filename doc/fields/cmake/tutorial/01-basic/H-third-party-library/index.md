# 包含第三方库

几乎所有非简单的项目都会有包含第三方库、头文件或程序的需求。CMake 支持使用 find_package() 函数查找这些工具的路径。这将从 CMAKE_MODULE_PATH 中的文件夹列表中搜索格式为"FindXXX.cmake"的 CMake 模块。在 Linux 系统上，默认搜索路径将包括 /usr/share/cmake/Modules 。

这个示例需要将 `boost` 库安装在系统的默认位置。

## 查找包

如上所述， find_package() 函数将从 CMAKE_MODULE_PATH 中的文件夹列表中搜索形式为 "FindXXX.cmake" 的 CMake 模块。find_package 的参数的确切格式将取决于你要查找的模块。这通常在 FindXXX.cmake 文件的顶部有文档记录。

下面是查找 boost 的基本示例：

```bash
find_package(Boost 1.46.1 REQUIRED COMPONENTS filesystem system)
```

参数如下：

- Boost - 库的名称。这是用于查找模块文件 FindBoost.cmake 的一部分
- 1.46.1 - 需要查找的 Boost 的最低版本
- REQUIRED - 告知模块这是必需的，如果找不到则失败
- COMPONENTS - 需要在库中查找的组件列表。

Boost 包含文件可以接受更多参数，并且也可以使用其他变量。更复杂的设置将在后面的示例中提供。

## 检查包是否找到

大多数包含的包会设置一个变量 XXX_FOUND ，该变量可用于检查该包是否在系统上可用。

在这个例子中，变量是 Boost_FOUND：

```bash
if(Boost_FOUND)
    message ("boost found")
    include_directories(${Boost_INCLUDE_DIRS})
else()
    message (FATAL_ERROR "Cannot find Boost")
endif()
```

## 导出的变量

在找到包之后，它通常会导出变量，这些变量可以告知用户在哪里找到库、头文件或可执行文件。类似于 XXX_FOUND 变量，这些是包特定的，并且通常在 FindXXX.cmake 文件的顶部进行文档说明。

本例中导出的变量包括：
- Boost_INCLUDE_DIRS - Boost 头文件路径。

在某些情况下，你也可以通过使用 ccmake 或 cmake-gui 检查这些变量，方法是检查缓存。

## 别名/导入目标

大多数现代的 CMake 库在其模块文件中导出 ALIAS 目标。导入目标的好处是它们也可以填充包含目录和链接库。

例如，从 CMake v3.5+版本开始，Boost 模块支持这一功能。类似于为库使用自己的 ALIAS 目标，模块中的 ALIAS 可以简化对已找到目标的引用。

在使用 Boost 的情况下，所有目标都使用 `Boost::` 标识符和子系统名称进行导出。例如，你可以使用：

- `Boost::boost` 仅用于头文件库
- `Boost::system` 用于 Boost 系统库。
- `Boost::filesystem` 用于文件系统库。

与您自己的目标一样，这些目标包含它们的依赖项，因此链接到 `Boost::filesystem` 将会自动添加 `Boost::boost` 和 `Boost::system` 的依赖项。

要链接到导入的目标，您可以使用以下方法：

```cmake
target_link_libraries( third_party_include
    PRIVATE
        Boost::filesystem
)
```

## 非别名目标

虽然大多数现代库使用导入目标，但并非所有模块都已更新。在库未更新的情况下，你通常会找到以下变量可用：
- `xxx_INCLUDE_DIRS` - 指向库的头文件目录的变量。
- `xxx_LIBRARY` - 指向库路径的变量。

然后可以将其添加到你的 target_include_directories 和 target_link_libraries 中，如下：

```cmake
# Include the boost headers
target_include_directories( third_party_include
    PRIVATE ${Boost_INCLUDE_DIRS}
)

# link against the boost libraries
target_link_libraries( third_party_include
    PRIVATE
    ${Boost_SYSTEM_LIBRARY}
    ${Boost_FILESYSTEM_LIBRARY}
)
```

## 构建示例

```bash
$ mkdir build

$ cd build/

$ cmake ..
-- The C compiler identification is GNU 4.8.4
-- The CXX compiler identification is GNU 4.8.4
-- Check for working C compiler: /usr/bin/cc
-- Check for working C compiler: /usr/bin/cc -- works
-- Detecting C compiler ABI info
-- Detecting C compiler ABI info - done
-- Check for working CXX compiler: /usr/bin/c++
-- Check for working CXX compiler: /usr/bin/c++ -- works
-- Detecting CXX compiler ABI info
-- Detecting CXX compiler ABI info - done
-- Boost version: 1.54.0
-- Found the following Boost libraries:
--   filesystem
--   system
boost found
-- Configuring done
-- Generating done
-- Build files have been written to: /home/matrim/workspace/cmake-examples/01-basic/H-third-party-library/build

$ make
Scanning dependencies of target third_party_include
[100%] Building CXX object CMakeFiles/third_party_include.dir/main.cpp.o
Linking CXX executable third_party_include
[100%] Built target third_party_include
matrim@freyr:~/workspace/cmake-examples/01-basic/H-third-party-library/build$ ./
CMakeFiles/          third_party_include
matrim@freyr:~/workspace/cmake-examples/01-basic/H-third-party-library/build$ ./third_party_include
Hello Third Party Include!
Path is not relative
$ cmake ..
-- The C compiler identification is GNU 4.8.4
-- The CXX compiler identification is GNU 4.8.4
-- Check for working C compiler: /usr/bin/cc
-- Check for working C compiler: /usr/bin/cc -- works
-- Detecting C compiler ABI info
-- Detecting C compiler ABI info - done
-- Check for working CXX compiler: /usr/bin/c++
-- Check for working CXX compiler: /usr/bin/c++ -- works
-- Detecting CXX compiler ABI info
-- Detecting CXX compiler ABI info - done
-- Boost version: 1.54.0
-- Found the following Boost libraries:
--   filesystem
--   system
boost found
-- Configuring done
-- Generating done
-- Build files have been written to: /home/matrim/workspace/cmake-examples/01-basic/H-third-party-library/build

$ make
Scanning dependencies of target third_party_include
[100%] Building CXX object CMakeFiles/third_party_include.dir/main.cpp.o
Linking CXX executable third_party_include
[100%] Built target third_party_include

$ ./third_party_include
Hello Third Party Include!
Path is not relative
```
