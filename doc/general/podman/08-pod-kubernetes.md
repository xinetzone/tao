---
title: Pod与Kubernetes集成
description: Podman Pod概念、管理操作、Kubernetes YAML集成、Kind与Minikube集成
---

# Pod与Kubernetes集成

## Pod概念

- **Kubernetes风格Pod**：共享网络命名空间的容器组
- **Infra container（pause容器）**：维持命名空间，Pod中的"骨架"容器
- **Pod内通信**：容器间通过 localhost 直接通信，无需额外网络配置
- **Pod级别生命周期管理**：启动/停止/重启作用于整个Pod

## Pod管理操作

```bash
# 创建Pod
podman pod create --name my-pod -p 8080:80 --network mynet

# 在Pod中添加容器
podman run -d --pod my-pod --name web nginx
podman run -d --pod my-pod --name api my-api:latest
podman run -d --pod my-pod --name db postgres:16

# Pod生命周期
podman pod start/stop/restart my-pod
podman pod inspect my-pod
podman pod ps
podman pod rm my-pod
```

## Kubernetes YAML 集成

### 生成YAML

```bash
podman generate kube my-pod > my-pod.yaml
podman generate kube --service my-pod > my-pod-with-service.yaml
```

### 从YAML部署

```bash
podman kube play deployment.yaml
podman kube play --network mynet deployment.yaml
podman kube down deployment.yaml
```

### 支持的K8s资源类型

- Pod
- Deployment
- DaemonSet
- ConfigMap
- Secret
- PersistentVolumeClaim

## 示例：完整Web应用Pod

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: webapp
spec:
  containers:
  - name: frontend
    image: docker.io/library/nginx:latest
    ports:
    - containerPort: 80
    volumeMounts:
    - name: html
      mountPath: /usr/share/nginx/html
  - name: backend
    image: docker.io/library/node:20-alpine
    ports:
    - containerPort: 3000
    env:
    - name: DB_HOST
      value: "localhost"
  - name: database
    image: docker.io/library/postgres:16
    env:
    - name: POSTGRES_PASSWORD
      value: "secret"
    volumeMounts:
    - name: pgdata
      mountPath: /var/lib/postgresql/data
  volumes:
  - name: html
    hostPath:
      path: ./frontend/dist
  - name: pgdata
    persistentVolumeClaim:
      claimName: pg-storage
```

## 与Kind集成

```bash
# 配置Podman作为Kind的运行时
export DOCKER_HOST=unix:///run/user/$(id -u)/podman/podman.sock
systemctl --user enable --now podman.socket

# 创建Kind集群
kind create cluster --name dev-cluster

# 加载本地镜像到Kind
podman save my-app:latest | kind load image-archive /dev/stdin --name dev-cluster
```

## 与Minikube集成

```bash
minikube start --driver=podman --container-runtime=containerd
```
