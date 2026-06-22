"""TOML 序列化工具函数。

手工格式化 TOML 文本，因标准库 ``tomllib`` 只读。
"""

from __future__ import annotations

from .models import LockInfo, SessionEvent, SessionManifest


def toml_basic_string(value: str) -> str:
    """将任意字符串编码为 TOML basic string，转义所有特殊字符。

    处理双引号、反斜杠、换行、回车、制表符，确保写入后仍可被
    ``tomllib`` 正确回读。

    Args:
        value: 原始字符串。

    Returns:
        带双引号包裹的转义后字符串，可直接嵌入 TOML 模板。
    """
    escaped = (
        str(value)
        .replace("\\", "\\\\")
        .replace("\n", "\\n")
        .replace("\r", "\\r")
        .replace("\t", "\\t")
        .replace('"', '\\"')
    )
    return f'"{escaped}"'


def toml_string_array(values: list[str]) -> str:
    """将字符串列表编码为 TOML 内联数组，每个元素复用 ``toml_basic_string``。

    Args:
        values: 字符串列表。

    Returns:
        TOML 内联数组文本，如 ``["a", "b c"]``。
    """
    return "[" + ", ".join(toml_basic_string(v) for v in values) + "]"


def format_manifest_toml(manifest: SessionManifest) -> str:
    """将 SessionManifest 序列化为 manifest.toml 文本。"""
    task_id_line = (
        f"task_id = {toml_basic_string(manifest.task_id)}"
        if manifest.task_id
        else 'task_id = ""'
    )
    return (
        "[session]\n"
        f"id = {toml_basic_string(manifest.id)}\n"
        f"title = {toml_basic_string(manifest.title)}\n"
        f"created_by = {toml_basic_string(manifest.created_by)}\n"
        f"created_at = {toml_basic_string(manifest.created_at)}\n"
        'schema_version = "world-session-v1"\n'
        "\n"
        "[session.task]\n"
        f"{task_id_line}\n"
        'parent_session = ""\n'
        "\n"
        "[session.allowed_runtimes]\n"
        f"runtimes = {toml_string_array(manifest.allowed_runtimes)}\n"
        "\n"
        "[session.status]\n"
        f"state = {toml_basic_string(manifest.state)}\n"
        f"last_event_seq = {manifest.last_event_seq}\n"
        f"last_writer = {toml_basic_string(manifest.last_writer)}\n"
    )


def format_lock_toml(lock: LockInfo) -> str:
    """将 LockInfo 序列化为 lock.toml 文本。"""
    return (
        "[holder]\n"
        f"surface = {toml_basic_string(lock.surface)}\n"
        f"instance_id = {toml_basic_string(lock.instance_id)}\n"
        f"actor = {toml_basic_string(lock.actor)}\n"
        "\n"
        "[lease]\n"
        f"acquired_at = {toml_basic_string(lock.acquired_at)}\n"
        f"lease_until = {toml_basic_string(lock.lease_until)}\n"
        f"renew_count = {lock.renew_count}\n"
    )


def format_event_block(event: SessionEvent) -> str:
    """将 SessionEvent 序列化为单个 ``[[event]]`` TOML 块文本。

    payload 中每个值根据类型选择合适的 TOML 表示。
    """
    lines: list[str] = [
        "",
        "[[event]]",
        f"seq = {event.seq}",
        f"ts = {toml_basic_string(event.ts)}",
        f"surface = {toml_basic_string(event.surface)}",
        f"actor = {toml_basic_string(event.actor)}",
        f"type = {toml_basic_string(event.type)}",
        "",
        "[event.payload]",
    ]
    for k, v in event.payload.items():
        if v is None:
            lines.append(f'{k} = ""')
        elif isinstance(v, bool):
            lines.append(f"{k} = {str(v).lower()}")
        elif isinstance(v, int | float):
            lines.append(f"{k} = {v}")
        elif isinstance(v, list):
            if all(isinstance(i, str) for i in v):
                lines.append(f"{k} = {toml_string_array(v)}")
            else:
                items = ", ".join(str(i) for i in v)
                lines.append(f"{k} = [{items}]")
        else:
            lines.append(f"{k} = {toml_basic_string(str(v))}")
    lines.append("")
    return "\n".join(lines)
