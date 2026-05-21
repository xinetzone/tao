# Python 3.15 迁移指南

> 本文档记录从较低 Python 版本迁移到 Python 3.15 时需要注意的兼容性变更。
> 数据来源：[Python 3.15 新特性 — 官方文档](https://docs.python.org/zh-cn/3.16/whatsnew/3.15.html) 的 "Porting to Python 3.15" 章节。

## 1. 参数签名变更

### 1.1 sqlite3 API 清理

多个 `sqlite3` API 的参数传递方式发生了变化：

| API | 变更 |
|-----|------|
| `sqlite3.connect()` | 除 *database* 外的所有参数变为 **keyword-only** |
| `Connection.create_function()` | 前三个参数变为 **positional-only** |
| `Connection.create_aggregate()` | 前三个参数变为 **positional-only** |
| `Connection.set_authorizer()` | 第一个参数变为 **positional-only** |
| `Connection.set_progress_handler()` | 第一个参数变为 **positional-only** |
| `Connection.set_trace_callback()` | 第一个参数变为 **positional-only** |

**迁移示例**：

```python
# 错误 (Python 3.15):
conn = sqlite3.connect("mydb.db", 5.0)  # timeout 现在是 keyword-only

# 正确:
conn = sqlite3.connect("mydb.db", timeout=5.0)

# 错误:
conn.create_function(name="myfunc", narg=1, func=myfunc)

# 正确:
conn.create_function("myfunc", 1, myfunc)
```

### 1.2 argparse dest 推断规则变更

当同时传入短选项和单横线长选项时，`dest` 现在从单横线长选项推断：

```python
# Python 3.14 及更早:
parser.add_argument('-f', '-foo')  # dest='f'

# Python 3.15:
parser.add_argument('-f', '-foo')  # dest='foo'  ← 变化！

# 如要保持旧行为，显式指定 dest:
parser.add_argument('-f', '-foo', dest='f')
```

## 2. 运行时行为变更

### 2.1 resource.RLIM_INFINITY 现在总是正数

`resource.RLIM_INFINITY` 现在始终返回正数值。传入负整数（如 `-1` 或 `-3`，视平台而定）到 `resource.setrlimit()` 和 `resource.prlimit()` 现在被弃用。

```python
import resource

# 检查 RLIM_INFINITY —— 现在始终为正数
assert resource.RLIM_INFINITY > 0

# 不要使用负数来代表无限制
# resource.setrlimit(resource.RLIMIT_NOFILE, (-1, -1))  # 已弃用！
```

### 2.2 mmap.resize() 在不支持的平台上被移除

在底层系统调用不支持的平台上，`mmap.mmap.resize()` 不再引发 `SystemError`，而是方法本身被移除。

```python
import mmap

with mmap.mmap(-1, 1024) as m:
    try:
        m.resize(2048)
    except AttributeError:
        # 该平台不支持 resize
        pass
```

### 2.3 xml.etree.ElementTree.iterparse() 未关闭发出 ResourceWarning

如果 `iterparse()` 打开了文件但迭代器未关闭，现在会发出 `ResourceWarning`。

```python
import xml.etree.ElementTree as ET
from contextlib import closing

# 推荐方式：使用 closing() 或显式 close()
with closing(ET.iterparse("large.xml", events=("start",))) as events:
    for event, elem in events:
        process(elem)

# 或显式关闭
it = ET.iterparse("large.xml")
for event, elem in it:
    process(elem)
it.close()
```

### 2.4 base64.urlsafe_b64decode() 不再要求填充

`base64.urlsafe_b64decode()` 不再要求输入填充。如需强制要求填充：

```python
import base64

# Python 3.15：无填充也能解码
base64.urlsafe_b64decode("aGVsbG8")  # OK

# 要求填充：
base64.urlsafe_b64decode("aGVsbG8=", padded=True)  # 仅 3.15+
# 或使用传统方式（兼容旧版本）
base64.b64decode("aGVsbG8=", altchars=b"-_")
```

### 2.5 unittest assertWarns 不再吞噬不匹配的警告

`assertWarns()` 和 `assertWarnsRegex()` 不再屏蔽与指定类别或正则表达式不匹配的警告。你的测试可能会开始泄漏之前被掩盖的警告。

```python
import unittest
import warnings

class TestMigration(unittest.TestCase):
    def test_warns(self):
        # 旧行为：不匹配的警告被吞噬
        # 新行为：不匹配的警告会传播
        with self.assertWarns(DeprecationWarning):
            warnings.warn("old", DeprecationWarning)  # OK，匹配
            # warnings.warn("other", FutureWarning)  # 会传播！之前被吞噬

        # 解决方案：使用警告过滤器屏蔽或额外的 assertWarns 捕获
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", FutureWarning)
            with self.assertWarns(DeprecationWarning):
                warnings.warn("old", DeprecationWarning)
                warnings.warn("will be ignored", FutureWarning)
```

## 3. 默认编码变更（PEP 686）

Python 3.15 将 UTF-8 作为默认编码。这影响所有无显式 `encoding` 参数的 I/O 操作。

### 3.1 受影响的场景

```python
# 以下所有操作默认使用 UTF-8（而非语言区域编码）

# 文件操作
f = open("data.txt")               # 默认 encoding='utf-8'
text = pathlib.Path("file").read_text()  # 默认 encoding='utf-8'

# 标准流
data = sys.stdin.read()            # 默认 encoding='utf-8'

# 子进程
result = subprocess.run(["cmd"], capture_output=True, text=True)
# stdout/stderr 默认 encoding='utf-8'

# 管道
proc = subprocess.Popen(["cmd"], stdout=subprocess.PIPE, text=True)
```

### 3.2 兼容性策略

| 场景 | 建议 |
|------|------|
| 新代码 | 始终显式提供 `encoding` 参数 |
| 需要旧行为 | 使用 `encoding='locale'` |
| 全局禁用 UTF-8 模式 | `PYTHONUTF8=0` 或 `-X utf8=0` |
| 识别受影响代码 | 启用 [opt-in encoding warning](https://docs.python.org/3.16/library/io.html#io-encoding-warning) |

```python
# 推荐写法：显式指定编码
with open("data.txt", encoding="utf-8") as f:
    content = f.read()

# 使用语言区域编码（兼容旧行为）
with open("data.txt", encoding="locale") as f:
    content = f.read()
```

## 4. GC 回退说明

Python 3.14.0-3.14.4 引入了增量垃圾收集器，但因生产环境内存压力问题，从 3.14.5 和 3.15 起回退到 3.13 的分代 GC。

如果你在 3.14.0-3.14.4 上调整了 GC 参数或行为以适应增量 GC，迁移到 3.15 时无需特殊处理——行为与 3.13 的分代 GC 一致。

## 5. pprint 默认格式变更

`pprint` 的默认参数已更新：

| 参数 | 旧默认值 | 新默认值 |
|------|---------|---------|
| `indent` | 1 | **4** |
| `width` | 80 | **88** |

新格式类似于 `json.dumps()` 的美化输出。

```python
import pprint

data = {"name": "Python", "version": "3.15", "features": ["lazy import", "frozendict"]}

# Python 3.15 默认格式
pprint.pprint(data)
# {'features': ['lazy import', 'frozendict'],
#  'name': 'Python',
#  'version': '3.15'}

# 恢复旧的默认格式
pprint.pprint(data, indent=1, width=80)
```

## 6. cProfile 迁移到 profiling.tracing

`cProfile` 模块的功能已迁移到 `profiling.tracing`：

```python
# 旧代码
import cProfile
cProfile.run("my_function()")

# Python 3.15 推荐
import profiling.tracing
profiling.tracing.run("my_function()")

# cProfile 仍作为别名可用（向后兼容）
import cProfile  # 仍然有效
```

`profile` 模块（纯 Python 实现）已弃用，计划在 Python 3.17 中移除。

## 7. 导入系统死锁修复

导入系统现在按层级顺序获取锁（父包优先）。这修复了一个长期存在的死锁场景。

**影响**：如果你的代码依赖特定的导入锁顺序来工作，可能需要重新审视。正常情况下，此修复是透明的，不应产生负面影响。

## 8. 交互式 Shell Tab 补全着色

Tab 补全现在根据对象类型着色。如果你有自定义的 Tab 补全逻辑或自动化脚本依赖纯文本补全：

```bash
# 回退到旧的纯文本补全行为
export PYTHON_BASIC_COMPLETER=1
```

## 9. 彩色输出控制

Python 3.15 中多个工具默认启用彩色输出。全局控制方式：

```bash
# 强制彩色输出
export FORCE_COLOR=1

# 禁用彩色输出
export NO_COLOR=1
# 或
export PYTHON_COLORS=0
```

## 10. 迁移检查清单

在将项目迁移到 Python 3.15 时，建议按以下清单逐项检查：

- [ ] `sqlite3.connect()` 除 database 外的参数改为关键字参数
- [ ] `sqlite3.Connection` 方法的前几个参数改为仅位置参数
- [ ] 检查 `argparse.add_argument()` 的 `dest` 推断（如有 `-f, -foo` 形式）
- [ ] 检查 `base64.urlsafe_b64decode()` 调用是否依赖填充要求
- [ ] 检查 `resource.RLIM_INFINITY` 的负数值使用
- [ ] 检查 `mmap.resize()` 的平台兼容性处理
- [ ] `xml.etree.ElementTree.iterparse()` 添加 `close()` 或使用 `closing()`
- [ ] 检查 `unittest.assertWarns()` 测试是否依赖旧有的警告吞噬行为
- [ ] 显式指定文件 I/O 的 `encoding` 参数
- [ ] 检查 `pprint` 输出格式是否需要保持旧默认值
- [ ] 将 `cProfile` 迁移到 `profiling.tracing`（可选）
- [ ] 将 `profile` 迁移到 `profiling.tracing`（强制，3.17 前）
- [ ] 检查自定义 Tab 补全是否兼容着色输出
