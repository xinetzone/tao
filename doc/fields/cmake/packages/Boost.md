# Boost

Boost 库包含在 CMake 提供的查找包中，但在其工作方式上存在一些奇特之处。请参阅 [FindBoost](https://cmake.org/cmake/help/latest/module/FindBoost.html) 获取完整描述；这里将仅提供简要概述并提供解决方案。请务必检查您正在使用的 CMake 的最低版本要求，并查看您有哪些选项。

首先，您可以使用一组在搜索 Boost 之前设置的变量来定制所选 Boost 库的行为。设置选项越来越多，但这里列出三个最常用的：

```cmake
set(Boost_USE_STATIC_LIBS OFF)
set(Boost_USE_MULTITHREADED ON)
set(Boost_USE_STATIC_RUNTIME OFF)
```

在 CMake 3.5 中，引入了 `import target`。这些 target 会为你处理依赖关系，因此它们是添加 Boost 库的非常好的方式。然而，CMake 将所有已知的 Boost 版本的依赖信息都内嵌了，所以 CMake 必须比 Boost 更新，这些功能才能正常工作。在最近的[合并请求](https://gitlab.kitware.com/cmake/cmake/merge_requests/1172)中，CMake 开始假设依赖关系从它最后知道的版本开始有效，并会使用该版本（同时给出警告）。这项功能被回退到了 CMake 3.9 版本中。

`import target` 位于 `Boost::` 命名空间中。`Boost::boost` 是仅包含头文件的部分。其他编译库也是可用的，并且会根据需要包含依赖。

使用 Boost::filesystem 库的示例：

```cmake
set(Boost_USE_STATIC_LIBS OFF)
set(Boost_USE_MULTITHREADED ON)
set(Boost_USE_STATIC_RUNTIME OFF)
find_package(Boost 1.50 REQUIRED COMPONENTS filesystem)
message(STATUS "Boost version: ${Boost_VERSION}")

# This is needed if your Boost version is newer than your CMake version
# or if you have an old version of CMake (<3.5)
if(NOT TARGET Boost::filesystem)
    add_library(Boost::filesystem IMPORTED INTERFACE)
    set_property(TARGET Boost::filesystem PROPERTY
        INTERFACE_INCLUDE_DIRECTORIES ${Boost_INCLUDE_DIR})
    set_property(TARGET Boost::filesystem PROPERTY
        INTERFACE_LINK_LIBRARIES ${Boost_LIBRARIES})
endif()

target_link_libraries(MyExeOrLibrary PUBLIC Boost::filesystem)
```
