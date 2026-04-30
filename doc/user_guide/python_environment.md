# Python 环境

执行 Python 相关测试和代码运行时，默认使用路径为 `${PYTHON_ENV_DIR:-C:\Users\XMICUser\.conda\envs\py314}` 的 Python 环境（Python 3.14）。

## Python 3.14 新特性

- **PEP 649/PEP 749**：标注延迟求值，提高性能并简化前向引用
- **PEP 734**：标准库中的多解释器支持（`concurrent.interpreters` 模块）
- **PEP 750**：模板字符串字面值
- **PEP 758**：允许不带圆括号的 except 和 except* 表达式
- **PEP 765**：finally 代码块中的控制流
- **PEP 784**：标准库中的 Zstandard 支持（`compression.zstd` 模块）

## Qoder 规范中的 Python 环境

执行 Python 测试和代码运行时，默认使用 `${PYTHON_ENV_DIR:-C:\Users\XMICUser\.conda\envs\py314}` 环境。