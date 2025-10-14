# 🔧 CMake 构建环境配置

参考文档：[CMake 示例](https://daobook.github.io/pygallery/study/examples/cmake/index.html) · [Conan 使用](https://daobook.github.io/pygallery/study/fields/conan/index.html)

---

## 1. 安装依赖工具

```bash
# 更新 conda
conda update -n base -c defaults conda

# 安装 CMake
pip install cmake -i https://pypi.tuna.tsinghua.edu.cn/simple

# 安装 Ninja（作为 CMake 的构建后端）
conda install -c conda-forge ninja

# 安装 Clang/LLVM 作为 C/C++ 编译器
conda install -c conda-forge clangdev
```

---

## 2. 配置 `pyproject.toml`

```toml
[build-system]
requires = ["scikit-build-core-conan"]
build-backend = "scikit_build_core_conan.build"

[tool.scikit-build]
cmake.args = ["-G", "Ninja"]
cmake.build-type = "Release"

[tool.scikit-build.cmake.define]
CMAKE_C_COMPILER = "clang"
CMAKE_CXX_COMPILER = "clang++"
```

说明：
- `-G Ninja` 指定使用 Ninja 作为生成器  
- `CMAKE_C_COMPILER` / `CMAKE_CXX_COMPILER` 显式指定 Clang 编译器  
- `cmake.build-type` 可选 `Debug` / `Release` / `RelWithDebInfo` 等  

---

## 3. （可选）安装 Conan 依赖管理器

```bash
pip install conan -i https://pypi.tuna.tsinghua.edu.cn/simple
```

Conan 可用于自动化管理第三方 C/C++ 库依赖，推荐在需要复杂依赖时启用。
