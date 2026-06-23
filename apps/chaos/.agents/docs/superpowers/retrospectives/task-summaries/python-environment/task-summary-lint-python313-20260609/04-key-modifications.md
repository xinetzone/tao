# 4. 关键修改清单

## 4.1 `podman_win.py`

文件：`d:\spaces\AgentForge\apps\chaos\src\taolib\flowkit\podman_win.py`

主要修改：

1. 运行环境说明从 Python 3.10+ 改为 Python 3.13+。
2. 移除 `from __future__ import annotations`。
3. 调整 `SSHTunnel._instances` 类型注解，避免在移除 future annotations 后出现类体内前向引用问题。

最终关键片段：

```python
import atexit
import json
import socket
import subprocess
import time
from typing import Any, ClassVar
```

```python
class SSHTunnel:
    """通过 SSH 建立 TCP → podman socket 的隧道."""

    _instances: ClassVar[list[Any]] = []
```

## 4.2 `podman_context.py`

文件：`d:\spaces\AgentForge\apps\chaos\src\taolib\flowkit\podman_context.py`

主要修改：

- 引入 `TracebackType`
- 为 `__exit__` 和 `__aexit__` 添加完整类型注解

修复后签名：

```python
def __exit__(
    self,
    exc_type: type[BaseException] | None,
    exc_val: BaseException | None,
    exc_tb: TracebackType | None,
) -> bool:
```

```python
async def __aexit__(
    self,
    exc_type: type[BaseException] | None,
    exc_val: BaseException | None,
    exc_tb: TracebackType | None,
) -> bool:
```

## 4.3 `container.py`

文件：`d:\spaces\AgentForge\apps\chaos\src\taolib\flowkit\container.py`

主要修改：

- 将列表拼接改为 unpacking 风格。
- 删除未使用变量 `now`。

修复方向：

```python
args = [
    "run",
    "-d",
    "--name",
    name,
    "-w",
    self.config.workdir,
    *self._volume_args(),
    *self._env_args(),
    self.config.image,
    "sleep",
    "infinity",
]
```

## 4.4 `build_workflow.py`

文件：`d:\spaces\AgentForge\apps\chaos\examples\flowkit\build_workflow.py`

主要修改：

- 为示例函数补充返回类型注解：

```python
def example_build_workflow() -> bool:
def example_container_config() -> None:
def example_nuitka_configs() -> None:
```

## 4.5 `test_flowkit.py`

文件：`d:\spaces\AgentForge\apps\chaos\tests\flowkit\test_flowkit.py`

主要修改：

- 将未使用变量改为下划线前缀，满足 Ruff 对 unused unpacked variable 的要求：

```python
success, _message = verify_checksum_file(checksum_path)
success, _errors = ArtifactManifest.verify(manifest_path)
```

## 4.6 `__init__.py`、`artifacts.py`、`models.py`

相关文件：

- `d:\spaces\AgentForge\apps\chaos\src\taolib\flowkit\__init__.py`
- `d:\spaces\AgentForge\apps\chaos\src\taolib\flowkit\artifacts.py`
- `d:\spaces\AgentForge\apps\chaos\src\taolib\flowkit\models.py`

主要处理：

- import 排序
- 删除无效 `noqa`
- 清理空白行尾随空格
- 执行 Ruff 格式化
