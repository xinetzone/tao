# `make install`

本示例演示如何生成`make install`目标来安装文件和二进制到系统。基于之前的共享库示例扩展实现。

项目结构：

```
.  
├── cmake-examples.conf
├── CMakeLists.txt
├── include
│   └── installing
│       └── Hello.h
├── README.md
└── src
    ├── Hello.cpp
    └── main.cpp
```

- **CMakeLists.txt**: 包含CMake构建指令
- **cmake-examples.conf**: 示例配置文件
- **Hello.h**: 头文件
- **Hello.cpp**: 库源文件
- **main.cpp**: 主程序文件

## 核心概念

### 安装机制

通过`install()`命令配置安装规则：

```cmake
install(TARGETS cmake_examples_inst_bin
    DESTINATION bin)
```

将可执行文件安装到`${CMAKE_INSTALL_PREFIX}/bin`

```cmake
install(TARGETS cmake_examples_inst
    LIBRARY DESTINATION lib)
```

将共享库安装到`${CMAKE_INSTALL_PREFIX}/lib`

> **Windows注意**：
> 需添加运行时目标配置
> ```cmake
> install(TARGETS cmake_examples_inst
>     LIBRARY DESTINATION lib
>     RUNTIME DESTINATION bin)
> ```

### 文件安装

```cmake
install(DIRECTORY ${PROJECT_SOURCE_DIR}/include/
    DESTINATION include)
```

安装头文件到`${CMAKE_INSTALL_PREFIX}/include`

```cmake
install(FILES cmake-examples.conf
    DESTINATION etc)
```

安装配置文件到`${CMAKE_INSTALL_PREFIX}/etc`

## 构建验证

```bash
mkdir build
cd build
cmake ..
make
sudo make install
```

安装后生成`install_manifest.txt`记录安装路径：

```
/usr/local/bin/cmake_examples_inst_bin
/usr/local/lib/libcmake_examples_inst.so
/usr/local/etc/cmake-examples.conf
```

## 高级配置

### 自定义安装路径

在CMakeLists.txt顶部添加：

```cmake
if(CMAKE_INSTALL_PREFIX_INITIALIZED_TO_DEFAULT)
  message(STATUS "设置默认安装路径: ${CMAKE_BINARY_DIR}/install")
  set(CMAKE_INSTALL_PREFIX "${CMAKE_BINARY_DIR}/install" CACHE STRING "make install路径" FORCE)
endif()
```

### 暂存安装

使用DESTDIR参数进行预安装验证：

```bash
make install DESTDIR=/tmp/stage
```

目录结构：

```
/tmp/stage
└── usr
    └── local
        ├── bin
        │   └── cmake_examples_inst_bin
        ├── etc
        │   └── cmake-examples.conf
        └── lib
            └── libcmake_examples_inst.so
```

### 卸载机制

通过安装清单执行卸载：

```bash
sudo xargs rm < install_manifest.txt
```

## 环境配置

运行时需配置库路径：
```bash
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib
```

> 若`/usr/local/lib`不在默认库路径中，需手动添加

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
-- Build files have been written to: /home/matrim/workspace/cmake-examples/01-basic/E-installing/build

$ make
Scanning dependencies of target cmake_examples_inst
[ 50%] Building CXX object CMakeFiles/cmake_examples_inst.dir/src/Hello.cpp.o
Linking CXX shared library libcmake_examples_inst.so
[ 50%] Built target cmake_examples_inst
Scanning dependencies of target cmake_examples_inst_bin
[100%] Building CXX object CMakeFiles/cmake_examples_inst_bin.dir/src/main.cpp.o
Linking CXX executable cmake_examples_inst_bin
[100%] Built target cmake_examples_inst_bin

$ sudo make install
[sudo] password for matrim:
[ 50%] Built target cmake_examples_inst
[100%] Built target cmake_examples_inst_bin
Install the project...
-- Install configuration: ""
-- Installing: /usr/local/bin/cmake_examples_inst_bin
-- Removed runtime path from "/usr/local/bin/cmake_examples_inst_bin"
-- Installing: /usr/local/lib/libcmake_examples_inst.so
-- Installing: /usr/local/etc/cmake-examples.conf

$ cat install_manifest.txt
/usr/local/bin/cmake_examples_inst_bin
/usr/local/lib/libcmake_examples_inst.so
/usr/local/etc/cmake-examples.conf

$ ls /usr/local/bin/
cmake_examples_inst_bin

$ ls /usr/local/lib
libcmake_examples_inst.so

$ ls /usr/local/etc/
cmake-examples.conf

$ LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib cmake_examples_inst_bin
Hello Install!
```
