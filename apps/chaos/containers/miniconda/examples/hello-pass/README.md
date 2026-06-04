# HelloPass — LLVM Pass 开发模板

基于 LLVM 22.x New Pass Manager 的 Pass 开发模板项目。

## 功能

示例 Pass 遍历每个函数，统计并输出：
- 函数名
- 基本块数量
- 指令数量

## 快速开始

### 前置条件

- 构建好的 `miniconda3:llvm` 容器镜像

### 一键运行

```bash
# 从宿主机执行（在 hello-pass/ 目录下）
podman run --rm -v $(pwd):/workspace/pass:Z miniconda3:llvm \
    bash /workspace/pass/scripts/run-pass.sh
```

### 手动构建

```bash
# 进入容器
podman run -it --rm -v $(pwd):/workspace/pass:Z miniconda3:llvm

# 容器内执行
cd /workspace/pass
mkdir -p build && cd build
cmake .. -G Ninja \
    -DCMAKE_C_COMPILER=clang \
    -DCMAKE_CXX_COMPILER=clang++ \
    -DLLVM_DIR=$(llvm-config --cmakedir)
ninja
```

### 运行 Pass

```bash
# 生成 IR
clang -S -emit-llvm -Xclang -disable-O0-optnone test/input.c -o build/input.ll

# 加载并运行 Pass
opt -load-pass-plugin ./build/HelloPass.so -passes=hello-pass -disable-output build/input.ll
```

预期输出：
```
=== HelloPass: factorial ===
  Basic blocks:  ...
  Instructions:  ...

=== HelloPass: fibonacci ===
  Basic blocks:  ...
  Instructions:  ...
```

## 基于模板创建新 Pass

1. 复制本目录为新项目：`cp -r hello-pass my-pass`
2. 重命名 `src/HelloPass.cpp` 为你的 Pass 名称
3. 修改 `CMakeLists.txt` 中的项目名和库名
4. 修改 Pass 注册名（`PipelineParsingCallback` 中的字符串）
5. 实现你的 Pass 逻辑

## 已知注意事项

| 事项 | 说明 |
|------|------|
| 头文件 | LLVM 22.x: `#include "llvm/Plugins/PassPlugin.h"` |
| optnone | 加 `-Xclang -disable-O0-optnone` 或实现 `isRequired()` 返回 true |
| 链接 | MODULE 库无需链接 LLVM 静态库，符号由 opt 在加载时解析 |
| 构建方式 | 也可不用 CMake：`clang++ -shared -fPIC $(llvm-config --cxxflags) -o Pass.so src/Pass.cpp` |
