# OpenMP

在 CMake 3.9+ 中，[OpenMP](https://cmake.org/cmake/help/latest/module/FindOpenMP.html) 的支持得到了大幅改进。将 OpenMP 添加到目标的现代（TM）方法是：

```cmake
find_package(OpenMP)
if(OpenMP_CXX_FOUND)
    target_link_libraries(MyTarget PUBLIC OpenMP::OpenMP_CXX)
endif()
```

这种方法不仅比旧方法更简洁，而且如果需要，它还会正确地设置库链接行与编译行不同。在 CMake 3.12+ 中，这甚至支持 macOS 上的 OpenMP（如果库可用，例如使用 brew install libomp ）。然而，如果你需要支持较旧的 CMake，以下方法适用于 CMake 3.1+：

```cmake
# For CMake < 3.9, we need to make the target ourselves
if(NOT TARGET OpenMP::OpenMP_CXX)
    find_package(Threads REQUIRED)
    add_library(OpenMP::OpenMP_CXX IMPORTED INTERFACE)
    set_property(TARGET OpenMP::OpenMP_CXX
                 PROPERTY INTERFACE_COMPILE_OPTIONS ${OpenMP_CXX_FLAGS})
    # Only works if the same flag is passed to the linker; use CMake 3.9+ otherwise (Intel, AppleClang)
    set_property(TARGET OpenMP::OpenMP_CXX
                 PROPERTY INTERFACE_LINK_LIBRARIES ${OpenMP_CXX_FLAGS} Threads::Threads)

endif()
target_link_libraries(MyTarget PUBLIC OpenMP::OpenMP_CXX)
```

```{danger}
CMake < 3.4 在 Threads 包中存在错误，需要启用 C 语言。
```
