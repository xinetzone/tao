# `xeus-cling`

[`xeus-cling`](https://xeus-cling.readthedocs.io/en/latest/) 是基于 C++ 的 Jupyter 内核，它基于 C++ 解释器 cling 和 Jupyter 协议 xeus 的原生实现。

安装
```bash
conda create -n cling
conda activate cling
conda install -c conda-forge xeus-cling
conda install ipykernel
conda install conda-forge::jupyter_client
```

## 安装内核规范

当在给定的安装前缀中安装 `xeus-cling` 时，相应的 Jupyter kernelspecs 也会安装在同一环境中，如果 Jupyter 也安装在同一前缀中，它将自动识别这些新的内核。

但是，如果 Jupyter 安装在不同的位置，它将无法识别新的内核。xeus-cling 内核（分别为 C++11、C++14 和 C++17）可以通过以下命令进行注册：
```bash
jupyter kernelspec install PREFIX/share/jupyter/xcpp11 --sys-prefix
jupyter kernelspec install PREFIX/share/jupyter/xcpp14 --sys-prefix
jupyter kernelspec install PREFIX/share/jupyter/xcpp17 --sys-prefix
```

有关 `jupyter kernelspec` 命令的更多信息，请参阅 jupyter_client 文档。

```{toctree}
build-options
magics
```
