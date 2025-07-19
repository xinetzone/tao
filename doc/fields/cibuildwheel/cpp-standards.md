# 现代 C++ 标准

使用现代 C++ 标准（C++11 及更高版本）构建 Python 轮子需要一些技巧。

## manylinux2014 和 C++20

过去的结束支持 manylinux2014 镜像（基于 CentOS 7）包含的 GCC 和 libstdc++ 版本仅支持 C++17 及更早的标准。

manylinux_2_28 是更新的，支持所有 C++ 标准（最高到 C++20）。
