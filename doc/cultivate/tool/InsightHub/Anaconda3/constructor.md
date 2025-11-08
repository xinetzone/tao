# conda-constructor 用户文档

## 工具概述

conda-constructor 是 Conda 官方提供的跨平台安装器构建工具，能够将 Conda 环境打包为独立的可执行安装程序（`.exe`/`.sh`/`.pkg`），支持 Windows、macOS 和 Linux 三大操作系统。其核心价值在于简化环境分发流程，用户无需手动配置 Conda 或处理依赖冲突，即可一键部署标准化环境。该工具广泛适用于企业内部工具链部署、开源项目分发（如机器学习框架）、教学环境统一配置等场景，尤其适合需要向非技术用户交付复杂环境的场景。

## 安装指南

### 前置依赖

- **Conda 环境**：需安装 Conda 4.7.10 或更高版本（推荐 Miniconda3 以减少体积）。
- **系统工具**：
   - **Windows**：需安装 NSIS（Nullsoft Scriptable Install System）用于生成 `.exe` 安装器。
   - **macOS**：生成 `.pkg` 格式需系统预装 `pkgbuild`（通常随 Xcode 命令行工具提供）。
   - **Linux**：无需额外依赖，但生成的 `.sh` 脚本需手动添加执行权限。

### 通用安装步骤

```bash
# 1. 创建专用环境（推荐隔离）
conda create -n constructor-env python=3.10 -y
conda activate constructor-env

# 2. 安装 constructor（从 conda-forge 通道）
conda install constructor -c conda-forge -y

# 3. 验证安装
constructor --version  # 成功输出示例：constructor 3.4.0

```

### 多平台差异配置

| 平台 | 额外步骤 | 验证命令 |
| ------ | ------------ | ------------ |
| Windows | `conda install nsis -y`（安装 NSIS 工具） | `nsis --version` |
| macOS | `xcode-select --install`（安装命令行工具，用于 `.pkg` 构建） | `pkgbuild --version` |
| Linux | 无需额外步骤，但生成后需执行 `chmod +x installer.sh` 赋予执行权限 | `ls -l installer.sh`（检查权限） |


## 基础使用

### 核心工作流程

- **创建配置文件目录**：
```bash
   mkdir my_installer && cd my_installer
   touch construct.yaml  # 核心配置文件

```

- **编写基础配置文件**（construct.yaml）：
```yaml
   name: my_miniconda       # 安装器名称（将显示在安装界面）
   version: "1.0.0"         # 版本号（遵循语义化版本）
   channels:                 # 依赖包来源通道
     - https://repo.anaconda.com/pkgs/main
     - conda-forge
   specs:                    # 需打包的包列表（支持版本约束）
     - python 3.10.*        # Python 版本（使用通配符兼容小版本更新）
     - conda                # 必须包含 conda 以支持环境管理
     - numpy 1.23.*         # 科学计算依赖
     - pandas 1.5.*         # 数据处理库
   license_file: LICENSE.txt # 可选：许可协议文件（需放在当前目录）

```

- **构建安装器**：
```bash
   constructor .  # 读取当前目录的 construct.yaml 并构建

```

- **输出产物**：
   - Windows： `my_miniconda-1.0.0-Windows-x86_64.exe`
   - macOS： `my_miniconda-1.0.0-MacOSX-x86_64.sh`（默认）或 `.pkg`
   - Linux： `my_miniconda-1.0.0-Linux-x86_64.sh`
### 命令行参数说明

| 参数 | 作用 | 示例 |
| ------ | ------ | ------ |
| `--version` | 查看版本 | `constructor --version` |
| `--debug` | 启用调试模式（输出详细日志） | `constructor . --debug` |
| `--output-dir` | 指定输出目录 | `constructor . --output-dir ./dist` |
| `--platform` | 强制指定目标平台（实验性，需对应依赖） | `constructor . --platform linux-64` |


## 高级配置

### 平台特定配置

通过 **选择器语法** 为不同平台定义差异化配置：

```yaml
# 基础配置（所有平台共享）
name: cross_platform_installer
version: "2.0.0"
channels:
  - conda-forge
# 平台特定配置（使用 [win|osx|linux] 选择器）
specs:
  - python 3.11.*
  - conda
  - pywin32  # [win] 仅 Windows 需安装的系统交互库
  - lighttpd # [linux] Linux 专用 Web 服务器
  - cctools  # [osx] macOS 编译工具链
# 安装器类型（macOS 可选 .sh 或 .pkg）
installer_type: pkg  # [osx] 生成 .pkg 格式
welcome_image: welcome.png  # [win] Windows 安装界面图片（分辨率建议 150x300）
```

### 环境变量与脚本注入

```yaml
# 设置环境变量（安装后自动生效）
extra_envs:
  MY_APP_PATH: "$PREFIX/bin"  # $PREFIX 为用户安装路径
  LOG_LEVEL: "INFO"

# 预安装脚本（仅 Windows 支持，NSIS 语法）
pre_install: pre_install.nsh  # 相对路径，内容为 NSIS 脚本片段
# 后安装脚本（所有平台支持，Bash/PowerShell 语法）
post_install: post_install.sh  # 示例：添加桌面快捷方式、启动服务等
```

### 高级选项参考

| 参数 | 作用 | 适用场景 |
| ------ | ------ | ------------ |
| `default_prefix` | 指定默认安装路径 | `default_prefix: "C:\\Apps\\myenv"` |
| `keep_pkgs` | 保留缓存包（用于离线二次安装） | `keep_pkgs: true` |
| `signing_identity` | 代码签名标识（macOS 公证） | `signing_identity: "Developer ID"` |


## 常见问题

### 构建失败

- **依赖解析错误**：
   - **现象**： `ResolvePackageNotFound` 或 `UnsatisfiableError`。
   - **解决**：
      ```bash
      # 1. 清理 Conda 缓存
      conda clean --all -y
      # 2. 指定更宽松的版本约束（如用 3.10.* 代替 3.10.6）
      # 3. 添加 conda-forge 通道优先
      constructor . -c conda-forge
      ```

2. Windows 缺少 NSIS：
   - 错误提示：`makensis: command not found`。
   - 解决：`conda install nsis -y`。
### 安装器运行问题
1. Linux 权限不足：
   - 错误：`Permission denied`。
   - 解决：`chmod +x installer.sh`。
2. macOS 公证失败（.pkg 格式）：
   - 错误：`The package is damaged and cannot be opened`。
   - 解决：使用 `xcrun altool` 进行公证，或降级为 .sh 格式。
3. 离线环境构建：
   - 需求：在无网络环境中构建安装器。
   - 方法：
   ```bash
   # 提前下载所有依赖到本地缓存
   conda create --prefix ./local_cache --copy -y python=3.10 numpy pandas
   # 构建时指定本地通道
   constructor . --channels ./local_cache
   ```

## 最佳实践

### 体积优化
1. 精确指定版本：避免使用 `*` 通配符，如 `python=3.10.6` 而非 `3.10.*`，减少冗余依赖。
2. 使用 `--no-deps`：仅打包显式声明的包，不包含依赖（需确保用户环境联网）。
3. 清理缓存：
   ```bash
   conda clean --all -y  # 构建前清理无用缓存
   ```

### 构建效率提升

- **使用 Mamba 加速依赖解析**：
   ```bash
   conda install mamba -c conda-forge -y
   mamba install constructor -c conda-forge -y  # 依赖解析速度提升 5-10 倍
   ```

- **并行构建**：
   ```bash
   constructor . --jobs 4  # 多线程下载包（根据 CPU 核心数调整）
   ```

### 分发与维护

- **版本管理**：遵循 [语义化版本](https://semver.org/)，重大变更递增主版本号。- **日志记录**：构建时启用详细日志以便调试：
   ```bash
   CONDA_VERBOSITY=3 constructor . > build.log 2>&1  # 保存日志到文件
   ```

- **用户体验优化**：
   - 添加 `welcome_text` 和 `conclusion_text` 自定义安装界面说明。
   - Windows 平台提供静默安装选项： `installer.exe /S /D=C:\path\to\install`。
## 附录：配置文件模板

```yaml
# 完整示例：带平台差异化和后安装脚本的配置
name: ai_research_env
version: "1.2.0"
channels:
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main  # 国内镜像加速
  - conda-forge
specs:
  - python 3.10.8
  - conda 23.3.1
  - pytorch 1.13.1  # [linux64]
  - tensorflow 2.12.0  # [win|osx]
  - jupyterlab 3.6.3
  - scikit-learn 1.2.2
installer_type: pkg  # [osx]
welcome_image: welcome.png  # [win]
post_install: setup_jupyter.sh  # 启动 Jupyter 服务
extra_envs:
  PYTHONPATH: "$PREFIX/lib/python3.10/site-packages"
default_prefix: "$HOME/ai_research_env"  # 用户主目录下的默认路径
```

通过以上步骤，您可以快速构建标准化的 Conda 环境安装器，显著降低环境配置门槛。更多高级功能可参考 [官方文档](https://conda.github.io/constructor/) 或 GitHub 仓库的示例项目。