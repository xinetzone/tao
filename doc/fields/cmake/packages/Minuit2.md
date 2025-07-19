# Minuit2

Minuit2 可在独立模式下使用，适用于 ROOT 不可用或未启用 Minuit2 的情况。这将涵盖推荐的用法，以及设计的一些方面。

## 用法

Minuit2 可以通过标准的 CMake 方法使用，无论是从 ROOT 源代码还是从独立的源代码分发版：

```cmake
# Check for Minuit2 in ROOT if you want
# and then link to ROOT::Minuit2 instead

add_subdirectory(minuit2) # or root/math/minuit2
# OR
find_package(Minuit2 CONFIG) # Either build or install

target_link_libraries(MyProgram PRIVATE Minuit2::Minuit2)
```

## 开发

Minuit2 是一个很好的例子，展示了如何将现代（CMake 3.1+）构建集成到现有框架中的潜在解决方案。

为了处理两种不同的 CMake 系统，主 `CMakeLists.txt` 定义了通用选项，然后如果不是作为 ROOT 的一部分进行构建，就会调用一个 `Standalone.cmake` 文件。

在 ROOT 案例中，最难的部分是 Minuit2 需要 `math/minuit2` 目录外的文件。这个问题通过添加一个 `copy_standalone.cmake` 文件解决，该文件包含一个函数，接受文件名列表，然后要么在原始源代码中直接返回文件名列表，要么将文件复制到本地源代码并返回新位置的列表，或者如果原始源代码不存在，则只返回新位置的列表（独立运行）。

```bash
# Copies files into source directory
cmake /root/math/minuit2 -Dminuit2-standalone=ON

# Makes .tar.gz from source directory
make package_source

# Optional, clean the source directory
make purge
```

这仅适用于希望生成源代码包的开发者——普通用户不会传递此选项，也不会创建源代码副本。

您可以在不添加此 `standalone` 选项的情况下使用 `make install` 或 `make package` （二进制包），无论是从 ROOT 源代码内部还是从独立包使用。
