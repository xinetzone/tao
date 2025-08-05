# 协议缓冲区基础：Python

参考：[基本的 Python 程序员使用协议缓冲区的入门指南](https://protobuf.dev/getting-started/pythontutorial/)

```{topic} 目标
本教程为基本的 Python 程序员提供了使用协议缓冲区的入门介绍。通过创建简单的示例应用程序，它展示了如何

- 在 `.proto` 文件中定义消息格式。
- 使用协议缓冲区编译器。
- 使用 Python 协议缓冲区 API 来写入和读取消息。\

这不是一份关于在 Python 中使用协议缓冲区的全面指南。有关更详细的参考信息，请参阅[协议缓冲区语言指南（proto2）](https://protobuf.dev/programming-guides/proto2)、[协议缓冲区语言指南（proto3）](https://protobuf.dev/programming-guides/proto3)、[Python API 参考](https://googleapis.dev/python/protobuf/latest/)、[Python 生成代码指南](https://protobuf.dev/reference/python/python-generated)和[编码参考](https://protobuf.dev/programming-guides/encoding)。
```

## 问题领域

使用的示例是非常简单的“通讯录”应用程序，它可以从文件中读取和写入人们的联系信息。通讯录中的每个人都有姓名、ID、电子邮件地址和联系电话号码。