# 使用 CMake 编程 

CMake 有 [`if` 语句](https://cmake.org/cmake/help/latest/command/if.html)，尽管多年来它变得相当复杂。你可以在 `if` 语句中使用一系列全大写关键字，并且通常可以通过直接名称或使用 `${}` 语法来引用变量（`if` 语句在历史上早于变量扩展）。`if` 语句的示例：

```cmake
if(variable)
    # If variable is `ON`, `YES`, `TRUE`, `Y`, or non zero number
else()
    # If variable is `0`, `OFF`, `NO`, `FALSE`, `N`, `IGNORE`, `NOTFOUND`, `""`, or ends in `-NOTFOUND`
endif()
# If variable does not expand to one of the above, CMake will expand it then try again
```

如果你明确地放入变量扩展，比如 `${variable}`，由于扩展的潜在扩展可能会造成一些混淆，CMake 3.1+ 中添加了一个策略（[CMP0054](https://cmake.org/cmake/help/latest/policy/CMP0054.html)），该策略保持引号扩展不被再次扩展。因此，只要 CMake 的最低版本是 3.1+，你就可以这样做：

```cmake
if("${variable}")
    # True if variable is not false-like
else()
    # Note that undefined variables would be `""` thus false
endif()
```

有多种关键字，例如：

- 一元： `NOT`、 `TARGET`、 `EXISTS`（文件）、 `DEFINED` 等。
- 二元： `STREQUAL`、 `AND`、 `OR`、 `MATCHES`（正则表达式）、 `VERSION_LESS`、 `VERSION_LESS_EQUAL`（CMake 3.7+）等。
- 可以使用括号来分组

## 生成器表达式

[生成器表达式](https://cmake.org/cmake/help/latest/manual/cmake-generator-expressions.7.html)非常强大，但有点奇怪和专门化。大多数 CMake 命令发生在配置时间，包括上面看到的 if 语句。但如果你需要在构建时间甚至安装时间发生逻辑呢？生成器表达式就是为了这个目的添加的。它们在目标属性中被评估。

最简单的生成器表达式是信息性表达式，形式为 `$<KEYWORD>`；它们会评估出与当前配置相关的信息片段。另一种形式是 `$<KEYWORD:value>`，其中 `KEYWORD` 是控制评估的关键字，而 `value` 是要评估的项（这里也可以是信息性表达式关键字）。如果 `KEYWORD` 是生成器表达式或变量，其评估结果为 `0` 或 `1`，当结果为 `1` 时会替换 `value` ，而为 `0` 时不替换。你可以嵌套生成器表达式，并且可以使用变量来使嵌套变量的阅读变得可行。某些表达式允许使用逗号分隔的多个值。

如果你想只为 `DEBUG` 配置添加编译标志，例如，你可以这样做：

```cmake
target_compile_options(MyTarget PRIVATE "$<$<CONFIG:Debug>:--my-flag>")
```

这是一种比使用专门的 `*_DEBUG` 变量来添加东西的新颖且更好的方法，并且可以推广到生成器表达式支持的所有事物。请注意，你永远不应该使用当前配置的配置时值，因为像 IDE 这样的多配置生成器在配置时没有“当前”配置，只有在构建时通过生成器表达式和自定义 `*_<CONFIG>` 变量才能获得。

生成器表达式其他常见用途：

- 将项目限制在特定的语言中，例如 `CXX`，以避免它与 `CUDA` 等东西混合，或者将其包装起来，使其根据目标语言而不同。
- 访问与配置相关的属性，例如目标文件位置。
- 为构建和安装目录指定不同的位置。

最后一个非常常见。你几乎会在每个支持安装的软件包中看到类似这样的内容：

```cmake
target_include_directories(
    MyTarget
  PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)
```

## 宏和函数

你可以轻松地定义自己的 CMake [函数](https://cmake.org/cmake/help/latest/command/function.html)或[宏](https://cmake.org/cmake/help/latest/command/macro.html)。函数和宏之间的唯一区别是作用域；宏没有作用域。因此，如果你在函数中设置一个变量并希望它在函数外部可见，你需要使用 export。因此，嵌套函数有点棘手，因为你必须在每个函数中将你希望对外部世界可见的变量显式地设置为 `export`。但是，函数不像宏那样“泄漏”它们的所有变量。在以下示例中，我将使用函数。

简单的函数示例如下：

```cmake
function(SIMPLE REQUIRED_ARG)
    message(STATUS "Simple arguments: ${REQUIRED_ARG}, followed by ${ARGN}")
    set(${REQUIRED_ARG} "From SIMPLE" PARENT_SCOPE)
endfunction()

simple(This Foo Bar)
message("Output: ${This}")
```

输出将会是：
```bash
-- Simple arguments: This, followed by Foo;Bar
Output: From SIMPLE
```

如果你需要位置参数，它们会明确列出，而所有其他参数都会收集到 `ARGN` （`ARGV` 会包含所有参数，包括你列出的那些）。你必须通过设置变量来绕过 CMake 没有返回值的事实。在上面的例子中，你可以明确地给变量名来设置。

## 参数

CMake 具有命名变量系统，你已经在大多数 CMake 构建函数中看到过它。你可以使用 [cmake_parse_arguments](https://cmake.org/cmake/help/latest/command/cmake_parse_arguments.html) 函数来使用它。如果你想要支持低于 3.5 版本的 CMake，你还需要包含 [CMakeParseArguments](https://cmake.org/cmake/help/latest/module/CMakeParseArguments.html) 模块，它就是在这个模块中成为内置命令之前的所在位置。这里是一个如何使用它的示例：

```cmake
function(COMPLEX)
    cmake_parse_arguments(
        COMPLEX_PREFIX
        "SINGLE;ANOTHER"
        "ONE_VALUE;ALSO_ONE_VALUE"
        "MULTI_VALUES"
        ${ARGN}
    )
endfunction()

complex(SINGLE ONE_VALUE value MULTI_VALUES some other values)
```

在这个函数调用之后，你会找到：
```
COMPLEX_PREFIX_SINGLE = TRUE
COMPLEX_PREFIX_ANOTHER = FALSE
COMPLEX_PREFIX_ONE_VALUE = "value"
COMPLEX_PREFIX_ALSO_ONE_VALUE = <UNDEFINED>
COMPLEX_PREFIX_MULTI_VALUES = "some;other;values"
```

如果你查看官方页面，你会看到一个稍微不同的方法，使用 `set` 来避免在列表中显式地写分号；你可以自由地使用你最喜欢的结构。你可以将其与上面列出的位置参数混合；任何剩余的参数（因此是可选的位置参数）都在 `COMPLEX_PREFIX_UNPARSED_ARGUMENTS` 中。
