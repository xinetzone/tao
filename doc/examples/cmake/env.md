# 环境配置

本篇使用 conda 配置 cmake 环境。

1. 创建并激活 conda 环境

```bash
conda create -n ai python=3.12
conda activate ai
```

2. 安装 cmake

```bash
pip install cmake -i https://pypi.tuna.tsinghua.edu.cn/simple
```

3. 安装 ninja，作为 cmake 的 generator：

```bash
conda install -c conda-forge ninja
```

4. 安装 C/C++ 编译器

```bash
conda install -c conda-forge gcc gxx
```

5. 安装 `ipykernel` 用于 Jupyter  notebook
```bash
pip install ipykernel -i https://pypi.tuna.tsinghua.edu.cn/simple
```

6. 安装 Conan
```bash
pip install conan -i https://pypi.tuna.tsinghua.edu.cn/simple
```
