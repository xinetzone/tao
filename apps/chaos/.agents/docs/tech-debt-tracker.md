# Python 3.15 技术债务追踪台账

> 本文档记录 Python 3.15 中所有废弃、移除及计划移除的功能，按时间线分类，用于跟踪项目中的技术债务。
> 数据来源：[Python 3.15 新特性 — 官方文档](https://docs.python.org/zh-cn/3.16/whatsnew/3.15.html) 的弃用/移除章节

## 1. 已在 Python 3.15 移除

| 模块/功能 | 说明 | 替代方案 |
|-----------|------|----------|
| `ast` 节点构造器 | 缺失必要参数或传入无效关键字参数现在引发 `TypeError`（而非 `DeprecationWarning`） | 确保所有参数正确 |
| `ctypes.SetPointerType()` | 未写入文档的函数，自 3.13 起弃用 | 使用其他方式设置指针类型 |
| `ctypes` 复数 `_type_` | `c_float_complex`/`c_double_complex`/`c_longdouble_complex` 的 `_type_` 从 `F`/`D`/`G` 改为 `Zf`/`Zd`/`Zg` | 兼容 numpy 的格式字符 |
| `datetime.strptime()` 的 `%d` 无年份 | 格式字符串含 `%d`（月日）但无年份指令时引发 `ValueError` | 格式字符串始终包含 `%Y` 或 `%y` |
| `glob.glob0()` / `glob.glob1()` | 未写入文档的内部函数，自 3.13 起弃用 | `glob.glob()` + `root_dir` 参数 |
| `http.server.CGIHTTPRequestHandler` | 类和 `--cgi` 命令行标志，自 3.13 起弃用 | 使用 WSGI/ASGI 替代 |
| `importlib.resources.files(package=...)` | 弃用的 `package` 参数 | 使用位置参数 |
| `pathlib.PurePath.is_reserved()` | 自 3.13 起弃用 | `os.path.isreserved()` |
| `platform.java_ver()` | 自 3.13 起弃用 | 不再支持 Jython |
| `sre_compile`, `sre_constants`, `sre_parse` | 内部正则表达式模块 | 使用 `re` 模块公开 API |
| `sysconfig.is_python_build(check_home=...)` | 移除 `check_home` 参数 | 无参数调用 |
| `threading.RLock` 额外参数 | C 实现的 `RLock` 不再接受任意位置或关键字参数 | 仅使用 `RLock()` 无参构造 |
| `typing.ByteString`（从 `__all__` 移除） | 自 3.9 起弃用，3.17 移除 | `collections.abc.Buffer` 或 `bytes \| bytearray \| memoryview` |
| `typing.NamedTuple` 关键字语法 | 未写入文档的关键字参数语法 | 类语法或函数语法 |
| `TypedDict("TD")` / `TypedDict("TD", None)` | 零字段构造方式 | `class TD(TypedDict): pass` 或 `TypedDict("TD", {})` |
| `typing.no_type_check_decorator()` | 已弃用函数 | 使用 `@typing.no_type_check` |
| `zipimport.zipimporter.load_module()` | 废弃方法 | `zipimport.zipimporter.exec_module()` |

## 2. 计划在 Python 3.16 移除

| 模块/功能 | 弃用版本 | 说明 | 替代方案 |
|-----------|---------|------|----------|
| 导入系统 `__loader__` | 3.14 | 设置 `__spec__.loader` 失败时不再设置 `__loader__` | 使用 `__spec__.loader` |
| `array` `'u'` 格式码 | 3.3（文档）/ 3.13（运行时） | `wchar_t` 格式 | `'w'` 格式码 (`Py_UCS4`) |
| `asyncio.iscoroutinefunction()` | 3.14 | 已弃用 | `inspect.iscoroutinefunction()` |
| `asyncio` 策略系统 | 3.14 | 整个策略系统 | `asyncio.run()` 或 `asyncio.Runner` + `loop_factory` |
| `~True` / `~False` | 3.12 | 布尔值按位取反 | `not x` 或 `~int(x)` |
| `functools.reduce()` 关键字参数 | 3.14 | 传入 `function` 或 `sequence` 作为关键字参数 | 使用位置参数 |
| `logging` *strm* 参数 | 3.14 | 自定义处理器参数 | 使用 *stream* 参数 |
| `mimetypes` 未加点扩展名 | 3.14 | 有效扩展以 `.` 开头 | 确保扩展名以 `.` 开头 |
| `shutil.ExecError` | 3.14 | 自 3.4 起未被使用，`RuntimeError` 别名 | 直接使用 `RuntimeError` |
| `symtable.Class.get_methods()` | 3.14 | 已弃用 | 其他 symtable API |
| `sys._enablelegacywindowsfsencoding()` | 3.13 | 已弃用 | `PYTHONLEGACYWINDOWSFSENCODING` 环境变量 |
| `sysconfig.expand_makefile_vars()` | 3.14 | 已弃用 | `sysconfig.get_paths()` 的 `vars` 参数 |
| `tarfile.TarInfo.tarfile` | 3.13 | 未使用且未写入文档的属性 | — |

### asyncio 策略系统迁移示例

```python
import asyncio

# 已弃用方式
# asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# 迁移方式
async def main():
    ...

asyncio.run(main(), loop_factory=asyncio.SelectorEventLoop)
```

## 3. 计划在 Python 3.17 移除

| 模块/功能 | 弃用版本 | 说明 | 替代方案 |
|-----------|---------|------|----------|
| CLI `-b` / `-bb` 选项 | 3.15 | Python 2→3 迁移辅助，变为无操作 | 使用类型检查器 |
| `datetime.strptime()` 的 `%e` 无年份 | 3.15 | 不含年份的 `%e` 格式 | 格式字符串始终包含年份 |
| `collections.abc.ByteString` | 3.9 | ABC 类 | `collections.abc.Buffer` |
| `encodings.normalize_encoding()` 非ASCII名称 | 3.15 | 非 ASCII 编码名 | 使用 ASCII 编码名 |
| `webbrowser.MacOSXOSAScript` | 3.15 | macOS 旧类 | `webbrowser.MacOS` |
| `typing._UnionGenericAlias` | 3.14 | 私有实现类 | `typing.get_origin()` / `typing.get_args()` |
| `typing.ByteString` | 3.9 | 类型标注 | `collections.abc.Buffer` 或联合类型 |
| `profile` 模块 | 3.15 | 纯 Python profiler | `profiling.tracing` |

## 4. 计划在 Python 3.18 移除

| 模块/功能 | 弃用版本 | 说明 | 替代方案 |
|-----------|---------|------|----------|
| 布尔值作为文件描述符 | 3.？（较早） | `True`/`False` 作为 fd | 使用整数文件描述符 |
| `decimal` `'N'` 格式 | 3.13 | 非标准格式说明符 | 标准格式说明符 |
| `.pth` 文件 `import` 行 | 3.15（PEP 829） | 静默忽略 | `.start` 文件 |

## 5. 计划在 Python 3.19 移除

| 模块/功能 | 弃用版本 | 说明 | 替代方案 |
|-----------|---------|------|----------|
| `ctypes` `_pack_` 隐式 MSVC 布局 | 3.15 | 非 Windows 平台上通过 `_pack_` 隐式切换布局 | 显式使用 `_layout_` |
| `hashlib` `string=` 关键字参数 | 3.15 | 构造函数的关键字参数别名 | 使用位置参数 |
| `http.cookies` `js_output()` | 3.15 | `Morsel.js_output()` / `BaseCookie.js_output()` | `Morsel.output()` / `BaseCookie.output()` |
| `imaplib.IMAP4.file` | 3.15 | 修改此属性不再有用 | — |

## 6. 计划在 Python 3.20 移除

| 模块/功能 | 弃用版本 | 说明 | 替代方案 |
|-----------|---------|------|----------|
| `struct.Struct.__new__()` 无参数 | 3.15 | 不带 format 参数调用 `__new__` | 提供 format 参数 |
| `struct.Struct.__init__()` 重复调用 | 3.15 | 对已初始化的对象调用 `__init__` | 不重复初始化 |
| `__version__` / `version` / `VERSION` 属性 | 3.15 | 多个标准库模块中的版本属性（见下方列表） | `sys.version_info` |
| `.pth` 文件 `import` 行警告 | 3.15（PEP 829） | 未迁移的 `import` 行产生警告 | `.start` 文件 |
| `.pth` 文件编码 | 3.15（PEP 829） | 必须使用 `utf-8-sig` 编码 | 转换编码 |
| `ast` 抽象节点构造 | 3.15 | 创建抽象 AST 节点（如 `ast.AST`、`ast.expr`） | — |

### `__version__` 属性弃用模块列表

以下模块的 `__version__`、`version` 和 `VERSION` 属性均被弃用，统一改用 `sys.version_info`：

`argparse`, `csv`, `ctypes`, `ctypes.macholib`, `decimal`（改用 `decimal.SPEC_VERSION`）, `http.server`, `imaplib`, `ipaddress`, `json`, `logging`（`__date__` 也弃用）, `optparse`, `pickle`, `platform`, `re`, `socketserver`, `tabnanny`, `tarfile`, `tkinter.font`, `tkinter.ttk`, `wsgiref.simple_server`, `xml.etree.ElementTree`, `xml.sax.expatreader`, `xml.sax.handler`, `zlib`

## 7. 未来移除（无具体日期）

这些 API 已被标记为弃用，但尚未安排具体移除版本。

| 模块/功能 | 说明 | 替代方案 |
|-----------|------|----------|
| `argparse` 嵌套参数组 | 嵌套参数组和嵌套互斥组 | 扁平结构 |
| `argparse` `add_argument_group()` 的 `prefix_chars` | 未写入文档的关键字参数 | — |
| `argparse.FileType` | 类型转换器 | 使用 `argparse.FileType` 需自行评估 |
| `builtins` 生成器 `throw(type, exc, tb)` | 三参数签名 | `throw(exc)` 单参数签名 |
| 数字字面量后紧跟关键字 | `0in x`, `1or x` 等歧义语法 | 添加空格 |
| `__index__`/`__int__` 返回非 int 类型 | 将要求返回 `int` 的严格子类 | 确保返回 `int` |
| `__float__` 返回非 float 类型 | 将要求返回 `float` 实例 | 确保返回 `float` |
| `__complex__` 返回非 complex 类型 | 将要求返回 `complex` 实例 | 确保返回 `complex` |
| `complex()` 复数作为 real/imag 参数 | 传入复数作为 real 或 imag | 仅传入单个位置参数 |
| `calendar.January` / `calendar.February` | 旧式常量名 | `calendar.JANUARY` / `calendar.FEBRUARY` |
| `codecs.open()` | 旧式文件打开方式 | `open()` |
| `codeobject.co_lnotab` | 旧式行号表 | `codeobject.co_lines()` |
| `datetime.utcnow()` | 时区不明确的 UTC 现在 | `datetime.datetime.now(tz=datetime.UTC)` |
| `datetime.utcfromtimestamp()` | 时区不明确的 UTC 时间戳转换 | `datetime.datetime.fromtimestamp(timestamp, tz=datetime.UTC)` |
| `gettext` 复数值非整数 | 复数形式的值 | 使用整数 |
| `importlib.util.cache_from_source()` 的 `debug_override` | 弃用参数 | 使用 `optimization` 参数 |
| `importlib.metadata.EntryPoints` 元组接口 | 旧接口 | 新接口 |
| `importlib.metadata` 返回值隐式 `None` | — | — |
| `logging.warn()` | 自 3.3 起弃用 | `logging.warning()` |
| `mailbox` StringIO / 文本模式 | 弃用 | BytesIO / 二进制模式 |
| `os.register_at_fork()` 多线程 | 多线程进程中调用 | 确保在单线程时调用 |
| `os.path.commonprefix()` | 名称和模块位置具有误导性（不安全） | `os.path.commonpath()` |
| `pydoc.ErrorDuringImport` 元组 `exc_info` | 元组值 | 异常实例 |
| `re` 数字分组引用规则 | 更严格的分组引用规则 | 使用正确的分组引用格式 |
| `shutil.rmtree()` 的 `onerror` | 自 3.12 起弃用 | `onexc` 参数 |
| `ssl.SSLContext` 无 protocol 参数 | 弃用 | 显式指定 protocol |
| `ssl` `set_npn_protocols()` / `selected_npn_protocol()` | NPN 协议 | ALPN |
| `ssl.OP_NO_SSL*` / `ssl.OP_NO_TLS*` | 旧选项 | — |
| `ssl.PROTOCOL_SSLv3` / `PROTOCOL_TLS` / `PROTOCOL_TLSv1` / `PROTOCOL_TLSv1_1` / `PROTOCOL_TLSv1_2` | 旧协议常量 | — |
| `ssl.TLSVersion.SSLv3` / `TLSv1` / `TLSv1_1` | 旧 TLS 版本 | — |
| `threading.Condition.notifyAll()` | 旧方法名 | `notify_all()` |
| `threading.Event.isSet()` | 旧方法名 | `is_set()` |
| `threading.Thread.isDaemon()` / `setDaemon()` | 旧方法名 | `daemon` 属性 |
| `threading.Thread.getName()` / `setName()` | 旧方法名 | `name` 属性 |
| `threading.currentThread()` | 旧方法名 | `current_thread()` |
| `threading.activeCount()` | 旧方法名 | `active_count()` |
| `typing.Text` | Python 2 兼容类型 | `str` |
| `unittest.IsolatedAsyncioTestCase` 非None返回值 | 测试用例返回非 None | 不返回值 |
| `urllib.parse` 旧函数系列 | `splitattr()`, `splithost()`, `splitnport()`, `splitpasswd()`, `splitport()`, `splitquery()`, `splittag()`, `splittype()`, `splituser()`, `splitvalue()`, `to_bytes()` | `urlparse()` |
| `wsgiref.SimpleHandler.stdout.write()` 部分写入 | 不应执行部分写入 | 确保完整写入 |
| `xml.etree.ElementTree.Element` 真值检测 | 弃用真值检测 | 显式 `len(elem)` 或 `elem is not None` |
| `sys._clear_type_cache()` | 已弃用 | `sys._clear_internal_caches()` |

## 8. 软弃用（无移除计划）

这些 API 被标记为"软弃用"（soft deprecated），**暂无移除计划**。

| 模块/功能 | 弃用版本 | 说明 | 替代方案 |
|-----------|---------|------|----------|
| `re.match()` / `re.Pattern.match()` | 3.15 | 名称容易引起歧义，但已使用 30+ 年 | `re.prefixmatch()` / `re.Pattern.prefixmatch()` |

```python
import re

# 新代码推荐（更明确的命名）
m = re.prefixmatch(r"\d+", "123abc")

# 旧代码继续有效（不计划移除）
m = re.match(r"\d+", "123abc")
```

## 9. C API 弃用

| API | 弃用版本 | 移除版本 | 替代方案 |
|-----|---------|---------|----------|
| PEP 456 外部哈希 (`Py_HASH_EXTERNAL`) | 3.15 | 3.19 | — |
| `PyArg_ParseTuple()` 无符号整数溢出 | 3.15 | 未定 | 接受有符号范围 |
| `PyBytes_FromStringAndSize(NULL, len)` | 3.15 | 软弃用 | `PyBytesWriter` API |
| `_PyBytes_Resize()` | 3.15 | 软弃用 | `PyBytesWriter` API |
| `_PyObject_CallMethodId()` | 3.15 | 3.20 | `PyUnicode_InternFromString()` + `PyObject_CallMethod()` |
| `_PyObject_GetAttrId()` | 3.15 | 3.20 | `PyUnicode_InternFromString()` + `PyObject_GetAttr()` |
| `_PyUnicode_FromId()` | 3.15 | 3.20 | `PyUnicode_InternFromString()` |
| `PyComplexObject.cval` 字段 | 3.15 | 未定 | `PyComplex_AsCComplex()` / `PyComplex_FromCComplex()` |
| `_Py_c_sum`, `_Py_c_diff`, `_Py_c_neg`, `_Py_c_prod`, `_Py_c_quot`, `_Py_c_pow`, `_Py_c_abs` | 3.15 | 软弃用 | C11 标准 `<complex.h>` |
| `PyConfig.bytes_warning` | 3.15 | 3.17 | — |
| `Py_INFINITY` 宏 | 3.15 | 软弃用 | C11 `<math.h>` `INFINITY` |
| `Py_MATH_El` / `Py_MATH_PIl` | 3.15 | 3.20 | C11 标准常量 |
| `Py_ALIGNED` | 3.15 | 软弃用 | `alignas` |
| `PY_FORMAT_SIZE_T` | 3.15 | 软弃用 | `"z"` 格式说明符 |
| `Py_LL` / `Py_ULL` | 3.15 | 软弃用 | `LL` / `ULL` 标准后缀 |
| `PY_LONG_LONG`, `PY_LLONG_MIN`, `PY_LLONG_MAX`, `PY_ULLONG_MAX` | 3.15 | 软弃用 | C99 类型/限制 |
| `PY_INT32_T`, `PY_UINT32_T`, `PY_INT64_T`, `PY_UINT64_T`, `PY_SIZE_MAX` | 3.15 | 软弃用 | C99 类型/限制 |
| `Py_UNICODE_SIZE` | 3.15 | 软弃用 | `sizeof(wchar_t)` |
| `Py_VA_COPY` | 3.15 | 软弃用 | `va_copy` |
| `Py_UNICODE_WIDE` | 3.15 | 软弃用 | — |
| `PyType_FromSpec()` 系列 | 3.15 | 软弃用 | `PyType_FromSlots()` |
| `PyModule_FromDefAndSpec()` 系列 | 3.15 | 软弃用 | `PyModule_FromSlotsAndSpec()` |
| `PyGILState` API | 3.15（PEP 788） | 软弃用 | 新的线程附加/分离 API |

## 10. 已移除的 C API

| API | 替代方案 |
|-----|----------|
| `PyUnicode_AsDecodedObject()` | `PyCodec_Decode()` |
| `PyUnicode_AsDecodedUnicode()` | `PyCodec_Decode()` |
| `PyUnicode_AsEncodedObject()` | `PyCodec_Encode()` |
| `PyUnicode_AsEncodedUnicode()` | `PyCodec_Encode()` |
| `PyImport_ImportModuleNoBlock()` | `PyImport_ImportModule()` |
| `PyWeakref_GetObject()` / `PyWeakref_GET_OBJECT` | `PyWeakref_GetRef()` |
| `PySys_ResetWarnOptions()` | 清空 `sys.warnoptions` 和 `warnings.filters` |
| `Py_GetExecPrefix()` | `PyConfig_Get("base_exec_prefix")` |
| `Py_GetPath()` | `PyConfig_Get("module_search_paths")` |
| `Py_GetPrefix()` | `PyConfig_Get("base_prefix")` |
| `Py_GetProgramFullPath()` | `PyConfig_Get("executable")` |
| `Py_GetProgramName()` | `PyConfig_Get("executable")` |
| `Py_GetPythonHome()` | `PyConfig_Get("home")` |
