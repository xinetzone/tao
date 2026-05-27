"""同步作业路由。"""

from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, Field

from ...errors import SyncJobNotFoundError
from ...models import SyncJobCreate, SyncJobResponse, SyncStatus

router = APIRouter(tags=["Jobs"])


def get_job_repo(request: Request):
    """获取作业 Repository。"""
    from ...repository.job_repo import SyncJobRepository

    return SyncJobRepository(request.app.state.db.sync_jobs)


def get_orchestrator(request: Request):
    """获取编排器。"""
    from ...repository.checkpoint_repo import CheckpointRepository
    from ...repository.failure_repo import FailureRecordRepository
    from ...repository.log_repo import SyncLogRepository
    from ...services.orchestrator import SyncOrchestrator

    return SyncOrchestrator(
        job_repo=get_job_repo(request),
        log_repo=SyncLogRepository(request.app.state.db.sync_logs),
        checkpoint_repo=CheckpointRepository(request.app.state.db.sync_checkpoints),
        failure_repo=FailureRecordRepository(request.app.state.db.sync_failures),
    )


class JobListResponse(BaseModel):
    """作业列表响应。"""

    items: list[SyncJobResponse]
    total: int


class JobRunResponse(BaseModel):
    """作业运行响应。"""

    log_id: str
    status: str
    message: str


@router.get("", response_model=JobListResponse)
async def list_jobs(
    request: Request,
    skip: int = 0,
    limit: int = 20,
    enabled: bool | None = None,
) -> JobListResponse:
    """列出所有同步作业。"""
    repo = get_job_repo(request)

    if enabled is not None:
        if enabled:
            items = await repo.find_enabled_jobs()
        else:
            items = []
    else:
        items = await repo.find_all(skip=skip, limit=limit)

    total = len(items)  # 简化版，实际应使用 count
    return JobListResponse(
        items=[item.to_response() for item in items],
        total=total,
    )


@router.get("/{job_id}", response_model=SyncJobResponse)
async def get_job(request: Request, job_id: str) -> SyncJobResponse:
    """获取指定作业。"""
    repo = get_job_repo(request)
    job = await repo.get_by_id(job_id)

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job not found: {job_id}",
        )

    return job.to_response()


class CreateJobRequest(BaseModel):
    """创建作业请求。"""

    name: str = Field(..., description="作业名称")
    description: str | None = Field(None, description="作业描述")
    scope: str = Field(..., description="同步范围")
    mode: str = Field(..., description="同步模式")
    source: dict = Field(..., description="源数据库配置")
    target: dict = Field(..., description="目标数据库配置")
    batch_size: int = Field(100, description="批处理大小")
    failure_action: str = Field("skip", description="失败处理策略")
    schedule_cron: str | None = Field(None, description="Cron 表达式")
    tags: list[str] = Field(default_factory=list, description="标签")


@router.post("", response_model=SyncJobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(request: Request, data: CreateJobRequest) -> SyncJobResponse:
    """创建新的同步作业。"""
    repo = get_job_repo(request)

    # 检查名称是否已存在
    existing = await repo.find_by_name(data.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Job with name '{data.name}' already exists",
        )

    # 构建创建数据
    job_data = SyncJobCreate(
        name=data.name,
        description=data.description,
        scope=data.scope,
        mode=data.mode,
        source=data.source,
        target=data.target,
        batch_size=data.batch_size,
        failure_action=data.failure_action,
        schedule_cron=data.schedule_cron,
        tags=data.tags,
    )

    # 创建作业
    job_id = f"{data.name}:{datetime.now(UTC).isoformat()}"
    job = await repo.create(job_id, job_data.model_dump())

    return job.to_response()


class UpdateJobRequest(BaseModel):
    """更新作业请求。"""

    enabled: bool | None = None
    batch_size: int | None = None
    failure_action: str | None = None
    schedule_cron: str | None = None


@router.patch("/{job_id}", response_model=SyncJobResponse)
async def update_job(
    request: Request,
    job_id: str,
    data: UpdateJobRequest,
) -> SyncJobResponse:
    """更新同步作业。"""
    repo = get_job_repo(request)

    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update",
        )

    updated = await repo.update(job_id, update_data)

    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job not found: {job_id}",
        )

    return updated.to_response()


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(request: Request, job_id: str) -> None:
    """删除同步作业。"""
    repo = get_job_repo(request)
    deleted = await repo.delete(job_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job not found: {job_id}",
        )


@router.post("/{job_id}/run", response_model=JobRunResponse)
async def run_job(request: Request, job_id: str) -> JobRunResponse:
    """手动触发同步作业。"""
    orchestrator = get_orchestrator(request)

    try:
        log = await orchestrator.run_job(job_id)
        return JobRunResponse(
            log_id=log.id,
            status=log.status,
            message="Job completed successfully",
        )
    except SyncJobNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job not found or disabled: {job_id}",
        )
    except Exception as e:
        return JobRunResponse(
            log_id="",
            status=SyncStatus.FAILED,
            message=str(e),
        )
