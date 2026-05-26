"""任务路由。"""

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, Field

from ...errors import TaskNotFoundError
from ...models import TaskCreate, TaskPriority, TaskResponse, TaskStatus

router = APIRouter()

TASKSCHEDULE_MODULE_DESCRIPTION = """
任务队列 API 文档
任务队列 API 提供任务提交、查询和管理功能。

## 功能特性

- **任务提交**：支持异步任务提交和执行
- **优先级队列**：高/普通/低优先级
- **失败重试**：指数退避重试
- **幂等性**：支持幂等任务
- **任务标签**：任务分类和追踪
- **任务监控**：任务状态查询

## 任务状态

- `PENDING`: 等待执行
- `RUNNING`: 正在执行
- `COMPLETED`: 执行完成
- `FAILED`: 执行失败
- `CANCELLED`: 已取消
"""


def get_task_service(request: Request):
    """获取任务服务。"""
    from ...queue.redis_queue import RedisTaskQueue
    from ...repository.task_repo import TaskRepository
    from ...services.task_service import TaskService

    task_repo = TaskRepository(request.app.state.db.tasks)
    redis_queue = RedisTaskQueue(
        request.app.state.redis, request.app.state.redis_key_prefix
    )
    return TaskService(task_repo, redis_queue)


class TaskListResponse(BaseModel):
    """任务列表响应。"""

    items: list[TaskResponse]
    total: int


class SubmitTaskRequest(BaseModel):
    """提交任务请求。"""

    task_type: str = Field(..., description="任务类型")
    params: dict = Field(default_factory=dict, description="任务参数")
    priority: TaskPriority = Field(
        default=TaskPriority.NORMAL, description="任务优先级"
    )
    max_retries: int = Field(default=3, description="最大重试次数")
    retry_delays: list[int] = Field(
        default_factory=lambda: [60, 300, 900],
        description="重试延迟（秒）",
    )
    idempotency_key: str | None = Field(None, description="幂等键")
    tags: list[str] = Field(default_factory=list, description="标签")


class TaskActionResponse(BaseModel):
    """任务操作响应。"""

    task_id: str
    status: str
    message: str


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    request: Request,
    skip: int = 0,
    limit: int = 20,
    status: TaskStatus | None = None,
    task_type: str | None = None,
    priority: TaskPriority | None = None,
) -> TaskListResponse:
    """列出任务。"""
    service = get_task_service(request)
    items = await service.list_tasks(
        status=status,
        task_type=task_type,
        priority=priority,
        skip=skip,
        limit=limit,
    )
    return TaskListResponse(
        items=[item.to_response() for item in items],
        total=len(items),
    )


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(request: Request, task_id: str) -> TaskResponse:
    """获取任务详情。"""
    service = get_task_service(request)
    try:
        task = await service.get_task(task_id)
        return task.to_response()
    except TaskNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task not found: {task_id}",
        )


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def submit_task(request: Request, data: SubmitTaskRequest) -> TaskResponse:
    """提交新任务。"""
    service = get_task_service(request)

    task_create = TaskCreate(
        task_type=data.task_type,
        params=data.params,
        priority=data.priority,
        max_retries=data.max_retries,
        retry_delays=data.retry_delays,
        idempotency_key=data.idempotency_key,
        tags=data.tags,
    )

    try:
        task = await service.submit_task(task_create)
        return task.to_response()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.post("/{task_id}/retry", response_model=TaskResponse)
async def retry_task(request: Request, task_id: str) -> TaskResponse:
    """手动重试失败任务。"""
    service = get_task_service(request)
    try:
        task = await service.retry_task(task_id)
        return task.to_response()
    except TaskNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task not found: {task_id}",
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/{task_id}/cancel", response_model=TaskResponse)
async def cancel_task(request: Request, task_id: str) -> TaskResponse:
    """取消任务。"""
    service = get_task_service(request)
    try:
        task = await service.cancel_task(task_id)
        return task.to_response()
    except TaskNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task not found: {task_id}",
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(request: Request, task_id: str) -> None:
    """删除终态任务（仅 COMPLETED/FAILED/CANCELLED）。"""
    service = get_task_service(request)
    try:
        task = await service.get_task(task_id)
    except TaskNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task not found: {task_id}",
        )

    terminal_statuses = {TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED}
    if task.status not in terminal_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Can only delete terminal tasks. Current status: {task.status}",
        )

    from ...repository.task_repo import TaskRepository

    repo = TaskRepository(request.app.state.db.tasks)
    await repo.delete(task_id)


