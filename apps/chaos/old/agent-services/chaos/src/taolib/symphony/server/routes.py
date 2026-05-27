"""Symphony API 路由定义。

提供系统状态查询、单问题详情和即时轮询触发的 REST API。
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, HTTPException, Request

from ..observability.snapshot import SnapshotGenerator

api_router = APIRouter(prefix="/api/v1")


@api_router.get("/state")
async def get_state(request: Request) -> dict[str, Any]:
    """获取系统状态快照。

    返回运行中的 worker 列表、重试队列、令牌汇总和配置参数。
    如果编排器不可用，返回 snapshot_unavailable 错误。
    """
    orchestrator = request.app.state.orchestrator
    if orchestrator is None:
        return {
            "generated_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "error": {
                "code": "snapshot_unavailable",
                "message": "Orchestrator is unavailable",
            },
        }

    try:
        snapshot_generator = SnapshotGenerator()
        state = _get_orchestrator_state(orchestrator)
        if state is None:
            return {
                "generated_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "error": {
                    "code": "snapshot_unavailable",
                    "message": "Orchestrator state is unavailable",
                },
            }
        snapshot = snapshot_generator.generate(state)
        return snapshot.to_dict()
    except Exception:
        return {
            "generated_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "error": {
                "code": "snapshot_timeout",
                "message": "Snapshot timed out",
            },
        }


@api_router.get("/{issue_identifier}")
async def get_issue(issue_identifier: str, request: Request) -> dict[str, Any]:
    """获取单个问题的详情。

    在运行中 worker 和重试队列中查找匹配 issue_identifier 的条目，
    返回其完整详情。如果未找到，返回 404。

    Args:
        issue_identifier: 人类可读的问题标识（如 "PROJ-123"）。
    """
    orchestrator = request.app.state.orchestrator
    if orchestrator is None:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "orchestrator_unavailable",
                "message": "Orchestrator is unavailable",
            },
        )

    state = _get_orchestrator_state(orchestrator)
    if state is None:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "orchestrator_unavailable",
                "message": "Orchestrator state is unavailable",
            },
        )

    # 在 running 中查找
    running_entry = None
    for _issue_id, entry in state.running.items():
        if getattr(entry, "identifier", None) == issue_identifier:
            running_entry = entry
            break

    # 在 retry_attempts 中查找
    retry_entry = None
    for entry in state.retry_attempts.values():
        if getattr(entry, "identifier", None) == issue_identifier:
            retry_entry = entry
            break

    if running_entry is None and retry_entry is None:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "issue_not_found",
                "message": f"Issue '{issue_identifier}' not found",
            },
        )

    # 构建响应
    result: dict[str, Any] = {
        "issue_identifier": issue_identifier,
        "issue_id": _get_issue_id(running_entry, retry_entry),
        "status": _determine_issue_status(running_entry, retry_entry),
    }

    if running_entry is not None:
        result["running"] = {
            "turn_count": getattr(running_entry, "turn_count", 0),
            "session_id": getattr(running_entry, "session_id", None),
            "last_event": getattr(running_entry, "last_codex_event", None),
            "started_at": _format_datetime(getattr(running_entry, "started_at", None)),
            "tokens": {
                "input_tokens": getattr(running_entry, "codex_input_tokens", 0),
                "output_tokens": getattr(running_entry, "codex_output_tokens", 0),
                "total_tokens": getattr(running_entry, "codex_total_tokens", 0),
            },
        }

    if retry_entry is not None:
        result["retry"] = {
            "attempt": getattr(retry_entry, "attempt", 0),
            "error": getattr(retry_entry, "error", None),
        }

    return result


@api_router.post("/refresh", status_code=202)
async def trigger_refresh(request: Request) -> dict[str, Any]:
    """触发即时轮询。

    请求编排器立即执行一次轮询周期，而不是等待下一个定时触发。
    返回 202 Accepted 表示请求已被接受。

    如果编排器不可用，返回 503。
    """
    orchestrator = request.app.state.orchestrator
    if orchestrator is None:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "orchestrator_unavailable",
                "message": "Orchestrator is unavailable",
            },
        )

    # 尝试调用编排器的 request_refresh 方法
    if hasattr(orchestrator, "request_refresh"):
        result = orchestrator.request_refresh()
        if result is None or result == "unavailable":
            raise HTTPException(
                status_code=503,
                detail={
                    "code": "orchestrator_unavailable",
                    "message": "Orchestrator is unavailable",
                },
            )
        return {
            "status": "accepted",
            "requested_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }

    # 没有专用方法时，返回已接受
    return {
        "status": "accepted",
        "requested_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def _get_orchestrator_state(orchestrator: Any) -> Any:
    """从编排器实例获取运行时状态。

    支持多种编排器实现：
    - 有 get_state() 方法的编排器
    - 有 state 属性的编排器
    - 直接作为状态使用的编排器
    """
    if hasattr(orchestrator, "get_state"):
        return orchestrator.get_state()
    if hasattr(orchestrator, "state"):
        return orchestrator.state
    # 编排器自身就是状态
    if hasattr(orchestrator, "running"):
        return orchestrator
    return None


def _get_issue_id(running_entry: Any, retry_entry: Any) -> str | None:
    """从 running/retry 条目中提取 issue_id。"""
    if running_entry is not None:
        return getattr(running_entry, "issue_id", None)
    if retry_entry is not None:
        return getattr(retry_entry, "issue_id", None)
    return None


def _determine_issue_status(running_entry: Any, retry_entry: Any) -> str:
    """判断问题当前状态。"""
    if running_entry is not None:
        return "running"
    if retry_entry is not None:
        return "retrying"
    return "unknown"


def _format_datetime(value: Any) -> str | None:
    """将日期时间格式化为 ISO 8601。"""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%dT%H:%M:%SZ")
    if isinstance(value, str):
        return value
    return str(value)
