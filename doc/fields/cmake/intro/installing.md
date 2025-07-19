# 安装 CMake

详细教程见：[安装 CMake](https://cliutils.gitlab.io/modern-cmake/chapters/intro/installing.html)

## Pip(x)(推荐) (官方，通常每日更新)

由 CMake 的作者在 KitWare 在内的多个 PyPA 成员维护。现在它支持一些特殊架构，比如 Linux 上的 PowerPC 和 macOS 上的 Apple Silicon，也支持 Alpine 这样的 MUSL 系统。如果你有 pip（Python 的包管理器），你可以这样做（[pip(x)](https://pypi.org/project/cmake/)）：

```bash
pip install cmake
```

只要你的系统存在可执行文件，你几乎可以立即开始使用。如果不存在可执行文件，它将尝试使用 KitWare 的 `scikit-build` 软件包来构建，并且需要较旧版本的 CMake 来构建。所以只有当可执行文件存在时才使用这个系统，而这通常是情况。

这也有尊重你当前虚拟环境的优点。然而，当放在 `pyproject.toml` 文件中时，它确实非常出色——它将仅用于构建你的包，之后不会保留！太棒了。

当然，这也适用于 `pipx`。因此，你甚至可以使用 `pipx run cmake` 在可丢弃的虚拟环境中运行 CMake，无需任何设置——而且这可以直接在 GitHub Actions 上运行，因为 pipx 在那里是一个受支持的包管理器！

## Anaconda / Conda-Forge

使用 [Anaconda](https://anaconda.org/anaconda/cmake) / [Conda-Forge](https://github.com/conda-forge/cmake-feedstock) 安装 CMake

```bash
conda install anaconda::cmake
```

或者

```bash
conda -c conda-forge cmake
```
