# podman

[Podman](https://docs.podman.io/en/latest/) 是一款无守护程序的开源 Linux 原生工具，旨在使用开放容器计划 （OCI） 容器和容器映像轻松查找、运行、构建、共享和部署应用程序。Podman 提供了命令行界面 （CLI），任何使用过 Docker Container Engine 的人都熟悉该界面。大多数用户可以简单地将 Docker 别名为 Podman（别名 docker=podman），而不会出现任何问题。与其他常见的容器引擎（Docker、CRI-O、containerd）类似，Podman 依靠符合 OCI 标准的容器运行时（runc、crun、runv 等）与作系统交互并创建正在运行的容器。这使得 Podman 创建的正在运行的容器与任何其他常见容器引擎创建的容器几乎没有区别。

Podman 控制下的容器可以由 root 或非特权用户运行。Podman 使用 libpod 库管理整个容器生态系统，包括 Pod、容器、容器镜像和容器卷。Podman 专注于帮助您维护和修改 OCI 容器映像的所有命令和功能，例如拉取和标记。它允许您在生产环境中创建、运行和维护这些容器和容器镜像。

[PodmanPy](https://podman-py.readthedocs.io/en/latest/) 是 Python3 模块，允许您编写 Python 脚本来访问由 Podman 服务维护的资源。它利用 Podman 服务 RESTful API。

以 Ubuntu 为例安装 Podman：
```bash
sudo apt update
sudo apt install podman
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
RUN apt-get install -y locales && \
    locale-gen zh_CN.UTF-8 && \
    update-locale LANG=zh_CN.UTF-8 LANGUAGE=zh_CN.UTF-8
ENV LANG=zh_CN.UTF-8
ENV LANGUAGE=zh_CN.UTF-8
```
````