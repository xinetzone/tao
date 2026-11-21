---
title: Podman 命令参考
description: 完整的 Podman 命令速查与详解，涵盖容器生命周期、镜像管理、Pod、系统管理、网络、卷等全部核心命令
---

# Podman 命令参考

## 容器生命周期命令

### podman run — 创建并运行容器

最常用的命令，等价于 `podman create` + `podman start`。

#### 关键选项

| 选项 | 说明 |
|------|------|
| `-d, --detach` | 后台运行容器 |
| `--name` | 指定容器名称 |
| `-p, --publish` | 端口映射（主机端口:容器端口） |
| `-v, --volume` | 卷挂载（主机路径:容器路径[:选项]） |
| `--env, -e` | 设置环境变量 |
| `--rm` | 容器退出后自动删除 |
| `--network` | 指定网络模式 |
| `--security-opt` | 安全选项（label, seccomp, apparmor） |
| `--userns` | 用户命名空间设置 |
| `--pid` | PID 命名空间设置 |
| `--uts` | UTS 命名空间设置 |

#### 示例

```bash
# 基础运行
podman run -d --name myapp nginx:latest

# 端口映射
podman run -d -p 8080:80 -p 8443:443 nginx

# 卷挂载
podman run -d -v /host/data:/app/data:Z --name app myimage

# 环境变量
podman run -d --env DB_HOST=localhost --env DB_PORT=5432 myapp

# 安全选项
podman run --security-opt label=disable --security-opt seccomp=unconfined myapp

# 完整示例：组合多个选项
podman run -d \
  --name web-server \
  -p 8080:80 \
  -v ./html:/usr/share/nginx/html:ro,Z \
  --env NGINX_HOST=example.com \
  --network mynet \
  --rm \
  nginx:alpine
```

### podman create — 创建容器（不启动）

```bash
# 创建容器，后续手动启动
podman create --name mydb -p 5432:5432 -e POSTGRES_PASSWORD=secret postgres:16

# 启动已创建的容器
podman start mydb
```

### podman start/stop/restart — 生命周期控制

```bash
# 启动容器
podman start myapp

# 停止容器（默认发送 SIGTERM，10秒后 SIGKILL）
podman stop myapp

# 指定超时时间
podman stop -t 30 myapp

# 重启容器
podman restart myapp

# 批量停止所有容器
podman stop --all
```

### podman rm — 删除容器

```bash
# 删除已停止的容器
podman rm myapp

# 强制删除运行中的容器
podman rm -f myapp

# 删除所有已停止容器
podman rm --all

# 删除容器及其关联的匿名卷
podman rm -v myapp
```

### podman exec — 在运行中容器执行命令

```bash
# 交互式 shell
podman exec -it myapp /bin/bash

# 执行单条命令
podman exec myapp cat /etc/hostname

# 以指定用户执行
podman exec --user root myapp apt-get update

# 设置环境变量
podman exec --env MY_VAR=value myapp printenv MY_VAR

# 指定工作目录
podman exec -w /app myapp ls -la
```

### podman logs — 查看容器日志

```bash
# 查看全部日志
podman logs myapp

# 实时跟踪日志
podman logs -f myapp

# 显示最近 50 行
podman logs --tail 50 myapp

# 带时间戳
podman logs -t myapp

# 指定时间范围
podman logs --since 2024-01-01T00:00:00 myapp
podman logs --until 1h myapp
```

### podman inspect — 查看容器详细信息

```bash
# 查看完整 JSON 信息
podman inspect myapp

# 格式化输出指定字段
podman inspect --format '{{.NetworkSettings.IPAddress}}' myapp
podman inspect --format '{{.State.Status}}' myapp

# 查看挂载信息
podman inspect --format '{{json .Mounts}}' myapp
```

### podman cp — 容器与主机之间复制文件

```bash
# 从主机复制到容器
podman cp ./config.yaml myapp:/etc/app/config.yaml

# 从容器复制到主机
podman cp myapp:/var/log/app.log ./app.log

# 复制目录
podman cp ./dist/ myapp:/usr/share/nginx/html/
```

### podman attach — 连接到运行中的容器

```bash
# 连接到容器标准输入输出
podman attach myapp

# 仅查看输出，不发送输入（Ctrl+C 不会停止容器）
podman attach --no-stdin myapp

# 指定分离快捷键
podman attach --detach-keys="ctrl-x" myapp
```

### podman wait — 等待容器停止

```bash
# 等待容器退出并返回退出码
podman wait myapp

# 等待特定条件
podman wait --condition stopped myapp
podman wait --condition removed myapp
```

### podman stats — 实时资源使用统计

```bash
# 实时监控所有容器
podman stats

# 监控指定容器
podman stats myapp mydb

# 仅输出一次（非流式）
podman stats --no-stream

# 自定义输出格式
podman stats --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

### podman top — 显示容器进程

```bash
# 显示容器内进程
podman top myapp

# 自定义输出字段
podman top myapp pid user comm

# 显示完整命令行
podman top myapp args
```

---

## 镜像管理命令

### podman build — 构建镜像

#### 高级选项

| 选项 | 说明 |
|------|------|
| `--layers` | 启用层缓存（默认启用） |
| `--cache-from` | 指定远程缓存源 |
| `--secret` | 构建时传入密钥（不写入镜像层） |
| `--ssh` | 传入 SSH agent |
| `--platform` | 指定目标平台（多架构构建） |
| `--squash` | 将所有层压缩为一层 |

#### 示例

```bash
# 基础构建
podman build -t myapp:latest .

# 指定 Containerfile
podman build -t myapp:v1 -f Containerfile.prod .

# 多阶段构建
podman build --target production -t myapp:prod .

# 多架构构建
podman build --platform linux/amd64,linux/arm64 -t myapp:multi .

# 使用 secrets（构建时可用，不写入镜像）
podman build --secret id=mysecret,src=./secret.txt -t myapp .

# 利用层缓存加速
podman build --layers --cache-from=registry.example.com/myapp:cache -t myapp .

# 传入构建参数
podman build --build-arg VERSION=1.2.3 --build-arg ENV=prod -t myapp .

# 压缩镜像层
podman build --squash -t myapp:slim .
```

### podman pull/push — 拉取/推送镜像

```bash
# 拉取镜像
podman pull docker.io/library/nginx:alpine
podman pull ghcr.io/myorg/myapp:latest

# 推送镜像
podman push myapp:latest docker.io/myuser/myapp:latest

# 拉取特定架构
podman pull --arch arm64 nginx:alpine

# 推送到本地目录（OCI格式）
podman push myapp:latest dir:/tmp/myapp-image

# 推送到本地 Docker archive
podman push myapp:latest docker-archive:/tmp/myapp.tar
```

### podman images — 列出镜像

```bash
# 列出所有镜像
podman images

# 显示所有（包括中间层）
podman images -a

# 格式化输出
podman images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"

# 过滤
podman images --filter dangling=true
podman images --filter reference=nginx
```

### podman rmi — 删除镜像

```bash
# 删除指定镜像
podman rmi nginx:alpine

# 强制删除（即使有容器引用）
podman rmi -f myapp:old

# 删除所有未使用镜像
podman rmi --all
```

### podman tag — 标记镜像

```bash
# 添加标签
podman tag myapp:latest myapp:v1.0.0
podman tag myapp:latest registry.example.com/myorg/myapp:v1.0.0
```

### podman save/load — 导出/导入镜像

```bash
# 导出为 tar 文件
podman save -o myapp.tar myapp:latest

# 导出多个镜像
podman save -o images.tar myapp:v1 myapp:v2

# 压缩导出
podman save myapp:latest | gzip > myapp.tar.gz

# 导入镜像
podman load -i myapp.tar

# 从压缩文件导入
gunzip -c myapp.tar.gz | podman load
```

### podman manifest — 管理多架构 manifest

```bash
# 创建 manifest 列表
podman manifest create myapp:multi

# 添加不同架构镜像
podman manifest add myapp:multi myapp:amd64
podman manifest add myapp:multi myapp:arm64

# 查看 manifest 详情
podman manifest inspect myapp:multi

# 推送 manifest（含所有架构）
podman manifest push myapp:multi docker.io/myuser/myapp:latest

# 删除 manifest
podman manifest rm myapp:multi
```

---

## Pod 管理命令

### podman pod create — 创建 Pod

```bash
# 基础创建
podman pod create --name mypod

# 指定端口映射（Pod级别）
podman pod create --name webpod -p 8080:80 -p 8443:443

# 指定网络
podman pod create --name mypod --network mynet

# 指定共享命名空间
podman pod create --name mypod --share net,ipc,uts

# 设置 Pod infra 容器的资源限制
podman pod create --name mypod --cpus 2 --memory 1g
```

### podman pod start/stop/restart/rm — Pod 生命周期

```bash
# 启动 Pod（及其中所有容器）
podman pod start mypod

# 停止 Pod
podman pod stop mypod

# 重启 Pod
podman pod restart mypod

# 删除 Pod（必须先停止）
podman pod rm mypod

# 强制删除运行中的 Pod
podman pod rm -f mypod
```

### podman pod inspect/ps — Pod 信息查看

```bash
# 查看 Pod 详情
podman pod inspect mypod

# 列出所有 Pod
podman pod ps

# 列出 Pod 中的容器
podman pod ps --ctr-names
```

### podman generate kube — 导出 K8s YAML

```bash
# 从 Pod 生成 Kubernetes YAML
podman generate kube mypod > mypod.yaml

# 从容器生成
podman generate kube mycontainer > deployment.yaml

# 包含 Service 定义
podman generate kube -s mypod > mypod-with-svc.yaml
```

### podman kube play — 从 YAML 部署

```bash
# 从 YAML 文件部署
podman kube play mypod.yaml

# 指定网络
podman kube play --network mynet mypod.yaml

# 替换已有部署
podman kube play --replace mypod.yaml

# 使用 ConfigMap
podman kube play --configmap configmap.yaml deployment.yaml
```

### podman kube down — 停止 YAML 部署

```bash
# 停止并删除 YAML 部署的资源
podman kube down mypod.yaml
```

---

## 系统管理命令

### podman system prune — 清理未使用资源

```bash
# 清理已停止容器、未使用网络、悬挂镜像
podman system prune

# 清理所有未使用资源（含未引用镜像和卷）
podman system prune --all --volumes

# 强制执行（不提示确认）
podman system prune -f

# 按时间过滤
podman system prune --filter until=24h
```

### podman system reset — 重置所有数据

```bash
# 删除所有容器、镜像、卷（危险操作）
podman system reset

# 强制执行
podman system reset --force
```

### podman system info — 系统信息

```bash
# 显示 Podman 系统信息
podman system info

# JSON 格式
podman system info --format json
```

### podman system check — 系统健康检查

```bash
# 检查存储一致性
podman system check
```

### podman system connection — 远程连接管理

```bash
# 添加远程连接
podman system connection add myserver ssh://user@192.168.1.100/run/podman/podman.sock

# 列出连接
podman system connection list

# 设置默认连接
podman system connection default myserver

# 删除连接
podman system connection remove myserver
```

---

## Machine 命令（macOS/Windows）

### podman machine init — 初始化 VM

```bash
# 默认初始化
podman machine init

# 自定义资源
podman machine init --cpus 4 --memory 8192 --disk-size 100

# 指定虚拟机类型（Windows 可选 wsl/hyperv）
podman machine init --machine-type hyperv

# 指定镜像
podman machine init --image-path /path/to/image
```

### podman machine start/stop — 启动/停止

```bash
# 启动默认 Machine
podman machine start

# 停止
podman machine stop
```

### podman machine set — 修改配置

```bash
# 修改 CPU 和内存（需先停止）
podman machine set --cpus 8 --memory 16384

# 设置挂载类型（macOS）
podman machine set --mount-type virtiofs
```

### podman machine ssh — SSH 连接

```bash
# SSH 进入 Machine
podman machine ssh

# 在 Machine 中执行命令
podman machine ssh "cat /etc/os-release"
```

### podman machine inspect — 查看详情

```bash
podman machine inspect
```

### podman machine rm — 删除

```bash
# 删除 Machine（需先停止）
podman machine rm

# 强制删除
podman machine rm -f
```

---

## 网络命令

### podman network create — 创建网络

```bash
# 创建默认 bridge 网络
podman network create mynet

# 指定子网和网关
podman network create --subnet 10.89.0.0/24 --gateway 10.89.0.1 mynet

# 创建 macvlan 网络
podman network create -d macvlan --subnet 192.168.1.0/24 -o parent=eth0 macvlan-net

# 启用 IPv6
podman network create --ipv6 --subnet fd00::/64 mynet6

# 禁用 DNS
podman network create --disable-dns mynet
```

### podman network ls/inspect/rm — 管理网络

```bash
# 列出网络
podman network ls

# 查看网络详情
podman network inspect mynet

# 删除网络
podman network rm mynet

# 清理未使用网络
podman network prune
```

### podman network connect/disconnect — 容器连接/断开网络

```bash
# 将运行中容器连接到网络
podman network connect mynet mycontainer

# 指定 IP 地址
podman network connect --ip 10.89.0.100 mynet mycontainer

# 断开网络
podman network disconnect mynet mycontainer
```

---

## 卷命令

```bash
# 创建命名卷
podman volume create mydata

# 列出所有卷
podman volume ls

# 查看卷详情
podman volume inspect mydata

# 删除卷
podman volume rm mydata

# 清理未使用卷
podman volume prune

# 创建带选项的卷
podman volume create --opt type=tmpfs --opt o=size=100m tmpvol
```

---

## Compose 支持

Podman 支持通过 `podman compose`（需安装 podman-compose 或 docker-compose）管理多容器应用。

```bash
# 启动服务（前台）
podman compose up

# 后台启动
podman compose up -d

# 停止并删除
podman compose down

# 停止并删除（含卷）
podman compose down -v

# 查看运行状态
podman compose ps

# 查看日志
podman compose logs
podman compose logs -f web

# 重新构建
podman compose build

# 缩放服务
podman compose up -d --scale web=3
```
