# Python 3.15 代码合规性审查报告

## 审查概要
- **扫描文件数**: 13
- **发现问题数**: 13 → 已修复 12，剩余 1 (远期技术债务)
- **严重度分布**: Critical 0, Warning 0, Info 11 (全部已修复), 技术债务 2 (1 已修复, 1 远期)
- **总体评估**: ✅ 项目代码对 Python 3.15 兼容性良好。所有 Info 级别问题已在 2026-05-21 修复。`re.prefixmatch()` 迁移需 Python ≥ 3.15 运行时支持，当前暂缓。

---

## Critical (已移除/不再支持，必须立即修复)

**未发现 Critical 级别问题。** 项目中不存在以下已移除的 API 调用：
- `ctypes.SetPointerType()` ✗ 未使用
- `glob.glob0()` / `glob.glob1()` ✗ 未使用
- `platform.java_ver()` ✗ 未使用
- `sre_compile` / `sre_constants` / `sre_parse` ✗ 未导入
- `sysconfig.is_python_build(check_home=...)` ✗ 未使用
- `zipimport.zipimporter.load_module()` ✗ 未使用
- `typing.NamedTuple("Name", x=int, y=int)` ✗ 未使用
- `typing.no_type_check_decorator()` ✗ 未使用
- `http.server.CGIHTTPRequestHandler` ✗ 未使用
- `importlib.resources.files(package=...)` ✗ 未使用
- `pathlib.PurePath.is_reserved()` ✗ 未使用
- `typing.ByteString` ✗ 未使用
- `TypedDict("TD")` / `TypedDict("TD", None)` ✗ 未使用
- `datetime.strptime(date_string, "%d")` ✗ 未使用
- `ssl.SSLContext()` 不带 protocol 参数 ✗ 未使用

---

## Warning (已弃用，建议尽快修复)

**未发现 Warning 级别问题。**

---

## Info (行为变更，需要关注)

### 默认编码行为变更 (Python 3.15 默认编码变为 UTF-8)

Python 3.15 中 `open()`、`Path.read_text()`、`Path.write_text()` 的默认编码从"平台相关"统一变更为 **UTF-8**。这在 Windows 平台（此前默认 locale 编码如 cp936/cp1252）上行为会发生变化。以下代码未显式指定 encoding 参数：

#### [aggregate_benchmark.py:L90] `open()` 读取文件未指定 encoding
- **当前代码**:
  ```python
  with open(metadata_path) as mf:
      eval_id = json.load(mf).get("eval_id", eval_idx)
  ```
- **问题说明**: 读取 JSON 元数据文件。在 Python 3.14 及之前，Windows 上默认使用 cp936 编码，可能导致 UTF-8 JSON 文件读取失败。Python 3.15 默认改为 UTF-8，实际上修复了这个问题。
- **整改建议**: 为保持跨版本一致性，显式指定 encoding:
  ```python
  with open(metadata_path, encoding="utf-8") as mf:
      eval_id = json.load(mf).get("eval_id", eval_idx)
  ```

#### [aggregate_benchmark.py:L120] `open()` 读取文件未指定 encoding
- **当前代码**:
  ```python
  with open(grading_file) as f:
      grading = json.load(f)
  ```
- **问题说明**: 读取 grading.json 文件，同上。
- **整改建议**: 添加 `encoding="utf-8"`。

#### [aggregate_benchmark.py:L142] `open()` 读取文件未指定 encoding
- **当前代码**:
  ```python
  with open(timing_file) as tf:
      timing_data = json.load(tf)
  ```
- **问题说明**: 读取 timing.json 文件，同上。
- **整改建议**: 添加 `encoding="utf-8"`。

#### [aggregate_benchmark.py:L377] `open()` 写入文件未指定 encoding
- **当前代码**:
  ```python
  with open(output_json, "w") as f:
      json.dump(benchmark, f, indent=2)
  ```
- **问题说明**: 写入 benchmark.json。在 3.14 及之前，Windows 上 `json.dump` 通过 cp936 编码的文件对象间接写入。3.15 默认 UTF-8 实际上更安全。
- **整改建议**: 添加 `encoding="utf-8"`。

#### [aggregate_benchmark.py:L383] `open()` 写入文件未指定 encoding
- **当前代码**:
  ```python
  with open(output_md, "w") as f:
      f.write(markdown)
  ```
- **问题说明**: 写入 Markdown 报告文件，同上。
- **整改建议**: 添加 `encoding="utf-8"`。

#### [quick_validate.py:L22] `Path.read_text()` 未指定 encoding
- **当前代码**:
  ```python
  content = skill_md.read_text()
  ```
- **问题说明**: 读取 SKILL.md 文件（Markdown）。3.15 默认 UTF-8，行为安全。
- **整改建议**: 显式指定以消除歧义:
  ```python
  content = skill_md.read_text(encoding="utf-8")
  ```

#### [generate_review.py:L94-L95] `Path.read_text()` 未指定 encoding
- **当前代码**:
  ```python
  metadata = json.loads(candidate.read_text())
  ```
- **问题说明**: 读取 JSON 元数据，同上。
- **整改建议**: 添加 `encoding="utf-8"`。

#### [generate_review.py:L156] `Path.read_text()` 未指定 encoding
- **当前代码**:
  ```python
  content = path.read_text(errors="replace")
  ```
- **问题说明**: 读取各类文本文件（.py, .md, .json, .txt 等），同上。
- **整改建议**: 添加 `encoding="utf-8"`。

#### [generate_report.py:L314] `Path.read_text()` 未指定 encoding
- **当前代码**:
  ```python
  data = json.loads(Path(args.input).read_text())
  ```
- **问题说明**: 读取 JSON 输入文件，同上。
- **整改建议**: 添加 `encoding="utf-8"`。

#### [generate_report.py:L319] `Path.write_text()` 未指定 encoding
- **当前代码**:
  ```python
  Path(args.output).write_text(html_output)
  ```
- **问题说明**: 写入 HTML 报告文件，同上。
- **整改建议**: 添加 `encoding="utf-8"`。

#### [generate_review.py:L369] `Path.write_text()` 未指定 encoding
- **当前代码**:
  ```python
  self.feedback_path.write_text(json.dumps(data, indent=2) + "\n")
  ```
- **问题说明**: 写入 feedback.json，同上。
- **整改建议**: 添加 `encoding="utf-8"`。

---

## 技术债务追踪 (未来版本将移除)

### [quick_validate.py:L27] `re.match()` 软弃用 — ⏳ 暂缓 (需 Python ≥ 3.15)
- **当前代码**:
  ```python
  match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
  ```
- **问题说明**: `re.match()` 在 Python 3.15+ 被标记为软弃用。`re.prefixmatch()` 在 3.15 新增，当前运行时不可用。
- **延迟原因**: 需等待 Python ≥ 3.15 成为项目最低运行时版本。
- **远期迁移方案**:
  ```python
  match = re.prefixmatch(r'---\n(.*?)\n---', content, flags=re.DOTALL)
  ```

### [quick_validate.py:L65] `re.match()` 软弃用 — ✅ 已迁移至 `re.fullmatch()` (2026-05-21)
- **当前代码**:
  ```python
  if not re.fullmatch(r'[a-z0-9-]+', name):
  ```
- **状态**: 已修复。`re.fullmatch()` 自 Python 3.4 起可用，语义等价。

---

## 附录

### 扫描文件清单

| # | 文件路径 | 行数 |
|---|---------|------|
| 1 | `src\taolib\__init__.py` | 5 |
| 2 | `docs\conf.py` | 185 |
| 3 | `.agents\skills\skill-creator\scripts\__init__.py` | 0 (空) |
| 4 | `.agents\skills\skill-creator\scripts\utils.py` | 47 |
| 5 | `.agents\skills\skill-creator\scripts\run_loop.py` | 331 |
| 6 | `.agents\skills\skill-creator\scripts\run_eval.py` | 343 |
| 7 | `.agents\skills\skill-creator\scripts\quick_validate.py` | 103 |
| 8 | `.agents\skills\skill-creator\scripts\package_skill.py` | 136 |
| 9 | `.agents\skills\skill-creator\scripts\improve_description.py` | 248 |
| 10 | `.agents\skills\skill-creator\scripts\generate_report.py` | 326 |
| 11 | `.agents\skills\skill-creator\scripts\aggregate_benchmark.py` | 401 |
| 12 | `.agents\skills\skill-creator\eval-viewer\generate_review.py` | 471 |
| 13 | `.agents\skills\skill-creator\tests\test_windows_compat.py` | 62 |

### 已检查但未发现问题的 API 清单

以下检查项均已扫描，确认项目中未使用：

**3.15 已移除**: `ctypes.SetPointerType`, `glob.glob0/1`, `platform.java_ver`, `sre_*`, `sysconfig.is_python_build(check_home=)`, `zipimport.load_module`, `typing.NamedTuple(keyword)`, `no_type_check_decorator`, `CGIHTTPRequestHandler`, `importlib.resources.files(package=)`, `PurePath.is_reserved`, `typing.ByteString`, `TypedDict(no fields)`, `datetime.strptime(no year)`, `ssl.SSLContext(no protocol)`

**行为变更(未受影响)**: `pprint.pprint` 默认格式、`argparse.ArgumentParser` dest 推断、`base64.urlsafe_b64decode` 填充、`unittest.assertWarns` 警告屏蔽

**3.16 计划移除(未受影响)**: `asyncio.iscoroutinefunction`, `array('u')`, `functools.reduce(keyword)`, `sys._enablelegacywindowsfsencoding`, `sysconfig.expand_makefile_vars`

**未来移除(未受影响)**: `datetime.utcnow/utcfromtimestamp`, `threading` 旧方法名, `logging.warn`, `calendar.January/February`, `codecs.open`, `shutil.rmtree(onerror=)`, `ssl.PROTOCOL_*`, `typing.Text`, `urllib.parse` 旧函数, `os.path.commonprefix`, 标准库模块 `__version__`

### 建议修复优先级 (更新于 2026-05-21)

1. ✅ **已修复 (P1)**: 所有 `open()` / `read_text()` / `write_text()` 调用已添加 `encoding="utf-8"` 参数 (11 处)。
2. ✅ **已修复 (P2)**：`quick_validate.py:L65` 的 `re.match(r'^[a-z0-9-]+$', name)` → `re.fullmatch(r'[a-z0-9-]+', name)`。`re.fullmatch()` 自 Python 3.4 起可用。
3. ⏳ **远期 (P2)**：`quick_validate.py:L27` 的 `re.match()` → `re.prefixmatch()` 需 Python ≥ 3.15 运行时支持。
