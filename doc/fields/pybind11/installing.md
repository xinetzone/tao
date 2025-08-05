# 安装库

获取 pybind11 源代码的方式有几种，这些代码位于 GitHub 的 [pybind/pybind11](https://github.com/pybind/pybind11) 上。pybind11 开发者推荐使用这里列出的前三种方式之一来获取 pybind11：子模块、PyPI 或 conda-forge。

## 作为子模块包含

当你使用 Git 进行项目开发时，可以将 pybind11 仓库作为子模块使用。在你的 git 仓库中，使用：
```bash
git submodule add -b stable ../../pybind/pybind11 extern/pybind11
git submodule update --init
```

这假设你将你的依赖项放在 `extern/` ，并且你正在使用 GitHub；如果你不使用 GitHub，请使用完整的 https 或 ssh URL 而不是上面提到的相对 URL `../../pybind/pybind11` 。一些其他的服务器也需要 `.git` 扩展名（GitHub 不需要）。

从这里，你现在可以包含 `extern/pybind11/include` ，或者你可以使用 pybind11 提供的各种集成工具（参见[构建系统](https://pybind11.readthedocs.io/en/stable/compiling.html#compiling)）直接从本地文件夹使用。

## 通过 PyPI 包含

你可以使用 Pip 从 PyPI 下载源代码和 CMake 文件作为 Python 包。只需使用：

```bash
pip install pybind11
```

这将提供标准 Python 包格式的 pybind11。如果你希望 pybind11 直接在你的环境根目录下可用，你可以使用：

```bash
pip install "pybind11[global]"
```

如果你使用系统 Python 进行安装，不建议这样做，因为它会将文件添加到 `/usr/local/include/pybind11` 和 `/usr/local/share/cmake/pybind11` ，除非这就是你想要的，否则建议仅在虚拟环境或你的 `pyproject.toml` 文件（参见[构建系统](https://pybind11.readthedocs.io/en/stable/compiling.html#compiling)）中使用。

## 使用 conda-forge 包含

你可以通过 conda-forge 使用 conda 打包来使用 pybind11。

```bash
conda install -c conda-forge pybind11
```
