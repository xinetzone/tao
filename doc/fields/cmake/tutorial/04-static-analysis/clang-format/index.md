# Clang 格式化

本示例展示了如何调用 Clang Format 来检查您的源代码是否符合您的代码风格指南。

The files included in this example are:
本示例包含的文件有：

```bash
$ tree
.
├── .clang-format # 描述风格指南的文件
├── CMakeLists.txt # 顶层 CMakeLists.txt
├── cmake
│   ├── modules
│   │   ├── clang-format.cmake # 设置格式目标的脚本
│   │   └── FindClangFormat.cmake # 查找 clang-format 二进制文件的脚本
│   └── scripts
│       └── clang-format-check-changed # 辅助脚本，用于检查 git 中已更改的文件
├── subproject1
│   ├── CMakeLists.txt
│   └── main1.cpp # 没有样式错误的子项目源代码
└── subproject2
    ├── CMakeLists.txt
    └── main2.cpp # 子项目的源文件，包含样式错误
```

要运行此示例，您必须安装 clang 格式工具。在 Ubuntu 上，您可以使用以下命令安装。

```bash
sudo apt-get install clang-format
```

## clang-format

clang-format 可以扫描源文件，然后找到并选择性地将其格式化为符合您公司风格指南的格式。内置有默认风格，但您也可以使用名为 .clang-format 的自定义文件来设置风格指南，例如，这个仓库中的 .clang-format 示例如下：

```
Language:        Cpp
# BasedOnStyle:  LLVM
AccessModifierOffset: -4
AlignAfterOpenBracket: Align
AlignConsecutiveAssignments: false
AlignConsecutiveDeclarations: false
```

## 格式风格

如前所述，此示例中的样式基于 `.clang-format` 文件。可以通过编辑 [clang-format.cmake](https://github.com/ttroy50/cmake-examples/blob/master/04-static-analysis/clang-format/cmake/modules/clang-format.cmake) 并将 -style=file 更改为所需的样式来更改此样式；

## 目标
This example will setup 3 targets:
这个示例将设置 3 个目标：

- format  格式
-format-check  格式检查
- format-check-changed  格式检查已更改

### format  格式

格式化目标将查找任何 C++源文件，并将其就地修改以匹配 `.clang-format` 风格。源文件是使用以下 cmake 代码查找的

```cmake
file(GLOB_RECURSE ALL_SOURCE_FILES *.cpp *.h *.cxx *.hxx *.hpp *.cc *.ipp)

# Don't include some common build folders
set(CLANG_FORMAT_EXCLUDE_PATTERNS ${CLANG_FORMAT_EXCLUDE_PATTERNS} "/CMakeFiles/" "cmake")

# get all project files file
foreach (SOURCE_FILE ${ALL_SOURCE_FILES})
    foreach (EXCLUDE_PATTERN ${CLANG_FORMAT_EXCLUDE_PATTERNS})
        string(FIND ${SOURCE_FILE} ${EXCLUDE_PATTERN} EXCLUDE_FOUND)
        if (NOT ${EXCLUDE_FOUND} EQUAL -1)
            list(REMOVE_ITEM ALL_SOURCE_FILES ${SOURCE_FILE})
        endif ()
    endforeach ()
endforeach ()
```

这将查找匹配常见 C++后缀的文件，然后删除与某些常见 CMake 目录匹配的文件。

在根目录 CMakeList.txt 中，我们通过添加行来排除构建目录
```bash
set(CLANG_FORMAT_EXCLUDE_PATTERNS  "build/")
```

## format-check  格式检查

此目标将按上述方式工作，但不是格式化文件，而是如果任何文件不符合 clang-format 风格，则会引发失败

## format-check-changed  格式检查已更改

此目标将检查 git status 的输出，并扫描文件以检查它们是否符合风格。开发者可以使用此功能来确保他们修改的文件符合正确的风格。

在这个示例中，实际的检查是通过一个辅助脚本 clang-format-check-changed.py 完成的。这个脚本将运行 git status --porcelain --ignore-submodules 来获取已更改的文件列表，将它们与上面列表中的允许扩展名进行匹配，并最终移除与 CLANG_FORMAT_EXCLUDE_PATTERNS 中的排除模式匹配的任何文件。然后，它将使用这些文件通过 clang-format 进行格式化，如果文件不符合样式，则退出并报错。

调用 clang-format-check-changed.py 脚本的示例为：

```bash
cmake/scripts/clang-format-check-changed.py --file-extensions ".cpp,*.cpp,*.h,*.cxx,*.hxx,*.hpp,*.cc,*.ipp" --exclude=build/ --exclude=/CMakeFiles/ --exclude=cmake --clang-format-bin /usr/bin/clang-format-3.6
```
