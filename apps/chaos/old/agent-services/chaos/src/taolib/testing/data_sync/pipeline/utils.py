"""Pipeline 工具函数。

提供文档快照截断等通用工具。
"""

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)

_DEFAULT_MAX_BYTES = 4096


def truncate_snapshot(
    doc: dict[str, Any],
    max_bytes: int = _DEFAULT_MAX_BYTES,
) -> dict[str, Any]:
    """将文档快照截断至指定字节限制。

    保留 ``_id`` 字段，逐步移除其余键值对直到序列化后
    的 JSON 字节数在 ``max_bytes`` 以内。

    Args:
        doc: 原始文档字典
        max_bytes: 最大字节数（默认 4096）

    Returns:
        截断后的文档字典，若发生截断则包含 ``__truncated__: True``
    """
    if not doc:
        return doc

    try:
        raw = json.dumps(doc, default=str, ensure_ascii=False)
    except (TypeError, ValueError):
        return {"_id": doc.get("_id", "unknown"), "__truncated__": True}

    if len(raw.encode("utf-8")) <= max_bytes:
        return doc

    # 保留 _id，按序添加键直到超限
    result: dict[str, Any] = {}
    doc_id = doc.get("_id")
    if doc_id is not None:
        result["_id"] = doc_id

    result["__truncated__"] = True

    for key, value in doc.items():
        if key in ("_id", "__truncated__"):
            continue

        result[key] = value
        try:
            candidate = json.dumps(result, default=str, ensure_ascii=False)
        except (TypeError, ValueError):
            result.pop(key)
            continue

        if len(candidate.encode("utf-8")) > max_bytes:
            result.pop(key)
            break

    return result
