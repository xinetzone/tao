# Miniconda 容器镜像构建与使用指南

## 镜像标签

| 标签 | Containerfile | 描述 |
|------|---------------|------|
| `miniconda3:ubuntu26.04` | `Containerfile` | 基础镜像：Ubuntu 26.04 + Miniconda3 |
| `miniconda3:llvm` | `Containerfile.llvm` | 扩展镜像：基础镜像 + LLVM/Clang (conda-forge) |

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
