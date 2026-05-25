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
conda install -c conda-forge clangdev llvmdev
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

## 4. Windows 下用 Clang 的典型“坑”

这是 Windows 下用 Clang 的一个典型“坑”：Clang 在 Windows 上默认模拟 **MSVC 工具链**，所以会去找 `link.exe` 和 MSVC 的运行库。如果你没装 Visual Studio Build Tools，就会报错。  

不过，**conda 环境里有办法绕过对 MSVC 的依赖**，主要有两条路线：

---

### 🛠️ 方案一：使用 LLVM 自带的 `lld-link`
1. 安装 Clang 和 lld：
   ```bash
   conda install -c conda-forge clang lld
   ```
2. 在 CMake 或构建系统中指定使用 `lld-link` 作为链接器：
   ```bash
   cmake -G Ninja -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_LINKER=lld-link .
   ```
3. 这样 Clang 就不会再调用 MSVC 的 `link.exe`，而是用 LLVM 的 `lld-link` 来完成链接。

---

### 🛠️ 方案二：使用 MinGW 工具链
1. 安装 MinGW-w64 工具链：
   ```bash
   # 稳定版（推荐，适合 Python 扩展）
    conda install -c conda-forge m2w64-toolchain

    # 最新版（适合追新或和 MSYS2 环境统一）
    conda install -c msys2 m2w64-toolchain
   ```
2. 配置 CMake，让 Clang 使用 MinGW 的 `ld` 和运行库：
   ```bash
   cmake -G Ninja -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_SYSTEM_NAME=Windows -DCMAKE_CXX_STANDARD_LIBRARIES="-lstdc++ -lgcc -lm -lpthread"
   ```
3. 这样 Clang 会走 MinGW 的运行库，而不是 MSVC。

---

### ⚖️ 对比
| 路线 | 优点 | 缺点 |
|------|------|------|
| **LLVM + lld-link** | 完整 LLVM 工具链，现代化，链接速度快 | 仍需 Windows SDK 的头文件和库（可通过 `conda-forge::vs2015_runtime` 等包解决一部分(即 `conda install -c conda-forge vs2015_runtime`)） |
| **MinGW 工具链** | 完全不依赖 MSVC，conda 内即可自洽 | 与 Windows 原生 ABI 不完全兼容，某些库可能不适配 |

---

### 🎯 建议
- 如果你要做 **跨平台科学计算/扩展模块**（比如 Python C 扩展），推荐 **方案一（Clang + lld-link）**，更接近 MSVC ABI，兼容性好。  
- 如果你要做 **纯开源跨平台项目**，不依赖 MSVC ABI，可以用 **方案二（MinGW）**，完全摆脱 Visual Studio。  

