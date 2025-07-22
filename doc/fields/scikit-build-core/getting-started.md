# 入门指南

如果你以前从未制作过 Python 包，[`packaging.python.org`](https://packaging.python.org/en/latest/tutorials/packaging-projects) 的教程是很好的起点。它将指导你使用现代工具和配置创建简单的纯 Python 包。另一个很好的资源是 [Scientific Python Developer Guide](https://github.com/scikit-build/scikit-build-sample-projects)。在 [INTERSECT Training: Packaging](https://intersect-training.org/packaging) 也可以找到教程。 

有几种机制可以快速构建包：

- [`uv`](https://docs.astral.sh/uv/) 对 scikit-build-core 有内置支持。只需为你的包创建目录并运行：`uv init --lib --build-backend=scikit`。
- [`scientific-python/cookie`](https://github.com/scientific-python/cookie) 提供了 `cookiecutter/copier` 模板，用于创建包含[科学 Python 开发者指南中所有建议的包](https://github.com/scikit-build/scikit-build-sample-projects)。
- 对于 pybind11，[`pybind11/scikit_build_example`](https://github.com/pybind/scikit_build_example) 中有示例模板。对于 nanobind，[nanobind 示例](https://github.com/wjakob/nanobind_example)包含了 Python 3.12+ 的稳定 ABI！
- 在 scikit-build-sample-projects 中，有几个示例，包括 [scikit-build-core 示例（包括 free-threading）](https://github.com/scikit-build/scikit-build-sample-projects)。