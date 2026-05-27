"""统计路由。"""

from typing import Any

from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter()


class StatsResponse(BaseModel):
    """统计响应。"""

    total_tasks: int
    pending: int
    running: int
    completed: int
    failed: int
    retrying: int
    queue_high: int
    queue_normal: int
    queue_low: int
    total_submitted: int
    total_completed: int
    total_failed: int
    total_retried: int


class QueueDepthsResponse(BaseModel):
    """队列深度响应。"""

    high: int
    normal: int
    low: int


@router.get("", response_model=StatsResponse)
async def get_stats(request: Request) -> StatsResponse:
    """获取全局统计信息。"""
    from ...queue.redis_queue import RedisTaskQueue
    from ...repository.task_repo import TaskRepository
    from ...services.task_service import TaskService

    task_repo = TaskRepository(request.app.state.db.tasks)
    redis_queue = RedisTaskQueue(
        request.app.state.redis, request.app.state.redis_key_prefix
    )
    service = TaskService(task_repo, redis_queue)
    stats: dict[str, Any] = await service.get_stats()
    return StatsResponse(**stats)


@router.get("/queue-depths", response_model=QueueDepthsResponse)
async def get_queue_depths(request: Request) -> QueueDepthsResponse:
    """获取各优先级队列深度。"""
    from ...queue.redis_queue import RedisTaskQueue

    redis_queue = RedisTaskQueue(
        request.app.state.redis, request.app.state.redis_key_prefix
    )
    depths = await redis_queue.get_queue_lengths()
    return QueueDepthsResponse(**depths)
