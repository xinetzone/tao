# Protocol Buffers 概述

[协议缓冲区(Protocol Buffers)](https://protobuf.dev/)是 Google 开发的一种语言无关、平台无关、可扩展的结构化数据序列化机制——可以将其视为 XML，但更小、更快、更简单。您只需定义一次数据的结构，然后可以使用特殊生成的源代码轻松地在各种数据流之间以及使用各种语言读写您的结构化数据。

协议缓冲区支持 C++、C#、Dart、Go、Java、Kotlin、Objective-C、Python 和 Ruby 的生成代码。使用 proto3，您还可以使用 PHP。

## 示例实现

Protocol Buffers 是一种语言中立、平台中立的可扩展结构化数据序列化机制。它类似于 JSON，但更小、更快，并且能生成原生语言绑定。你只需定义一次数据的结构，然后可以使用特殊生成的源代码轻松地在各种数据流中读写你的结构化数据，并使用多种语言。

协议缓冲区是一种组合，包括定义语言（在 `.proto` 文件中创建）、proto 编译器生成的用于与数据交互的代码、特定语言的运行时库、写入文件（或跨网络连接发送）的数据的序列化格式，以及序列化数据。

proto 定义：
```proto
edition = "2023";

message Person {
  string name = 1;
  int32 id = 2;
  string email = 3;
}
```

使用生成的类来持久化数据：
```java
// Java code
Person john = Person.newBuilder()
    .setId(1234)
    .setName("John Doe")
    .setEmail("jdoe@example.com")
    .build();
output = new FileOutputStream(args[0]);
john.writeTo(output);
```

使用生成的类来解析持久化数据
```cpp
// C++ code
Person john;
fstream input(argv[1],
    ios::in | ios::binary);
john.ParseFromIstream(&input);
id = john.id();
name = john.name();
email = john.email();
```

## 协议缓冲区解决了哪些问题

协议缓冲区为类型化的结构化数据包提供了一种序列化格式，这些数据包的大小可达几兆字节。该格式适用于短暂的网络流量和长期数据存储。协议缓冲区可以通过添加新信息来扩展，而不会使现有数据失效或需要更新代码。

协议缓冲区是谷歌最常用的数据格式。它们被广泛用于服务器间通信以及磁盘上的数据归档存储。协议缓冲区消息和服务由工程师编写的 `.proto` 文件描述。以下是 `message` 的示例：

```proto
edition = "2023";

message Person {
  string name = 1;
  int32 id = 2;
  string email = 3;
}
```

原型编译器在构建时被调用，用于 `.proto` 文件以生成多种编程语言（本主题后文将涵盖[跨语言兼容性](https://protobuf.dev/overview/#cross-lang)）的代码，以操作相应的协议缓冲区。每个生成的类都包含每个字段的简单访问器，以及将整个结构序列化和解析为原始字节的相应方法。以下展示了使用这些生成方法的示例：
```proto
Person john = Person.newBuilder()
    .setId(1234)
    .setName("John Doe")
    .setEmail("jdoe@example.com")
    .build();
output = new FileOutputStream(args[0]);
john.writeTo(output);
```

由于协议缓冲区在谷歌的各种服务中被广泛使用，并且其中数据可能会持久存在一段时间，因此维护向后兼容性至关重要。协议缓冲区允许无缝支持变更，包括向任何协议缓冲区添加新字段和删除现有字段，而不会破坏现有服务。关于此主题的更多信息，请参阅本主题后文的[“无需更新代码即可更新原型定义”](https://protobuf.dev/overview/#updating-defs)。

## 使用协议缓冲区的优势是什么？

协议缓冲区适用于任何需要以语言无关、平台无关、可扩展的方式序列化结构化、记录式、类型化数据的场景。它们通常用于定义通信协议（与 gRPC 一起使用）和数据存储。

使用协议缓冲区的优势包括：

- 紧凑的数据存储
- 快速解析
- 多种编程语言支持
- 通过自动生成的类实现优化功能

## 跨语言兼容性

相同消息可以被任何支持的语言编写的代码读取。你可以在一个平台上运行 Java 程序，从某个软件系统捕获数据，根据 `.proto` 定义进行序列化，然后在另一个平台上运行的独立 Python 应用程序中提取该序列化数据中的特定值。

以下语言直接在协议缓冲区编译器 `protoc` 中得到支持：

- [C++](https://protobuf.dev/reference/cpp/cpp-generated#invocation)
- [C#](https://protobuf.dev/reference/csharp/csharp-generated#invocation)
- [Java](https://protobuf.dev/reference/java/java-generated#invocation)
- [Kotlin](https://protobuf.dev/reference/kotlin/kotlin-generated#invocation)
- [Objective-C](https://protobuf.dev/reference/objective-c/objective-c-generated#invocation)
- [PHP](https://protobuf.dev/reference/php/php-generated#invocation)
- [Python](https://protobuf.dev/reference/python/python-generated#invocation)
- [Ruby](https://protobuf.dev/reference/ruby/ruby-generated#invocation)

以下语言由 Google 支持，但项目源代码位于 GitHub 仓库中。protoc 编译器使用这些语言的插件：
- [Dart](https://github.com/google/protobuf.dart)
- [Go](https://github.com/protocolbuffers/protobuf-go)

其他语言并非由 Google 直接支持，而是由[其他 GitHub 项目](https://github.com/protocolbuffers/protobuf/blob/master/docs/third_party.md)支持。这些语言在 Protocol Buffers 的第三方插件中有介绍。

## 跨项目支持

您可以通过在特定项目代码库之外定义 `message` 类型的 `.proto` 文件来跨项目使用协议缓冲区。如果您正在定义 `message `类型或枚举，并且预计它们将被您的团队之外广泛使用，可以将它们放在无依赖关系的独立文件中。

谷歌内部广泛使用的 proto 定义示例有 [`timestamp.proto`](https://github.com/protocolbuffers/protobuf/blob/master/src/google/protobuf/timestamp.proto) 和 [`status.proto`](https://github.com/googleapis/googleapis/blob/master/google/rpc/status.proto)。

## 无需更新代码即可更新 Proto 定义

软件产品通常需要向后兼容，但向前兼容则不太常见。只要在更新 `.proto` 定义时遵循一些[简单的实践](https://protobuf.dev/programming-guides/proto3#updating)，旧代码就能无问题地读取新消息，忽略任何新增的字段。对于旧代码来说，被删除的字段将具有默认值，被删除的重复字段将为空。有关“重复”字段的详细信息，请参阅本主题后面的[“Protocol Buffers 定义语法”](https://protobuf.dev/overview/#syntax)。

新代码也会透明地读取旧消息。旧消息中不会包含新字段；在这些情况下，协议缓冲区会提供合理的默认值。

## 什么时候 Protocol Buffers 不适合使用？

Protocol Buffers 并非适用于所有数据。具体来说：

- Protocol Buffers 倾向于假设整个消息可以一次性加载到内存中，并且不会大于对象图。对于超过几兆字节的数据，建议考虑其他解决方案；在处理大型数据时，由于序列化副本，你可能会有效地得到数据的多个副本，这可能导致内存使用量出现意外的峰值。
- 当 Protocol Buffers 被序列化时，相同的数据可以有多种不同的二进制序列化形式。在不完全解析它们的情况下，你不能比较两个消息是否相等。
消息不会被压缩。虽然消息可以像任何其他文件一样被 zip 或 gzip 压缩，但像 JPEG 和 PNG 使用的专用压缩算法对于适当类型的数据会产生更小的文件。
- 对于涉及大型多维浮点数数组的科学和工程应用，协议缓冲区消息在大小和速度上都不是最有效的。对于这些应用，[FITS](https://en.wikipedia.org/wiki/FITS) 和类似格式有更少的开销。
- 协议缓冲区在科学计算中流行的非面向对象语言（如 Fortran 和 IDL）中支持不佳。
- 协议缓冲区消息不会内在地描述其数据，但它们有一个完全反射的架构，你可以使用它来实现自我描述。也就是说，如果没有访问其对应的 `.proto` 文件，你无法完全解释一个消息。
- 协议缓冲区并非任何组织的正式标准。这使得它们不适用于需要在标准基础上构建且具有法律或其他要求的环境。

## 谁在使用协议缓冲区？

许多项目使用协议缓冲区，包括以下这些：

- [gRPC](https://grpc.io/)
- [Google Cloud](https://cloud.google.com/)
- [Envoy Proxy](https://www.envoyproxy.io/)

## 协议缓冲区是如何工作的？

下面的图表展示了如何使用协议缓冲区来处理你的数据。
![协议缓冲区工作流程](https://protobuf.dev/images/protocol-buffers-concepts.png)

协议缓冲区生成的代码提供了从文件和流中检索数据、从数据中提取单个值、检查数据是否存在、将数据序列化回文件或流以及其他有用功能的工具方法。

以下代码示例展示了在 Java 中的这个流程示例。如前所示，这是 `.proto` 定义：

```proto
message Person {
  string name = 1;
  int32 id = 2;
  string email = 3;
}
```

编译这个 `.proto` 文件会创建 Builder 类，你可以使用它来创建新的实例，如下面的 Java 代码所示：

```java
Person john = Person.newBuilder()
    .setId(1234)
    .setName("John Doe")
    .setEmail("jdoe@example.com")
    .build();
output = new FileOutputStream(args[0]);
john.writeTo(output);
```

然后你可以使用协议缓冲区在其他语言（如 C++）中创建的方法来反序列化数据：

```cpp
Person john;
fstream input(argv[1], ios::in | ios::binary);
john.ParseFromIstream(&input);
int id = john.id();
std::string name = john.name();
std::string email = john.email();
```

## 协议缓冲区定义语法

在定义 `.proto` 文件时，你可以指定基数（单一或重复）。在 proto2 和 proto3 中，你还可以指定字段是否可选。在 proto3 中，将字段设置为可选会[将其从隐式存在更改为显式存在](https://protobuf.dev/programming-guides/field_presence)。

在设置字段的基数后，您需要指定数据类型。Protocol Buffers 支持常见的原始数据类型，如整数、布尔值和浮点数。完整列表请参阅[标量值类型](https://protobuf.dev/programming-guides/proto3#scalar)。

字段也可以是：

- `message` 类型，以便您可以嵌套定义的部分，例如用于重复数据集。
- `enum` 类型，以便您可以指定一组可选值。
- `oneof` 类型，适用于消息包含许多可选字段，且同一时间最多只有一个字段会被设置的情况。
- `map` 类型，用于向你的定义中添加键值对。

消息可以允许扩展定义消息本身之外的字段。例如，protobuf 库的内部消息架构允许为自定义、特定用途的选项进行扩展。

有关可用选项的更多信息，请参阅 [proto2](https://protobuf.dev/programming-guides/proto2)、[proto3](https://protobuf.dev/programming-guides/proto3) 或 [2023 版本](https://protobuf.dev/programming-guides/editions)的语言指南。

在设置基数和数据类型后，你需要为字段选择名称。在设置字段名称时，有一些事项需要注意：

- 字段一旦在生产中使用后，有时甚至不可能更改名称。
- 字段名称不能包含连字符。有关字段名称语法的更多信息，请参阅[消息和字段名称](https://protobuf.dev/programming-guides/style#message-field-names)。
- 对于重复字段，请使用复数名称。

为字段分配名称后，你需要为其分配字段编号。字段编号不能被重新使用或重复使用。如果你删除了字段，应该保留其字段编号，以防止有人意外地重新使用该编号。

## 额外的数据类型支持

Protocol Buffers 支持多种标量值类型，包括使用变长编码和固定大小的整数。你也可以通过定义本身即为数据类型的消息来创建自己的复合数据类型，这些数据类型可以被分配给字段。除了简单和复合值类型外，还有一些[常用类型](https://protobuf.dev/best-practices/dos-donts#common)被发布。
