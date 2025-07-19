# 简单的 ROOT 项目：UseFile 系统

使用 UseFile 系统且不包含字典的 ROOT 项目最小示例。

## `examples/root-usefile/CMakeLists.txt`

```cmake
cmake_minimum_required(VERSION 3.15...4.0)

project(RootUseFileExample LANGUAGES CXX)

find_package(ROOT 6.16 CONFIG REQUIRED)

## [core]
# Sets up global settings
include("${ROOT_USE_FILE}")

# This is required for ROOT < 6.16
# string(REPLACE "-L " "-L" ROOT_EXE_LINKER_FLAGS "${ROOT_EXE_LINKER_FLAGS}")

# This is required on if there is more than one flag (like on macOS)
separate_arguments(ROOT_EXE_LINKER_FLAGS)

add_executable(RootUseFileExample SimpleExample.cxx)
target_link_libraries(RootUseFileExample PUBLIC ${ROOT_LIBRARIES}
                                                ${ROOT_EXE_LINKER_FLAGS})
## [core]
```

## `examples/root-usefile/SimpleExample.cxx`

```cpp
#include <TLorentzVector.h>

int main() {
    TLorentzVector v(1,2,3,4);
    v.Print();
    return 0;
}
```
