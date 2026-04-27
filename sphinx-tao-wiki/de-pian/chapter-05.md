# 第五章：文本之德 - reStructuredText 与 Markdown

> 道恒无为也，而无不为也。侯王若能守之，万物将自化。化而欲作，吾将镇之以无名之朴。夫亦将知足，知足以静，万物将自定。

## 5.1 文本之道

Sphinx 支持两种主要的标记语言：

- **reStructuredText** - 原生支持，功能最丰富
- **Markdown** - 通过 MyST 扩展支持

二者各有千秋，相辅相成。

> 曲则全，枉则正，洼则盈，敝则新，少则得，多则惑。

## 5.2 reStructuredText 基础

### 5.2.1 标题层级

```rst
=======
一级标题
=======

二级标题
========

三级标题
--------
```

### 5.2.2 文本格式化

```rst
*斜体*
**粗体**
``代码``
```

### 5.2.3 列表

```rst
- 无序列表项1
- 无序列表项2

1. 有序列表项1
2. 有序列表项2
```

### 5.2.4 链接与引用

```rst
.. _my-label:

引用位置
========

请见 :ref:`my-label`

外部链接：`链接文本 <https://example.com>`_
```

## 5.3 Sphinx 特有指令

### 5.3.1 文档树

```rst
.. toctree::
   :maxdepth: 2
   
   intro
   chapter1
   chapter2
```

### 5.3.2 代码块

```rst
.. code-block:: python
   :linenos:
   
   def hello():
       print("Hello, Sphinx!")
```

### 5.3.3 警告与提示

```rst
.. note::
   这是一个笔记

.. warning::
   这是一个警告

.. tip::
   这是一个提示
```

## 5.4 MyST Markdown

使用 MyST 扩展，可以在 Sphinx 中使用 Markdown：

```markdown
```{toctree}
:maxdepth: 2
intro
chapter1
```

```{code-block} python
:linenos:
def hello():
    print("Hello, Sphinx!")
```

:::{note}
这是一个笔记
:::
```

> 为学者日益，为道者日损。损之又损，以至于无为。无为而无不为也。将欲取天下也，恒无事。及其有事也，又不足以取天下矣。

标记语言的学习，也是一个日益日损的过程，从繁复到简洁，最终达到无为而无不为的境界。

---

**本章要义**：文本是文档的载体，选择合适的标记语言，善用其功能，方能成就优秀的文档。
