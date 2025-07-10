# Clang 静态分析器

本示例展示了如何使用 scan-build 工具调用 [Clang 静态分析器](https://clang-analyzer.llvm.org/)进行静态分析。

本示例包含的文件有：

```bash
$ tree
.
├── CMakeLists.txt # 顶层 CMakeLists.txt
├── subproject1
│   ├── CMakeLists.txt # 子项目 1 的 CMake 命令
│   └── main1.cpp # 子项目的源文件，没有错误
└── subproject2
    ├── CMakeLists.txt # 子项目 2 的 CMake 命令 
    └── main2.cpp # 子项目的源文件，包含错误
```

要运行此示例，你必须安装 clang 分析器和 scan-build 工具。这可以在 Ubuntu 上使用以下命令安装。
```bash
sudo apt-get install clang
```

## scan-build

要运行 clang 静态分析器，您可以使用工具 scan-build 在运行编译器时运行分析器。这会覆盖 CC 和 CXX 环境变量，并用它自己的工具替换它们。要运行它，您可以这样做

```bash
mkdir -p build
scan-build-21 cmake ..
scan-build-21 make
```

默认情况下，这将运行您平台的标准编译器，即 gcc 在 linux 上。但是，如果您想覆盖这一点，可以将命令更改为：

```bash
scan-build-21 --use-cc=clang-21 --use-c++=clang++-21 -o ./scanbuildout/ make
```

### scan-build 输出

scan-build 仅在编译时输出警告，并且还会生成一个包含错误详细分析的 HTML 文件列表。

```bash
$ cd scanbuildout/
$ tree
.
└── 2017-07-03-213514-3653-1
    ├── index.html
    ├── report-42eba1.html
    ├── scanview.css
    └── sorttable.js

1 directory, 4 files
```

默认情况下，这些输出到 `/tmp/scanbuildout/{运行文件夹}`。您可以使用 `scan-build -o /output/folder` 更改此设置。

## 构建示例

```bash
$ mkdir build

$ cd build/

$ scan-build-3.6 -o ./scanbuildout make
scan-build: Using '/usr/lib/llvm-3.6/bin/clang' for static analysis
make: *** No targets specified and no makefile found.  Stop.
scan-build: Removing directory '/data/code/clang-analyzer/build/scanbuildout/2017-07-03-211632-937-1' because it contains no reports.
scan-build: No bugs found.
devuser@91457fbfa423:/data/code/clang-analyzer/build$ scan-build-3.6 -o ./scanbuildout cmake ..
scan-build: Using '/usr/lib/llvm-3.6/bin/clang' for static analysis
-- The C compiler identification is GNU 5.4.0
-- The CXX compiler identification is GNU 5.4.0
-- Check for working C compiler: /usr/share/clang/scan-build-3.6/ccc-analyzer
-- Check for working C compiler: /usr/share/clang/scan-build-3.6/ccc-analyzer -- works
-- Detecting C compiler ABI info
-- Detecting C compiler ABI info - done
-- Detecting C compile features
-- Detecting C compile features - done
-- Check for working CXX compiler: /usr/share/clang/scan-build-3.6/c++-analyzer
-- Check for working CXX compiler: /usr/share/clang/scan-build-3.6/c++-analyzer -- works
-- Detecting CXX compiler ABI info
-- Detecting CXX compiler ABI info - done
-- Detecting CXX compile features
-- Detecting CXX compile features - done
-- Found CPPCHECK: /usr/local/bin/cppcheck
cppcheck found. Use cppccheck-analysis targets to run it
-- Configuring done
-- Generating done
-- Build files have been written to: /data/code/clang-analyzer/build
scan-build: Removing directory '/data/code/clang-analyzer/build/scanbuildout/2017-07-03-211641-941-1' because it contains no reports.
scan-build: No bugs found.

$ $ scan-build-3.6 -o ./scanbuildout make
scan-build: Using '/usr/lib/llvm-3.6/bin/clang' for static analysis
Scanning dependencies of target subproject1
[ 25%] Building CXX object subproject1/CMakeFiles/subproject1.dir/main1.cpp.o
[ 50%] Linking CXX executable subproject1
[ 50%] Built target subproject1
Scanning dependencies of target subproject2
[ 75%] Building CXX object subproject2/CMakeFiles/subproject2.dir/main2.cpp.o
/data/code/clang-analyzer/subproject2/main2.cpp:7:17: warning: Dereference of null pointer (loaded from variable 'x')
   std::cout << *x << std::endl;
                ^~
1 warning generated.
[100%] Linking CXX executable subproject2
[100%] Built target subproject2
scan-build: 1 bug found.
scan-build: Run 'scan-view /data/code/clang-analyzer/build/scanbuildout/2017-07-03-211647-1172-1' to examine bug reports.

$ cd scanbuildout/
$ tree
.
└── 2017-07-03-213514-3653-1
    ├── index.html
    ├── report-42eba1.html
    ├── scanview.css
    └── sorttable.js

1 directory, 4 files
```
