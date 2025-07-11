# Ninja 构建系统

参考：[Ninja 手册](https://ninja-build.org/manual.html)

Ninja 是专注于速度的小型构建系统。它与其他构建系统有两个主要区别：它被设计为让更高层的构建系统生成其输入文件，并且它被设计为尽可能快地运行构建。

```{admonition} 是否应使用 Ninja？
Ninja 的低级方法使其非常适合嵌入到功能更丰富的构建系统中；查看[现有工具列表](https://github.com/ninja-build/ninja/wiki/List-of-generators-producing-ninja-build-files)。Ninja 用于构建 Google Chrome、Android 的部分内容、LLVM，并且由于 CMake 的 Ninja 后端，它还可以用于许多其他项目。
```

## 使用 `conda` 安装 Ninja

```bash
conda install -c conda-forge ninja
```

```{toctree}
manual
```
