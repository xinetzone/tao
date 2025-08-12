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

如何序列化和检索这种结构化数据？有几种方法可以解决这个问题：

- 使用 Python 的序列化。这是默认方法，因为它内置在语言中，但它处理模式演化不佳，而且如果你需要与用 C++或 Java 编写的应用程序共享数据，它也不太适用。
- 你可以发明一种将数据项编码为单个字符串的临时方法——例如将 4 个 int 编码为“12:3:-23:67”。这是一种简单且灵活的方法，尽管它需要编写定制的编码和解析代码，而且解析会带来一定的运行时成本。这种方法最适合编码非常简单的数据。
- 将数据序列化为 XML。这种方法可以很有吸引力，因为 XML（某种程度上）是可读的，而且有适用于多种语言的绑定库。如果你想要与其他应用程序/项目共享数据，这可以是一个不错的选择。然而，XML 以占用空间大而闻名，编码/解码它会对应用程序的性能造成巨大的惩罚。此外，导航 XML DOM 树比通常在类中导航简单字段要复杂得多。

您可以选择这些选项，也可以使用协议缓冲区。协议缓冲区是解决此类问题的灵活、高效、自动化的解决方案。使用协议缓冲区，您编写 `.proto` 描述您希望存储的数据结构的描述。从那里，协议缓冲区编译器创建类，该类使用高效的二进制格式实现协议缓冲区数据的自动编码和解析。生成的类为构成协议缓冲区的字段提供获取器和设置器，并负责将协议缓冲区作为整体进行读取和写入的细节。重要的是，协议缓冲区格式支持随着时间的推移扩展格式，以便代码仍然可以读取使用旧格式编码的数据。

## 定义您的协议格式

要创建您的地址簿应用程序，您需要从 `.proto` 文件开始。 `.proto` 文件中的定义很简单：您为每个要序列化的数据结构添加一个消息，然后在消息中为每个字段指定名称和类型。以下是定义您的消息的 `.proto` 文件， `addressbook.proto` 。

```protobuf
edition = "2023";

package tutorial;

message Person {
  string name = 1;
  int32 id = 2;
  string email = 3;

  enum PhoneType {
    PHONE_TYPE_UNSPECIFIED = 0;
    PHONE_TYPE_MOBILE = 1;
    PHONE_TYPE_HOME = 2;
    PHONE_TYPE_WORK = 3;
  }

  message PhoneNumber {
    string number = 1;
    PhoneType type = 2 [default = PHONE_TYPE_HOME];
  }

  repeated PhoneNumber phones = 4;
}

message AddressBook {
  repeated Person people = 1;
}
```

`.proto` 文件以 `package` 声明开始，这有助于防止不同项目之间的命名冲突。在 Python 中，包通常由目录结构决定，因此你在 `package` 文件中定义的内容对生成的代码没有影响。然而，你仍然应该声明包，以避免在 Protocol Buffers 命名空间以及非 Python 语言中的命名冲突。

接下来是你的消息定义。消息只是包含一组类型字段的聚合。许多标准简单数据类型可用作字段类型，包括 `bool` 、 `int32` 、 `float` 、 `double` 和 `string` 。你也可以通过将其他消息类型用作字段类型来为你的消息添加更多结构——在上面的示例中， `Person` 消息包含 `PhoneNumber` 消息，而 `AddressBook` 消息包含 `Person` 消息。你甚至可以定义嵌套在其他消息中的消息类型——正如你所见， `PhoneNumber` 类型定义在 `Person` 中。如果你想让某个字段具有预定义值列表中的值，你也可以定义 `enum` 类型——在这里，你想要指定电话号码可以是以下电话类型之一： `PHONE_TYPE_MOBILE` 、 `PHONE_TYPE_HOME` 或 `PHONE_TYPE_WORK` 。

每个元素上的 `" = 1`"、`" = 2"` 标记标识了该字段在二进制编码中使用的唯一“标签”。1-15 的标签编码比更高数字的标签少一个字节，因此你可以选择将这些标签用于常用或重复的元素，将 16 及以上的标签留给不常用的可选元素。`repeated` 字段中的每个元素都需要重新编码标签号，因此 `repeated` 字段特别适合这种优化。

会在 [Protocol Buffer 语言指南](https://protobuf.dev/programming-guides/editions)中找到关于编写 `.proto` 文件的完整指南——包括所有可能的字段类型。不过，不要寻找类似类继承的功能——协议缓冲区并不支持这种功能。

## 编译协议缓冲区

现在您已经拥有 `.proto` ，接下来您需要生成用于读取和写入 `AddressBook` （以及 `Person` 和 `PhoneNumber` ）消息所需的类。为此，您需要在您的 `.proto` 上运行协议缓冲区编译器 `protoc` ：

1. 如果您尚未安装编译器，请[下载软件包](https://protobuf.dev/downloads)并按照 README 中的说明进行操作。
2. 现在运行编译器，指定源目录（你的应用程序源代码所在的位置——如果没有提供值，则使用当前目录）、目标目录（你希望生成的代码存放的位置；通常与 `$SRC_DIR` 相同）以及你的 `.proto` 的路径。在这种情况下：
```bash
protoc --proto_path=$SRC_DIR --python_out=$DST_DIR $SRC_DIR/addressbook.proto
```
因为你需要 Python 类，所以你使用 `--python_out` 选项——为其他支持的语言也提供了类似的选项。

Protoc 也能够使用 `--pyi_out` 生成 Python 存根 ( `.pyi` ) 。

这会在您指定的目标目录中生成 `addressbook_pb2.py` （或 `addressbook_pb2.pyi` ）。

## Protocol Buffer API

Python 协议缓冲区编译器不会直接为您生成数据访问代码。相反（如果您查看 `addressbook_pb2.py` 就会看到这一点），它会为所有消息、枚举和字段生成特殊的描述符，以及一些神秘地空置的类，每个消息类型一个：

```python
import google3
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.GOOGLE_INTERNAL,
    0,
    20240502,
    0,
    '',
    'main.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()

DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\nmain.proto\x12\x08tutorial\"\xa3\x02\n\x06Person\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\n\n\x02id\x18\x02 \x01(\x05\x12\r\n\x05\x65mail\x18\x03 \x01(\t\x12,\n\x06phones\x18\x04 \x03(\x0b\x32\x1c.tutorial.Person.PhoneNumber\x1aX\n\x0bPhoneNumber\x12\x0e\n\x06number\x18\x01 \x01(\t\x12\x39\n\x04type\x18\x02 \x01(\x0e\x32\x1a.tutorial.Person.PhoneType:\x0fPHONE_TYPE_HOME\"h\n\tPhoneType\x12\x1a\n\x16PHONE_TYPE_UNSPECIFIED\x10\x00\x12\x15\n\x11PHONE_TYPE_MOBILE\x10\x01\x12\x13\n\x0fPHONE_TYPE_HOME\x10\x02\x12\x13\n\x0fPHONE_TYPE_WORK\x10\x03\"/\n\x0b\x41\x64\x64ressBook\x12 \n\x06people\x18\x01 \x03(\x0b\x32\x10.tutorial.Person')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'google3.main_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_PERSON']._serialized_start=25
  _globals['_PERSON']._serialized_end=316
  _globals['_PERSON_PHONENUMBER']._serialized_start=122
  _globals['_PERSON_PHONENUMBER']._serialized_end=210
  _globals['_PERSON_PHONETYPE']._serialized_start=212
  _globals['_PERSON_PHONETYPE']._serialized_end=316
  _globals['_ADDRESSBOOK']._serialized_start=318
  _globals['_ADDRESSBOOK']._serialized_end=365
# @@protoc_insertion_point(module_scope)

```

每个类中重要的行是 `__metaclass__ = reflection.GeneratedProtocolMessageType` 。虽然 Python 元类的工作细节超出了本教程的范围，但你可以将它们视为创建类的模板。在加载时， `GeneratedProtocolMessageType` 元类使用指定的描述符来创建所有与每种消息类型一起工作的 Python 方法，并将它们添加到相关的类中。然后你可以在代码中使用这些完全填充的类。

所有这些操作最终的效果是，你可以像 `Person` 类定义了 `Message` 基类的每个字段为常规字段一样使用它。例如，你可以这样写：

```python
import addressbook_pb2
person = addressbook_pb2.Person()
person.id = 1234
person.name = "John Doe"
person.email = "jdoe@example.com"
phone = person.phones.add()
phone.number = "555-4321"
phone.type = addressbook_pb2.Person.PHONE_TYPE_HOME
```

请注意，这些赋值并不仅仅是向通用的 Python 对象中添加任意的新字段。如果你尝试为在 `.proto` 文件中未定义的字段赋值，将引发 `AttributeError` 异常。如果你为字段赋值时类型不正确，将引发 `TypeError` 异常。此外，在字段被设置之前读取其值将返回默认值。

```python
person.no_such_field = 1  # raises AttributeError
person.id = "1234"        # raises TypeError
```

### 枚举

枚举是由元类扩展为具有整数值的一组符号常量。因此，例如，常量 `addressbook_pb2.Person.PhoneType.PHONE_TYPE_WORK` 的值为 `2`。

### 标准消息方法

每个消息类还包含一些其他方法，允许你检查或操作整个消息，包括：

- `IsInitialized()` : 检查是否已设置所有必需字段。
- `__str__()` : 返回消息的可读表示形式，特别适用于调试。（通常作为 `str(message)` 或 `print(message)` 调用。）
- `CopyFrom(other_msg)` : 使用给定消息的值覆盖消息。
- `Clear()` : 将所有元素清空至空状态。

这些方法实现了 `Message` 接口。更多信息，请参阅 [Message 的完整 API 文档](https://googleapis.dev/python/protobuf/latest/google/protobuf/message.html#google.protobuf.message.Message)。

### 解析和序列化

最后，每个协议缓冲区类都有方法，可以使用协议缓冲区[二进制格式](https://protobuf.dev/programming-guides/encoding)来写入和读取你选择的类型消息。这些方法包括：

- `SerializeToString()` : 将消息序列化并返回其作为字符串。请注意，字节是二进制的，不是文本；我们只使用 str 类型作为方便的容器。
- `ParseFromString(data)` : 从给定的字符串中解析消息。

```{important}
协议缓冲区和面向对象设计协议缓冲区类基本上是数据持有者（类似于 C 语言中的 struct），它们不提供额外功能；在对象模型中，它们不是很好的第一类公民。如果你想要为生成的类添加更丰富的行为，最好的方法是将生成的协议缓冲区类包装在特定于应用程序的类中。如果你无法控制 `.proto` 文件的设计（例如，如果你是从另一个项目中重用的话），那么包装协议缓冲区也是个好主意。在这种情况下，你可以使用包装类来构建更适合你应用程序独特环境的接口：隐藏一些数据和函数，暴露便利函数等。你永远不应该通过继承来为生成的类添加行为。这将破坏内部机制，而且无论如何都不是好的面向对象实践。
```

## 编写消息

现在尝试使用你的协议缓冲区类。你希望你的地址簿应用程序能够做到的第一件事是将个人详细信息写入地址簿文件。为此，你需要创建并填充你的协议缓冲区类的实例，然后将它们写入输出流。

这里有个程序，它从文件中读取 `AddressBook` ，根据用户输入向其中添加一个新 `Person` ，然后将新的 `AddressBook` 写回文件。
```python
#!/usr/bin/env python3

import addressbook_pb2
import sys

# This function fills in a Person message based on user input.
def PromptForAddress(person):
  person.id = int(input("Enter person ID number: "))
  person.name = input("Enter name: ")

  email = input("Enter email address (blank for none): ")
  if email != "":
    person.email = email

  while True:
    number = input("Enter a phone number (or leave blank to finish): ")
    if number == "":
      break

    phone_number = person.phones.add()
    phone_number.number = number

    phone_type = input("Is this a mobile, home, or work phone? ")
    if phone_type == "mobile":
      phone_number.type = addressbook_pb2.Person.PhoneType.PHONE_TYPE_MOBILE
    elif phone_type == "home":
      phone_number.type = addressbook_pb2.Person.PhoneType.PHONE_TYPE_HOME
    elif phone_type == "work":
      phone_number.type = addressbook_pb2.Person.PhoneType.PHONE_TYPE_WORK
    else:
      print("Unknown phone type; leaving as default value.")

# Main procedure:  Reads the entire address book from a file,
#   adds one person based on user input, then writes it back out to the same
#   file.
if len(sys.argv) != 2:
  print("Usage:", sys.argv[0], "ADDRESS_BOOK_FILE")
  sys.exit(-1)

address_book = addressbook_pb2.AddressBook()

# Read the existing address book.
try:
  with open(sys.argv[1], "rb") as f:
    address_book.ParseFromString(f.read())
except IOError:
  print(sys.argv[1] + ": Could not open file.  Creating a new one.")

# Add an address.
PromptForAddress(address_book.people.add())

# Write the new address book back to disk.
with open(sys.argv[1], "wb") as f:
  f.write(address_book.SerializeToString())
```

## 读取消息

当然，如果无法从中获取任何信息，通讯录将毫无用处！这个示例读取上述示例创建的文件，并打印其中的所有信息。

```python
#!/usr/bin/env python3

import addressbook_pb2
import sys

# Iterates though all people in the AddressBook and prints info about them.
def ListPeople(address_book):
  for person in address_book.people:
    print("Person ID:", person.id)
    print("  Name:", person.name)
    if person.HasField('email'):
      print("  E-mail address:", person.email)

    for phone_number in person.phones:
      if phone_number.type == addressbook_pb2.Person.PhoneType.PHONE_TYPE_MOBILE:
        print("  Mobile phone #: ", end="")
      elif phone_number.type == addressbook_pb2.Person.PhoneType.PHONE_TYPE_HOME:
        print("  Home phone #: ", end="")
      elif phone_number.type == addressbook_pb2.Person.PhoneType.PHONE_TYPE_WORK:
        print("  Work phone #: ", end="")
      print(phone_number.number)

# Main procedure:  Reads the entire address book from a file and prints all
#   the information inside.
if len(sys.argv) != 2:
  print("Usage:", sys.argv[0], "ADDRESS_BOOK_FILE")
  sys.exit(-1)

address_book = addressbook_pb2.AddressBook()

# Read the existing address book.
with open(sys.argv[1], "rb") as f:
  address_book.ParseFromString(f.read())

ListPeople(address_book)

```

## 扩展协议缓冲区

在发布使用你的协议缓冲区的代码之后，迟早你肯定会想要“改进”协议缓冲区的定义。如果你希望你的新缓冲区向后兼容，并且你的旧缓冲区向前兼容——而几乎你肯定会希望如此——那么你需要遵循一些规则。在新版本的协议缓冲区中：

- 你不可以更改任何现有字段的标签编号。
- 你不可以添加或删除任何必需字段。
- 你可以删除可选或重复字段。
- 你可以添加新的可选或重复字段，但你必须使用全新的标签编号（也就是说，这些标签编号在这个协议缓冲区中从未被使用过，即使是被删除的字段也没有使用过）。

如果你遵循这些规则，旧代码将愉快地读取新消息，并简单地忽略任何新字段。对于旧代码，被删除的可选字段将简单地具有其默认值，而被删除的重复字段将是空的。新代码也将透明地读取旧消息。但是请注意，新可选字段不会出现在旧消息中，因此你需要明确地检查它们是否已设置（使用 `HasField('field_name')` ），或者在你的 `.proto` 文件中在标签号后提供合理的默认值。如果可选元素未指定默认值，则使用特定类型的默认值：对于字符串，默认值是空字符串。对于布尔值，默认值是 `false`。对于数值类型，默认值是零。请注意，如果你添加了新的重复字段，你的新代码将无法判断它是被新代码留空了，还是从未被旧代码设置过，因为没有 `HasField` 检查。

## 高级用法

Protocol Buffers 的用途不仅限于简单的访问器和序列化。请务必探索 [Python API 参考](https://googleapis.dev/python/protobuf/latest/)，看看你还可以用它来做些什么。

协议消息类提供的一项关键特性是反射。你可以遍历消息的字段并操作它们的值，而无需针对任何特定的消息类型编写代码。使用反射的非常实用的方式是将协议消息转换为和从其他编码格式（如 XML 或 JSON）进行转换。反射的更高级的用法可能是找出两个相同类型的消息之间的差异，或者开发一种“协议消息的正则表达式”，在其中你可以编写匹配特定消息内容的表达式。如果你发挥想象力，Protocol Buffers 可以应用于比你最初预期的更广泛的问题范围！
