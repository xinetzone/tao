# 导入目标

如前所述，第三方库中，较新版本的 CMake 允许您使用导入的 ALIAS 目标链接第三方库。

本示例需要以下内容：

- CMake v3.5+
- 需要安装在默认系统位置的 boost 库。

## 导入目标

导入目标是 FindXXX 模块导出的只读目标。

要包含 boost filesystem，你可以这样做：
```bash
target_link_libraries( imported_targets
    PRIVATE
        Boost::filesystem
)
```

这将自动链接 `Boost::filesystem` 和 `Boost::system` 库，同时包含 Boost 的包含目录。

## 构建示例

```bash
$ mkdir build

$ cd build/

$ cmake ..
-- The C compiler identification is GNU 5.4.0
-- The CXX compiler identification is GNU 5.4.0
-- Check for working C compiler: /usr/bin/cc
-- Check for working C compiler: /usr/bin/cc -- works
-- Detecting C compiler ABI info
-- Detecting C compiler ABI info - done
-- Detecting C compile features
-- Detecting C compile features - done
-- Check for working CXX compiler: /usr/bin/c++
-- Check for working CXX compiler: /usr/bin/c++ -- works
-- Detecting CXX compiler ABI info
-- Detecting CXX compiler ABI info - done
-- Detecting CXX compile features
-- Detecting CXX compile features - done
-- Boost version: 1.58.0
-- Found the following Boost libraries:
--   filesystem
--   system
boost found
-- Configuring done
-- Generating done
-- Build files have been written to: /data/code/01-basic/K-imported-targets/build

$ make
Scanning dependencies of target imported_targets
[ 50%] Building CXX object CMakeFiles/imported_targets.dir/main.cpp.o
[100%] Linking CXX executable imported_targets
[100%] Built target imported_targets


$ ./imported_targets
Hello Third Party Include!
Path is not relative
```
