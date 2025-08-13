# pybind11 基本功能

````{note}
为了简洁，所有代码示例都假定存在以下两行：
```cpp
#include <pybind11/pybind11.h>

namespace py = pybind11;
```
`pybind11/pybind11.h` 包含 `Python.h` ，因此它必须是任何源文件或头文件中包含的第一份文件，[原因与 `Python.h` 相同](https://docs.python.org/3/extending/extending.html#a-simple-example)。
````

## 为简单函数创建绑定

从极其简单的函数开始，该函数将两个数字相加并返回结果：
```cpp
int add(int i, int j) {
    return i + j;
}
```

为简化起见，将这个函数和绑定代码都放入名为 `example.cpp` 的文件中，内容如下：
```cpp
#include <pybind11/pybind11.h>

int add(int i, int j) {
    return i + j;
}

PYBIND11_MODULE(example, m) {
    m.doc() = "pybind11 example plugin"; // optional module docstring

    m.def("add", &add, "A function that adds two numbers");
}
```
```{tip}
在实践中，实现代码和绑定代码通常位于不同的文件中。
```

`PYBIND11_MODULE()` 宏创建函数，当从 Python 中发出 `import` 语句时会被调用。模块名称（ `example` ）作为第一个宏参数给出（不应加引号）。第二个参数（ `m` ）定义了类型为 `py::module_` 的变量，这是创建绑定的主要接口。方法 [`module_::def()`](https://pybind11.readthedocs.io/en/stable/reference.html#_CPPv4I0DpEN7module_3defER7module_PKcRR4FuncDpRK5Extra) 生成绑定代码，将 `add()` 函数暴露给 Python。

```{note}
注意只需要很少的代码就能将函数暴露给 Python：所有关于函数参数和返回值的细节都通过模板元编程自动推断。这种整体方法和使用的语法借鉴自 Boost.Python，尽管其底层实现非常不同。
```

`pybind11` 是仅包含头文件的库，因此无需链接任何特殊库，也没有中间（魔法）翻译步骤。在 Linux 上，可以使用以下命令编译上述示例：
```bash
c++ -O3 -Wall -shared -std=c++11 -fPIC $(python3 -m pybind11 --includes) example.cpp -o example$(python3 -m pybind11 --extension-suffix)
```

```{note}
如果你使用 [`Include` 作为子模块](https://pybind11.readthedocs.io/en/stable/installing.html#include-as-a-submodule)获取 `pybind11` 源代码，那么在上述编译中，应使用 `$(python3-config --includes) -Iextern/pybind11/include` 而不是 `$(python3 -m pybind11 --includes)` ，如 [Building manually 中](https://pybind11.readthedocs.io/en/stable/compiling.html#building-manually)所述
```

[`python_example`](https://github.com/pybind/python_example) 和 [`cmake_example`](https://github.com/pybind/cmake_example) 仓库也是很好的起点。它们都是具有跨平台构建系统的完整项目示例。两者之间的唯一区别在于，`python_example` 使用 Python 的 setuptools 来构建模块，而 `cmake_example` 使用 CMake（这可能更适合现有的 C++ 项目）。

编译上述 C++代码将生成可被 Python 导入的二进制模块文件。假设编译后的模块位于当前目录，以下交互式 Python 会话展示了如何加载和执行示例：

```bash
$ python
Python 3.9.10 (main, Jan 15 2022, 11:48:04)
[Clang 13.0.0 (clang-1300.0.29.3)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> import example
>>> example.add(1, 2)
3
>>>
```

## 关键字参数

通过简单的代码修改，可以通知 Python 参数的名称（在本例中为“i”和“j”）。

```cpp
m.def("add", &add, "A function which adds two numbers",
      py::arg("i"), py::arg("j"));
```

[`arg`](https://pybind11.readthedocs.io/en/stable/reference.html#_CPPv43arg) 是一组特殊的标签(tag)类之一，可用于将元数据传递给 `module_::def()` 。通过修改后的绑定代码，现在可以使用关键字参数调用该函数，这对于参数较多的函数来说是一种更易读的替代方案：

```python
>>> import example
>>> example.add(i=1, j=2)
3L
```

关键字名称也出现在文档中的函数签名中。

```python
>>> help(example)

....

FUNCTIONS
    add(...)
        Signature : (i: int, j: int) -> int

        A function which adds two numbers
```

还提供了更简短的命名参数表示法：

```cpp
// regular notation
m.def("add1", &add, py::arg("i"), py::arg("j"));
// shorthand
using namespace pybind11::literals;
m.def("add2", &add, "i"_a, "j"_a);
```

`_a` 后缀形成了 C++11 字面量，它等同于 `arg` 。请注意，字面量运算符必须首先通过指令 `using namespace pybind11::literals` 使其可见。这除了字面量之外，不会从 `pybind11` 命名空间引入任何其他内容。

## 默认参数

假设现在要绑定的函数有默认参数，例如：

```cpp
int add(int i = 1, int j = 2) {
    return i + j;
}
```

不幸的是，pybind11 无法自动提取这些参数，因为它们不是函数类型信息的一部分。然而，使用 `arg` 的扩展方式可以轻松指定它们：

```cpp
m.def("add", &add, "A function which adds two numbers",
      py::arg("i") = 1, py::arg("j") = 2);
```

默认值也出现在文档中。

```python
>>> help(example)

....

FUNCTIONS
    add(...)
        Signature : (i: int = 1, j: int = 2) -> int

        A function which adds two numbers
```

为默认参数也提供了简写符号：

```cpp
// regular notation
m.def("add1", &add, py::arg("i") = 1, py::arg("j") = 2);
// shorthand
m.def("add2", &add, "i"_a=1, "j"_a=2);
```

## 导出变量

要在 C++中暴露一个值，使用 `attr` 函数将其注册到模块中，如下所示。内置类型和普通对象（稍后会详细介绍）在作为属性赋值时会自动转换，并可以使用 `py::cast` 函数显式转换。

```cpp
PYBIND11_MODULE(example, m) {
    m.attr("the_answer") = 42;
    py::object world = py::cast("World");
    m.attr("what") = world;
}
```

这些随后可以从 Python 中访问：

```python
>>> import example
>>> example.the_answer
42
>>> example.what
'World'
```

## 支持的数据类型

内置支持大量数据类型，可直接作为函数参数、返回值或一般情况下的 `py::cast` 使用。完整概述请参阅[类型转换](https://pybind11.readthedocs.io/en/stable/advanced/cast/index.html)部分。
