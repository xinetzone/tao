"""执行回放工具 - 录制 Agent 执行轨迹并支持变速 / 步进 / 跳转回放。

提供六类标准事件（节点进入/退出、边遍历、状态更新、工具调用、LLM 调用）
和 :class:`ReplayEngine`：

* :meth:`record` - 注入回调收集事件；
* :meth:`replay` / :meth:`areplay` - 顺序回放，支持速度倍率、断点、步进；
* :meth:`seek` - 跳转到指定步骤；
* :meth:`export` / :meth:`import_recording` - JSON 持久化。
"""

from __future__ import annotations

import asyncio
import json
import time
import uuid
from collections.abc import Awaitable, Callable, Iterable, Sequence
from enum import StrEnum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

__all__ = [
    "ExecutionRecording",
    "RecordedEvent",
    "ReplayCallback",
    "ReplayConfig",
    "ReplayEngine",
    "ReplayEventType",
    "ReplayMode",
]


class ReplayEventType(StrEnum):
    """回放事件类型。"""

    NODE_ENTER = "node_enter"
    NODE_EXIT = "node_exit"
    EDGE_TRAVERSE = "edge_traverse"
    STATE_UPDATE = "state_update"
    TOOL_CALL = "tool_call"
    LLM_CALL = "llm_call"


class ReplayMode(StrEnum):
    """回放模式。"""

    CONTINUOUS = "continuous"
    STEP = "step"
    BREAKPOINT = "breakpoint"


class RecordedEvent(BaseModel):
    """单条录制事件。"""

    model_config = ConfigDict(extra="allow")

    event_id: str = Field(default_factory=lambda: f"evt-{uuid.uuid4().hex[:10]}")
    type: ReplayEventType
    timestamp: float = Field(default_factory=time.time)
    payload: dict[str, Any] = Field(default_factory=dict)
    thread_id: str | None = None
    node: str | None = None


class ExecutionRecording(BaseModel):
    """一次执行的事件序列录制。"""

    model_config = ConfigDict(extra="allow")

    recording_id: str = Field(default_factory=lambda: f"rec-{uuid.uuid4().hex[:10]}")
    started_at: float = Field(default_factory=time.time)
    finished_at: float | None = None
    events: list[RecordedEvent] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def duration_seconds(self) -> float:
        """录制总时长（秒）。"""
        end = self.finished_at if self.finished_at is not None else time.time()
        return max(0.0, end - self.started_at)

    def append(self, event: RecordedEvent) -> None:
        """追加一条事件。"""
        self.events.append(event)


class ReplayConfig(BaseModel):
    """回放配置。"""

    model_config = ConfigDict(extra="allow")

    speed: float = Field(default=1.0, gt=0)
    breakpoints: list[int] = Field(
        default_factory=list, description="断点的事件下标列表"
    )
    mode: ReplayMode = ReplayMode.CONTINUOUS
    start_index: int = 0
    end_index: int | None = None
    preserve_timing: bool = True


type ReplayCallback = Callable[[int, RecordedEvent], Awaitable[None] | None]
"""回放回调签名：``(事件下标, 事件) -> None``。"""


class _Recorder:
    """与 :meth:`ReplayEngine.record` 配合的回调投递器。"""

    def __init__(self, recording: ExecutionRecording) -> None:
        self._recording = recording

    def emit(
        self,
        event_type: ReplayEventType | str,
        payload: dict[str, Any] | None = None,
        *,
        thread_id: str | None = None,
        node: str | None = None,
    ) -> RecordedEvent:
        kind = (
            ReplayEventType(event_type) if isinstance(event_type, str) else event_type
        )
        event = RecordedEvent(
            type=kind,
            payload=payload or {},
            thread_id=thread_id,
            node=node,
        )
        self._recording.append(event)
        return event

    @property
    def recording(self) -> ExecutionRecording:
        """已录制的执行序列。"""
        return self._recording


class ReplayEngine:
    """执行回放引擎。"""

    def __init__(self) -> None:
        self._loaded: dict[str, ExecutionRecording] = {}

    # ------------------------------------------------------------------
    # 录制
    # ------------------------------------------------------------------
    def record(
        self,
        execution: Callable[[_Recorder], Awaitable[Any] | Any] | None = None,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> _Recorder | ExecutionRecording:
        """录制执行过程。

        两种用法：

        * 不传 ``execution``，返回 :class:`_Recorder` 由调用方主动调用 ``emit``；
        * 传入 ``execution``，由引擎驱动其执行，期间通过回调收集事件，
          返回最终的 :class:`ExecutionRecording`。
        """
        recording = ExecutionRecording(metadata=metadata or {})
        recorder = _Recorder(recording)
        if execution is None:
            return recorder

        result = execution(recorder)
        if isinstance(result, Awaitable):
            asyncio.get_event_loop().run_until_complete(result)
        recording.finished_at = time.time()
        return recording

    async def arecord(
        self,
        execution: Callable[[_Recorder], Awaitable[Any]],
        *,
        metadata: dict[str, Any] | None = None,
    ) -> ExecutionRecording:
        """异步录制：等待 ``execution`` 协程完成后冻结录制。"""
        recording = ExecutionRecording(metadata=metadata or {})
        recorder = _Recorder(recording)
        await execution(recorder)
        recording.finished_at = time.time()
        return recording

    # ------------------------------------------------------------------
    # 回放
    # ------------------------------------------------------------------
    def replay(
        self,
        recording: ExecutionRecording,
        config: ReplayConfig | None = None,
        *,
        callback: ReplayCallback | None = None,
    ) -> list[RecordedEvent]:
        """同步回放（在新事件循环中运行 :meth:`areplay`）。"""
        return asyncio.run(self.areplay(recording, config, callback=callback))

    async def areplay(
        self,
        recording: ExecutionRecording,
        config: ReplayConfig | None = None,
        *,
        callback: ReplayCallback | None = None,
        step_signal: asyncio.Event | None = None,
    ) -> list[RecordedEvent]:
        """异步回放，可被 ``step_signal`` 控制单步步进。"""
        cfg = config or ReplayConfig()
        events = recording.events
        end = cfg.end_index if cfg.end_index is not None else len(events)
        played: list[RecordedEvent] = []
        breakpoints = set(cfg.breakpoints)
        previous_ts: float | None = None

        for idx in range(cfg.start_index, end):
            event = events[idx]
            await self._wait_pacing(event, previous_ts, cfg)
            previous_ts = event.timestamp

            if callback is not None:
                outcome = callback(idx, event)
                if isinstance(outcome, Awaitable):
                    await outcome
            played.append(event)

            should_pause = cfg.mode == ReplayMode.STEP or (
                cfg.mode == ReplayMode.BREAKPOINT and idx in breakpoints
            )
            if should_pause and step_signal is not None:
                await step_signal.wait()
                step_signal.clear()
        return played

    @staticmethod
    async def _wait_pacing(
        event: RecordedEvent,
        previous_ts: float | None,
        cfg: ReplayConfig,
    ) -> None:
        if not cfg.preserve_timing or previous_ts is None:
            return
        delta = event.timestamp - previous_ts
        if delta <= 0:
            return
        wait = delta / cfg.speed
        if wait > 0:
            await asyncio.sleep(wait)

    # ------------------------------------------------------------------
    # 跳转 / 导入导出
    # ------------------------------------------------------------------
    @staticmethod
    def seek(recording: ExecutionRecording, step_index: int) -> RecordedEvent:
        """跳转到指定下标的事件并返回该事件。"""
        if not recording.events:
            raise IndexError("录制为空，无法跳转")
        if step_index < 0:
            step_index += len(recording.events)
        if step_index < 0 or step_index >= len(recording.events):
            raise IndexError(f"step_index 越界: {step_index}")
        return recording.events[step_index]

    @staticmethod
    def export(
        recording: ExecutionRecording,
        path: str | Path | None = None,
        *,
        format: str = "json",
    ) -> str:
        """导出录制为 JSON 字符串；若提供 ``path`` 则同时落盘。"""
        if format != "json":
            raise ValueError(f"暂不支持的导出格式: {format!r}")
        text = recording.model_dump_json(indent=2)
        if path is not None:
            target = Path(path)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8")
        return text

    def import_recording(self, path: str | Path) -> ExecutionRecording:
        """从 JSON 文件导入录制并缓存。"""
        target = Path(path)
        if not target.exists():
            raise FileNotFoundError(f"录制文件不存在: {target}")
        data = json.loads(target.read_text(encoding="utf-8"))
        recording = ExecutionRecording.model_validate(data)
        self._loaded[recording.recording_id] = recording
        return recording

    @property
    def loaded(self) -> dict[str, ExecutionRecording]:
        """已导入的录制集合。"""
        return dict(self._loaded)

    @staticmethod
    def filter_events(
        recording: ExecutionRecording,
        *,
        types: Iterable[ReplayEventType | str] | None = None,
        nodes: Iterable[str] | None = None,
    ) -> list[RecordedEvent]:
        """按类型 / 节点过滤事件。"""
        type_set = (
            {ReplayEventType(t) if isinstance(t, str) else t for t in types}
            if types is not None
            else None
        )
        node_set = set(nodes) if nodes is not None else None
        result: list[RecordedEvent] = []
        for event in recording.events:
            if type_set is not None and event.type not in type_set:
                continue
            if node_set is not None and event.node not in node_set:
                continue
            result.append(event)
        return result

    @staticmethod
    def merge(recordings: Sequence[ExecutionRecording]) -> ExecutionRecording:
        """按时间戳合并多个录制为一份。"""
        merged = ExecutionRecording(
            metadata={"merged_from": [r.recording_id for r in recordings]}
        )
        events: list[RecordedEvent] = []
        for rec in recordings:
            events.extend(rec.events)
        events.sort(key=lambda e: e.timestamp)
        merged.events = events
        if recordings:
            merged.started_at = min(r.started_at for r in recordings)
            merged.finished_at = max(
                (r.finished_at or r.started_at) for r in recordings
            )
        return merged
