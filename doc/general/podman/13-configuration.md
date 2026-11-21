---
title: 配置文件参考
description: Podman 配置文件层级、containers.conf、storage.conf、registries.conf 及 policy.json 完整参考
---

# 配置文件参考

## 配置文件层级

```
/usr/share/containers/    ← 系统默认（包管理器提供）
/etc/containers/          ← 系统级覆盖（管理员配置）
~/.config/containers/     ← 用户级覆盖（rootless）
```

## containers.conf

```toml
# 容器引擎配置
[containers]
# 默认capabilities
default_capabilities = ["CHOWN", "DAC_OVERRIDE", "FOWNER", "FSETID", "KILL", "NET_BIND_SERVICE", "SETFCAP", "SETGID", "SETPCAP", "SETUID", "SYS_CHROOT"]
# 默认系统调用过滤
default_sysctls = ["net.ipv4.ping_group_range=0 0"]
# DNS
dns_servers = ["8.8.8.8", "8.8.4.4"]
# 日志驱动
log_driver = "journald"
# 默认ulimits
default_ulimits = ["nofile=1024:1048576"]

[engine]
# OCI运行时
runtime = "crun"
# 事件日志
events_logger = "journald"
# compose提供者
compose_providers = ["podman-compose", "docker-compose"]
# 镜像拉取策略
pull_policy = "missing"

[engine.runtimes]
crun = ["/usr/bin/crun"]
runc = ["/usr/bin/runc"]

[network]
# 网络后端
network_backend = "netavark"
# 默认网络
default_network = "podman"
# DNS端口
dns_bind_port = 53

[machine]
# Machine默认配置
cpus = 4
memory = 8192
disk_size = 100
provider = "applehv"  # 或 "wsl", "hyperv", "qemu"
```

## storage.conf

```toml
[storage]
driver = "overlay"
graphroot = "/var/lib/containers/storage"  # root模式
# graphroot = "$HOME/.local/share/containers/storage"  # rootless
runroot = "/run/containers/storage"

[storage.options]
# 覆盖最大层数
size = ""
# 启用额外镜像存储
additionalimagestores = []

[storage.options.overlay]
mountopt = "nodev,metacopy=on"
# Rootless使用fuse-overlayfs
mount_program = "/usr/bin/fuse-overlayfs"
```

## registries.conf

```toml
# 未限定名称搜索顺序
unqualified-search-registries = ["docker.io", "quay.io", "ghcr.io"]

# Docker Hub配置
[[registry]]
prefix = "docker.io"
location = "docker.io"

# 镜像加速
[[registry.mirror]]
location = "mirror.gcr.io"
insecure = false

# 私有仓库
[[registry]]
prefix = "registry.example.com"
location = "registry.example.com"
insecure = false

# 阻止特定仓库
[[registry]]
prefix = "untrusted.example.com"
blocked = true
```

## policy.json

```json
{
  "default": [
    {"type": "insecureAcceptAnything"}
  ],
  "transports": {
    "docker": {
      "registry.example.com/signed": [
        {
          "type": "sigstoreSigned",
          "keyPath": "/etc/pki/containers/cosign.pub",
          "signedIdentity": {
            "type": "matchRepository"
          }
        }
      ],
      "docker.io": [
        {"type": "insecureAcceptAnything"}
      ]
    },
    "dir": {
      "": [{"type": "insecureAcceptAnything"}]
    }
  }
}
```

## 配置优先级

1. 命令行参数（最高优先级）
2. 环境变量（CONTAINERS_CONF, CONTAINERS_STORAGE_CONF等）
3. 用户级配置（~/.config/containers/）
4. 系统级配置（/etc/containers/）
5. 默认配置（/usr/share/containers/）
