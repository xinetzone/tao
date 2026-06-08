# Miniconda 容器镜像构建与使用指南

## 镜像标签

| 标签 | Containerfile | 描述 |
|------|---------------|------|
| `miniconda3:ubuntu26.04` | `Containerfile` | 基础镜像：Ubuntu 26.04 + Miniconda3 |
| `miniconda3:llvm` | `Containerfile.llvm` | 扩展镜像：基础镜像 + LLVM/Clang (conda-forge) |
| `miniconda3:llvm-gcc` | `Containerfile.llvm.gcc` | 扩展镜像：`miniconda3:llvm` + GCC/G++ (apt) |

## 构建镜像

### 基础镜像

```bash
podman build --format docker -t miniconda3:ubuntu26.04 -f Containerfile .
```

### LLVM/Clang 镜像

```bash
# 需先构建基础镜像
podman build --format docker -t miniconda3:llvm -f Containerfile.llvm .
```

### LLVM/Clang + GCC/G++ 镜像

```bash
# 需先构建 LLVM/Clang 镜像
podman build --format docker -t miniconda3:llvm-gcc -f Containerfile.llvm.gcc .
```

> `--format docker` 用于支持 `SHELL` 指令，避免 OCI 格式兼容警告。

如需指定平台（在非 x86_64 机器上构建）：

```bash
podman build --format docker --platform linux/amd64 -t miniconda3:ubuntu26.04 -f Containerfile .
```

## 运行容器

### 交互式运行

```bash
podman run -it --rm miniconda3:ubuntu26.04
```

### 挂载本地目录

```bash
podman run -it --rm -v $(pwd):/workspace:Z miniconda3:ubuntu26.04
```

### 后台运行

```bash
podman run -d --name conda-dev miniconda3:ubuntu26.04 sleep infinity
podman exec -it conda-dev bash
```

## 验证 conda 环境

进入容器后执行以下命令验证环境正常：

```bash
# 检查 conda 版本
conda --version

# 检查 Python 版本
python --version

# 查看 conda 信息
conda info

# 列出已安装的包
conda list
```

预期输出示例：

```
conda 24.x.x
Python 3.1x.x
```

## 常用操作示例

### 创建新环境

```bash
# 创建指定 Python 版本的环境
conda create -n myenv python=3.11 -y

# 激活环境
conda activate myenv

# 确认环境切换成功
which python
python --version
```

### 安装包

```bash
# 使用 conda 安装
conda install numpy pandas scikit-learn -y

# 使用 pip 安装（在 conda 环境中）
pip install requests flask
```

### 从 environment.yml 创建环境

```bash
# 导出当前环境
conda env export > environment.yml

# 从文件创建环境
conda env create -f environment.yml
```

### 管理环境

```bash
# 列出所有环境
conda env list

# 删除环境
conda env remove -n myenv

# 克隆环境
conda create --name newenv --clone myenv
```

### 清理缓存

```bash
# 清理所有缓存（减小容器体积）
conda clean -afy
```

## 已知注意事项

### Anaconda 频道服务条款（ToS）

从 Miniconda 26.x 起，非交互模式下首次使用 Anaconda 默认频道需显式接受服务条款。
Containerfile 中已包含 `conda tos accept` 命令。如需添加新频道，可能需要类似操作：

```bash
conda tos accept --override-channels --channel <channel-url>
```

替代方案：使用 conda-forge 频道（无 ToS 要求）：

```bash
conda install -c conda-forge <package-name>
```

### OCI vs Docker 格式

Podman 默认使用 OCI 镜像格式，不支持 Dockerfile 的 `SHELL` 指令。
构建时使用 `--format docker` 可启用完整 Docker 兼容性。

### 版本锁定

Containerfile 中 conda 版本已锁定为 26.3.2。如需更新，修改对应的 `conda install` 行中的版本号即可。

## LLVM/Clang 开发镜像

### 镜像概览

- 基于 `miniconda3:ubuntu26.04`，通过 conda-forge 安装 LLVM/Clang 22.1.x 全套工具链
- 包含：`clang`, `clangdev`, `llvmdev`, `lld`, `cmake`, `ninja`
- 镜像裁剪策略：
  - 保留 sysroot 核心文件（CRT 启动对象 + 基础库），移除文档和 locale 数据
  - 保留 LLVM/Clang/LLD 静态库（支持 CMake `find_package`），移除其他非必要 `.a`
  - 移除 sanitizer/fuzzer 运行时（不影响 Pass 开发）

### Pass 开发构建方式

#### 方式 A: CMake + Ninja（推荐）

```bash
podman run --rm -v $(pwd)/my-pass:/workspace/pass:Z miniconda3:llvm bash -c '
cd /workspace/pass &&
mkdir -p build && cd build &&
cmake .. -G Ninja \
    -DCMAKE_C_COMPILER=clang \
    -DCMAKE_CXX_COMPILER=clang++ \
    -DLLVM_DIR=$(llvm-config --cmakedir) &&
ninja
'
```

CMakeLists.txt 关键配置：

```cmake
find_package(LLVM REQUIRED CONFIG)
include_directories(${LLVM_INCLUDE_DIRS})
add_definitions(${LLVM_DEFINITIONS})
add_library(MyPass MODULE src/MyPass.cpp)
```

#### 方式 B: 直接编译

```bash
podman run --rm -v $(pwd)/my-pass:/workspace/pass:Z miniconda3:llvm bash -c '
cd /workspace/pass &&
clang++ -shared -fPIC \
    $(llvm-config --cxxflags) \
    -o MyPass.so src/MyPass.cpp
'
```

适合快速原型验证，无需 CMake 配置。

### 运行 Pass

```bash
# 生成 LLVM IR（注意 -Xclang -disable-O0-optnone 避免 optnone 跳过 Pass）
clang -S -emit-llvm -Xclang -disable-O0-optnone input.c -o input.ll

# 使用 opt 加载并运行 Pass
opt -load-pass-plugin ./MyPass.so -passes=my-pass -disable-output input.ll
```

### 容器挂载开发工作流

```bash
# 交互式开发（挂载源码目录）
podman run -it --rm -v $(pwd)/my-pass:/workspace/pass:Z miniconda3:llvm

# 一次性构建+测试
podman run --rm -v $(pwd)/my-pass:/workspace/pass:Z miniconda3:llvm \
    bash /workspace/pass/scripts/run-pass.sh
```

### 已知注意事项

| 事项 | 说明 |
|------|------|
| 头文件路径 | LLVM 22.x 中 PassPlugin 头文件路径为 `llvm/Plugins/PassPlugin.h`（非旧版 `llvm/Passes/PassPlugin.h`） |
| O0 optnone | 默认 `-O0` 编译的 IR 带有 `optnone` 属性，会跳过自定义 Pass 执行。需加 `-Xclang -disable-O0-optnone` |
| CMake LLVM_DIR | 若 `find_package(LLVM)` 失败，显式设置 `-DLLVM_DIR=$(llvm-config --cmakedir)` |
| Pass 链接 | MODULE 库不需要链接 LLVM 静态库，符号在 opt/clang 加载时动态解析 |
| 网络超时 | 首次构建镜像时 conda 下载大包可能超时，镜像已配置 120s 读取超时 |

### 镜像导出/导入

```bash
# 导出为 tar 归档
podman save miniconda3:llvm -o miniconda3-llvm.tar

# 导入镜像
podman load -i miniconda3-llvm.tar

# 压缩导出（节省传输体积）
podman save miniconda3:llvm | gzip > miniconda3-llvm.tar.gz
gunzip -c miniconda3-llvm.tar.gz | podman load
```

### 示例项目

参见 `examples/hello-pass/` 目录，提供了完整的 Pass 模板项目，可作为新 Pass 开发的起点。
