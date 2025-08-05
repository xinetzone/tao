# Protocol Buffer 编译器安装

## 如何安装协议缓冲区编译器。

Protocol Buffer 编译器 `protoc` 用于编译 `.proto` 文件，这些文件包含服务和消息定义。选择下方给出的一种方法来安装 `protoc`。

## 安装预编译二进制文件（任何操作系统）

要从预编译的二进制文件安装最新版本的协议编译器，请按照以下说明操作：

1. 从 <https://github.com/google/protobuf/releases>，手动下载与您的操作系统和计算机架构对应的 zip 文件（ `protoc-<version>-<os>-<arch>.zip`），或使用如下命令获取文件：

```bash
PB_REL="https://github.com/protocolbuffers/protobuf/releases"
curl -LO $PB_REL/download/v30.2/protoc-30.2-linux-x86_64.zip
```

2. 在 `$HOME/.local` 或您选择的目录下解压文件。例如：

```bash
unzip protoc-30.2-linux-x86_64.zip -d $HOME/.local
```

3. 更新您环境中的路径变量，以包含 `protoc` 可执行文件的路径。例如：
```bash
export PATH="$PATH:$HOME/.local/bin"
```

## 使用软件包管理器安装

```{warning}
运行 `protoc --version` 来检查使用包管理器安装后的 `protoc` 版本，以确保其足够新。某些包管理器安装的 `protoc` 版本可能非常过时。请参阅版本[支持页面](https://protobuf.dev/support/version-support)，将版本检查的输出与您正在使用语言的受支持版本的小版本号进行比较。
```

您可以使用以下命令在 Linux、macOS 或 Windows 上使用包管理器安装协议编译器 `protoc`。

- Linux，使用 `apt` 或 `apt-get`，例如：
```bash
apt install -y protobuf-compiler
protoc --version  # Ensure compiler version is 3+
```

- macOS，使用 [Homebrew](https://brew.sh/)，例如：
```bash
brew install protobuf
protoc --version  # Ensure compiler version is 3+
```

- Windows，使用 [winget](https://learn.microsoft.com/en-us/windows/package-manager/winget/)，例如：
```bash
winget install protobuf
protoc --version # Ensure compiler version is 3+
```

## 源代码安装

如果您想从源代码构建协议编译器，或访问预编译二进制文件的老版本，请参阅[下载 Protocol Buffers](https://protobuf.dev/downloads)。

## conda+pip 组合安装

**`conda-forge::libprotobuf + pip install protobuf`的组合在特定场景下更优**，尤其适合需要**C++编译支持+Python绑定细粒度控制**的开发环境。以下是分场景分析：

C++ 库与 Python 绑定解耦：
`conda install conda-forge::libprotobuf`|`pip install protobuf`
:-:|:-:
提供**原生C++库**（`libprotobuf.so/dll`）和**protoc编译器**，支持从 `.proto` 文件生成多语言代码（如C++、Python）。 |仅安装**Python运行时库**（`google.protobuf`模块），版本与Google官方PyPI一致（如`pip install protobuf==4.24.3`）。
包含开发依赖（如`libprotobuf-dev`标签），解决 `protoc --python_out` 时的头文件缺失问题。  | 
避免conda通道中`anaconda::protobuf`可能的版本滞后（conda-forge的`libprotobuf`更新更快）。|当Python绑定依赖特定C++库（如`protobuf`包要求`libprotobuf>=3.19.4`），conda可优先安装指定版本的C++库，pip安装对应Python包，避免`ImportError: libprotobuf.so.23: cannot open shared object file`。
 **C++库**：通过conda指定精确版本（如`conda install conda-forge::libprotobuf=3.20.3`），兼容旧项目（如Linux-ppc64le的v3.20.3）。  |**Python绑定**：pip直接匹配官方版本（如`pip install protobuf==3.6.1`），解决conda通道中Python包版本混乱问题（如`anaconda::protobuf`的win-32仅v3.14.0）。

### 推荐使用场景

| 场景 | 组合优势 | 示例命令 |
|------|----------|----------|
| **C++开发+Python调用** | 同时获得C++编译支持和Python API | `conda install conda-forge::libprotobuf=3.20.3` 和 `pip install protobuf==3.20.3` |
| **旧项目兼容性** | 安装历史版本C++库（如v3.6.1）+ 对应Python绑定 | `conda install conda-forge::libprotobuf=3.6.1` 和 `pip install protobuf==3.6.1`|
| **protoc编译器定制** | 使用conda的`libprotobuf`提供的`protoc`生成代码，pip安装轻量Python运行时 | `protoc --python_out=. my.proto` 和 `pip install protobuf`（无需重复安装protoc） |
| **解决复杂依赖** | 修复`google.protobuf.internal`导入错误（需`libprotobuf-dev`） | `conda install conda-forge/label/libprotobuf_dev::libprotobuf` 和 `pip install protobuf`|

### 注意事项（避坑指南）

1. **版本必须对齐**  
   - C++库版本（如`libprotobuf=3.20.3`）需与Python包版本（`protobuf==3.20.3`）**主版本号一致**，否则可能出现协议不兼容（如`protoc`生成的代码无法被低版本Python库解析）。  
   - 例外：`libprotobuf 21.5`（conda-forge自定义版本）实际对应`protobuf 3.21.5`（Google官方），需通过`conda search libprotobuf --channel conda-forge`确认映射关系（摘要1）。

2. **避免重复安装**  
   - 不要同时通过`conda install protobuf`（含C++库）和`pip install protobuf`，可能导致库路径冲突。**优先用conda管理C++，pip管理Python**。

3. **环境隔离**  
   - 在conda环境中先安装`libprotobuf`，再`pip install protobuf`，确保Python包链接到conda的C++库（通过`LD_LIBRARY_PATH`或`DYLD_LIBRARY_PATH`）。  
   - 若出现`ImportError: libprotobuf.so.XX`，添加conda环境的`lib`目录到系统路径：  

```bash
# 强制Python使用conda环境的库
export LD_LIBRARY_PATH=$(conda info --base)/envs/your_env/lib:$LD_LIBRARY_PATH
  
# 验证加载路径
python -c "import google.protobuf; print(google.protobuf.__file__)"
ldd $(which python) | grep protobuf  # 检查依赖库路径
```

4. **性能敏感场景**  
   - 若需极致性能，`conda-forge::libprotobuf`提供`static`标签，可编译为静态库避免动态链接开销：  
```bash
conda install conda-forge::libprotobuf-static
```

### 对比：纯conda vs 组合方案
| 方案 | 优点 | 缺点 |
|------|------|------|
| **纯conda（`anaconda::protobuf`）** | 一键安装，Python友好，无版本冲突 | C++库版本固定，缺乏开发依赖（如`protoc`旧版），无法定制编译 |
| **纯conda（`conda-forge::libprotobuf`+`conda install protobuf`）** | C++灵活，Python绑定由conda管理 | 可能因conda通道版本混乱导致延迟（如`protobuf`包滞后于PyPI） |
| **组合方案（conda C++ + pip Python）** | 版本精准，开发/运行时分离，兼容新旧项目 | 需手动对齐版本，适合进阶用户 |


### 何时选择组合？
✅ **推荐**：  
- 开发跨语言项目（`C++` + `Python`），需自定义 `protoc` 生成代码。  
- 修复旧项目依赖（如Caffe要求`libprotobuf=3.6.0`+`protobuf=3.6.0`）。  
- 需要`libprotobuf-dev`头文件（如编译自定义扩展）。  

❌ **不推荐**：  
- 纯Python项目（直接`pip install protobuf`更简单）。  
- 追求“零配置”的新手（`conda install protobuf`更省心）。  

**示例工作流**：  
```bash
# 1. 创建conda环境，安装C++库+protoc（指定版本）
conda create -n proto-env python=3.12
conda activate proto-env
conda install -c conda-forge libprotobuf=3.20.3 # 含开发头文件

# 2. 安装Python绑定（与C++版本对齐）
pip install protobuf==3.20.3

# 3. 验证（C++编译器+Python库）
protoc --version  # 应显示3.20.3
python -c "import google.protobuf; print(google.protobuf.__version__)"  # 应输出3.20.3
```

通过分工协作，组合方案在灵活性、版本控制和跨语言支持上更胜一筹，尤其适合需要深度定制的开发者。

在 `environment.yml` 中明确记录组合依赖
```yaml
# Build environment that can be used to build tvm.
name: proto_env

# The conda channels to lookup the dependencies
channels:
  - conda-forge

# The packages to install to the environment
dependencies:
  - libprotobuf=3.20.3
  - pip  # 显式声明 pip 依赖
  - pip: # Include pip dependencies last
    - protobuf==3.20.3
```

### 配合 Conan 使用

此时可以使用最新版本的 Protobuf 库。
```bash
# 1. 创建conda环境，安装C++库+protoc（指定版本）
conda create -n proto-env python=3.12
conda activate proto-env
conda install -c conda-forge libprotobuf # 含开发头文件

# 2. 安装Python绑定（与C++版本对齐）
pip install protobuf

# 3. 验证（C++编译器+Python库）
protoc --version  # 应显示最新版本
python -c "import google.protobuf; print(google.protobuf.__version__)"  # 应显示最新版本
```

详细说明请参考 [使用相同的依赖作为 `requires` 和 `tool_requires`](https://xinetzone.github.io/tao/examples/conan/graph/tool-requires-using-protobuf.html)。
