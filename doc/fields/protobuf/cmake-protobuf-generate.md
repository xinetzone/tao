# 如何使用 `cmake_protobuf_generate`

- 参考：[cmake_protobuf_generate](https://github.com/protocolbuffers/protobuf/blob/main/docs/cmake_protobuf_generate.md)

本文档解释了如何使用由 protobuf 的 CMake 模块提供的 protobuf_generate 函数。

## 用法

在调用 `find_package(protobuf CONFIG)` 及其任何子目录的相同目录中，由 [`protobuf-generate.cmake`](https://github.com/protocolbuffers/protobuf/blob/main/cmake/protobuf-generate.cmake) 提供 CMake 函数 `protobuf_generate` 。它可用于在构建时自动从 `.proto` 模式文件生成源文件。

## 基本示例

看看如何使用 `protobuf_generate` 在构建名为 `proto-objects` 的对象目标时生成和编译 proto 模板的源文件。

假设有以下目录结构：
```bash
proto/helloworld/helloworld.proto
CMakeLists.txt
```

其中 `helloworld.proto` 是 protobuf 模板文件，而 `CMakeLists.txt` 包含：

```cmake
find_package(protobuf CONFIG REQUIRED)

add_library(proto-objects OBJECT "${CMAKE_CURRENT_LIST_DIR}/proto/helloworld/helloworld.proto")

target_link_libraries(proto-objects PUBLIC protobuf::libprotobuf)

set(PROTO_BINARY_DIR "${CMAKE_CURRENT_BINARY_DIR}/generated")

target_include_directories(proto-objects PUBLIC "$<BUILD_INTERFACE:${PROTO_BINARY_DIR}>")

protobuf_generate(
    TARGET proto-objects
    IMPORT_DIRS "${CMAKE_CURRENT_LIST_DIR}/proto"
    PROTOC_OUT_DIR "${PROTO_BINARY_DIR}")
```

构建目标 `proto-objects` 将生成以下文件：
```
${CMAKE_CURRENT_BINARY_DIR}/generated/helloworld/helloworld.pb.h
${CMAKE_CURRENT_BINARY_DIR}/generated/helloworld/helloworld.pb.cc
```

和（取决于构建系统）输出：

```bash
[build] [1/2] Running cpp protocol buffer compiler on /proto/helloworld/helloworld.proto
[build] [2/2] Building CXX object /build/generated/helloworld/helloworld.pb.cc.o
```

## 📘 参数详解

`protobuf_generate` 接受的参数如下。

### Flag 参数

- `APPEND_PATH` — 用于将所有 proto 模板文件的基本路径添加到 `IMPORT_DIRS` 的 flag。

### 单值参数

- `LANGUAGE` — 单一值：`cpp` 或 `python`。决定生成何种类型的源文件。
- `OUT_VAR` — 一个 CMake 变量的名称，该变量将被填充为生成的源文件路径。
- `EXPORT_MACRO` — 一个应用于所有生成的 Protobuf 消息类和外部变量的宏。例如，它可用于声明 DLL 导出。
- `PROTOC_EXE` — 命令名称、路径或用于运行 `protoc` 命令的 CMake 可执行文件。默认为 `protobuf::protoc` 。
- `PROTOC_OUT_DIR` — 生成的源文件输出目录。默认为 `CMAKE_CURRENT_BINARY_DIR` 。
- `PLUGIN` — 可选的插件可执行文件。例如，这可以是 `grpc_cpp_plugin` 或 `grpc_python_plugin` 的路径。
- `PLUGIN_OPTIONS` — 为插件提供的附加选项，例如 generate_mock_code=true 用于 gRPC cpp 插件。
- `DEPENDENCIES` — 传递给底层 `add_custom_command` 调用的 `DEPENDS` 参数。
- `TARGET` — 将生成的文件作为源文件添加到的 CMake 目标。

### 多值参数

- `PROTOS` — proto 模式文件列表。如果省略，则使用 `TARGET` 中所有以 proto 结尾的源文件。
- `IMPORT_DIRS` — 用于存放模式文件的公共父目录。例如，如果模式文件是 `proto/helloworld/helloworld.proto` ，导入目录是 `proto/` ，那么生成的文件是 `${PROTOC_OUT_DIR}/helloworld/helloworld.pb.h` 和 `${PROTOC_OUT_DIR}/helloworld/helloworld.pb.cc` 。
- `GENERATE_EXTENSIONS` — 如果省略了 `LANGUAGE`，则必须设置为 `protoc` 生成的扩展。
- `PROTOC_OPTIONS` — 额外传递给 `protoc` 的参数。

## 它是如何工作的

对于提供给 `TARGET` 或通过 `PROTOS` 提供的以 `proto` 结尾的每个源文件， `protobuf_generate` 将设置依赖于 `protobuf::protoc` 和 `proto` 文件的 [`add_custom_command`](https://cmake.org/cmake/help/latest/command/add_custom_command.html)。它将生成的源文件声明为 `OUTPUT` ，这意味着任何依赖于它们的靶标在更新时将自动触发自定义命令的执行。该命令本身由 protoc 的参数组成，例如输出目录、模式文件、生成语言、使用的插件等。

