# 第三章：流转之道 - Sphinx 构建流程

> 致虚极，守静笃，万物并作，吾以观其复。夫物芸芸，各复归于其根。曰静，静是谓复命。复命，常也。知常，明也。不知常，妄。妄作，凶。

## 3.1 构建之流转

Sphinx 的构建流程，如水流般，从源文档开始，经过解析、转换、输出，最终到达目标格式。此过程可分为四个阶段：

1. **源阶段** - 读取与解析
2. **境阶段** - 环境与解析
3. **树阶段** - 转换与处理
4. **果阶段** - 输出与生成

## 3.2 详细流程解析

### 3.2.1 源阶段：发现与准备

```python
# 发现源文档
env.find_files(config, builder)

# 确定哪些文件需要重新构建
added, changed, removed = env.get_outdated_files(config_changed)
```

> 合抱之木，生于毫末。九层之台，起于累土。千里之行，始于足下。

### 3.2.2 境阶段：读取与解析

对于每个文档，执行以下操作：

```python
# 读取文档并解析为 doctree
doctree = parser.parse(content, filename)

# 应用转换
transformer.apply_transforms()

# 保存 doctree 以便复用
builder.write_doctree(docname, doctree)
```

此阶段，源文本被解析为抽象语法树（Docutils 的 doctree），环境记录所有相关信息。

### 3.2.3 树阶段：解析与转换

```python
# 从 pickle 读取 doctree
doctree = env.get_and_resolve_doctree(docname, builder)

# 解析引用
env.resolve_references(doctree, docname, builder)

# 应用后处理转换
env.apply_post_transforms(doctree, docname)
```

### 3.2.4 果阶段：输出与生成

```python
# 写入具体格式
builder.write_doc(docname, doctree)
```

## 3.3 完整构建序列

```
┌─────────────────────────────────────────────────┐
│   Sphinx.build()                                │
└──────────────┬──────────────────────────────────┘
               │
               ▼
     ┌───────────────────┐
     │ 读取与解析阶段    │
     │ (Read/Parse)     │
     └────────┬──────────┘
              │
              ▼
     ┌───────────────────┐
     │ 环境更新阶段      │
     │ (Env Update)      │
     └────────┬──────────┘
              │
              ▼
     ┌───────────────────┐
     │ 文档解析阶段      │
     │ (Resolve)         │
     └────────┬──────────┘
              │
              ▼
     ┌───────────────────┐
     │ 输出写入阶段      │
     │ (Write)           │
     └───────────────────┘
```

> 执大象，天下往。往而不害，安平大。乐与饵，过格止。故道之出言也，淡呵其无味也。视之不足见也，听之不足闻也，用之不可既也。

Sphinx 构建之道，淡而无味，视之不见，听之不闻，但用之不尽。

---

**本章要义**：构建如水流，从源到果，流转不息，周而复始。
