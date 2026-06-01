"""跨层持久化适配器 - 实现 LangGraph Checkpointer 接口，底层桥接多种存储后端。

本模块提供 :class:`HarnessCheckpointer`：

* 在结构上与 LangGraph 1.x 的 ``BaseCheckpointSaver`` 接口对齐（同步 + 异步
  方法对：``put`` / ``aput``、``get_tuple`` / ``aget_tuple`` 等）；
* 支持 ``memory``（默认）与 ``redis`` 两种后端，通过配置切换；
* 序列化采用 JSON（Pydantic ``model_dump_json`` / ``model_validate_json``）。

LangGraph 与 redis 在当前环境可能未安装，本模块通过运行时探测决定是否
启用对应后端，不强依赖第三方库。
"""

from __future__ import annotations

import asyncio
import time
import uuid
from collections.abc import AsyncIterator, Iterator
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

__all__ = [
    "CheckpointBackend",
    "CheckpointMetadata",
    "CheckpointRecord",
    "CheckpointerConfig",
    "HarnessCheckpointer",
    "MemoryBackend",
    "RedisBackend",
]


class CheckpointBackend(StrEnum):
    """检查点后端类型。"""

    MEMORY = "memory"
    REDIS = "redis"


class CheckpointMetadata(BaseModel):
    """检查点附加元数据。"""

    model_config = ConfigDict(extra="allow")

    source_layer: str = Field(default="unified", description="检查点来源层标识")
    step: int = Field(default=0, ge=0, description="检查点序号")
    writes: dict[str, Any] = Field(default_factory=dict)
    parents: dict[str, str] = Field(default_factory=dict)
    timestamp: float = Field(default_factory=time.time)


class CheckpointRecord(BaseModel):
    """检查点记录 - 持久化的最小单元。"""

    model_config = ConfigDict(extra="allow")

    thread_id: str
    checkpoint_id: str = Field(default_factory=lambda: f"ckpt-{uuid.uuid4().hex[:16]}")
    checkpoint_ns: str = ""
    checkpoint: dict[str, Any] = Field(default_factory=dict)
    metadata: CheckpointMetadata = Field(default_factory=CheckpointMetadata)
    parent_checkpoint_id: str | None = None


class CheckpointerConfig(BaseModel):
    """检查点适配器配置。"""

    model_config = ConfigDict(extra="forbid")

    backend: CheckpointBackend = CheckpointBackend.MEMORY
    redis_url: str = Field(
        default="redis://localhost:6379/0", description="Redis 连接 URL"
    )
    key_prefix: str = Field(default="harness:ckpt:", description="Redis key 前缀")
    ttl_seconds: int | None = Field(
        default=None, ge=1, description="Redis key 过期秒数"
    )


class _Backend:
    """检查点后端协议（结构化基类，便于扩展）。"""

    async def aput(self, record: CheckpointRecord) -> None:
        raise NotImplementedError

    async def aget(
        self, thread_id: str, checkpoint_id: str | None
    ) -> CheckpointRecord | None:
        raise NotImplementedError

    async def alist(
        self, thread_id: str, *, limit: int | None = None
    ) -> list[CheckpointRecord]:
        raise NotImplementedError

    async def adelete(self, thread_id: str) -> int:
        raise NotImplementedError


class MemoryBackend(_Backend):
    """基于进程内字典的内存后端（默认/测试用）。"""

    def __init__(self) -> None:
        self._store: dict[str, list[CheckpointRecord]] = {}
        self._lock = asyncio.Lock()

    async def aput(self, record: CheckpointRecord) -> None:
        async with self._lock:
            self._store.setdefault(record.thread_id, []).append(record)

    async def aget(
        self, thread_id: str, checkpoint_id: str | None
    ) -> CheckpointRecord | None:
        async with self._lock:
            records = self._store.get(thread_id, [])
            if not records:
                return None
            if checkpoint_id is None:
                return records[-1]
            for r in reversed(records):
                if r.checkpoint_id == checkpoint_id:
                    return r
            return None

    async def alist(
        self, thread_id: str, *, limit: int | None = None
    ) -> list[CheckpointRecord]:
        async with self._lock:
            records = list(self._store.get(thread_id, []))
        records.reverse()
        if limit is not None:
            records = records[:limit]
        return records

    async def adelete(self, thread_id: str) -> int:
        async with self._lock:
            removed = self._store.pop(thread_id, [])
            return len(removed)


class RedisBackend(_Backend):
    """Redis 后端 - 延迟导入 ``redis.asyncio``，未安装时抛出明确错误。

    数据组织：

    * ``{prefix}{thread_id}:index`` —— 有序集合，按时间戳存放 checkpoint_id；
    * ``{prefix}{thread_id}:item:{checkpoint_id}`` —— 检查点 JSON 字符串。
    """

    def __init__(self, config: CheckpointerConfig) -> None:
        self._config = config
        self._client: Any | None = None

    async def _ensure_client(self) -> Any:
        if self._client is not None:
            return self._client
        try:
            import redis.asyncio as redis  # type: ignore
        except ImportError as exc:  # pragma: no cover - 运行环境相关
            raise RuntimeError(
                "Redis 后端需要安装 'redis' 包: pip install 'redis>=5.0,<6'"
            ) from exc
        self._client = redis.from_url(self._config.redis_url, decode_responses=True)
        return self._client

    def _index_key(self, thread_id: str) -> str:
        return f"{self._config.key_prefix}{thread_id}:index"

    def _item_key(self, thread_id: str, checkpoint_id: str) -> str:
        return f"{self._config.key_prefix}{thread_id}:item:{checkpoint_id}"

    async def aput(self, record: CheckpointRecord) -> None:
        client = await self._ensure_client()
        payload = record.model_dump_json()
        item_key = self._item_key(record.thread_id, record.checkpoint_id)
        idx_key = self._index_key(record.thread_id)
        await client.set(item_key, payload, ex=self._config.ttl_seconds)
        await client.zadd(idx_key, {record.checkpoint_id: record.metadata.timestamp})
        if self._config.ttl_seconds is not None:
            await client.expire(idx_key, self._config.ttl_seconds)

    async def aget(
        self, thread_id: str, checkpoint_id: str | None
    ) -> CheckpointRecord | None:
        client = await self._ensure_client()
        if checkpoint_id is None:
            ids = await client.zrevrange(self._index_key(thread_id), 0, 0)
            if not ids:
                return None
            checkpoint_id = ids[0]
        raw = await client.get(self._item_key(thread_id, checkpoint_id))
        if raw is None:
            return None
        return CheckpointRecord.model_validate_json(raw)

    async def alist(
        self, thread_id: str, *, limit: int | None = None
    ) -> list[CheckpointRecord]:
        client = await self._ensure_client()
        end = -1 if limit is None else max(0, limit - 1)
        ids: list[str] = await client.zrevrange(self._index_key(thread_id), 0, end)
        records: list[CheckpointRecord] = []
        for cid in ids:
            raw = await client.get(self._item_key(thread_id, cid))
            if raw is not None:
                records.append(CheckpointRecord.model_validate_json(raw))
        return records

    async def adelete(self, thread_id: str) -> int:
        client = await self._ensure_client()
        ids: list[str] = await client.zrange(self._index_key(thread_id), 0, -1)
        keys = [self._item_key(thread_id, cid) for cid in ids]
        keys.append(self._index_key(thread_id))
        if not keys:
            return 0
        return int(await client.delete(*keys))


def _build_backend(config: CheckpointerConfig) -> _Backend:
    match config.backend:
        case CheckpointBackend.MEMORY:
            return MemoryBackend()
        case CheckpointBackend.REDIS:
            return RedisBackend(config)
        case _:  # pragma: no cover - 枚举穷举
            raise ValueError(f"未知的后端类型: {config.backend!r}")


class HarnessCheckpointer:
    """Harness 跨层检查点适配器。

    在 LangGraph 1.x 的 ``BaseCheckpointSaver`` 之上提供统一封装，
    可被 ``StateGraph.compile(checkpointer=...)`` 直接接入。本实现不
    强依赖 ``langgraph_checkpoint`` 包，未安装时也能独立使用。
    """

    def __init__(
        self,
        config: CheckpointerConfig | None = None,
        *,
        backend: _Backend | None = None,
    ) -> None:
        self._config = config or CheckpointerConfig()
        self._backend = backend or _build_backend(self._config)

    @property
    def backend(self) -> _Backend:
        """底层后端实例。"""
        return self._backend

    @property
    def config(self) -> CheckpointerConfig:
        """当前配置。"""
        return self._config

    # ------------------------------------------------------------------
    # 异步接口（与 LangGraph BaseCheckpointSaver 对齐）
    # ------------------------------------------------------------------
    async def aput(
        self,
        config: dict[str, Any],
        checkpoint: dict[str, Any],
        metadata: CheckpointMetadata | dict[str, Any] | None = None,
        new_versions: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """写入一个检查点并返回新的 config 字典（含 ``checkpoint_id``）。"""
        thread_id, ns, parent_id = self._extract_config(config)
        meta = self._normalize_metadata(metadata)
        record = CheckpointRecord(
            thread_id=thread_id,
            checkpoint_ns=ns,
            checkpoint=dict(checkpoint),
            metadata=meta,
            parent_checkpoint_id=parent_id,
        )
        await self._backend.aput(record)
        return {
            "configurable": {
                "thread_id": thread_id,
                "checkpoint_ns": ns,
                "checkpoint_id": record.checkpoint_id,
            }
        }

    async def aget_tuple(self, config: dict[str, Any]) -> CheckpointRecord | None:
        """获取指定 config 对应的检查点记录。"""
        thread_id, _, checkpoint_id = self._extract_config(config)
        return await self._backend.aget(thread_id, checkpoint_id)

    async def alist(
        self,
        config: dict[str, Any],
        *,
        limit: int | None = None,
    ) -> AsyncIterator[CheckpointRecord]:
        """异步遍历指定线程的检查点（按时间倒序）。"""
        thread_id, _, _ = self._extract_config(config)
        records = await self._backend.alist(thread_id, limit=limit)
        for record in records:
            yield record

    async def adelete_thread(self, thread_id: str) -> int:
        """删除指定线程下的全部检查点。"""
        return await self._backend.adelete(thread_id)

    # ------------------------------------------------------------------
    # 同步接口（由异步接口包装）
    # ------------------------------------------------------------------
    def put(
        self,
        config: dict[str, Any],
        checkpoint: dict[str, Any],
        metadata: CheckpointMetadata | dict[str, Any] | None = None,
        new_versions: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """同步版本的 :meth:`aput`。"""
        return _run_sync(self.aput(config, checkpoint, metadata, new_versions))

    def get_tuple(self, config: dict[str, Any]) -> CheckpointRecord | None:
        """同步版本的 :meth:`aget_tuple`。"""
        return _run_sync(self.aget_tuple(config))

    def list(
        self, config: dict[str, Any], *, limit: int | None = None
    ) -> Iterator[CheckpointRecord]:
        """同步版本的 :meth:`alist`。"""
        thread_id, _, _ = self._extract_config(config)
        records = _run_sync(self._backend.alist(thread_id, limit=limit))
        return iter(records)

    def delete_thread(self, thread_id: str) -> int:
        """同步版本的 :meth:`adelete_thread`。"""
        return _run_sync(self.adelete_thread(thread_id))

    # ------------------------------------------------------------------
    # 辅助方法
    # ------------------------------------------------------------------
    @staticmethod
    def _extract_config(
        config: dict[str, Any],
    ) -> tuple[str, str, str | None]:
        configurable = config.get("configurable", config)
        thread_id = configurable.get("thread_id")
        if not thread_id:
            raise KeyError("config 缺少 'thread_id'")
        ns = configurable.get("checkpoint_ns", "") or ""
        checkpoint_id = configurable.get("checkpoint_id")
        return str(thread_id), str(ns), checkpoint_id

    @staticmethod
    def _normalize_metadata(
        metadata: CheckpointMetadata | dict[str, Any] | None,
    ) -> CheckpointMetadata:
        if metadata is None:
            return CheckpointMetadata()
        if isinstance(metadata, CheckpointMetadata):
            return metadata
        return CheckpointMetadata.model_validate(metadata)


def _run_sync(coro: Any) -> Any:
    """在没有运行中事件循环时同步执行协程；否则抛出明确错误。"""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if loop is not None and loop.is_running():
        raise RuntimeError(
            "已存在运行中的事件循环，请使用对应的异步方法（aput/aget_tuple/...）"
        )
    return asyncio.run(coro)
