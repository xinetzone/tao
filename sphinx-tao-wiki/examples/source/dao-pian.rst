======
道篇
======

.. contents::
   :local:
   :depth: 2

架构之道
========

Sphinx 的核心架构包括：

1. **Sphinx 类** - 主应用程序
2. **Build Environment** - 构建环境
3. **Builder** - 构建器
4. **Domains** - 领域系统

.. code-block:: python

    from sphinx.application import Sphinx
    
    app = Sphinx(
        srcdir='./source',
        confdir='./source',
        outdir='./build/html',
        doctreedir='./build/doctrees',
        buildername='html',
    )
    app.build()

扩展之道
========

Sphinx 的扩展系统非常强大：

- 内置扩展
- 第三方扩展
- 自定义扩展

.. note::
   扩展是 Sphinx 的活力之源，善用之。
