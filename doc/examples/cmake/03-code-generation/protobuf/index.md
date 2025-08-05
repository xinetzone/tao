# 使用 Google Protocol Buffers 生成 C++源代码

本示例展示了如何使用 protobuf 生成源文件。Protocol Buffers 是由 Google 开发的一种数据序列化格式。用户提供描述数据的 `.proto` 文件，然后使用 protobuf 编译器，可以将 proto 文件翻译成包括 C++在内的多种语言的源代码。

本教程中的文件如下：

```bash
$ tree
.
├── AddressBook.proto # 主协议缓冲区示例的 proto 文件
├── CMakeLists.txt # 包含你希望运行的 CMake 命令
├── main.cpp # 来自 protobuf 示例的源文件。
```

## 导出的变量

CMake protobuf 包导出的变量以及在此示例中使用的变量包括：

- `PROTOBUF_FOUND` - 查找是否安装了 Protocol Buffers。
- `PROTOBUF_INCLUDE_DIRS` - protobuf 头文件
- `PROTOBUF_LIBRARIES` - protobuf 库

## 生成源代码

protobuf 的 CMake 包包含许多辅助函数，以简化代码生成。在这个例子中，正在生成 C++ 源代码并使用以下代码：

参数如下：

- `PROTO_SRCS` - 存储 `.pb.cc` 文件的变量名。
- `PROTO_HDRS` - 存储 `.pb.h` 文件的变量名。
- `AddressBook.proto` - 用于生成代码的 `.proto` 文件。

## 生成文件

在调用 `PROTOBUF_GENERATE_CPP` 函数后，您将拥有上述提到的变量。这些变量将被标记为调用 protobuf 编译器二进制文件来生成它们的自定义命令的输出。

要生成这些文件，您应该将它们添加到库或可执行文件中。例如：

```cmake
add_executable(protobuf_example
    main.cpp
    ${PROTO_SRCS}
    ${PROTO_HDRS})
```

这将导致在调用该可执行目标上的 make 时调用 protobuf 编译器。

当对 `.proto` 文件进行修改时，相关的源文件将再次自动生成。但是，如果 `.proto` 文件没有进行任何修改，并且你重新运行 make，那么将不会执行任何操作。

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
-- Looking for include file pthread.h
-- Looking for include file pthread.h - found
-- Looking for pthread_create
-- Looking for pthread_create - not found
-- Looking for pthread_create in pthreads
-- Looking for pthread_create in pthreads - not found
-- Looking for pthread_create in pthread
-- Looking for pthread_create in pthread - found
-- Found Threads: TRUE
-- Found PROTOBUF: /usr/lib/x86_64-linux-gnu/libprotobuf.so
protobuf found
PROTO_SRCS = /home/matrim/workspace/cmake-examples/03-code-generation/protobuf/build/AddressBook.pb.cc
PROTO_HDRS = /home/matrim/workspace/cmake-examples/03-code-generation/protobuf/build/AddressBook.pb.h
-- Configuring done
-- Generating done
-- Build files have been written to: /home/matrim/workspace/cmake-examples/03-code-generation/protobuf/build

$ ls
CMakeCache.txt  CMakeFiles  cmake_install.cmake  Makefile

$ make VERBOSE=1
/usr/bin/cmake -H/home/matrim/workspace/cmake-examples/03-code-generation/protobuf -B/home/matrim/workspace/cmake-examples/03-code-generation/protobuf/build --check-build-system CMakeFiles/Makefile.cmake 0
/usr/bin/cmake -E cmake_progress_start /home/matrim/workspace/cmake-examples/03-code-generation/protobuf/build/CMakeFiles /home/matrim/workspace/cmake-examples/03-code-generation/protobuf/build/CMakeFiles/progress.marks
make -f CMakeFiles/Makefile2 all
make[1]: Entering directory `/home/matrim/workspace/cmake-examples/03-code-generation/protobuf/build'
make -f CMakeFiles/protobuf_example.dir/build.make CMakeFiles/protobuf_example.dir/depend
make[2]: Entering directory `/home/matrim/workspace/cmake-examples/03-code-generation/protobuf/build'
/usr/bin/cmake -E cmake_progress_report /home/matrim/workspace/cmake-examples/03-code-generation/protobuf/build/CMakeFiles 1
[ 33%] Running C++ protocol buffer compiler on AddressBook.proto
/usr/bin/protoc --cpp_out /home/matrim/workspace/cmake-examples/03-code-generation/protobuf/build -I /home/matrim/workspace/cmake-examples/03-code-generation/protobuf /home/matrim/workspace/cmake-examples/03-code-generation/protobuf/AddressBook.proto
cd /home/matrim/workspace/cmake-examples/03-code-generation/protobuf/build && /usr/bin/cmake -E cmake_depends "Unix Makefiles" /home/matrim/workspace/cmake-examples/03-code-generation/protobuf /home/matrim/workspace/cmake-examples/03-code-generation/protobuf /home/matrim/workspace/cmake-examples/03-code-generation/protobuf/build /home/matrim/workspace/cmake-examples/03-code-generation/protobuf/build /home/matrim/workspace/cmake-examples/03-code-generation/protobuf/build/CMakeFiles/protobuf_example.dir/DependInfo.cmake --color=
Dependee "/home/matrim/workspace/cmake-examples/03-code-generation/protobuf/build/CMakeFiles/protobuf_example.dir/DependInfo.cmake" is newer than depender "/home/matrim/workspace/cmake-examples/03-code-generation/protobuf/build/CMakeFiles/protobuf_example.dir/depend.internal".
Dependee "/home/matrim/workspace/cmake-examples/03-code-generation/protobuf/build/CMakeFiles/CMakeDirectoryInformation.cmake" is newer than depender "/home/matrim/workspace/cmake-examples/03-code-generation/protobuf/build/CMakeFiles/protobuf_example.dir/depend.internal".
Scanning dependencies of target protobuf_example
make[2]: Leaving directory `/home/matrim/workspace/cmake-examples/03-code-generation/protobuf/build'
make -f CMakeFiles/protobuf_example.dir/build.make CMakeFiles/protobuf_example.dir/build
make[2]: Entering directory `/home/matrim/workspace/cmake-examples/03-code-generation/protobuf/build'
/usr/bin/cmake -E cmake_progress_report /home/matrim/workspace/cmake-examples/03-code-generation/protobuf/build/CMakeFiles 2
[ 66%] Building CXX object CMakeFiles/protobuf_example.dir/main.cpp.o
/usr/bin/c++    -I/home/matrim/workspace/cmake-examples/03-code-generation/protobuf/build    -o CMakeFiles/protobuf_example.dir/main.cpp.o -c /home/matrim/workspace/cmake-examples/03-code-generation/protobuf/main.cpp
/usr/bin/cmake -E cmake_progress_report /home/matrim/workspace/cmake-examples/03-code-generation/protobuf/build/CMakeFiles 3
[100%] Building CXX object CMakeFiles/protobuf_example.dir/AddressBook.pb.cc.o
/usr/bin/c++    -I/home/matrim/workspace/cmake-examples/03-code-generation/protobuf/build    -o CMakeFiles/protobuf_example.dir/AddressBook.pb.cc.o -c /home/matrim/workspace/cmake-examples/03-code-generation/protobuf/build/AddressBook.pb.cc
Linking CXX executable protobuf_example
/usr/bin/cmake -E cmake_link_script CMakeFiles/protobuf_example.dir/link.txt --verbose=1
/usr/bin/c++       CMakeFiles/protobuf_example.dir/main.cpp.o CMakeFiles/protobuf_example.dir/AddressBook.pb.cc.o  -o protobuf_example -rdynamic -lprotobuf -lpthread
make[2]: Leaving directory `/home/matrim/workspace/cmake-examples/03-code-generation/protobuf/build'
/usr/bin/cmake -E cmake_progress_report /home/matrim/workspace/cmake-examples/03-code-generation/protobuf/build/CMakeFiles  1 2 3
[100%] Built target protobuf_example
make[1]: Leaving directory `/home/matrim/workspace/cmake-examples/03-code-generation/protobuf/build'
/usr/bin/cmake -E cmake_progress_start /home/matrim/workspace/cmake-examples/03-code-generation/protobuf/build/CMakeFiles 0
$ make VERBOSE=1
/usr/bin/cmake -H/home/matrim/workspace/cmake-examples/03-code-generation/protobuf -B/home/matrim/workspace/cmake-examples/03-code-generation/protobuf/build --check-build-system CMakeFiles/Makefile.cmake 0
/usr/bin/cmake -E cmake_progress_start /home/matrim/workspace/cmake-examples/03-code-generation/protobuf/build/CMakeFiles /home/matrim/workspace/cmake-examples/03-code-generation/protobuf/build/CMakeFiles/progress.marks
make -f CMakeFiles/Makefile2 all
make[1]: Entering directory `/home/matrim/workspace/cmake-examples/03-code-generation/protobuf/build'
make -f CMakeFiles/protobuf_example.dir/build.make CMakeFiles/protobuf_example.dir/depend
make[2]: Entering directory `/home/matrim/workspace/cmake-examples/03-code-generation/protobuf/build'
/usr/bin/cmake -E cmake_progress_report /home/matrim/workspace/cmake-examples/03-code-generation/protobuf/build/CMakeFiles 1
[ 33%] Running C++ protocol buffer compiler on AddressBook.proto
/usr/bin/protoc --cpp_out /home/matrim/workspace/cmake-examples/03-code-generation/protobuf/build -I /home/matrim/workspace/cmake-examples/03-code-generation/protobuf /home/matrim/workspace/cmake-examples/03-code-generation/protobuf/AddressBook.proto
cd /home/matrim/workspace/cmake-examples/03-code-generation/protobuf/build && /usr/bin/cmake -E cmake_depends "Unix Makefiles" /home/matrim/workspace/cmake-examples/03-code-generation/protobuf /home/matrim/workspace/cmake-examples/03-code-generation/protobuf /home/matrim/workspace/cmake-examples/03-code-generation/protobuf/build /home/matrim/workspace/cmake-examples/03-code-generation/protobuf/build /home/matrim/workspace/cmake-examples/03-code-generation/protobuf/build/CMakeFiles/protobuf_example.dir/DependInfo.cmake --color=
Dependee "/home/matrim/workspace/cmake-examples/03-code-generation/protobuf/build/CMakeFiles/protobuf_example.dir/DependInfo.cmake" is newer than depender "/home/matrim/workspace/cmake-examples/03-code-generation/protobuf/build/CMakeFiles/protobuf_example.dir/depend.internal".
Dependee "/home/matrim/workspace/cmake-examples/03-code-generation/protobuf/build/CMakeFiles/CMakeDirectoryInformation.cmake" is newer than depender "/home/matrim/workspace/cmake-examples/03-code-generation/protobuf/build/CMakeFiles/protobuf_example.dir/depend.internal".
Scanning dependencies of target protobuf_example
make[2]: Leaving directory `/home/matrim/workspace/cmake-examples/03-code-generation/protobuf/build'
make -f CMakeFiles/protobuf_example.dir/build.make CMakeFiles/protobuf_example.dir/build
make[2]: Entering directory `/home/matrim/workspace/cmake-examples/03-code-generation/protobuf/build'
/usr/bin/cmake -E cmake_progress_report /home/matrim/workspace/cmake-examples/03-code-generation/protobuf/build/CMakeFiles 2
[ 66%] Building CXX object CMakeFiles/protobuf_example.dir/main.cpp.o
/usr/bin/c++    -I/home/matrim/workspace/cmake-examples/03-code-generation/protobuf/build    -o CMakeFiles/protobuf_example.dir/main.cpp.o -c /home/matrim/workspace/cmake-examples/03-code-generation/protobuf/main.cpp
/usr/bin/cmake -E cmake_progress_report /home/matrim/workspace/cmake-examples/03-code-generation/protobuf/build/CMakeFiles 3
[100%] Building CXX object CMakeFiles/protobuf_example.dir/AddressBook.pb.cc.o
/usr/bin/c++    -I/home/matrim/workspace/cmake-examples/03-code-generation/protobuf/build    -o CMakeFiles/protobuf_example.dir/AddressBook.pb.cc.o -c /home/matrim/workspace/cmake-examples/03-code-generation/protobuf/build/AddressBook.pb.cc
Linking CXX executable protobuf_example
/usr/bin/cmake -E cmake_link_script CMakeFiles/protobuf_example.dir/link.txt --verbose=1
/usr/bin/c++       CMakeFiles/protobuf_example.dir/main.cpp.o CMakeFiles/protobuf_example.dir/AddressBook.pb.cc.o  -o protobuf_example -rdynamic -lprotobuf -lpthread
make[2]: Leaving directory `/home/matrim/workspace/cmake-examples/03-code-generation/protobuf/build'
/usr/bin/cmake -E cmake_progress_report /home/matrim/workspace/cmake-examples/03-code-generation/protobuf/build/CMakeFiles  1 2 3
[100%] Built target protobuf_example
make[1]: Leaving directory `/home/matrim/workspace/cmake-examples/03-code-generation/protobuf/build'
/usr/bin/cmake -E cmake_progress_start /home/matrim/workspace/cmake-examples/03-code-generation/protobuf/build/CMakeFiles 0

$ ls
AddressBook.pb.cc  CMakeCache.txt  cmake_install.cmake  protobuf_example
AddressBook.pb.h   CMakeFiles      Makefile

$ ./protobuf_example test.db
test.db: File not found.  Creating a new file.
Enter person ID number: 11
Enter name: John Doe
Enter email address (blank for none): wolly@sheep.ie
Enter a phone number (or leave blank to finish):

$ ls
AddressBook.pb.cc  CMakeCache.txt  cmake_install.cmake  protobuf_example
AddressBook.pb.h   CMakeFiles      Makefile             test.db
```
