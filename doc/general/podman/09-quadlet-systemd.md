---
title: Quadlet与systemd集成
description: Quadlet概述、单元文件类型、.container/.pod/.network/.volume/.kube/.image文件语法、操作命令与最佳实践
---

# Quadlet与systemd集成

## Quadlet概述

- **Quadlet** = systemd原生容器管理
- 将容器声明为systemd单元文件
- 自动生成 `.service` 文件
- 系统启动自动拉起容器
- 支持7种单元文件类型

## 文件类型与位置

### 存放位置

- 系统级：`/etc/containers/systemd/`
- 用户级：`~/.config/containers/systemd/`

### 支持类型

| 后缀 | 用途 |
|------|------|
| .container | 容器定义 |
| .pod | Pod定义 |
| .network | 网络定义 |
| .volume | 卷定义 |
| .kube | Kubernetes YAML部署 |
| .image | 镜像构建 |
| .build | 构建任务 |

## .container 文件（完整语法）

```ini
# /etc/containers/systemd/webapp.container
[Unit]
Description=Web Application Container
After=network-online.target
Wants=network-online.target

[Container]
Image=docker.io/library/nginx:latest
ContainerName=webapp
PublishPort=8080:80
Volume=./html:/usr/share/nginx/html:Z
Environment=NGINX_HOST=example.com
Environment=NGINX_PORT=80
HealthCmd=curl -f http://localhost/ || exit 1
HealthInterval=30s
HealthTimeout=10s
HealthRetries=3
AutoUpdate=registry
Network=mynet.network

[Service]
Restart=always
RestartSec=5
TimeoutStartSec=300

[Install]
WantedBy=multi-user.target default.target
```

## .pod 文件

```ini
# /etc/containers/systemd/myapp.pod
[Unit]
Description=My Application Pod

[Pod]
PodName=myapp
PublishPort=8080:80
PublishPort=5432:5432
Network=mynet.network

[Install]
WantedBy=multi-user.target
```

## .network 文件

```ini
# /etc/containers/systemd/mynet.network
[Unit]
Description=Application Network

[Network]
Subnet=10.89.0.0/24
Gateway=10.89.0.1
IPv6=true
Driver=bridge
DNS=8.8.8.8

[Install]
WantedBy=multi-user.target
```

## .volume 文件

```ini
# /etc/containers/systemd/pgdata.volume
[Unit]
Description=PostgreSQL Data Volume

[Volume]
VolumeName=pgdata
Label=app=postgres

# NFS卷示例
# Type=nfs
# Options=addr=nfs-server,rw
# Device=:/export/data

[Install]
WantedBy=multi-user.target
```

## .kube 文件

```ini
# /etc/containers/systemd/webapp.kube
[Unit]
Description=Web App from K8s YAML

[Kube]
Yaml=/etc/containers/systemd/webapp.yaml
Network=mynet.network
PublishPort=8080:80
AutoUpdate=registry

[Service]
Restart=always

[Install]
WantedBy=multi-user.target
```

## .image 文件

```ini
# /etc/containers/systemd/myapp.image
[Unit]
Description=Build my application image

[Image]
Image=localhost/myapp:latest
ContainerFile=/path/to/Containerfile
```

## 操作命令

```bash
# 创建单元文件后
systemctl daemon-reload

# 启动/停止
systemctl start webapp.service
systemctl stop webapp.service

# 查看状态与日志
systemctl status webapp.service
journalctl -u webapp.service -f

# 开机自启
systemctl enable webapp.service

# 查看生成的service文件
systemctl cat webapp.service

# 自动更新
podman auto-update
```

## 依赖管理与启动顺序

```ini
[Unit]
# 数据库先启动
After=postgres.service
Requires=postgres.service

# 网络依赖
After=mynet-network.service
```

## Quadlet最佳实践

1. 每个服务一个.container文件
2. 使用.pod组织相关容器
3. 网络和卷独立定义（.network/.volume）
4. 配置HealthCmd确保服务就绪
5. 设置Restart=always和合理的RestartSec
6. 使用AutoUpdate=registry启用自动更新
7. 用户级服务放~/.config/containers/systemd/
