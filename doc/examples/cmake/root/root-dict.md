# ROOT 字典示例 

这是一个在 CMake 中构建包含字典的模块的示例。我们不会使用 ROOT 建议的标志，而是通过 find_package 手动添加线程，这是大多数系统上列表中唯一重要的标志。

## `examples/root-dict/CMakeLists.txt`

```cmake
cmake_minimum_required(VERSION 3.15...4.0)

project(RootDictExample LANGUAGES CXX)

set(CMAKE_CXX_STANDARD
    11
    CACHE STRING "C++ standard to use")
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_PLATFORM_INDEPENDENT_CODE ON)

find_package(ROOT 6.20 CONFIG REQUIRED)
# If you want to support <6.20, add this line:
# include("${ROOT_DIR}/modules/RootNewMacros.cmake")
# However, it was moved and included by default in 6.201

root_generate_dictionary(G__DictExample DictExample.h LINKDEF DictLinkDef.h)

add_library(DictExample SHARED DictExample.cxx DictExample.h G__DictExample.cxx)
target_include_directories(DictExample PUBLIC "${CMAKE_CURRENT_SOURCE_DIR}")
target_link_libraries(DictExample PUBLIC ROOT::Core)

## Alternative to add the dictionary to an existing target:
# add_library(DictExample SHARED DictExample.cxx DictExample.h)
# target_include_directories(DictExample PUBLIC "${CMAKE_CURRENT_SOURCE_DIR}")
# target_link_libraries(DictExample PUBLIC ROOT::Core)
# root_generate_dictionary(G__DictExample DictExample.h MODULE DictExample LINKDEF DictLinkDef.h)
```

## 支持文件

这是尽可能简单的类定义，只有一个方法：

### `examples/root-dict/DictExample.cxx`

```cpp
#include "DictExample.h"

Double_t Simple::GetX() const {return x;}

ClassImp(Simple)
```

### `examples/root-dict/DictExample.h`

```cpp
#pragma once

#include <TROOT.h>

class Simple {
    Double_t x;

public:
    Simple() : x(2.5) {}
    Double_t GetX() const;

    ClassDef(Simple,1)
};
```

需要 `LinkDef.h`，同样。

### `examples/root-dict/DictLinkDef.h`

```cpp
// See: https://root.cern.ch/selecting-dictionary-entries-linkdefh
#ifdef __CINT__

#pragma link off all globals;
#pragma link off all classes;
#pragma link off all functions;
#pragma link C++ nestedclasses;

#pragma link C++ class Simple+;

#endif
```

## 测试

测试上述文件正确生成的宏的示例。

### `examples/root-dict/CheckLoad.C`

```c
{
gSystem->Load("libDictExample");
Simple s;
cout << s.GetX() << endl;
TFile *_file = TFile::Open("tmp.root", "RECREATE");
gDirectory->WriteObject(&s, "MyS");
Simple *MyS = nullptr;
gDirectory->GetObject("MyS", MyS);
cout << MyS->GetX() << endl;
_file->Close();
}
```
