# cmake-conan

[cmake-conan](https://github.com/conan-io/cmake-conan) 是 Conan C 和 C++包管理器的 CMake 依赖提供者。

前提条件：
- CMake 3.24
- Conan 2.0.5
- 基于 CMake 的项目，其中包含 `conanfile.txt` 或 `conanfile.py` 来列出所需的依赖项。

首先，在 `develop2` 分支上克隆这个仓库。
```bash
git clone https://github.com/conan-io/cmake-conan.git -b develop2
```

## 示例项目

仓库包含 `CMakeLists.txt`，其中有依赖 `fmt` 的示例项目。

```bash
cd cmake-conan/example
cmake -G Ninja -B build -S . -DCMAKE_PROJECT_TOP_LEVEL_INCLUDES=../conan_provider.cmake -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release
```

## 在你的项目中

1. 确保你在项目的根目录放置 `conanfile.txt` 或 `conanfile.py`，列出你的需求。
2. 当第一次使用 CMake 配置项目时，传递 `-DCMAKE_PROJECT_TOP_LEVEL_INCLUDES=[path-to-cmake-conan]/conan_provider.cmake`。这将确保 `conan install` 从 CMake 内部被调用。这种集成不需要对你的 `CMakeLists.txt` 脚本进行任何更改。
```bash
cd [your-project]
mkdir build
cmake -G Ninja -B build -S . -DCMAKE_PROJECT_TOP_LEVEL_INCLUDES=[path-to-cmake-conan]/conan_provider.cmake -DCMAKE_BUILD_TYPE=Release
```

## 已知的 Conan 2.0 限制

- 仅指定了 CMakeDeps 生成器——对于原本由 CMakeToolchain 提供的构建设置（例如编译器本身或其他全局构建设置），请根据[文档](https://docs.conan.io/2/tutorial/consuming_packages/build_simple_cmake_project.html)单独调用 Conan。
- 目前，这仅适用于 Conan 能够满足对 CMake 的 `find_package` 的调用。对于逻辑超出 `find_package` 的依赖项，例如通过直接调用  `find_program` 、 `find_library`、 `find_path` 或 `find_file`，这些可能无法正常工作。
- 在使用单配置 CMake 生成器时，你必须指定有效的 `CMAKE_BUILD_TYPE` （不能留空）
- 目前仅支持在最常见的平台上使用最流行的编译器来派生 Conan 设置。

## 自定义 Conan 配置文件

CMake-Conan 依赖提供器会创建 Conan 配置文件，其中的设置（ os , arch , compiler , build_type ）会从 CMake 检测到的当前构建中获取。Conan 使用两个配置文件来处理依赖关系，分别是主机配置文件和构建配置文件。你可以在这里了解更多信息。在 CMake-Conan 中，默认行为如下：
- Conan 主机配置文件：从 CMake 检测到的设置。对于 CMake 无法检测到的任何内容，它会回退到 default Conan 配置文件。
- Conan 构建配置文件： default Conan 配置文件。

请注意，要使上述功能正常工作，必须已存在 `default` 配置文件。如果没有，cmake-conan 将调用 Conan 的自动检测机制，该机制尝试猜测系统默认设置。

如果您需要自定义配置文件，可以通过修改 `CONAN_HOST_PROFILE` 和 `CONAN_BUILD_PROFILE` 的值，并将它们作为 CMake 缓存变量传递。以下是一些示例：
- `-DCONAN_HOST_PROFILE="default;auto-cmake"`：执行上述描述的自动检测，对于其他任何情况则回退到默认配置文件（默认行为）。
- `-DCONAN_HOST_PROFILE=clang16`：不执行自动检测，并使用必须存在于 Conan 配置文件文件夹中的 clang16 配置文件（参见[文档](https://docs.conan.io/2.0/reference/commands/profile.html?highlight=profiles%20folder#conan-profile-list)）。
- `-DCONAN_BUILD_PROFILE="/path/to/profile"`: 或者，提供可能位于文件系统任何位置的配置文件路径。
- `-DCONAN_HOST_PROFILE="default;custom"`: 分号分隔的配置文件列表。将使用复合配置文件（参见[文档](https://docs.conan.io/2.0/reference/commands/install.html#profiles-settings-options-conf)）- 从左到右组合，其中右侧具有最高优先级。

## 自定义 Conan 安装的调用

CMake-Conan 依赖提供器将自动检测并传递上述描述的配置信息。如果需要进一步自定义 `conan install` 命令的调用，可以使用 `CONAN_INSTALL_ARGS` 变量。
- 默认情况下，`CONAN_INSTALL_ARGS` 初始化为传递 `--build=missing`。如果你自定义这个变量，请注意，除非你指定 `--build` 标志，否则 Conan 将恢复其默认行为。
- 有两个参数是为依赖提供者实现保留的，不得设置： `conanfile.txt|.py` 的路径和输出格式（ `--format` ）。
- 值以分号分隔，例如 `--build=never;--update;--lockfile-out=''`