# 第七章：域分之德 - Domains 系统

> 知者不言，言者不知。塞其兑，闭其门，和其光，同其尘，挫其锐，解其纷，是谓玄同。故不可得而亲，亦不可得而疏；不可得而利，亦不可得而害；不可得而贵，亦不可得而贱。故为天下贵。

## 7.1 Domain 之德

Domain 是 Sphinx 的领域系统，用于处理特定领域的文档，如 Python、C、JavaScript 等。每个 Domain 提供：

- 特定的指令和角色
- 索引生成
- 交叉引用支持

## 7.2 主要 Domain 详解

### 7.2.1 Python Domain

```python
from sphinx.domains.python import PythonDomain
```

Python Domain 用于记录 Python 代码的文档：

```rst
.. py:function:: my_function(arg1, arg2=None)
   :module: my_module
   
   这是一个函数描述
   
   :param arg1: 参数1说明
   :param arg2: 参数2说明（可选）
   :return: 返回值说明

.. py:class:: MyClass(arg1)
   
   这是一个类
   
   .. py:method:: my_method()
      
      这是一个方法

使用 :py:func:`my_function` 或 :py:class:`MyClass` 进行引用
```

### 7.2.2 其他内置 Domain

- **C Domain** - 用于 C 代码文档
- **C++ Domain** - 用于 C++ 代码文档
- **JavaScript Domain** - 用于 JavaScript 代码文档
- **Standard Domain** - 通用文档元素
- **Math Domain** - 数学公式
- **Changes Domain** - 变更记录

## 7.3 自定义 Domain

创建自定义 Domain：

```python
from sphinx.domains import Domain

class MyDomain(Domain):
    name = 'mydomain'
    label = 'My Domain'
    
    # 配置对象类型
    object_types = {
        'object': ('obj', 'obj'),
    }
    
    # 配置指令
    directives = {
        'object': MyObjectDirective,
    }
    
    # 配置角色
    roles = {
        'obj': MyObjectRole,
    }
    
    # 配置索引
    indices = [MyIndex]
    
    def find_obj(self, env, name, type, searchmode=0):
        """查找对象"""
        pass
```

## 7.4 Domain 的妙用

Domain 的设计体现了"和其光，同其尘"的思想：

- 保持统一的接口
- 适配不同领域的特点
- 无缝集成到 Sphinx 中

> 故立天子，置三卿，虽有拱璧以先驷马，不如坐进此道。古之所以贵此道者何也？不曰求以得，有罪以免邪？故为天下贵。

---

**本章要义**：Domain 使 Sphinx 能适应不同的领域，以统一的方式处理各种文档。
