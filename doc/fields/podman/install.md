# Podman 安装说明

参考：[Podman 安装说明](https://podman.io/docs/installation)

## 在 Mac 和 Windows 上安装

虽然"容器是 Linux"，但 Podman 也运行在 Mac 和 Windows 上，它提供原生的 podman CLI，并嵌入了客机 Linux 系统来启动你的容器。这个客机被称为 Podman 机器，并通过 `podman machine` 命令进行管理。Mac 和 Windows 上的 Podman 还会监听 Docker API 客户端，支持直接使用基于 Docker 的工具，并可以从你选择的编程语言进行程序化访问。

### 在 Windows 上安装 Podman

在 Windows 上，每个 Podman 机器都由虚拟化的 Windows 子系统 Linux（WSLv2）发行版支持。安装完成后，可以直接从你的 Windows PowerShell（或 CMD）提示符运行 `podman` 命令，它将远程与在 WSL 环境中运行的 podman 服务通信。或者，如果你更喜欢 Linux 提示符和 Linux 工具，可以直接从 WSL 实例访问 Podman。请参阅 [Podman for Windows 指南](https://github.com/containers/podman/blob/main/docs/tutorials/podman-for-windows.md)，了解设置和使用说明。

#### 前提条件

由于 Podman 使用 WSL，您需要 Windows 10 或 Windows 11 的最新版本。在 x64 系统上，WSL 需要 18362 版本或更高版本，而 arm64 系统则需要 19041 版本或更高版本。内部 WSL 使用虚拟化技术，因此您的系统必须支持并已启用硬件虚拟化。如果您在虚拟机中运行 Windows，您必须有支持嵌套虚拟化的虚拟机。

还建议安装现代的"Windows Terminal"，它比标准的 PowerShell 和 CMD 提示符以及 WSL 提示符提供更优越的用户体验。

````{note}
参考：[Install Hyper-V](https://learn.microsoft.com/zh-cn/windows-server/virtualization/hyper-v/get-started/Install-Hyper-V?tabs=powershell&pivots=windows)
1. 右键单击 Windows PowerShell，然后选择“ 以管理员身份运行”。
```bash
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All
```
2. 重启电脑后，右键单击 Windows PowerShell，然后选择“ 以管理员身份运行”。
```bash
DISM /Online /Enable-Feature /All /FeatureName:Microsoft-Hyper-V
```
````

您可以通过在 Windows 商店中搜索或运行以下命令来安装它：
```bash
winget install Microsoft.WindowsTerminal
```

#### 安装 Podman

安装 Windows Podman 客户端首先需要下载 Podman Windows 安装程序。Windows 安装程序是随每个 Podman 版本构建的，可以从官方 [GitHub 发布页面](https://github.com/containers/podman/releases)下载。请确保下载 4.1 或更高版本的发布版，以获得本指南中讨论的功能。

下载后，只需运行 EXE 文件，并重新启动新终端。从这一点开始，`podman.exe` 将会出现在您的 PATH 中，您将能够运行 `podman machine init` 命令来创建您的第一台机器。

#### 自动 WSL 安装

如果您的系统尚未安装 WSL，第一次机器初始化命令将提示对话框以开始自动安装。如果接受，此过程将安装必要的 Windows 组件，重启系统，并在登录后，在终端窗口中重新启动机器创建过程。请确保等待一分钟左右让重新启动发生，因为 Windows 在执行启动项之前有延迟。或者，您可以拒绝自动安装，并手动安装 WSL。但是，这将需要额外的下载和设置时间。

#### 机器初始化过程

在安装 WSL 后，init 命令将安装最小化的 Fedora 系统，并对其进行定制以运行 `podman`。

```bash
(base) PS C:\Users\xinzo> podman machine init                                                                           
Looking up Podman Machine image at quay.io/podman/machine-os-wsl:5.5 to create VM                                       
Getting image source signatures                                                                                         
Copying blob f08d7238a47a done   |                                                                                      
Copying config 44136fa355 done   |                                                                                      
Writing manifest to image destination                                                                                   
f08d7238a47aa9e8fe7dfdf9803207bf5f8b6ab2e64d4dc114854d8c2bb27ce1                                                        
Extracting compressed file: podman-machine-default-amd64: done                                                          
Importing operating system into WSL (this may take a few minutes on a new WSL install)...                               
操作成功完成。                                                                                                          
Configuring system...                                                                                                   
Machine init complete                                                                                                   
To start your machine run:                                                                                              
                                                                                                                        
        podman machine start                                                                                            
```

#### 启动机器

机器初始化过程完成后，它就可以根据需要启动和停止：

```bash                                                                                                              
(base) PS C:\Users\xinzo> podman machine start                                                                          
Starting machine "podman-machine-default"                                                                               
                                                                                                                        
This machine is currently configured in rootless mode. If your containers                                               
require root permissions (e.g. ports < 1024), or if you run into compatibility                                          
issues with non-podman clients, you can switch using the following command:                                             
                                                                                                                        
        podman machine set --rootful                                                                                    
                                                                                                                        
API forwarding listening on: npipe:////./pipe/docker_engine                                                             
                                                                                                                        
Docker API clients default to this address. You do not need to set DOCKER_HOST.                                         
Machine "podman-machine-default" started successfully    
```

#### 第一个 Podman 命令

从此刻开始，podman 命令的操作方式与在 Linux 上类似。

如果你想在小型镜像上快速运行工作示例，可以在 PowerShell 上运行 Linux 的 `date` 命令。

```bash
(base) PS C:\Users\xinzo> podman run ubi8-micro date
Resolved "ubi8-micro" as an alias (/etc/containers/registries.conf.d/000-shortnames.conf)
Trying to pull registry.access.redhat.com/ubi8-micro:latest...
Getting image source signatures
Checking if image destination supports signatures
Copying blob sha256:437cae84145b182d39688e9217a2b9ff8474fbf21db2f1a64ed6e0a6dfc7fa5b
Copying config sha256:910e722b30d52b52da5ec87e19aae4431cc1b92d84e1c1db06f37f5cc026719b
Writing manifest to image destination
Storing signatures
Thu Jul 17 07:25:37 UTC 2025
```

#### 端口转发

端口转发(Port Forwarding)也按预期工作；端口将绑定到本地主机（`127.0.0.1`）。注意：以无根权限(rootless)运行时（默认设置），你必须使用大于 1023 的端口。有关详细信息，请参阅“有根和无根”(Rootful and Rootless)部分。

要启动 `httpd`，你可以运行：

```bash
(base) PS C:\Users\xinzo> podman run --rm -d -p 8080:80 --name httpd docker.io/library/httpd
Trying to pull docker.io/library/httpd:latest...
Getting image source signatures
Copying blob sha256:14bacd2841b05072a5a7292447f2f4e57011b72cd19252f6a3250faa14580306
Copying blob sha256:3da95a905ed546f99c4564407923a681757d89651a388ec3f1f5e9bf5ed0b39d
Copying blob sha256:71018c0d16cb7c911af28aee0f97f3230f354d237f4774d9968c188a50554824
Copying blob sha256:4f4fb700ef54461cfa02571ae0db9a0dc1e0cdb5577484a6d75e68dc38e8acc1
Copying blob sha256:3b93b8c3888ba6380a4e5ed20ec4ac1d1164cc9250e1790087984004d11859ec
Copying blob sha256:c5094faccdbbeaf5a63f87a83623e5ecb1807d79d65cb68a1cb3a2e0af97f8a0
Copying config sha256:90f191b9781e01f5cd601af7b32d4ebb46770d1a98fa9170c328f9a78458b758
Writing manifest to image destination
1eeddb42cb3e91eb74cafccee3a4465faf6ecf618111ae7e9dfeb4af509e5ce6
```

在 PowerShell 提示符下对 `localhost` 发起 `curl` 命令将返回成功的 HTTP 响应：

```bash
(base) PS C:\Users\xinzo> curl http://localhost:8080/ -UseBasicParsing                                                  
                                                         
StatusCode        : 200                                                                                                 
StatusDescription : OK                                                                                                  
Content           : <html><body><h1>It works!</h1></body></html>      

```

和 Linux 一样，要停止，运行：

```bash
podman stop httpd
```

#### 使用 API 转发

API 转发允许 Docker API 工具和客户端像使用 Docker 一样使用 podman。只要 Docker API 管道上没有其他服务在监听；就不需要任何特殊设置。

```bash
PS C:\Users\User> .\docker.exe run -it fedora echo "Hello Podman!"
Hello Podman!
```

否则，在启动机器后，你会收到环境变量的通知，该变量可用于工具指向 podman。或者，你可以关闭冲突的服务和 podman，然后运行 `podman machine start` 重启，这应该会获取 Docker API 地址。

```bash
Another process was listening on the default Docker API pipe address.
You can still connect Docker API clients by setting DOCKER HOST using the
following PowerShell command in your terminal session:

        $Env:DOCKER_HOST = 'npipe:////./pipe/podman-machine-default'

Or in a classic CMD prompt:

        set DOCKER_HOST=npipe:////./pipe/podman-machine-default

Alternatively, terminate the other process and restart podman machine.
Machine "podman-machine-default" started successfully

PS C:\Users\User> $Env:DOCKER_HOST = 'npipe:////./pipe/podman-machine-default'
PS C:\Users\User>.\docker.exe version --format '{{(index .Server.Components 0).Name}}'
Podman Engine
```

#### Rootful & Rootless 

在嵌入式 WSL Linux 发行版上，podman 可以以 root 用户（rootful）或非特权用户（rootless）的方式运行。为了与 Linux 上的 Podman 行为保持一致，`rootless` 是默认设置。注意：rootful 和 rootless 容器是相互独立且隔离的。针对其中一个容器执行的 Podman 命令（例如，podman ps）不会显示另一个容器的结果/状态。

虽然大多数容器在无根环境下运行良好，但你可能会遇到容器只有在具有根权限的情况下才能正常工作的案例。如果是这种情况，你可以通过停止机器并使用 `set` 命令将其切换为有根环境：

```bash
podman machine stop
podman machine set --rootful
```

要恢复无根执行，将 `rootful` 设置为 `false`:

```bash
podman machine stop
podman machine set --rootful=false
```

在以下情况下，您可能希望使用 rootful 的执行方式：绑定端口小于 1024。然而，podman 的后续版本可能会将其降低到更低的数字，以提高与系统端口服务（如 MySQL）默认设置的兼容性。

#### 卷挂载

Podman v4.1 新增了从 Windows 路径挂载卷到 Linux 容器的能力。这支持多种符号方案，包括：

- Windows 风格路径：
```bash
podman run --rm -v c:\Users\User\myfolder:/myfolder ubi8-micro ls /myfolder
```

- 类 Unix Windows 路径：
```bash
podman run --rm -v /c/Users/User/myfolder:/myfolder ubi8-micro ls /myfolder
```
- Linux 路径（WSL 文件系统本地路径）：
```bash
podman run --rm -v /var/myfolder:/myfolder ubi-micro ls /myfolder
```

以上所有约定在 Windows 提示符或 WSL Linux shell 上运行时都有效。但在 Linux 上使用 Windows 路径时，应适当引用或转义参数中的 Windows 路径部分。

#### 列出 Podman Machine(s)

要列出可用的 podman 机器实例及其当前资源使用情况，请使用 `podman machine ls` 命令：
```bash
(base) PS C:\Users\xinzo> podman machine ls                                                                             
NAME                     VM TYPE     CREATED         LAST UP            CPUS        MEMORY      DISK SIZE               
podman-machine-default*  wsl         23 minutes ago  Currently running  4           2GiB        100GiB 
```

由于 WSL 在多个发行版之间共享同一虚拟机和 Linux 内核，因此 CPU 和内存值表示运行系统中共享的总资源。磁盘值则相反，它是独立的，表示每个发行版各自的存储量。

#### 访问 Podman Linux 环境

虽然在使用 Windows 环境中的 `podman.exe` 客户端提供了无缝的本地体验，支持使用本地桌面工具和 API，但在某些情况下，您可能希望访问 Linux 环境：

- 在嵌入式 Fedora 实例上更新到最新的稳定版本软件包
- 直接使用 Linux 开发工具
- 依赖 EXT4 文件系统性能或行为语义的工作流程

访问嵌入式 WSL 发行版有三种机制：
- 使用 `podman machine ssh` 的 SSH
- 在 Windows PowerShell 提示符上使用 WSL 命令
- Windows 终端集成

##### 使用 SSH

SSH 访问提供了与 Mac 上的 Podman 类似的体验。它会根据你机器的 rootful/rootless 配置立即切换到适当的用户（前者为 root，后者为 'user'）。可以使用 --username 选项来覆盖指定用户。

使用 SSH 的示例任务是将您的 Linux 环境更新以获取最新的操作系统错误修复：
```bash
podman machine ssh sudo dnf upgrade -y
```

##### 使用 WSL 命令

`wsl` 命令可以直接访问 Linux 系统，但首先会以 root 身份进入 shell。这是由于 WSL 的设计限制，运行 `systemd` （Linux 的系统服务）需要使用特权进程命名空间。

除非你没有安装其他 WSL 发行版，否则建议使用 `-d` 选项并指定你的 podman 机器名称（`podman-machine-default` 是默认值）

```bash
PS C:\Users\User> wsl -d podman-machine-default
```

你将自动进入嵌套的进程命名空间，其中 `systemd` 正在运行。如果你需要访问父命名空间，请按 `ctrl-d` 或输入 `exit`。这也意味着要注销，你需要退出两次。
```bash
[root@WINPC /]# podman --version
podman version 5.5.2
```

要以非特权用户（rootless podman）访问命令，您必须首先输入 `su user`。或者，您可以将 `wsl` 命令前缀为特殊 `enterns`：

```bash
wsl -d podman-machine-default enterns su user
[user@WINPC /]$ id
uid=1000(user) gid=1000(user) groups=1000(user),10(wheel)
```

同样地，以 root 身份运行命令且不输入提示时，也应该以 `enterns` 为前缀。

```bash
wsl -d podman-machine-default enterns systemctl status
```

以特定用户身份通过 `wsl -u` 访问 WSL 实例或使用无需 `enterns` 的内联命令是不推荐的，因为命令将在错误的命名空间中执行。

##### 使用 Windows 终端集成

以 root 身份进入 WSL 是两步操作。只需点击下拉标签，选择`'podman-machine-default'`，即可直接以 root 身份进入。

如前所述，要切换到非特权用户以执行无根 podman 命令，请输入 `su user`。
```bash
[root@WINPC /]# su user
[user@WINPC /]$ podman info --format '{{.Store.RunRoot}}'
/run/user/1000/containers
```

#### 停止 Podman 机器

要停止正在运行的 podman 机器，使用 `podman machine stop` 命令：

```bash
PS C:\Users\User> podman machine stop
Machine "podman-machine-default" stopped successfully
```

#### 删除 Podman 机器

要删除机器，使用 `podman machine rm` 命令：
```bash
PS C:\Users\User> podman machine rm

The following files will be deleted:

C:\Users\User\.ssh\podman-machine-default
C:\Users\User\.ssh\podman-machine-default.pub
C:\Users\User\.local\share\containers\podman\machine\wsl\podman-machine-default_fedora-35-x86_64.tar
C:\Users\User\.config\containers\podman\machine\wsl\podman-machine-default.json
C:\Users\User\.local\share\containers\podman\machine\wsl\wsldist\podman-machine-default


Are you sure you want to continue? [y/N] y
```

#### 故障排除

从 WSL 失败的自动安装中恢复

如果自动安装失败且重试不成功，您可以尝试重置您的 WSL 系统状态，并使用 `wsl --install` 命令执行手动 WSL 安装。为此，请执行以下步骤：

1. 以管理员身份启动 PowerShell
```bash
Start-Process powershell -Verb RunAs
```

2. 禁用 WSL 功能
```bash
dism.exe /online /disable-feature /featurename:Microsoft-Windows-Subsystem-Linux /norestart
dism.exe /online /disable-feature /featurename:VirtualMachinePlatform /norestart
```

3. 重启
4. 运行手动 WSL 安装
```bash
wsl --install
```

5. 继续使用 `podman machine init`

## Ubuntu

Podman 软件包在 Ubuntu 20.10 及更高版本的官方仓库中可用。

```bash
# Ubuntu 20.10 and newer
sudo apt-get update
sudo apt-get -y install podman
```
