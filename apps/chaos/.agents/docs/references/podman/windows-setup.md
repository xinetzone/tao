# Podman Windows 配置指南

## 适用范围

Windows 10/11 环境下 Podman 的安装、虚拟机初始化、路径挂载、网络配置及 Python SDK 连接方式。

## 核心原理

Windows 无法原生运行 Linux 容器。Podman 通过 `podman machine` 启动一个轻量 Linux VM（基于 Fedora CoreOS），在 VM 内运行容器。推荐使用 **WSL2** 作为后端。

---

## 1. 安装

```powershell
# winget（推荐）
winget install RedHat.Podman

# chocolatey
choco install podman-desktop

# 官方安装包
# https://github.com/containers/podman/releases
```

安装后重启终端，验证：

```powershell
podman version
```

### 1.1 前置依赖：WSL2

```powershell
# 安装 WSL2（需管理员权限，一次性操作）
wsl --install

# 确认版本
wsl --version
```

---

## 2. 虚拟机初始化与生命周期

```powershell
# 初始化（WSL2 后端，推荐）
podman machine init --provider wsl

# 指定资源
podman machine init --provider wsl --memory 4096 --cpus 4 --disk-size 40

# 启动
podman machine start

# 查看状态
podman machine list

# 停止
podman machine stop

# 删除（重置）
podman machine rm
```

> 首次 `init` 下载 Fedora CoreOS 镜像（约 500MB）。网络慢时可手动下载后用 `--image-path` 指定本地路径。

---

## 3. 路径挂载

### 3.1 路径格式

| Windows 路径 | 挂载写法 |
|--------------|----------|
| `C:\Users\alice\project` | `C:\Users\alice\project` 或 `/c/Users/alice/project` |
| `D:\data\eval` | 需额外配置（见 3.2） |

```powershell
# 默认系统盘路径可直接挂载
podman run -v C:\Users\alice\project:/app:Z my-image

# 当前目录
podman run -v ${PWD}:/app:Z my-image
```

### 3.2 非系统盘挂载

Podman machine 默认仅挂载 `C:\Users`。其他盘符需显式配置：

**方法一：init 时指定（推荐，需重建 machine）**

```powershell
podman machine init --provider wsl --volume D\::/mnt/d
```

**方法二：修改现有 machine 配置**

```powershell
podman machine stop

# 编辑 JSON 配置
notepad $env:USERPROFILE\.config\containers\podman\machine\qemu\podman-machine-default.json
```

在 `Mounts` 数组中追加：

```json
{
  "Name": "D:",
  "Type": "virtiofs",
  "Source": "D:",
  "Target": "/mnt/d",
  "ReadOnly": false
}
```

```powershell
podman machine start
```

挂载使用：

```powershell
podman run -v /mnt/d/data/eval:/eval/data:Z my-image
```

### 3.3 权限后缀

| 后缀 | 说明 |
|------|------|
| `:Z` | SELinux 重新标记（共享卷） |
| `:U` | 自动调整宿主机目录属主以适应容器内 UID（非 SELinux 环境推荐） |

---

## 4. 网络

```powershell
# 端口映射
podman run -p 8080:8080 my-app

# 从 Windows 访问
curl http://localhost:8080
```

若 `localhost` 不通，使用 VM IP：

```powershell
podman machine list
# 查看输出中的 VM IP，如 192.168.127.2
curl http://192.168.127.2:8080
```

---

## 5. podman-py 连接方式

```python
import podman

# 默认连接（自动检测 podman machine）
with podman.PodmanClient() as client:
    if client.ping():
        print("连接成功")

# Windows npipe 连接
with podman.PodmanClient(base_url="npipe:////./pipe/podman-machine-default") as client:
    ...
```

环境变量方式：

```powershell
$env:CONTAINER_HOST = "npipe:////./pipe/podman-machine-default"
```

---

## 6. 常用命令速查

| 操作 | 命令 |
|------|------|
| 初始化 VM | `podman machine init --provider wsl` |
| 启动 VM | `podman machine start` |
| 停止 VM | `podman machine stop` |
| 删除 VM | `podman machine rm` |
| SSH 进 VM | `podman machine ssh` |
| 状态列表 | `podman machine list` |
| 系统信息 | `podman machine info` |

---

## 7. 故障排查

### VM 启动失败

```powershell
# 检查 WSL2 是否正常运行
wsl --list --verbose

# 查看 machine 详细日志
podman machine info

# 重置 machine（保留镜像需先导出）
podman machine rm
podman machine init --provider wsl
podman machine start
```

### 挂载路径容器内不可见

```powershell
# 进入 VM 确认路径存在
podman machine ssh
ls /mnt/
ls /mnt/d/
exit

# 在 VM 内不存在则重新配置挂载（见 3.2 节）
```

### network 不通 / localhost 不可达

```powershell
# 直接使用 VM IP
podman machine list
# 记下显示的 IP 地址，直接访问该 IP
```

### 镜像拉取慢

```powershell
# 设置国内镜像源
podman machine ssh
sudo sed -i 's|docker.io|registry-1.docker.io|' /etc/containers/registries.conf
# 或添加 mirror
echo '[[registry]]' | sudo tee -a /etc/containers/registries.conf
echo 'prefix = "docker.io"' | sudo tee -a /etc/containers/registries.conf
echo 'location = "docker.m.daocloud.io"' | sudo tee -a /etc/containers/registries.conf
exit
podman machine stop
podman machine start
```

---

## 参考来源

- [Podman 官方安装文档](https://podman.io/docs/installation)
- [Podman Windows 教程](https://github.com/containers/podman/blob/main/docs/tutorials/windows_tutorial.md)
- 本项目：[容器化规则](../../../rules/containerization.md)、[Podman SDK 参考](./podman-py-sdk.md)
