# Podman 概述

[Podman](https://docs.podman.io/en/latest/) 是一款无守护程序的开源 Linux 原生工具，旨在使用开放容器计划 （[OCI](https://www.opencontainers.org/)） [容器](https://developers.redhat.com/blog/2018/02/22/container-terminology-practical-introduction/#h.j2uq93kgxe0e)和[容器镜像](https://developers.redhat.com/blog/2018/02/22/container-terminology-practical-introduction/#h.dqlu6589ootw)轻松查找、运行、构建、共享和部署应用程序。Podman 提供了命令行界面 （CLI），任何使用过 [Docker Container Engine](https://developers.redhat.com/blog/2018/02/22/container-terminology-practical-introduction/#h.6yt1ex5wfo3l) 的人都熟悉该接口。大多数用户可以简单地将 Docker 别名为 Podman（别名 docker=podman），而不会出现任何问题。与其他常见的容器引擎（Docker、CRI-O、containerd）类似，Podman 依靠符合 OCI 标准的[容器运行时](https://developers.redhat.com/blog/2018/02/22/container-terminology-practical-introduction/#h.6yt1ex5wfo55)（runc、crun、runv 等）与作系统交互并创建正在运行的容器。这使得 Podman 创建的正在运行的容器与任何其他常见容器引擎创建的容器几乎没有区别。

Podman 控制下的容器可以由 root 用户或非特权用户运行。Podman 使用 [libpod](https://github.com/containers/podman) 库管理整个容器生态系统，包括 Pod、容器、容器镜像和容器卷。Podman 专注于帮助您维护和修改 OCI 容器映像的所有命令和功能，例如拉取和标记。它允许您在生产环境中创建、运行和维护这些容器和容器镜像。

有用于管理容器的 RESTful API。还提供了可以与 RESTful 服务交互的远程 Podman 客户端。目前支持 Linux、Mac 和 Windows 客户端。RESTful 服务仅在 Linux 上支持。

[PodmanPy](https://podman-py.readthedocs.io/en/latest/) 是 Python3 模块，允许您编写 Python 脚本来访问由 Podman 服务维护的资源。它利用 Podman 服务 RESTful API。

[get-started 教程](https://podman.io/get-started)将教你如何设置 Podman 并执行一些基本命令。

使用 conda 安装 Podman：
```bash
conda install conda-forge::podman
```
安装 PodmanPy：
```bash
pip install podman
```

## 安装 Docker 工具(可选)

已安装 Docker 工具的用户可跳过此步骤，未安装的用户请根据[官方手册进行安装](https://docs.docker.com/install/linux/docker-ce/ubuntu/)。

````{attention}
需要将用户添加到 docker 用户组：
```bash
# 创建 docker 用户组
sudo groupadd docker
# 把当前用户加入 docker 用户组
sudo usermod -aG docker $USER
# 更新激活 docker 用户组
newgrp docker
```
````

````{caution}
如果中文乱码，请参考下文的 Dockerfile 中文环境配置。
```bash
# 安装中文字体
RUN apt-get update && apt-get install -y fonts-wqy-microhei
# 配置中文环境
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y locales locales-all && \
    sed -i '/zh_CN.UTF-8/s/^# //g' /etc/locale.gen && \
    locale-gen zh_CN.UTF-8 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
```
````

## 容器

[容器](https://developers.redhat.com/blog/2018/02/22/container-terminology-practical-introduction/#h.j2uq93kgxe0e)简化了应用程序及其所有依赖项和默认配置文件的生产、分发、可发现性和使用。用户可以通过一两个命令来试用或部署新应用程序，而无需遵循冗长的安装说明。以下是如何找到你的第一个容器镜像：

```bash
podman search docker.io/busybox
```

该命令返回了 DockerHub 上公开可用的容器镜像列表。这些容器镜像易于使用，但质量和维护程度各不相同。我们使用列出的第一个镜像，因为它似乎维护得很好。

要运行 busybox 容器镜像，只需命令：
```bash
podman run -it docker.io/library/busybox
```

容器镜通常由多个层组成的仓库。这些层可以通过使用 Containerfile（Dockerfile）轻松地添加、保存和与他人分享。这个单一文件通常包含构建新容器镜像所需的所有指令，并且可以使用 GitHub 等工具轻松地公开与他人分享。

这里有一个示例，说明如何从存储在 git 仓库中的内容构建容器镜像：
```bash
podman build -t hello https://github.com/containers/PodmanHello.git
```

一旦镜像构建完成，就可以轻松从本地缓存运行新镜像：

```bash
podman run -it hello
```

Podman 和其他如 CRI-O、Docker 或 containerd 的容器引擎可以从 docker.io、quay.io、本地注册表甚至云提供商提供的注册表中创建和消费容器镜像。OCI 镜像格式通过单一标准促进了这一生态系统。

例如，如果想在 quay.io 上分享新构建的 hello 容器镜像，这很简单。首先登录 quay:

```bash
podman login quay.io
```

给镜像打上标签，以便我们可以将其推送到我们的用户账户：
```bash
podman tag localhost/hello quay.io/USERNAME/hello
```

推送镜像：
```bash
podman push quay.io/USERNAME/hello
```

经将一个层推送到注册中心，现在它可供其他人共享。快来看看：
```bash
podman inspect quay.io/USERNAME/hello
```
