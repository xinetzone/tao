# 第七章：字段变更对照

### 7.1 字段全景

| 字段 | 变更前 | 变更后 | 含义 |
|------|--------|--------|------|
| `image` | 第 5 个必填字段 | **唯一必填字段** | 容器镜像 |
| `host_path` | 必填 | `Path \| None = None` | 为 None 时不挂载 bind 卷 |
| `target` | 必填 | `str \| None = None` | 为 None 时不挂载 bind 卷 |
| `working_dir` | 必填 | `str \| None = None` | 为 None 时使用镜像默认值 |
| `name` | 必填 | `str \| None = None` | 为 None 时 Podman 自动生成 |
| `run_kwargs` | （不存在） | `dict[str, Any] = {}` | **新增**：透传给 `containers.run()` |
| `network_mode` | （不存在） | `str \| None = None` | **新增**：容器网络模式 |
| `start_container` | （不存在） | `bool = True` | **新增**：是否启动容器 |

### 7.2 使用场景对照

```python
# ── 场景 1：完整挂载模式（等效原用法）──
with ContainerRun(
    image="python:3.13",
    host_path=Path("."),
    target="/mnt",
    working_dir="/mnt",
    name="worker",
) as cr:
    cr.exec(["python", "script.py"])

# ── 场景 2：无挂载容器 ──
with ContainerRun(image="python:3.13") as cr:
    result = cr.exec(["python", "-c", "print(42)"])

# ── 场景 3：仅建连接（探活）──
with ContainerRun(
    image="localhost/myimage",
    client_kwargs={"base_url": "ssh://...", "identity": "..."},
    start_container=False,
) as cr:
    if cr._client.ping():
        print("连接成功")

# ── 场景 4：自定义参数容器 ──
with ContainerRun(
    image="python:3.13",
    network_mode="host",
    run_kwargs={"environment": {"FOO": "bar"}, "privileged": True},
) as cr:
    cr.exec(["echo $FOO"])

# ── 场景 5：自动命名 + 命名卷 ──
with ContainerRun(
    image="postgres:16",
    volumes={"pgdata": "/var/lib/postgresql/data"},
    run_kwargs={"environment": {"POSTGRES_PASSWORD": "secret"}},
) as cr:
    ...
```
