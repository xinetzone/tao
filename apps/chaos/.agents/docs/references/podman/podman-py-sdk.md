# Podman Python SDK 参考

PodmanPy 是 Podman 的 Python3 客户端，通过 Podman 服务的 RESTful API 实现对容器、镜像、Pod、网络、卷等资源的编程式管理。遵循 Docker SDK for Python 的 API 风格，但针对 Podman 做了扩展。

## 1. 安装与连接

```bash
pip install podman
```

### 1.1 连接 URL 格式

Podman 服务通过 URL 寻址，scheme 决定连接方式：

| Scheme      | 格式                                                             | 示例                                                                 |
| ----------- | -------------------------------------------------------------- | ------------------------------------------------------------------ |
| `http+ssh`  | `http+ssh://[<user>@]<host>[:<port>]/<socket路径>[?secure=True]` | `http+ssh://alice@api.example:22/run/user/1000/podman/podman.sock` |
| `http+unix` | `http+unix://<socket路径>`                                       | `http+unix:///run/podman/podman.sock`                              |
| `tcp`       | `tcp://<hostname>:<port>`                                      | `tcp://api.example:8888`                                           |

> 别名：`ssh` 等价于 `http+ssh`，`unix` 等价于 `http+unix`。

### 1.2 环境变量连接

`PodmanClient.from_env()` 支持以下环境变量：

| 环境变量                                         | 说明            |
| -------------------------------------------- | ------------- |
| `DOCKER_HOST` / `CONTAINER_HOST`             | Podman 服务 URL |
| `DOCKER_TLS_VERIFY` / `CONTAINER_TLS_VERIFY` | 是否验证主机 CA 证书  |
| `DOCKER_CERT_PATH` / `CONTAINER_CERT_PATH`   | TLS 证书路径      |

### 1.3 Windows 平台限制与替代方案

**PodmanPy 在 Windows 上存在已知限制，四种原生连接方式的状态：**

| 连接方式 | Windows 支持 | 原因 |
|----------|-------------|------|
| `unix://` | ❌ 不可用 | Windows 不支持 `AF_UNIX` socket |
| `ssh://` | ❌ 不可用 | `podman.api.ssh.SSHSocket` 硬编码 `socket.AF_UNIX`（[ssh.py:44](https://github.com/containers/podman-py/blob/main/podman/api/ssh.py#L44)），Windows 上直接报 `AttributeError` |
| `npipe://` | ❌ 不支持 | PodmanPy 仅支持 `unix/http+unix/ssh/http+ssh/tcp/http` 六种 scheme，`npipe` 不在其中 |
| `tcp://` | ✅ 可用 | 需先建立 SSH 隧道将 VM 内 Unix socket 转发为本地 TCP 端口 |

> **注意**：Podman 5.7+ 用 `podman machine inspect` 获取连接信息（无 `machine env` 子命令），但获取到的 Named Pipe / SSH 信息对 PodmanPy 均无效。

**推荐方案：SSH 隧道转发（零侵入，完整 SDK 支持）**

核心思路：利用 `podman machine` 自带的 SSH 配置，建立 TCP 隧道将 VM 内的 Unix socket 转发到 Windows 本地端口，然后使用 PodmanPy 原生支持的 `tcp://` scheme 连接。

```python
import subprocess
import socket
import time
import json

# 1. 读取 podman machine SSH 配置
result = subprocess.run(
    ["podman", "machine", "inspect", "podman-machine-default"],
    capture_output=True, text=True, check=True,
)
cfg = json.loads(result.stdout)[0]
ssh = cfg["SSHConfig"]

# 2. 分配本地空闲端口
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind(("", 0))
    local_port = s.getsockname()[1]

# 3. 启动 SSH 隧道：将远程 Unix socket 转发到本地 TCP 端口
tunnel = subprocess.Popen([
    "ssh", "-N",
    "-o", "StrictHostKeyChecking=no",
    "-o", "ExitOnForwardFailure=yes",
    "-L", f"{local_port}:/run/user/1000/podman/podman.sock",
    "-p", str(ssh["Port"]),
    "-i", ssh["IdentityPath"],
    f"{ssh['RemoteUsername']}@localhost",
], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# 4. 等待隧道就绪
deadline = time.monotonic() + 10
while time.monotonic() < deadline:
    time.sleep(0.3)
    try:
        s = socket.create_connection(("localhost", local_port), timeout=1)
        s.close()
        break
    except (OSError, ConnectionRefusedError):
        continue

# 5. 使用 tcp:// 连接 PodmanPy
from podman import PodmanClient

with PodmanClient(base_url=f"tcp://localhost:{local_port}") as client:
    if client.ping():
        print("连接成功")
        images = client.images.list()
        containers = client.containers.list(all=True)

# 6. 清理隧道
tunnel.terminate()
tunnel.wait()
```

> **原理**：`ssh -L PORT:/remote/socket`（需 OpenSSH 8.9+）可直接将远程 Unix domain socket 转发为本地 TCP 端口。PodmanPy 的 `tcp://` scheme 是原生支持的，无需任何库修改。

**完整封装模块**：上述逻辑已封装为可复用模块，支持 context manager、自动端口分配、降级方案和 `atexit` 清理。详见 `podman_win_patch.py`：

```python
import podman_win_patch

# 方式1：context manager（推荐）
with podman_win_patch.PodmanSSHClient() as client:
    if client.ping():
        images = client.images.list()

# 方式2：快速获取
client = podman_win_patch.quick_client()
containers = client.containers.list(all=True)
client.close()
```

**降级方案：手动 TCP API**（SSH 版本不够新时）：

```powershell
# 在 VM 内启动 TCP 监听
podman machine ssh -- podman system service --time=0 tcp:0.0.0.0:8888
```

```python
client = PodmanClient(base_url="tcp://localhost:8888")
```

> **安全提醒**：`podman system service tcp` 将 API 暴露在本地网络，仅在受信任环境使用。

**最简方案：subprocess 调用 CLI**（无需 SDK）：当不需要完整 Python API 时，直接用 `subprocess` 调用 `podman` CLI 是最可靠的选择（无需隧道、无库兼容问题）。

```python
import subprocess

def podman(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(["podman"] + args, capture_output=True, text=True, check=True)

podman(["run", "--rm", "python:3.14-slim", "python", "--version"])
```

## 2. PodmanClient

客户端入口，作为上下文管理器使用。

```python
import podman

# 默认连接
with podman.PodmanClient() as client:
    if client.ping():
        print("连接成功")

# 显式指定连接
with podman.PodmanClient(base_url="unix:///run/podman/podman.sock") as client:
    ...

# 从环境变量连接
client = podman.PodmanClient.from_env()
```

### 2.1 初始化参数

| 参数               | 类型     | 说明                      |
| ---------------- | ------ | ----------------------- |
| `base_url`       | `str`  | 服务完整 URL                |
| `version`        | `str`  | API 版本，默认 `auto`（自动检测）  |
| `timeout`        | `int`  | API 调用超时（秒）             |
| `user_agent`     | `str`  | 自定义 User-Agent          |
| `identity`       | `str`  | SSH 密钥路径（SSH 连接用）       |
| `use_ssh_client` | `bool` | 始终使用系统 SSH 客户端（默认 True） |
| `max_pool_size`  | `int`  | 连接池大小                   |

### 2.2 客户端方法

| 方法                                         | 返回         | 说明                                  |
| ------------------------------------------ | ---------- | ----------------------------------- |
| `ping()`                                   | `bool`     | 检测服务是否响应                            |
| `version(**kwargs)`                        | `dict`     | 获取版本信息，`api_version=True` 包含 API 版本 |
| `info()`                                   | `dict`     | 获取 Podman 服务信息                      |
| `df()`                                     | `dict`     | 获取各资源的磁盘使用量                         |
| `events(decode, filters, since, until)`    | `Iterator` | 订阅服务事件流                             |
| `login(username, password, registry, ...)` | -          | 登录镜像仓库                              |
| `close()`                                  | -          | 释放客户端资源                             |

### 2.3 客户端属性（Manager 入口）

| 属性           | 类型                  | 说明           |
| ------------ | ------------------- | ------------ |
| `containers` | `ContainersManager` | 容器管理器        |
| `images`     | `ImagesManager`     | 镜像管理器        |
| `pods`       | `PodsManager`       | Pod 管理器      |
| `networks`   | `NetworksManager`   | 网络管理器        |
| `volumes`    | `VolumesManager`    | 卷管理器         |
| `manifests`  | `ManifestsManager`  | Manifest 管理器 |
| `secrets`    | —                   | Secret 管理器   |
| `system`     | `SystemManager`     | 系统级信息        |

> Swarm 相关属性（`configs`、`nodes`、`services`、`swarm`）访问会抛出 `NotImplementedError`，Podman 不支持 Swarm。

## 3. 容器

### 3.1 ContainersManager

通过 `client.containers` 访问。

#### 容器列表与查询

```python
# 列出所有容器
containers = client.containers.list(all=True)

# 过滤器
containers = client.containers.list(
    all=True,
    filters={"status": "running", "label": "env=prod"}
)

# 按名称/ID 获取单个容器
ctr = client.containers.get("my-container")
# 或 ctr = client.containers.get("abc123def456")

# 检查容器是否存在
exists = client.containers.exists("my-container")
```

#### 创建与运行

`ContainersManager` 通过 Mixin 继承了 `create()` 和 `run()`：

```python
# 创建容器（不启动）
ctr = client.containers.create(
    "python:3.14-slim",
    command=["python", "-c", "print('hello')"],
    name="my-container",
    environment={"MY_VAR": "value"},
    volumes={"/host/path": {"bind": "/container/path", "mode": "rw"}},
    ports={"8080/tcp": 8080},
    detach=True,
)

# 运行容器（创建 + 启动 + 等待/返回）
# detach=False 时等待结束返回日志；detach=True 时返回 Container 对象
ctr = client.containers.run(
    "python:3.14-slim",
    command=["python", "--version"],
    remove=True,
    stdout=True,
    stderr=True,
)
```

#### create/run 核心关键字参数

以下参数同时适用于 `create()` 和 `run()`：

**基础与标识：**

| 参数                        | 类型                           | 说明                       |
| ------------------------- | ---------------------------- | ------------------------ |
| `name`                    | `str`                        | 容器名称                     |
| `hostname`                | `str`                        | 容器主机名                    |
| `domainname`              | `str \| list[str]`           | DNS 搜索域                  |
| `user`                    | `str \| int`                 | 运行用户名/UID                |
| `entrypoint`              | `str \| list[str]`           | 入口点覆盖                    |
| `working_dir` / `workdir` | `str`                        | 工作目录                     |
| `labels`                  | `dict[str,str] \| list[str]` | 标签                       |
| `platform`                | `str`                        | 平台 `os[/arch[/variant]]` |

**资源限制：**

| 参数              | 类型           | 说明                           |
| --------------- | ------------ | ---------------------------- |
| `mem_limit`     | `int \| str` | 内存限制（如 `"128m"`、`"1g"`）      |
| `memswap_limit` | `int \| str` | 内存 + swap 上限                 |
| `cpu_shares`    | `int`        | CPU 相对权重                     |
| `cpu_period`    | `int`        | CPU CFS 周期（微秒）               |
| `cpu_quota`     | `int`        | CPU CFS 配额（微秒）               |
| `cpuset_cpus`   | `str`        | 允许执行的 CPU（如 `"0-3"`、`"0,1"`） |
| `nano_cpus`     | `int`        | CPU 配额（1e-9 CPU 单位）          |
| `pids_limit`    | `int`        | PID 数量限制                     |
| `blkio_weight`  | `int`        | 块 IO 权重（10-1000）             |
| `shm_size`      | `str \| int` | `/dev/shm` 大小（如 `"1G"`）      |

**网络：**

| 参数                  | 类型              | 说明                                           |
| ------------------- | --------------- | -------------------------------------------- |
| `network_mode`      | `str`           | 网络模式：`bridge`、`none`、`host`、`container:<id>` |
| `networks`          | `dict`          | 连接的网络配置                                      |
| `ports`             | `dict`          | 端口映射，见下方详解                                   |
| `dns`               | `list[str]`     | 自定义 DNS                                      |
| `publish_all_ports` | `bool`          | 发布所有端口                                       |
| `extra_hosts`       | `dict[str,str]` | 额外 hosts 映射                                  |

**存储与挂载：**

| 参数             | 类型              | 说明                   |
| -------------- | --------------- | -------------------- |
| `volumes`      | `dict`          | Docker 兼容卷挂载格式       |
| `mounts`       | `list[Mount]`   | 更强大的挂载（bind、tmpfs 等） |
| `tmpfs`        | `dict[str,str]` | tmpfs 挂载             |
| `volumes_from` | `list[str]`     | 从其他容器继承卷             |

**安全与权限：**

| 参数             | 类型              | 说明              |
| -------------- | --------------- | --------------- |
| `privileged`   | `bool`          | 扩展特权            |
| `cap_add`      | `list[str]`     | 添加内核能力          |
| `cap_drop`     | `list[str]`     | 移除内核能力          |
| `security_opt` | `list[str]`     | 安全选项（SELinux 等） |
| `secrets`      | `list`          | 挂载的 Secret      |
| `secret_env`   | `dict[str,str]` | 环境变量形式的 Secret  |
| `read_only`    | `bool`          | 只读根文件系统         |

**生命周期与行为：**

| 参数                       | 类型     | 说明                                                    |
| ------------------------ | ------ | ----------------------------------------------------- |
| `detach`                 | `bool` | 后台运行（run 中影响返回类型）                                     |
| `remove` / `auto_remove` | `bool` | 退出后自动删除                                               |
| `restart_policy`         | `dict` | 重启策略 `{"Name": "on-failure", "MaximumRetryCount": 5}` |
| `stop_signal`            | `str`  | 停止信号                                                  |
| `tty`                    | `bool` | 分配伪 TTY                                               |
| `stdin_open`             | `bool` | 保持 STDIN 打开                                           |
| `init`                   | `bool` | 运行 init 进程                                            |
| `healthcheck`            | `dict` | 健康检查配置                                                |

**端口映射格式：**

```python
{
    "8080/tcp": 8080,                          # 容器端口 → 主机端口
    "2222/tcp": None,                           # 随机主机端口
    "1111/tcp": ("127.0.0.1", 1111),           # 指定主机 IP + 端口
    "9090/tcp": [1234, ("127.0.0.1", 4567)],   # 多端口绑定
    "2222/tcp": {"port": 3333, "range": 4},    # 端口范围
}
```

### 3.2 Container 对象方法

| 方法                                                      | 说明                                        |
| ------------------------------------------------------- | ----------------------------------------- |
| `start(**kwargs)`                                       | 启动容器，`detach_keys` 可覆盖分离键序列               |
| `stop(timeout=...)`                                     | 停止容器；Podman 额外支持 `all=True`、`ignore=True` |
| `restart(timeout=...)`                                  | 重启容器                                      |
| `kill(signal=None)`                                     | 发送信号                                      |
| `pause()` / `unpause()`                                 | 暂停/恢复进程                                   |
| `remove(v=False, force=False)`                          | 删除容器                                      |
| `rename(name)`                                          | 重命名                                       |
| `inspect()`                                             | 获取容器详细信息                                  |
| `reload()`                                              | 刷新容器数据                                    |
| `logs(stdout, stderr, stream, tail, since, timestamps)` | 获取日志                                      |
| `exec_run(cmd, **kwargs)`                               | 在容器内执行命令                                  |
| `commit(repository, tag, **kwargs)`                     | 将容器保存为镜像                                  |
| `stats(decode, stream)`                                 | 获取实时资源统计                                  |
| `top(ps_args, stream)`                                  | 查看容器内进程                                   |
| `diff()`                                                | 查看文件系统变更                                  |
| `export(chunk_size)`                                    | 导出容器文件系统为 tar                             |
| `get_archive(path, chunk_size)`                         | 下载容器内文件/目录                                |
| `put_archive(path, data)`                               | 上传文件到容器                                   |
| `attach(stdout, stderr, stream, logs)`                  | 附加到容器 TTY                                 |
| `resize(height, width)`                                 | 调整 TTY 尺寸                                 |
| `update(**kwargs)`                                      | 更新容器资源配置                                  |

#### exec\_run 示例

```python
# 基本用法
exit_code, output = container.exec_run("ls -la /app")

# 分离 stdout/stderr
exit_code, (stdout, stderr) = container.exec_run(
    ["python", "script.py"],
    demux=True,
    environment={"DEBUG": "1"},
    workdir="/app",
)

# 流式输出
exit_code, generator = container.exec_run(
    "tail -f /var/log/app.log",
    stream=True,
)
for chunk in generator:
    print(chunk)
```

#### logs 示例

```python
# 获取最近 100 行
logs = container.logs(tail=100)

# 流式实时日志
for line in container.logs(stream=True, follow=True, timestamps=True):
    print(line)
```

## 4. 镜像

### 4.1 ImagesManager

通过 `client.images` 访问。

```python
# 列出所有镜像
images = client.images.list(all=True)

# 按名称过滤
images = client.images.list(name="python")

# 获取单个镜像
img = client.images.get("python:3.14-slim")

# 检查是否存在
exists = client.images.exists("python:3.14-slim")
```

#### 拉取与推送

```python
# 拉取镜像
img = client.images.pull("python:3.14-slim")

# 拉取所有 tag
images = client.images.pull("python", all_tags=True)

# 流式拉取（获取进度）
for progress in client.images.pull("alpine", stream=True, decode=True):
    print(progress)

# 推送镜像
result = client.images.push(
    "my-registry/my-image",
    tag="latest",
    auth_config={"username": "user", "password": "pass"},
)
```

#### 构建镜像

```python
# 从 Dockerfile 路径构建
image, build_logs = client.images.build(
    path="./docker-context",
    tag="my-app:latest",
    dockerfile="Containerfile",
    buildargs={"VERSION": "1.0"},
    rm=True,
)

# 查看构建日志
for log in build_logs:
    print(log)
```

#### 其他操作

```python
# 搜索镜像
results = client.images.search("nginx", limit=5)

# 镜像保存（返回 tarball 迭代器）
for chunk in img.save():
    write_to_file(chunk)

# 加载镜像
for image in client.images.load(file_path="./backup.tar"):
    print(f"Loaded: {image.tags}")

# 删除镜像
result = client.images.remove("my-image:old", force=True)

# 清理未使用镜像
result = client.images.prune(all=True)
# {"ImagesDeleted": [...], "SpaceReclaimed": 123456}

# 镜像复制（跨主机）
client.images.scp("user@host1::myimage", "user@host2::myimage")
```

### 4.2 Image 对象

| 属性/方法                         | 说明                       |
| ----------------------------- | ------------------------ |
| `id`                          | 完整镜像 ID                  |
| `short_id`                    | 截断镜像 ID（保留 `sha256:` 前缀） |
| `tags`                        | `list[str]` 标签列表         |
| `labels`                      | `dict[str,str]` 标签       |
| `history()`                   | 镜像构建历史                   |
| `tag(repository, tag, force)` | 添加标签                     |
| `remove(force, noprune)`      | 删除镜像                     |
| `save(chunk_size, named)`     | 导出为 tarball              |
| `reload()`                    | 刷新镜像数据                   |

## 5. Pod

Podman 独有的 Pod 概念，将多个容器组织在一个共享命名空间的单元中。通过 `client.pods` 访问。

```python
# 创建 Pod
pod = client.pods.create("my-pod", ports={"8080/tcp": 8080})

# 列出 Pod
pods = client.pods.list()
pods = client.pods.list(filters={"name": "my-pod", "status": ["running"]})
pods = client.pods.list(filters={"ctr-ids": ["abc123"]})

# 获取 Pod
pod = client.pods.get("my-pod")

# 检查是否存在
client.pods.exists("my-pod")

# 统计信息
stats = client.pods.stats(all=True)
for stat in client.pods.stats(name=["pod1", "pod2"], stream=True, decode=True):
    print(stat)

# 清理未用 Pod
result = client.pods.prune()
# {"PodsDeleted": ["id1"], "SpaceReclaimed": 0}

# 删除 Pod
client.pods.remove("my-pod", force=True)  # force 会先停止并删除其中容器
```

## 6. 网络

通过 `client.networks` 访问。

```python
# 创建网络
net = client.networks.create(
    "my-net",
    driver="bridge",
    internal=False,
    enable_ipv6=False,
    labels={"env": "dev"},
)

# 列出网络
networks = client.networks.list()
networks = client.networks.list(filters={"driver": "bridge"})

# 获取网络
net = client.networks.get("my-net")

# 检查是否存在
client.networks.exists("my-net")

# 清理未用网络
result = client.networks.prune()

# 删除网络
client.networks.remove("my-net", force=True)
```

### NetworksManager.create 参数

| 参数            | 类型              | 说明                   |
| ------------- | --------------- | -------------------- |
| `name`        | `str`           | 网络名称                 |
| `driver`      | `str`           | 驱动类型（如 `"bridge"`）   |
| `internal`    | `bool`          | 限制外部访问               |
| `enable_ipv6` | `bool`          | 启用 IPv6              |
| `dns_enabled` | `bool`          | 是否禁用 DNS（False 表示启用） |
| `labels`      | `dict[str,str]` | 标签                   |
| `ipam`        | `IPAMConfig`    | 自定义 IP 分配方案          |
| `options`     | `dict[str,Any]` | 驱动选项                 |

## 7. 卷

通过 `client.volumes` 访问。

```python
# 创建卷
vol = client.volumes.create(
    "my-volume",
    driver="local",
    driver_opts={"type": "tmpfs", "device": "tmpfs"},
    labels={"backup": "daily"},
)

# 列出卷
volumes = client.volumes.list()
volumes = client.volumes.list(filters={"name": "my-volume"})

# 获取卷
vol = client.volumes.get("my-volume")

# 检查是否存在
client.volumes.exists("my-volume")

# 清理未用卷
result = client.volumes.prune()

# 删除卷
client.volumes.remove("my-volume", force=True)
```

### Volume 对象

| 属性/方法           | 说明    |
| --------------- | ----- |
| `id`            | 卷 ID  |
| `name`          | 卷名称   |
| `short_id`      | 截断 ID |
| `inspect()`     | 查看卷详情 |
| `remove(force)` | 删除此卷  |
| `reload()`      | 刷新卷数据 |

## 8. SystemManager

通过 `client.system` 访问，提供系统级信息。

```python
# 服务连通
client.system.ping()          # → bool

# 服务信息
info = client.system.info()

# 版本
version = client.system.version()
version_with_api = client.system.version(api_version=True)

# 磁盘使用
disk_usage = client.system.df()

# 登录仓库
client.system.login(
    username="user",
    password="pass",
    registry="quay.io",
)
```

## 9. 异常体系

```
PodmanError (DockerException)
 ├── APIError (HTTPError)
 │    ├── ImageNotFound
 │    └── NotFound
 ├── BuildError
 ├── ContainerError
 └── InvalidArgument
StreamParseError (RuntimeError)
```

| 异常                 | 说明                                                                               |
| ------------------ | -------------------------------------------------------------------------------- |
| `PodmanError`      | 所有 PodmanPy 异常的基类                                                                |
| `APIError`         | HTTP 错误包装。`status_code` 属性获取状态码，`is_client_error()` / `is_server_error()` 判断错误类型 |
| `NotFound`         | 通用资源未找到（兼容命名）                                                                    |
| `ImageNotFound`    | 镜像未找到                                                                            |
| `BuildError`       | 构建失败，包含 `reason` 和 `build_log`                                                   |
| `ContainerError`   | 容器非零退出码，包含 `exit_status`、`command`、`image`、`stderr`                              |
| `InvalidArgument`  | 方法参数无效                                                                           |
| `StreamParseError` | 流解析异常                                                                            |

### 异常处理示例

```python
from podman.errors.exceptions import ImageNotFound, ContainerError, APIError

try:
    ctr = client.containers.run("missing-image:latest", detach=True)
except ImageNotFound:
    print("镜像未找到，尝试拉取...")
except ContainerError as e:
    print(f"容器退出码 {e.exit_status}: {e.stderr}")
except APIError as e:
    print(f"API 错误 ({e.status_code}): {e.explanation}")
```

## 10. 完整示例

```python
import podman
from podman.errors.exceptions import ContainerError, ImageNotFound

with podman.PodmanClient(base_url="unix:///run/podman/podman.sock") as client:
    # 验证连接
    if not client.ping():
        raise RuntimeError("无法连接 Podman 服务")

    print(client.system.info()["host"]["os"])

    # 拉取镜像
    try:
        img = client.images.get("python:3.14-slim")
    except ImageNotFound:
        img = client.images.pull("python:3.14-slim")
        print(f"拉取完成: {img.tags}")

    # 创建并启动容器
    ctr = client.containers.run(
        img,
        command=["python", "-c", "import sys; print(sys.version)"],
        name="demo-container",
        remove=True,
        stdout=True,
        stderr=True,
    )
    print(ctr)  # 输出 Python 版本

    # exec_run 执行额外命令
    ctr2 = client.containers.create(img, detach=True, tty=True)
    ctr2.start()
    exit_code, output = ctr2.exec_run("pip list")
    print(output.decode())
    ctr2.stop()
    ctr2.remove()
```

## 11. 与 Docker SDK 的主要差异

| 方面         | Docker SDK   | PodmanPy                            |
| ---------- | ------------ | ----------------------------------- |
| Swarm 支持   | ✅ 完整         | ❌ 不支持，访问相关属性抛 `NotImplementedError` |
| Pod 概念     | ❌            | ✅ `client.pods` 原生支持                |
| 守护进程       | dockerd      | 无需守护进程（rootless）                    |
| SSH 连接     | 需特殊配置        | 原生 `ssh://` scheme 支持               |
| `stop()`   | `timeout` 参数 | 额外 `all`、`ignore` 参数                |
| `rename()` | 支持           | 支持（容器就地更新，避免 `reload()`）            |
| Manifest   | -            | `client.manifests` 管理 OCI 镜像索引      |
| Secret     | 通过 Swarm     | 原生支持                                |

## 参考来源

- [PodmanPy 官方文档](https://podman-py.readthedocs.io/en/latest/)
- [PodmanPy GitHub](https://github.com/containers/podman-py)
- [Podman 官方文档](https://docs.podman.io/)

