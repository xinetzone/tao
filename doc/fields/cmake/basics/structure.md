# 如何组织你的项目

以下信息是有偏好的。但在我看来，这是好的偏见。我将告诉你如何组织你的项目目录。这是基于惯例，但会帮助你：

- 轻松阅读遵循相同模式的其他项目
- 避免使用会导致冲突的模式，
- 防止构建过程变得混乱和复杂。

首先，如果你的项目创意地命名为 `project`，有名为 `lib` 的库，以及名为 `app` 的可执行文件，那么你的文件应该看起来像这样：

```bash
- project
  - .gitignore
  - README.md
  - LICENSE.md
  - CMakeLists.txt
  - cmake
    - FindSomeLib.cmake
    - something_else.cmake
  - include
    - project
      - lib.hpp
  - src
    - CMakeLists.txt
    - lib.cpp
  - apps
    - CMakeLists.txt
    - app.cpp
  - tests
    - CMakeLists.txt
    - testlib.cpp
  - doc
    - CMakeLists.txt
  - extern
    - googletest
  - scripts
    - helper.py
```

这些名称并非绝对；你会看到关于 `test/` 与 `tests/` 的冲突，应用程序文件夹的名称可能不同（或者对于只有库的项目可能不存在）。有时你还会看到用于 Python 绑定的 python 文件夹，或者用于辅助 CMake 文件的 cmake 文件夹，比如 `Find<library>.cmake` 文件。但基本结构已经存在。

已经注意到几点明显的情况： `CMakeLists.txt` 文件分布在所有源代码目录中，并不在 `include` 目录里。这是因为你应该能够直接将包含目录的内容复制到 `/usr/include` 或类似目录（配置头文件除外，将在另一章节中讨论），并且不会产生任何额外文件或冲突。这也是为什么在包含目录中为你的项目创建一个目录的原因。使用 `add_subdirectory` 添加包含 `CMakeLists.txt` 的子目录。

通常需要 cmake 文件夹，里面包含所有辅助模块。这就是你的 `Find*.cmake` 文件存放的地方。一些常见的辅助模块集合可以在 [`github.com/CLIUtils/cmake`](https://github.com/CLIUtils/cmake) 找到。要将这个文件夹添加到你的 CMake 路径中：

```cmake
set(CMAKE_MODULE_PATH "${PROJECT_SOURCE_DIR}/cmake" ${CMAKE_MODULE_PATH})
```

你的 `extern` 文件夹几乎应该只包含 `git` 子模块。这样，你可以明确控制依赖的版本，同时仍然可以轻松升级。有关添加子模块的示例，请参阅测试章节。

你应该在 `.gitignore` 中包含 `/build*`，这样用户就可以在源目录中创建构建目录并使用这些目录来构建。少数软件包禁止这样做，但与进行真正的源外构建并需要对每个构建的软件包输入不同内容相比，这要好得多。

如果你想避免构建目录位于有效的源目录中，在 `CMakeLists` 的顶部附近添加这个：

```cmake
### Require out-of-source builds
file(TO_CMAKE_PATH "${PROJECT_BINARY_DIR}/CMakeLists.txt" LOC_PATH)
if(EXISTS "${LOC_PATH}")
    message(FATAL_ERROR "You cannot build in a source directory (or any directory with a CMakeLists.txt file). Please make a build subdirectory. Feel free to remove CMakeCache.txt and CMakeFiles.")
endif()
```

请在[此处](https://gitlab.com/CLIUtils/modern-cmake/tree/master/examples/extended-project)查看扩展的代码示例。