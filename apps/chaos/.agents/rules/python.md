# Python 开发与版本适配规则

本文档定义本项目 Python 依赖管理、导入风格和版本适配任务的执行约束。

## 1. 环境与依赖管理

- 项目统一使用 `uv` 管理 Python 依赖与虚拟环境。
- 禁止直接使用 `pip` 或 `conda` 安装项目依赖。
- 执行依赖安装、脚本运行、测试和构建前，应优先查看项目已有命令约定。
- 不应依赖开发者本机全局环境完成项目任务。

## 2. 导入规则

Python 代码中的项目内导入必须保持包结构稳定，避免依赖本地文件系统路径或当前工作目录。

- 同一 Python 包内模块互相引用时，使用显式相对导入，例如 `from .module import name` 或 `from ..subpackage import name`。
- 跨包引用优先从稳定的包级公共接口导入。
- 需要直接执行的脚本应通过包入口、模块方式或项目定义的命令入口运行。
- 测试代码必须通过包结构导入被测对象。
- 默认禁止在项目代码、脚本与测试中动态修改 `sys.path`。

## 3. 路径独立性

- 禁止在 Python 代码中硬编码项目内绝对路径。
- 项目内文件引用应基于相对路径、包资源机制或配置入口。
- 代码应在本地开发、CI/CD 和跨操作系统环境中保持可移植。

## 4. Python 版本适配任务

遇到 Python 版本升级、弃用 API 清理、兼容性适配任务时，应读取以下资料并执行对应检查：

- `.agents/docs/version-tracking.md`
- `.agents/rules/citations.md`
- `.agents/scripts/check_python_compat.py`
- `.agents/scripts/check_python_deprecations.py`

版本适配输出应包含：

- 影响范围
- 兼容性风险
- 修改文件
- 验证命令与结果
- 官方引用或项目内相对路径引用
