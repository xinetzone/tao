# 静态分析

静态分析是指在不执行代码的情况下对代码进行分析。它可用于发现常见的编程错误并强制执行编码规范。使用静态分析工具可以发现的错误示例包括：

- Out of bounds errors（越界错误）
- Memory leaks （内存泄漏）
- Usage of uninitialized variables（未初始化变量的使用）
- Use of unsafe functions（不安全函数的使用）

分析工具能够及早检测错误，并已成为大多数构建链中的标准工具。一些构建工具如 [Clang](http://clang-analyzer.llvm.org/) 内置了静态分析工具，但独立的工具也存在。

这里的示例包括使用以下工具：

```{toctree}
:glob:

*/*
```
