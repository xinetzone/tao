# Python 3.14 版本适配指南

## 基本信息

| 字段 | 值 |
|------|-----|
| Python 版本 | 3.14.0（最终版 2025-10-07） |
| 项目当前版本 | 3.14.5（via mise） |
| 上一适配版本 | 3.13 → 3.15 追踪（跳过 3.14 系统学习） |
| 本文档创建 | 2026-05-23（复盘行动项 A7） |
| 最后一次更新 | 2026-05-23（基于官方 What's New 文档全面优化 + 合并 3.15 文档交叉引用） |
| 关联文档 | [python-version-adaptation.md](python-version-adaptation.md)（3.15 实际适配变更） |

## 摘要 — 发布重点

Python 3.14 最大的变化包括：

- 🧬 **标注的迟延求值**（PEP 649 & 749）：注解默认延迟求值，不再需要 `from __future__ import annotations`
- 🧵 **标准库中的多解释器**（PEP 734）：新增 `concurrent.interpreters` 模块，支持进程内子解释器并发
- 📝 **模板字符串**（PEP 750）：t-strings 支持自定义字符串处理（SQL 无害化、HTML 转义等）
- 🐛 **安全的外部调试器接口**（PEP 768）：零开销远程调试，`sys.remote_exec()`
- ⚡ **尾调用解释器**：新型 CPython 解释器，几何平均 3-5% 性能提升（x86-64/AArch64 + Clang 19+）
- 🗜️ **标准库 Zstandard 支持**（PEP 784）：新增 `compression.zstd` 模块
- 🔍 **asyncio 内省大幅增强**：`asyncio.Task` 可检查当前运行状态
- 🎨 **REPL 语法高亮** + 多个标准库 CLI 彩色输出
- 🧵 **自由线程模式正式支持**（PEP 779）并显著改进

> **注意**：3.14.0 引入的增量式 GC 在 3.14.5 中已回退到分代 GC（因生产环境内存压力）。本项目使用 3.14.5，因此增量 GC **不适用**。详见 [python-version-adaptation.md](python-version-adaptation.md) 第 5.2 节。

---

## 重大新特性

### PEP 649 & PEP 749：延迟注解求值（Deferred Annotations）

注解求值默认延迟，前向引用不再需要 `from __future__ import annotations`。

```python
# 3.13 之前：前向引用必须用字符串或 __future__ import
class Node:
    def add_child(self, child: "Node") -> None: ...

# 3.14+：自然写法，注解延迟求值
class Node:
    def add_child(self, child: Node) -> None: ...
```

新增 `annotationlib` 模块提供注解内省工具，支持三种求值格式：

```python
from annotationlib import get_annotations, Format

def func(arg: Undefined): ...

get_annotations(func, format=Format.VALUE)      # 运行时值（NameError 如未定义）
get_annotations(func, format=Format.FORWARDREF) # ForwardRef 标记未定义名
get_annotations(func, format=Format.STRING)     # 字符串形式返回
```

- `from __future__ import annotations` 在 3.14 中仍有效但已不必要
- 直接访问 `__annotations__` 的行为有变化（现在返回延迟描述器对象）

**项目影响**：✅ 低风险。typing 模块使用不受影响，Ruff UP 规则可处理旧式写法。使用 `__annotations__` 直接内省的代码需适配。

---

### PEP 734：标准库中的多解释器（Multiple Interpreters）

CPython 支持同进程内多个隔离的 Python 子解释器已 20 多年，但此前仅限 C-API。3.14 新增 `concurrent.interpreters` 模块向 Python 开放此能力。

**核心价值**：
- 全新的用户友好并发模型（类 Erlang/Go 的 CSP 或 Actor 模型）
- 真正的多核并行（自 3.12 起各解释器已足够隔离，可绕过 GIL）
- 比 `multiprocessing` 更轻量：进程级隔离 + 线程级效率

**关键限制（了解即可）**：
- 启动解释器尚未优化；内存占用偏高
- 解释器间数据共享选项有限（`memoryview` 为主）
- 部分 PyPI 第三方扩展模块尚未兼容（标准库扩展模块已全部兼容）

**配套新增**：`concurrent.futures.InterpreterPoolExecutor`，类比 `ProcessPoolExecutor` 但使用子解释器。

```python
from concurrent.futures import InterpreterPoolExecutor

with InterpreterPoolExecutor() as executor:
    future = executor.submit(pow, 2, 10)
    print(future.result())  # 1024
```

**项目影响**：✅ 无影响。可选特性，不会破坏现有代码。项目如需高并发 CPU 密集型任务可后续探索。

---

### PEP 750：模板字符串（t-strings）

```python
name = "World"
t = t"Hello {name}!"
type(t)  # <class 'string.templatelib.Template'>

list(t)  # ['Hello ', Interpolation('World', 'name', None, ''), '!']
```

`Template` 对象在组合前分离静态和插值部分，适用于：
- SQL 无害化（防注入）
- HTML 转义（防 XSS）
- 安全 shell 操作
- 日志格式化增强
- 轻量级业务 DSL

**项目影响**：✅ 无影响。可选特性，不会破坏现有代码。

---

### PEP 768：安全的外部调试器接口

零开销调试接口，允许调试器和性能分析工具在不停止/重启进程的情况下安全附加到运行中的 Python 进程。

```python
import sys
sys.remote_exec(1234, "/path/to/debug_script.py")
```

**安全控制**：
- `PYTHON_DISABLE_REMOTE_DEBUG` 环境变量
- `-X disable-remote-debug` 命令行选项
- `--without-remote-debug` 构建时禁用

**项目影响**：✅ 无影响。可选特性，可在生产环境中通过环境变量禁用。

---

### 尾调用解释器（Tail-Call Interpreter）

CPython 新增一种解释器类型，用 C 函数间的尾调用替代大 `case` 语句。基准测试几何平均 3-5% 性能提升。

- 仅适用 x86-64 和 AArch64 架构上的 Clang 19+
- 通过 `--with-tail-call-interp` 构建配置启用
- 建议搭配 PGO（配置文件引导优化）
- 属于 CPython 内部实现，不改变 Python 代码可见行为

**项目影响**：✅ 无影响。CPython 内部实现细节，用户不可见。

---

### PEP 784：标准库 Zstandard 压缩

新增 `compression.zstd` 模块，提供原生的 Zstandard 压缩/解压支持。

**项目影响**：✅ 无影响。可选特性。

---

### PEP 779：自由线程模式正式支持 + 改进

自由线程 CPython（PEP 703）从 3.13 的实验性进入 3.14 的正式支持，并得到显著改进：
- PEP 703 实现全部完成（包括 C API 变量）
- 专门化自适应解释器（PEP 659）在自由线程构建中启用
- 单线程性能影响降至约 5-10%
- 新增 `-X context_aware_warnings` 旗标（自由线程构建默认启用）
- 新增 `thread_inherit_context` 旗标（子线程继承 `Context` 和警告过滤器）

**项目影响**：✅ 无影响。默认行为不变（GIL 启用），opt-in 特性。

---

### 其他语言特性修改

#### PEP 758：except 表达式省略括号

```python
# 3.14+
except ValueError:            # 单异常可省略括号
    ...
except (ValueError, TypeError):  # 多异常仍需括号
    ...
```

**项目影响**：✅ 无影响。已有括号写法完全兼容。

#### PEP 765：finally 块中禁止 return/break/continue

```python
def bad():
    try:
        return 1
    finally:
        return 2  # 3.14+ 发出 SyntaxWarning（未来版本将升级为 SyntaxError）
```

- 3.14 中是 **SyntaxWarning**，不是 SyntaxError
- 预期在 3.19 升级为 SyntaxError

**项目影响**：⚠️ 需检查。项目代码中如有 finally 块内控制流，应优先调整。

#### ~~增量式垃圾回收（Incremental GC）~~ — 3.14.5 已回退

Python 3.14.0-3.14.4 引入了增量式 GC，但因生产环境内存压力问题，从 **3.14.5**（项目当前版本）和 3.15 起回退到 3.13 的分代 GC。因此本项目不包含此项变更。

> 参考：[python-version-adaptation.md](python-version-adaptation.md) §5.2

#### 改进的错误消息

多项错误消息用户体验提升，包括更精确的类型错误提示和更清晰的前向引用建议。

#### 默认交互式 shell（REPL 语法高亮）

默认交互式 shell 现已支持语法高亮，通过 pyrepl 实现。同时 `argparse` 和 `unittest` 也获得了彩色输出。

---

## 新增模块

| 模块 | 说明 | 项目影响 |
|------|------|---------|
| `concurrent.interpreters` | 子解释器管理（PEP 734） | ✅ 无影响 |
| `compression.zstd` | Zstandard 压缩/解压（PEP 784） | ✅ 无影响 |
| `annotationlib` | 延迟注解内省工具（PEP 649/749） | ✅ 低风险 |
| `string.templatelib` | t-strings 的 Template/Interpolation 类型 | ✅ 无影响 |

---

## 标准库改进

### 重点改进模块

| 模块 | 变更 | 项目影响 |
|------|------|---------|
| `asyncio` | 大幅增强内省能力：`Task.get_current()`, `Task.get_stack()`, `Task.get_coro()` 等 | ✅ 无影响 |
| `concurrent.futures` | 新增 `InterpreterPoolExecutor`（基于子解释器） | ✅ 无影响 |
| `argparse` | 彩色 CLI 输出支持；移除部分旧参数 | ⚠️ 参数移除需检查 |
| `unittest` | 彩色测试输出 | ✅ 无影响 |
| `uuid` | 支持 UUID 6-8；UUID 3-5/8 生成提速 40% | ✅ 无影响 |
| `re` | 性能优化；`re.match` 继续软弃用 | ⚠️ 已在 3.15 适配中处理 |
| `threading` | 旧方法名继续弃用（currentThread → current_thread） | ⚠️ 已在 3.15 适配中处理 |
| `datetime` | `utcnow()`/`utcfromtimestamp()` 弃用；`replace()` 支持 `fold` 关键字 | ⚠️ 已在弃用表记录 |
| `typing` | `typing.Text` 继续弃用；新增 `TypeIs` 支持等 | ⚠️ 已在 3.15 适配中处理 |
| `hmac` | 内置 HACL* 形式验证实现 | ✅ 无影响 |
| `warnings` | `-X context_aware_warnings` 并发安全警告控制 | ✅ 无影响 |
| `sys` | 新增 `remote_exec()`（PEP 768）；`thread_inherit_context` 旗标 | ✅ 无影响 |
| `os` | Windows 上 `open()` 新增 `create_new_console` 参数 | ✅ 无影响 |
| `pathlib` | 性能优化；新增 `from_uri()` 类方法 | ✅ 无影响 |
| `json` | `JSONDecoder` 新增 `object_pairs_hook_args` | ✅ 无影响 |
| `functools` | `reduce()` 关键字参数弃用 | ⚠️ 已在弃用表记录 |

### 其他改进模块

| 模块 | 关键变更 |
|------|---------|
| `ast` | AST 节点新增 `position` 属性；移除部分弃用 API |
| `calendar` | `HTMLCalendar` 支持自定义 CSS 类 |
| `configparser` | `read_dict()` 等函数性能改进 |
| `contextvars` | 配合 `thread_inherit_context` 旗标增强 |
| `ctypes` | `WinDLL` 和 `OleDLL` 移除 |
| `curses` | 新增 `has_extended_color_support()` |
| `decimal` | `Decimal` 构造器性能改进 |
| `difflib` | 性能优化 |
| `dis` | 新增伪指令支持 |
| `email` | 移除 `Message.get_payload()` 和 `Message.set_payload()` 弃用参数 |
| `http` | `HTTPStatus` 新增 `from_int()` |
| `inspect` | `iscoroutinefunction()` 取代 `asyncio.iscoroutinefunction()` |
| `io` | `BufferedIOBase` 等性能改进 |
| `logging.handlers` | `RotatingFileHandler` 新增 `namer` 和 `rotator` 选项 |
| `math` | `lcm()` 和 `gcd()` 支持更多参数类型 |
| `mimetypes` | `guess_type()` 新增 `strict` 参数 |
| `multiprocessing` | `Process.is_alive()` 改进 |
| `operator` | 新增 `call()` |
| `pickle` | 性能改进 |
| `pydoc` | 改进输出格式 |
| `socket` | `SO_EXCEPTION` 等新增常量 |
| `ssl` | `SSLContext` 新增 `minimum_version` / `maximum_version` |
| `sysconfig` | 改进 `get_platform()` 返回值 |
| `unicodedata` | Unicode 16.0.0 支持 |

---

## 移除项

| 移除内容 | 涉及模块 | 替代方案 |
|---------|---------|---------|
| PGP 签名（PEP 761） | 发布包 | Sigstore 验证 |
| `type` 关键字参数 | argparse | 使用 `type=` 替代 |
| 部分 `_private` API | argparse | 使用公开 API |
| `ast.Num`, `ast.Str`, `ast.Bytes`, `ast.NameConstant`, `ast.Ellipsis` | ast | `ast.Constant` |
| 部分弃用函数 | asyncio | `inspect` 模块对应函数 |
| `Message.get_payload()` 和 `set_payload()` 弃用参数 | email | 使用无参数版本 |
| `importlib.abc.ResourceReader`（部分） | importlib.abc | `Traversable` 协议 |
| `itertools.count()` 非整数参数 | itertools | 使用整数参数 |
| `PurePath.__init__()` 关键字参数 | pathlib | 使用位置参数 |
| `pkgutil.ImpImporter` / `pkgutil.ImpLoader` | pkgutil | `importlib` |
| `pty` 模块某些功能 | pty | 取决于平台 |
| `sqlite3` 旧版钩子 API | sqlite3 | 新版钩子 API |
| 部分弃用函数和属性 | urllib | 使用替代接口 |

**项目影响**：⚠️ 需根据项目实际依赖的模块评估。重点检查 `argparse`（旧参数移除）、`ast`（旧节点移除）、`sqlite3`（钩子 API）的使用情况。

---

## 弃用项

> **交叉引用**：本表列出 3.14 起标记的弃用项及其计划移除版本。3.15 实际移除内容、新增弃用项及性能变更见 [python-version-adaptation.md](python-version-adaptation.md)。

### 3.14 新增弃用

| API | 替代方案 | 计划移除 |
|-----|---------|---------|
| `datetime.datetime.utcnow()` | `datetime.now(tz=datetime.UTC)` | 3.17 |
| `datetime.datetime.utcfromtimestamp()` | `datetime.fromtimestamp(ts, tz=datetime.UTC)` | 3.17 |
| `logging.warn()` | `logging.warning()` | 3.17 |
| `codecs.open()` | 内置 `open()` | 3.17 |
| `functools.reduce()` 关键字参数 | 位置参数 | 3.16 |
| `asyncio.iscoroutinefunction()` | `inspect.iscoroutinefunction()` | 3.16 |
| `typing.Text` | `str` | 3.17 |

### 计划在 3.15 移除

| API | 替代方案 |
|-----|---------|
| 旧版 `typing` 别名（`typing.List`, `typing.Dict` 等作为运行时类）| 内置类型 / `collections.abc` |
| `urllib.parse.splitport()` | `urllib.parse.urlparse()` |
| `pydoc.apropos()` | `pydoc.apropos()` 新位置 |

### 计划在 3.16 移除

| API | 替代方案 |
|-----|---------|
| `asyncio.iscoroutinefunction()` | `inspect.iscoroutinefunction()` |
| `functools.reduce()` 关键字参数 | 位置参数 |

### 计划在 3.17 移除

| API | 替代方案 |
|-----|---------|
| `datetime.datetime.utcnow()` | `datetime.now(tz=datetime.UTC)` |
| `datetime.datetime.utcfromtimestamp()` | `datetime.fromtimestamp(ts, tz=datetime.UTC)` |
| `logging.warn()` | `logging.warning()` |
| `codecs.open()` | 内置 `open()` |
| `typing.Text` | `str` |

### 计划在 3.18 移除

| API | 替代方案 |
|-----|---------|
| `email.utils.localtime()` | `email.utils.localtime()` 调整后接口 |
| `ssl` 模块部分弃用 API | 新 SSL API |

### 计划在 3.19 移除

| API | 替代方案 |
|-----|---------|
| `finally` 块中 `return`/`break`/`continue`（PEP 765） | 重构控制流 |

### 计划在未来版本移除

| API | 替代方案 |
|-----|---------|
| `re` 模块旧版行为 | 新 `re` API |
| `threading` 旧方法名（`currentThread` 等） | 新命名规范方法 |

---

## 性能优化

| 模块 | 优化内容 |
|------|---------|
| **尾调用解释器** | 几何平均 3-5% 整体性能提升（Clang 19+, x86-64/AArch64） |
| **自由线程** | 单线程性能影响从 3.13 的 ~50% 降至 3.14 的 ~5-10% |
| **增量式 GC** | ❌ 3.14.5 已回退到分代 GC，本项目不适用 |
| `asyncio` | 事件循环和内省操作性能提升 |
| `base64` | 编码/解码性能提升 |
| `bdb` | 调试器跟踪性能提升 |
| `difflib` | 序列匹配算法性能提升 |
| `gc` | ❌ 增量回收已在 3.14.5 回退 |
| `io` | 缓冲 I/O 操作性能提升 |
| `pathlib` | 路径操作性能提升 |
| `pdb` | 调试器性能提升 |
| `textwrap` | 文本包装性能提升 |
| `uuid` | UUID 3-5/8 生成提速 40% |
| `zlib` | 压缩/解压性能提升 |

---

## 构建与平台变更

| 变更 | 说明 |
|------|------|
| **PEP 761** | 官方发布包停止 PGP 签名，改用 Sigstore |
| **PEP 779** | 自由线程 Python 正式支持 |
| **PEP 776** | Emscripten 平台进入 Tier 3 官方支持 |
| **Android** | 首次提供 Android 二进制发布包 |
| **JIT** | Windows 和 macOS 二进制发布包支持实验性 JIT 编译器 |
| `build-details.json` | 构建信息标准化 |

---

## 项目适配建议

### 已覆盖

- ✅ Ruff `target-version = "py314"` 已配置（A1）
- ✅ `requires-python = ">=3.14"` 已配置（A2）
- ✅ `check_python_compat.py` 和 `check_python_deprecations.py` 覆盖 3.15+ 弃用检测
- ✅ mise.toml 声明 `python = "3.14.5"`

### 待补充

- ⚠️ `check_python_compat.py` 需增加 3.14 专有规则条目：
  - PEP 765 `finally` 块内控制流检测（`return`/`break`/`continue`）
  - PEP 758 `except*` 无括号写法风格检查（可选）
  - `from __future__ import annotations` 冗余导入检测（3.14+ 不再需要）
- ⚠️ `check_python_deprecations.py` 需补充 3.14 新增弃用项：
  - `datetime.utcnow()` / `datetime.utcfromtimestamp()` → `datetime.now(tz=datetime.UTC)` / `datetime.fromtimestamp(ts, tz=datetime.UTC)`
  - `logging.warn()` → `logging.warning()`
  - `codecs.open()` → 内置 `open()`
  - `functools.reduce()` 关键字参数 → 位置参数
  - `asyncio.iscoroutinefunction()` → `inspect.iscoroutinefunction()`
- ⚠️ `argparse` 移除的旧参数需检查项目 CLI 入口
- ⚠️ `ast` 移除的旧节点（`ast.Num`, `ast.Str` 等）需检查项目中是否有 AST 操作代码
- ⚠️ `sqlite3` 旧版钩子 API 移除需检查数据库相关代码

### 可选的探索性工作

- 💡 `concurrent.interpreters` + `InterpreterPoolExecutor` 可用于 CPU 密集型任务的轻量并行（替代 `multiprocessing`）
- 💡 t-strings 可在日志格式化、SQL 无害化、HTML 模板等场景中探索应用
- 💡 `compression.zstd` 可作为高性能压缩选项
- 💡 REPL 语法高亮可改善开发体验

---

## 关键检查清单

| 检查项 | 风险 | 说明 |
|--------|------|------|
| `finally` 块中的 `return`/`break`/`continue` | ⚠️ 中 | 3.14 SyntaxWarning，3.19 将升级为 SyntaxError |
| `datetime.utcnow()` / `utcfromtimestamp()` | ⚠️ 中 | 3.17 移除 |
| `logging.warn()` | ⚠️ 中 | 3.17 移除 |
| `codecs.open()` | ⚠️ 低 | 3.17 移除 |
| `typing.Text` | ⚠️ 低 | 3.17 移除 |
| `functools.reduce()` 关键字参数 | ⚠️ 低 | 3.16 移除 |
| `asyncio.iscoroutinefunction()` | ⚠️ 低 | 3.16 移除，用 `inspect.iscoroutinefunction()` |
| `argparse` 旧参数移除 | ⚠️ 低 | 需检查 CLI 代码 |
| `ast.Num`/`ast.Str` 等旧节点移除 | ⚠️ 低 | 需检查 AST 操作代码 |
| `from __future__ import annotations` | ⚠️ 低 | 3.14+ 冗余，Ruff UP 可处理 |

---

## 参考资料

- [Python 3.14 官方发布页](https://www.python.org/downloads/release/python-3140/)
- [What's New in Python 3.14](https://docs.python.org/zh-cn/3.14/whatsnew/3.14.html)
- [Python 3.14 弃用时间线](https://docs.python.org/3.14/deprecations/index.html)
- [PEP 649 — 延迟注解求值](https://peps.python.org/pep-0649/)
- [PEP 734 — 多解释器](https://peps.python.org/pep-0734/)
- [PEP 749 — 实现 PEP 649](https://peps.python.org/pep-0749/)
- [PEP 750 — 模板字符串](https://peps.python.org/pep-0750/)
- [PEP 758 — except 无括号](https://peps.python.org/pep-0758/)
- [PEP 761 — PGP 签名停用](https://peps.python.org/pep-0761/)
- [PEP 765 — finally 控制流](https://peps.python.org/pep-0765/)
- [PEP 768 — 安全外部调试器接口](https://peps.python.org/pep-0768/)
- [PEP 776 — Emscripten Tier 3](https://peps.python.org/pep-0776/)
- [PEP 779 — 自由线程正式支持](https://peps.python.org/pep-0779/)
- [PEP 784 — Zstandard 标准库支持](https://peps.python.org/pep-0784/)
