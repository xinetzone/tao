# Python 3.15 版本适配技术规范

> 本文档记录 Python 3.15 核心语言特性更新，供项目开发与代码审查参考。
> 数据来源：[Python 3.15 新特性 — 官方文档](https://docs.python.org/zh-cn/3.16/whatsnew/3.15.html)
>
> **交叉引用**：3.14 版本的弃用时间线、移除项、适配检查清单见 [python-3.14-adaptation.md](python-3.14-adaptation.md)。

## 1. 核心语言特性

### 1.1 PEP 810: 显式惰性导入 (Lazy Import)

大型 Python 应用程序经常受启动时间困扰，主要原因是导入系统在有深层依赖树时执行了过多顶层代码。Python 3.15 引入 `lazy` 软关键字解决此问题。

**语法示例**：

```python
lazy import json
lazy from pathlib import Path

print("Starting up...")  # json 和 pathlib 尚未加载

data = json.loads('{"key": "value"}')  # json 在此处加载
p = Path(".")  # pathlib 在此处加载
```

**关键行为**：
- 延迟加载直到被导入的名称首次被使用
- 加载失败在首次使用时（而非导入时）抛出异常，回溯同时包含访问位置和初始 import 语句
- 仅允许在模块作用域使用，函数/类体/try 块内使用会引发 `SyntaxError`
- 星号导入和 future 导入不可设为 lazy

**全局控制**：

| 方式 | 说明 |
|------|------|
| `-X lazy_imports=all` | 命令行选项，所有导入变为 lazy |
| `PYTHON_LAZY_IMPORTS=all` | 环境变量，所有导入变为 lazy |
| `sys.set_lazy_imports("all")` | 运行时设置，`"normal"` 恢复默认 |
| `sys.get_lazy_imports()` | 查询当前模式 |
| `sys.set_lazy_imports_filter(callable)` | 设置筛选器，精确控制哪些模块延迟加载 |

**筛选器示例**：

```python
import sys

def myapp_filter(importing, imported, fromlist):
    return imported.startswith("myapp.")

sys.set_lazy_imports_filter(myapp_filter)
sys.set_lazy_imports("all")

import myapp.slow_module  # lazy (匹配筛选器)
import json               # eager (不匹配筛选器)
```

**向后兼容方案**：不支持 `lazy` 关键字的旧版本可通过 `__lazy_modules__` 实现：

```python
__lazy_modules__ = ["json", "pathlib"]

import json     # lazy
import os       # still eager
```

**代理类型**：`types.LazyImportType` 可供需要编程检测惰性导入的代码使用。

### 1.2 PEP 814: frozendict 内建类型

新增不可变映射类型 `frozendict`，直接继承自 `object`（非 `dict` 子类）。

**核心特性**：
- 创建后不可修改
- 所有键和值可哈希时，`frozendict` 本身也可哈希
- 保留插入顺序，但比较不依赖顺序
- `hash(a) == hash(b)` 且 `a == b` 为 `True`（顺序无关）

**基础用法**：

```python
>>> a = frozendict(x=1, y=2)
>>> a
frozendict({'x': 1, 'y': 2})
>>> a['z'] = 3
TypeError: 'frozendict' object does not support item assignment
>>> b = frozendict(y=2, x=1)
>>> hash(a) == hash(b)
True
>>> a == b
True
```

**已适配 frozendict 的模块**：
`copy`, `decimal`, `json`, `marshal`, `plistlib`（仅序列化）, `pickle`, `pprint`, `xml.etree.ElementTree`

**函数适配**：
`eval()`, `exec()` 接受 `frozendict` 作为 *globals*；
`type()`, `str.maketrans()` 接受 `frozendict` 作为 *dict* 参数。

> **迁移提示**：`isinstance(arg, dict)` 的代码应改为 `isinstance(arg, (dict, frozendict))` 或更好的 `isinstance(arg, collections.abc.Mapping)`。

### 1.3 PEP 661: sentinel 哨兵类型

新增 `sentinel` 内建类型，用于创建具有简洁表示的唯一哨兵值。

**核心特性**：
- 复制时保持身份不变
- 支持 `|` 运算符用于类型表达式
- 可通过模块名和名称 pickle（可导入时）

```python
from builtins import sentinel

MISSING = sentinel("MISSING")

def get_value(key, default=MISSING):
    if default is MISSING:
        raise KeyError(key)
    return default
```

### 1.4 PEP 798: 推导式中的解包 (Unpacking in Comprehensions)

列表、集合、字典推导式以及生成器表达式现支持 `*` 和 `**` 解包。

**列表推导**：

```python
>>> lists = [[1, 2], [3, 4], [5]]
>>> [*L for L in lists]  # 等价于 [x for L in lists for x in L]
[1, 2, 3, 4, 5]
```

**集合推导**：

```python
>>> sets = [{1, 2}, {2, 3}, {3, 4}]
>>> {*s for s in sets}  # 等价于 {x for s in sets for x in s}
{1, 2, 3, 4}
```

**字典推导**：

```python
>>> dicts = [{'a': 1}, {'b': 2}, {'a': 3}]
>>> {**d for d in dicts}  # 等价于 {k: v for d in dicts for k,v in d.items()}
{'a': 3, 'b': 2}
```

**生成器表达式与异步生成器**：

```python
>>> gen = (*L for L in lists)
>>> list(gen)
[1, 2, 3, 4, 5]

# 异步: (*a async for a in agen()) 等价于 (x async for a in agen() for x in a)
```

### 1.5 PEP 829: 包启动配置文件 (.start 文件)

引入 `.start` 文件替代 `.pth` 文件中的 `import` 行，提高启动时可审计性。

**格式**：`pkg.mod:callable`，其中 `pkg.mod` 为可导入路径，`callable` 被调用时无参数。

**关键行为**：
- 由 `site` 模块加载（当未传入 `-S` 时）
- `.start` 文件存在时，对应 `.pth` 中的 `import` 行被忽略
- `.pth` 中的 `sys.path` 扩展行不受影响

**弃用时间线**：
| 版本 | 行为 |
|------|------|
| 3.15 | `import` 行静默弃用 |
| 3.18 | `.pth` 中的 `import` 行被静默忽略 |
| 3.20 | `.pth` 文件必须使用 `utf-8-sig` 编码；为 `import` 行产生警告 |

### 1.6 PEP 831: 默认启用 Frame Pointer

CPython 现在默认启用帧指针（`-fno-omit-frame-pointer` 和 `-mno-omit-leaf-frame-pointer`），使系统性能分析器、调试器和 eBPF 工具能更快更可靠地进行原生栈展开。

**构建配置**：
- 通过 `--without-frame-pointers` 可取消启用
- 标志通过 `sysconfig` 暴露，扩展模块自动继承

> **重要**：第三方构建后端应保留这些编译标志。构建系统中任何原生组件未启用帧指针都可能破坏整个 Python 进程的栈展开能力。

### 1.7 PEP 800: 类型系统中的分离基类 (@typing.disjoint_base)

新增 `@typing.disjoint_base` 装饰器，标记类为"分离基类"（disjoint base）。

**语义**：若类 `C` 是分离基类，则 `C` 的子类不能同时继承其他分离基类（除非那些基类是 `C` 的父类或子类）。此功能主要面向类型检查器，用于忠实反映 C 扩展中内建类型的运行时语义。

```python
from typing import disjoint_base

@disjoint_base
class Atomic: ...

class String: ...
class Number(Atomic): ...  # OK

# 以下不允许：
# class Bad(String, Atomic): ...  # TypeError
```

### 1.8 PEP 747: TypeForm 类型表达式注解

新增 `TypeForm` 特殊形式，用于注解"值为类型表达式"的变量。

```python
from typing import Any, TypeForm

def cast[T](typ: TypeForm[T], value: Any) -> T: ...
```

`TypeForm(x)` 在运行时直接返回 `x`，允许显式注解类型形式值而不改变行为。这有助于接受用户提供的类型表达式（如 `int`、`str | None`、`TypedDict`、`list[int]`）的库暴露精确签名。

### 1.9 PEP 728: TypedDict 的 closed / extra_items

`TypedDict` 新增两个类参数：

| 参数 | 行为 |
|------|------|
| `closed=True` | 不允许超出类体定义的额外键 |
| `extra_items=SomeType` | 允许任意额外项，值类型为指定类型 |

```python
from typing import TypedDict

class StrictConfig(TypedDict, closed=True):
    name: str
    version: int

class FlexibleConfig(TypedDict, extra_items=str):
    name: str
    # 允许任意额外字符串值键
```

### 1.10 PEP 686: UTF-8 作为默认编码

Python 现在默认使用 UTF-8 编码，独立于系统环境。I/O 操作（如 `open('file.txt')`）在没有显式 `encoding` 参数时默认使用 UTF-8。

**回退到旧行为**：
- 环境变量：`PYTHONUTF8=0`
- 命令行：`-X utf8=0`
- 代码中：使用 `encoding='locale'` 显式指定当前语言区域编码

> 兼容性建议：始终显式提供 `encoding` 参数以确保版本间最佳兼容性。使用"opt-in encoding warning"来识别可能受影响的代码。

## 2. 改进的错误消息

### 2.1 AttributeError 智能建议

**成员属性建议**：当访问不存在的属性时，解释器会检查对象的成员属性并建议正确的访问路径：

```python
@dataclass
class Circle:
    radius: float
    @property
    def area(self) -> float:
        return pi * self.radius**2

class Container:
    def __init__(self, inner: Circle) -> None:
        self.inner = inner

circle = Circle(radius=4.0)
container = Container(circle)
print(container.area)

# AttributeError: 'Container' object has no attribute 'area'.
# Did you mean '.inner.area' instead of '.area'?
```

**跨语言方法提示**：当无 Levenshtein 近距离匹配时，检查静态跨语言方法名表并建议 Python 等价方法：

```
>>> [1, 2, 3].push(4)
AttributeError: 'list' object has no attribute 'push'. Did you mean '.append'?

>>> 'hello'.toUpperCase()
AttributeError: 'str' object has no attribute 'toUpperCase'. Did you mean '.upper'?

>>> {}.put("a", 1)
AttributeError: 'dict' object has no attribute 'put'. Use d[k] = v.

>>> (1, 2, 3).append(4)
AttributeError: 'tuple' object has no attribute 'append'. Did you mean to use a 'list' object?
```

**delattr 建议**：`delattr()` 失败时解释器也会提示相近的属性名。

## 3. 其他语言特性修改

### 3.1 ImportError __repr__ 改进

`ImportError` 和 `ModuleNotFoundError` 的 `__repr__()` 现在会显示 `name=<name>` 和 `path=<path>`（如果在构造时作为关键字参数传入）。

### 3.2 __dict__ / __weakref__ 共享描述符

`__dict__` 和 `__weakref__` 描述符现在每个解释器使用单一描述符实例，在所有需要的类型间共享。这加速了类创建并有助于避免引用循环。

### 3.3 -W / PYTHONWARNINGS 正则表达式支持

`-W` 选项和 `PYTHONWARNINGS` 环境变量现在可以指定正则表达式（以 `/` 开头和结尾的字段）。

```bash
python -W "error::/.*deprecated.*/" script.py
```

### 3.4 时间戳/超时参数支持任意实数

接受时间戳或超时参数的函数现在接受任意实数（如 `Decimal`、`Fraction`），而不仅限于整数或浮点数。

### 3.5 bytearray.take_bytes() 新方法

新增 `bytearray.take_bytes(n=None, /)` 方法，无需复制即可从 `bytearray` 中取出字节，优化数据缓冲、网络协议解析等场景。

```python
def read() -> bytes:
    buffer = bytearray(1024)
    ...
    return buffer.take_bytes()
```

### 3.6 编译函数支持模块名

`compile()`、`ast.parse()`、`symtable.symtable()` 和 `importlib.abc.InspectLoader.source_to_code()` 现允许传入模块名，用于按模块名明确过滤语法警告。

### 3.7 __slots__ 扩展

- 允许为任何类定义 `__dict__` 和 `__weakref__` 作为 `__slots__`
- 允许为 `tuple` 子类定义任意 `__slots__`（包括 `collections.namedtuple()` 创建的类）

### 3.8 slice 支持泛型

`slice` 类型现支持下标操作，成为泛型类型：

```python
from typing import get_origin, get_args

SliceOfInt = slice[int]
# get_origin(SliceOfInt) → <class 'slice'>
# get_args(SliceOfInt) → (<class 'int'>,)
```

### 3.9 memoryview 复数支持

`memoryview` 类现支持浮点复数和双精度复数 C 类型：格式化字符 `'Zf'` 和 `'Zd'`。

### 3.10 match 语句支持一元正号

`match` 语句的字面量模式现支持一元正号（`+`），与已有的一元负号（`-`）对称。

```python
match value:
    case +42:
        print("positive forty-two")
    case -42:
        print("negative forty-two")
```

### 3.11 导入系统死锁修复

导入系统现在按层级顺序获取每个模块的锁（父包在子模块之前）。这修复了长期存在的死锁问题：一个线程导入 `pkg.sub`，另一个线程导入 `pkg.sub.mod`，当 `pkg/sub/__init__.py` 导入 `pkg.sub.mod` 时，两个线程互相阻塞对方。

### 3.12 bytes.replace() count 参数改进

`bytes.replace()` 的 *count* 参数现在可以是关键字参数。

### 3.13 交互式 Shell Tab 补全着色

Tab 补全现在根据对象类型着色（基于 fancycompleter）。设置 `PYTHON_BASIC_COMPLETER` 可回退到 `rlcompleter`。

### 3.14 彩色输出功能扩展

以下功能的输出现在默认带颜色（可通过环境变量控制）：
- 解释器帮助（`python --help`）
- 不可引发的异常（Unraisable exceptions）

## 4. TypeVarTuple 扩展

`TypeVarTuple` 现接受 `bound`、`covariant`、`contravariant` 和 `infer_variance` 关键字参数，与 `TypeVar` 和 `ParamSpec` 的接口一致。`bound` 语义在规范中尚不明确。

## 5. 性能相关

### 5.1 JIT 编译器升级

Python 3.15 的 JIT 编译器在多个方面得到显著提升：
- 依赖 LLVM 21 进行构建时模板生成
- 新增跟踪前端，支持更多字节码操作和控制流
- 基本寄存器分配，避免内存读写的栈操作
- 更多常量传播和引用计数优化
- 改进的机器码生成（x86-64 和 AArch64）
- GDB 和 GNU `backtrace()` 展开支持

性能基准：x86-64 Linux 上几何平均提升 8-9%，AArch64 macOS 上 12-13%。

### 5.2 GC 回退到 Generational GC

Python 3.14.0-3.14.4 引入了增量 GC，但因生产环境内存压力问题，从 3.14.5 和 3.15 起回退到 3.13 的分代 GC。

> 项目当前使用 Python 3.14.5，因此增量 GC **不适用**。详见 [python-3.14-adaptation.md](python-3.14-adaptation.md)。

### 5.3 mimalloc 默认分配器

`mimalloc` 现作为原始内存分配默认实现（用于 `PyMem_RawMalloc()` 等），在自由线程构建版上表现更优。

### 5.4 base64 & binascii 性能

- Base64 编码 2 倍、解码 3 倍加速
- Ascii85/Base85/Z85 编码解码两个数量级加速（C 重写）
- Base32 编码解码两个数量级加速（C 重写）

### 5.5 csv.Sniffer 性能

`csv.Sniffer.sniff()` 分隔符检测最高 1.6 倍加速。

### 5.6 Windows 64-bit tail-calling 解释器

64 位 MSVC 18 构建现在使用 tail-calling 解释器，pyperformance 基准几何平均提升 15-20%。
