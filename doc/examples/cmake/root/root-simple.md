# 简单的 ROOT 项目：使用目标系统

使用目标系统且不包含字典的 ROOT 项目的最小示例。

## `examples/root-simple/CMakeLists.txt`

```cmake
cmake_minimum_required(VERSION 3.15...4.0)

project(RootSimpleExample LANGUAGES CXX)

# Finding the ROOT package
## [find_package]
find_package(ROOT 6.16 CONFIG REQUIRED)
## [find_package]

# Adding an executable program and linking to needed ROOT libraries
## [add_and_link]
add_executable(RootSimpleExample SimpleExample.cxx)
target_link_libraries(RootSimpleExample PUBLIC ROOT::Physics)
## [add_and_link]
```

## `examples/root-simple/SimpleExample.cxx`

```cpp
#include <TLorentzVector.h>

int main() {
    TLorentzVector v(1,2,3,4);
    v.Print();
    return 0;
}
```
