---
paths:
  - ".agents/scripts/**/*.py"
  - ".agents/skills/**/scripts/**/*.py"
  - "tasks.py"
---

# 数据流时序审查规则

本文档定义涉及"读取 → 变换 → 写入"链条的脚本与数据流水线在执行时序上的审查约束。

## 1. 适用场景

- 任何涉及"读取 → 变换 → 写入"链条的脚本或数据流水线。
- 包括但不限于：文件批量转换、PDF/Markdown 处理、数据 ETL、片段合并、产物生成等任务。

## 2. 核心原则

### 2.1 内存变换先于写入

所有内存中的变换、合并、清洗、修复操作必须在写入磁盘之前完成。磁盘只承载最终态，不参与中间态的串接。

### 2.2 单次推理步骤

任何 pipeline 默认最多只允许 1 个“推理步骤”（模型调用）。读取、过滤、解析、规范化、合并、落盘等确定性步骤必须由普通脚本完成；仅在需要语言理解、综合判断、生成结论/报告时调用模型。

## 3. 检查清单

执行或审查相关脚本时，应逐项核对：

- 写入语句是否在所有变换逻辑之后？
- 磁盘产物是否依赖内存中已变换后的最终状态，而非原始读入态？
- 多步写入之间是否存在隐式依赖（A 写入 → B 读取 A 的产物 → B 写入）？若存在，应改为内存中链式变换后统一写入。
- pipeline 中是否只有一次模型调用？若超过一次，能否合并为单次推理步骤并保持输入输出稳定？
- 模型调用的输入是否来自确定性的中间产物（文件/结构化数据），而不是混杂了“尚未定型的中间态”？

## 4. 反模式示例

```python
# 错误：先落盘原始内容，再基于磁盘读回的中间产物做变换
write_raw_text(path, raw)
detect_headings(path)        # 依赖磁盘上的中间态
fix_fragments(path)          # 又一次读写磁盘
```

```python
# 错误：在同一个 pipeline 里多次调用模型做“中间加工”，成本高、不可测试、难复现
raw = fetch_sources()
clean = llm_clean(raw)
normalized = llm_normalize(clean)
report = llm_summarize(normalized)
write_final(path, report)
```

## 5. 正确模式

```python
# 正确：内存中完成所有变换，最后统一写入
text = load_source(src)
text = detect_headings(text)
text = fix_fragments(text)
write_final(path, text)
```

```python
# 正确：确定性处理 + 单次推理步骤
raw = fetch_sources()
normalized = normalize(raw)
artifact = write_intermediate(normalized)
report = llm_analyze(artifact)
write_final(path, report)
```

## 6. 流程图

```mermaid
flowchart LR
    A["读取源数据"] --> B["内存变换 1"]
    B --> C["内存变换 2"]
    C --> D["内存变换 N"]
    D --> E["统一写入磁盘"]
```
