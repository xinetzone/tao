# Python 3.15 标准库接口变更

> 本文档记录 Python 3.15 标准库模块的接口变更，按模块分类。
> 数据来源：[Python 3.15 新特性 — 官方文档](https://docs.python.org/zh-cn/3.16/whatsnew/3.15.html)

## 1. 新增模块

### 1.1 math.integer (PEP 791)

提供整数参数的数学函数。

```python
import math.integer

# 整数数学运算
```

### 1.2 profiling (PEP 799)

统一的性能分析命名空间包：

| 子模块 | 说明 |
|--------|------|
| `profiling.tracing` | 确定性函数调用追踪（从 `cProfile` 迁移） |
| `profiling.sampling` | 新的统计采样分析器（代号 Tachyon） |

```python
import profiling.tracing
import profiling.sampling
```

> **注意**：`cProfile` 模块保留为向后兼容的别名。`profile` 模块已弃用，计划在 Python 3.17 中移除。

## 2. 标准库模块变更

### 2.1 argparse

| 变更 | 说明 |
|------|------|
| `BooleanOptionalAction` 支持单横线长选项 | `-enable` 和 `-no-enable` 现被支持 |
| `suggest_on_error` 默认 `True` | 拼写错误的参数默认启用建议 |
| 反引号标记支持 | description/epilog 中 \`code\` 语法高亮内联代码 |
| help 文本反引号/双反引号 | 扩展反引号标记到参数 help 和支持 RST 内联样式 |

```python
import argparse

parser = argparse.ArgumentParser()
# suggest_on_error 默认为 True，无需显式设置
parser.add_argument('--verbose', '-v', action=argparse.BooleanOptionalAction)
# 反引号标记自动高亮
parser.description = "使用 `--config` 指定配置文件路径"
```

### 2.2 array

| 变更 | 说明 |
|------|------|
| 新增复数类型 | 格式化字符 `'Zf'`（浮点复数）和 `'Zd'`（双精度复数） |
| 新增半精度浮点 | 格式化字符 `'e'`（16 位 IEEE 754） |
| `array.typecodes` 类型变更 | 从 `str` 变为 `tuple`，支持长度超过 1 的类型码 |

```python
import array

# 复数数组
c = array.array('Zf', [1+2j, 3+4j])

# 半精度浮点
h = array.array('e', [1.0, 2.0, 3.0])

# typecodes 现在是 tuple
print(array.typecodes)  # ('b', 'B', 'u', 'h', ..., 'Zf', 'Zd')
```

### 2.3 base64

新增参数概览：

| 参数 | 适用函数 | 说明 |
|------|----------|------|
| `pad` | `z85encode()` | 控制 Z85 填充 |
| `padded` | `b32encode/decode()`, `b32hexencode/decode()`, `b64encode/decode()`, `urlsafe_b64encode/decode()` | 控制是否需要填充 |
| `wrapcol` | `b16encode()`, `b32encode()`, `b32hexencode()`, `b64encode()`, `b85encode()`, `z85encode()` | 控制输出换行列宽 |
| `ignorechars` | `b16decode()`, `b32decode()`, `b32hexdecode()`, `b64decode()`, `b85decode()`, `z85decode()` | 解码时忽略指定字符 |
| `canonical` | `b32decode()`, `b32hexdecode()`, `b64decode()`, `urlsafe_b64decode()`, `a85decode()`, `b85decode()`, `z85decode()` | 拒绝非规范编码（非零填充位等） |

```python
import base64

# 无填充 Base64
data = base64.b64encode(b"hello", padded=False)

# 忽略空格/换行的解码
decoded = base64.b64decode("a G V s b G 8=", ignorechars=" ")
```

### 2.4 binascii

| 变更 | 说明 |
|------|------|
| `b2a_base32()` / `a2b_base32()` | 新增 Base32 编解码函数 |
| `b2a_ascii85()` / `a2b_ascii85()` | 新增 Ascii85 编解码函数 |
| `b2a_base85()` / `a2b_base85()` | 新增 Base85 编解码函数 |
| `padded` 参数 | 新增于 `b2a_base32()`, `a2b_base32()`, `b2a_base64()`, `a2b_base64()` |
| `wrapcol` 参数 | 新增于 `b2a_base64()` |
| `alphabet` 参数 | 新增于 `b2a_base64()` 和 `a2b_base64()`，支持替代字母表 |
| `ignorechars` 参数 | 新增于 `a2b_hex()`, `unhexlify()`, `a2b_base64()` |
| `canonical` 参数 | 新增于 `a2b_base64()`，拒绝非零填充位编码 |

```python
import binascii

# 指定字母表
encoded = binascii.b2a_base64(b"data", alphabet=b"-_")
```

### 2.5 contextlib

| 变更 | 说明 |
|------|------|
| `ExitStack` 支持任意描述符 | 支持任意 `__enter__()`/`__exit__()`/`__aenter__()`/`__aexit__()` 描述符 |
| `ContextDecorator` 检测生成器/协程 | 自动将上下文管理器保持在生成器/协程迭代/等待期间打开 |

```python
from contextlib import ContextDecorator, contextmanager

@contextmanager
def managed_resource():
    print("enter")
    yield "resource"
    print("exit")

# 作为装饰器使用时，生成器全程保持上下文管理器打开
@managed_resource()
def process():
    return "done"
```

### 2.6 asyncio

新增 `TaskGroup.cancel()` 方法，允许提前终止任务组：

```python
import asyncio

async def main():
    async with asyncio.TaskGroup() as tg:
        task = tg.create_task(long_running_job())
        await asyncio.sleep(1)
        tg.cancel()  # 目标已达成，取消剩余任务
```

### 2.7 json

| 变更 | 说明 |
|------|------|
| `array_hook` 参数 | 新增于 `load()`/`loads()`，允许对 JSON 数组类型回调以自定义 Python 列表 |
| `frozendict` 支持 | 结合 `object_pairs_hook=frozendict` 和 `array_hook=tuple` 生成深层不可变结构 |

```python
import json

data = json.loads('[1, 2, 3]', array_hook=tuple)
# data = (1, 2, 3)

# 完全不可变的 JSON 解析
immutable = json.loads(
    '{"items": [1, 2, 3], "meta": {"version": 1}}',
    object_pairs_hook=frozendict,
    array_hook=tuple
)
```

### 2.8 os

| 变更 | 说明 |
|------|------|
| `os.statx()` | Linux 4.11+ / glibc 2.28+ 新增，提供更丰富的文件状态信息 |
| `os.makedirs(parent_mode=...)` | 新增 *parent_mode* 参数，指定中间目录的权限模式 |

```python
import os

# statx 获取扩展文件信息
info = os.statx("/path/to/file")

# 创建目录树时控制所有目录的权限
os.makedirs("a/b/c", mode=0o755, parent_mode=0o755)
```

### 2.9 os.path

| 变更 | 说明 |
|------|------|
| `realpath()` all-but-last 模式 | 解析除最后一个组件外的所有符号链接 |
| `realpath(strict=os.path.ALLOW_MISSING)` | 新值：允许最终路径缺失但确保无符号链接 |

```python
import os.path

# 解析路径中除最后一个组件外的所有符号链接
resolved = os.path.realpath("/symlink_dir/final_file")

# 允许缺失的文件
try:
    path = os.path.realpath("/missing", strict=os.path.ALLOW_MISSING)
except FileNotFoundError:
    pass  # 只有非 FileNotFoundError 的错误会被重新引发
```

### 2.10 re

| 变更 | 说明 |
|------|------|
| `re.prefixmatch()` | 新增 API，`re.match()` 的显式替代名 |
| `re.Pattern.prefixmatch()` | 对应模式的方法版本 |
| `re.match()` 软弃用 | 仍可使用但推荐迁移到 `prefixmatch()` |

```python
import re

# 新代码建议
m = re.prefixmatch(r"\d+", "123abc")  # 匹配字符串前缀

# 旧代码仍有效（软弃用，不计划移除）
m = re.match(r"\d+", "123abc")
```

### 2.11 typing

| 变更 | PEP | 说明 |
|------|-----|------|
| `TypeForm[T]` | 747 | 注解值为类型表达式的变量 |
| `TypedDict(closed=True)` | 728 | 不允许额外键 |
| `TypedDict(extra_items=Type)` | 728 | 允许任意类型为指定类型的额外项 |
| `@typing.disjoint_base` | 800 | 标记分离基类 |
| `TypeVarTuple(bound=, covariant=, ...)` | — | 扩展关键字参数 |
| Protocol 参数检查 | — | 不在 Protocol 参数列表中的类型变量引发 `TypeError` |
| Protocol 参数顺序修复 | — | 修复多重继承时类型参数顺序推断 |

```python
from typing import TypeForm, TypedDict, TypeVarTuple

# TypeForm
def validate[T](schema: TypeForm[T], data: object) -> T: ...

# 闭合 TypedDict
class Config(TypedDict, closed=True):
    host: str
    port: int

# TypeVarTuple 扩展
Ts = TypeVarTuple("Ts", covariant=True, infer_variance=True)
```

### 2.12 ssl

| 变更 | 说明 |
|------|------|
| `ssl.HAS_PSK_TLS13` | 指示是否支持 TLS 1.3 外部 PSK |
| `SSLContext.set_groups()` | 设置密钥协商组，扩展了 `set_ecdh_curve()`（需要 OpenSSL 3.2+） |
| `SSLSocket.group()` | 返回当前连接的协商组（需要 OpenSSL 3.2+） |
| `SSLContext.get_groups()` | 返回所有可用密钥协商组列表（需要 OpenSSL 3.5+） |
| `SSLContext.set_ciphersuites()` | 设置 TLS 1.3 加密套件 |
| `ssl.get_sigalgs()` | 返回所有可用 TLS 签名算法列表（需要 OpenSSL 3.4+） |
| `SSLContext.set_client_sigalgs()` | 设置客户端认证的签名算法 |
| `SSLContext.set_server_sigalgs()` | 设置服务器完成握手的签名算法 |
| `SSLSocket.client_sigalg()` | 返回客户端认证选定的签名算法（需要 OpenSSL 3.5+） |
| `SSLSocket.server_sigalg()` | 返回服务器选定的签名算法（需要 OpenSSL 3.5+） |

### 2.13 subprocess

`Popen.wait()` 现在使用事件驱动机制（当 `timeout` 不为 `None` 时）：

| 平台 | 机制 |
|------|------|
| Linux >= 5.3 | `os.pidfd_open()` + `select.poll()` |
| macOS / BSD | `select.kqueue()` + `KQ_FILTER_PROC` + `KQ_NOTE_EXIT` |
| Windows | `WaitForSingleObject`（不变） |

回退：若上述机制都不可用，回退到传统忙循环（非阻塞调用 + 短睡眠）。

### 2.14 tomllib

更新到 TOML 1.1.0（向后兼容 TOML 1.0.0）：

- **内联表允许多行和尾逗号**
- **新增 `\xHH` 转义**（255 以下码点）和 `\e` 转义
- **datetime/time 值的秒可选**

```toml
# TOML 1.1.0
tbl = {
   key = "value",
   nested = { a = 1 },
}

null = "null byte: \x00"
csi = "\e["
dt = 2010-02-03 14:15
t  = 14:15
```

### 2.15 unicodedata

| 变更 | 说明 |
|------|------|
| Unicode 17.0.0 | 数据库更新 |
| `isxidstart()` / `isxidcontinue()` | 检查字符是否可作为 Unicode 标识符的开始/继续 |
| `iter_graphemes()` | 按 Unicode 文本分割规则迭代字素簇 |
| `grapheme_cluster_break()` | 获取字素簇断点属性 |
| `indic_conjunct_break()` | 获取印度文合取断点属性 |
| `extended_pictographic()` | 获取扩展象形属性 |
| `block()` | 返回字符所属的 Unicode 块名 |

```python
import unicodedata

for grapheme in unicodedata.iter_graphemes("café👨‍👩‍👧‍👦"):
    print(grapheme)

print(unicodedata.block("A"))  # 'Basic Latin'
print(unicodedata.isxidstart("_"))  # True
```

### 2.16 wave

| 变更 | 说明 |
|------|------|
| IEEE 浮点 WAVE 音频支持 | `WAVE_FORMAT_IEEE_FLOAT` 格式 |
| `getformat()` / `setformat()` | 显式帧格式处理 |
| `setparams()` 7 元组支持 | 接受包含 `format` 的 7 元组 |

```python
import wave

with wave.open("audio.wav", "wb") as wf:
    wf.setnchannels(2)
    wf.setsampwidth(4)
    wf.setframerate(44100)
    wf.setformat(wave.WAVE_FORMAT_IEEE_FLOAT)
    wf.writeframes(float_samples)
```

### 2.17 unittest

| 变更 | 说明 |
|------|------|
| `assertLogs()` 新增 formatter | 控制日志消息格式化 |
| `assertWarns()` 不再吞噬不匹配警告 | 不匹配的警告会被传播（而非屏蔽） |
| `assertWarns()` 支持嵌套上下文 | 允许嵌套使用 |

```python
import unittest
import logging

class TestExample(unittest.TestCase):
    def test_logs_format(self):
        fmt = logging.Formatter("%(levelname)s: %(message)s")
        with self.assertLogs("myapp", level="INFO") as cm:
            logging.getLogger("myapp").info("hello")
        # cm.formatter 可用于检查格式化输出

    def test_warns_no_swallow(self):
        with self.assertWarns(DeprecationWarning):
            warnings.warn("old", DeprecationWarning)
        # 其他类型的警告不再被吞噬，会正常传播
```

### 2.18 urllib.parse

| 变更 | 适用函数 | 说明 |
|------|----------|------|
| `missing_as_none` | `urlsplit()`, `urlparse()`, `urldefrag()` | 缺失组件返回 `None` 而非 `''` |
| `keep_empty` | `urlunsplit()`, `urlunparse()` | 保留空组件 |

```python
from urllib.parse import urlsplit, urlunsplit

# 区分缺失和空组件
parts = urlsplit("http://example.com", missing_as_none=True)
# parts.query → None (而非 '')

# 保留空组件
url = urlunsplit(("http", "example.com", "", None, None), keep_empty=True)
# "http://example.com/"
```

## 3. 其他模块变更

### 3.1 ast
- `dump()` 新增 *color* 参数，支持 ANSI 语法高亮
- 命令行输出默认语法高亮

### 3.2 calendar
- 命令行文本输出更多颜色
- HTML 输出支持年月选项：`python -m calendar -t html 2009 06`
- `HTMLCalendar` 支持暗黑模式和 HTML5

### 3.3 concurrent.futures
- `ProcessPoolExecutor` 子进程异常终止时改进错误报告，回溯包含 PID 和退出码

### 3.4 csv
- `Sniffer.sniff()` 分隔符检测最高 1.6 倍加速

### 3.5 dataclasses
- 生成的 `__init__` 注解不再包含内部类型名

### 3.6 difflib
- `unified_diff()` 新增 *color* 参数，类似 `git diff` 的彩色输出
- `HtmlDiff` HTML 页面样式改进，迁移到 HTML5

### 3.7 email
- 邮件生成器在地址头含非 ASCII 邮箱时引发错误，需 `EmailPolicy.utf8` 支持

### 3.8 functools
- `singledispatchmethod()` 支持非描述符可调用对象
- `singledispatchmethod()` 作为类属性调用时对第二个参数进行分派

### 3.9 hashlib
- 保证总是可用的哈希函数作为 `hashlib` 的属性存在，即使无后端实现也不会引发 `AttributeError`

### 3.10 http.client
- `HTTPConnection`/`HTTPSConnection` 新增 `max_response_headers` 关键字参数

### 3.11 http.server
- 日志着色化，默认彩色输出
- `default_content_type` 属性和 `--content-type` 命令行选项
- 新增 `extra_response_headers` 和 `-H/--header` 选项

### 3.12 inspect
- `getdoc()` 新增 `inherit_class_doc` 和 `fallback_to_class_doc` 参数

### 3.13 locale
- `setlocale()` 支持带 `@` 修饰符的语言代码
- `getlocale()` 不再静默移除 `@` 修饰符
- 恢复 `getdefaultlocale()` 函数（取消弃用）

### 3.14 mimetypes
- 新增多种 MIME 类型
- `application/x-texinfo` 重命名为 `application/texinfo`
- `.ai` 文件 MIME 类型改为 `application/pdf`

### 3.15 mmap
- Windows 上新增 `trackfd` 参数
- 新增 `set_name()` 方法（Linux 5.17+），注释匿名内存映射

### 3.16 pathlib
- `Path.mkdir()` 新增 `parent_mode` 参数

### 3.17 pdb
- 默认输入 shell 使用新的交互式 shell

### 3.18 pickle
- 支持 pickle 私有方法和嵌套类

### 3.19 pprint
- 默认值更新为 `indent=4, width=88`，格式类似 `json.dumps()`
- 新增 t-string 支持

### 3.20 shelve
- 新增 `reorganize()` 方法回收删除条目释放的空间
- 支持自定义序列化/反序列化函数

### 3.21 socket
- 新增 ISO-TP CAN 协议常量

### 3.22 sqlite3
- 命令行新增 SQL 关键字 Tab 补全
- 命令行输出着色
- 新增表/索引/触发器/视图/列/函数/模式 Tab 补全

### 3.23 sys
- 新增 `sys.abi_info` 命名空间，改进 ABI 信息访问

### 3.24 sys.monitoring
- `PY_THROW`, `PY_UNWIND`, `RAISE`, `EXCEPTION_HANDLED`, `RERAISE` 事件可按代码对象开关
- 从回调返回 `DISABLE` 将禁用整个代码对象的事件

### 3.25 symtable
- 新增 `Function.get_cells()` 和 `Symbol.is_cell()` 方法

### 3.26 tarfile
- `data_filter()` 规范化符号链接目标，防止路径遍历攻击
- `extractall()` 在目录被移除或被替代时跳过修复目录属性
- 链接替换时重新应用提取过滤器，引发 `LinkFallbackError`
- `errorlevel()` 为 0 时不再提取被拒绝的成员
- Windows 上将符号链接目标中的正斜杠替换为反斜杠

### 3.27 timeit
- 命令行输出默认着色
- 新增 `--target-time` 选项和可配置的 `autorange()` 目标时间

### 3.28 tkinter
- `Text.search()` 新增 `nolinestop` 和 `strictlimits` 参数
- 新增 `Text.search_all()` 方法
- 新增 `pack_content()`, `place_content()`, `grid_content()` 方法
- `Event` 新增 `user_data` 和 `detail` 属性

### 3.29 venv
- POSIX 平台：platlib 目录在需要时创建，不再使用 `lib64 → lib` 符号链接

### 3.30 warnings
- `warn_explicit()` 改进模块过滤，对多个父目录构造的模块名进行正则测试

### 3.31 webbrowser
- macOS：新增 `webbrowser.MacOS` 类，通过 `/usr/bin/open` 打开 URL

### 3.32 xml
- 新增 `xml.is_valid_name()` 检查字符串是否可作为 XML 元素/属性名
- 新增 `xml.is_valid_text()` 检查字符串是否可用于 XML 文档

### 3.33 xml.parsers.expat
- 新增 `SetAllocTrackerActivationThreshold()` 和 `SetAllocTrackerMaximumAmplification()`
- 新增 `SetBillionLaughsAttackProtectionActivationThreshold()` 和 `SetBillionLaughsAttackProtectionMaximumAmplification()`
