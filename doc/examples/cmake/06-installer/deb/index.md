# 创建 deb 文件

本示例展示了如何使用 deb 格式生成 Linux 安装程序。

本教程中的文件如下：

```bash
$ tree
.
├── cmake-examples.conf # 示例配置文件
├── CMakeLists.txt # 包含你希望运行的 CMake 命令
├── include
│   └── Hello.h # 要包含的头文件
└── src
    ├── Hello.cpp # 要编译的源文件
    └── main.cpp # 含有 main 的源文件
```

## CPack 生成器

`make package` 目标可以使用 CPack 生成器来创建安装程序。

对于 Debian 包，你可以告诉 CMake 使用以下方式创建生成器：

```cmake
set(CPACK_GENERATOR "DEB")
```

在设置各种描述包的设置后，你必须告诉 CMake 包含 CPack 生成器使用

```cmake
include(CPack)
```

一旦包含了通常使用 `make install` 目标安装的所有文件，现在可以将它们打包成 Debian 软件包。

## Debian 软件包设置

CPack 暴露了该软件包的各种设置。在这个示例中，设置了以下内容：

```cmake
# Set a Package Maintainer.
# This is required
set(CPACK_DEBIAN_PACKAGE_MAINTAINER "Thom Troy")

# Set a Package Version
set(CPACK_PACKAGE_VERSION ${deb_example_VERSION})
```

这设置了维护者和版本。更多与 Debian 相关的设置在下方或 CPack 维基中指定。

|Variable  变量	|Info  信息
|:-:|:-:
|CPACK_DEBIAN_PACKAGE_MAINTAINER |维护者信息
|CPACK_PACKAGE_DESCRIPTION_SUMMARY |软件包简短描述
|CPACK_PACKAGE_DESCRIPTION |软件包描述
|CPACK_DEBIAN_PACKAGE_DEPENDS |供高级用户添加自定义脚本。
|CPACK_DEBIAN_PACKAGE_CONTROL_EXTRA |您当前所在的构建目录。
|CPACK_DEBIAN_PACKAGE_SECTION |软件包部分（参见[此处](http://packages.debian.org/stable)）
|CPACK_DEBIAN_PACKAGE_VERSION |软件包版本

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
-- Configuring done
-- Generating done
-- Build files have been written to: /home/matrim/workspace/cmake-examples/06-installer/deb/build

$ make help
The following are some of the valid targets for this Makefile:
... all (the default if no target is provided)
... clean
... depend
... cmake_examples_deb
... cmake_examples_deb_bin
... edit_cache
... install
... install/local
... install/strip
... list_install_components
... package
... package_source
... rebuild_cache
... src/Hello.o
... src/Hello.i
... src/Hello.s
... src/main.o
... src/main.i
... src/main.s

$ make package
Scanning dependencies of target cmake_examples_deb
[ 50%] Building CXX object CMakeFiles/cmake_examples_deb.dir/src/Hello.cpp.o
Linking CXX shared library libcmake_examples_deb.so
[ 50%] Built target cmake_examples_deb
Scanning dependencies of target cmake_examples_deb_bin
[100%] Building CXX object CMakeFiles/cmake_examples_deb_bin.dir/src/main.cpp.o
Linking CXX executable cmake_examples_deb_bin
[100%] Built target cmake_examples_deb_bin
Run CPack packaging tool...
CPack: Create package using DEB
CPack: Install projects
CPack: - Run preinstall target for: cmake_examples_deb
CPack: - Install project: cmake_examples_deb
CPack: Create package
CPack: - package: /home/matrim/workspace/cmake-examples/06-installer/deb/build/cmake_examples_deb-0.2.2-Linux.deb generated.

$ ls
CMakeCache.txt  cmake_examples_deb-0.2.2-Linux.deb  cmake_examples_deb_bin  CMakeFiles  cmake_install.cmake  CPackConfig.cmake  _CPack_Packages  CPackSourceConfig.cmake  install_manifest.txt  libcmake_examples_deb.so  Makefile
```
