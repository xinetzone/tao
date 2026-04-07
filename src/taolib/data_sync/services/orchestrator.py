"""同步管道编排器。

核心 ETL 流程控制：Extract → Transform → Validate → Load
"""

import logging
from datetime import UTC, datetime
from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient

from taolib.data_sync.errors import (
    SyncAbortError,
    SyncConnectionError,
    SyncJobNotFoundError,
)
from taolib.data_sync.events.types import (
    SyncCompletedEvent,
    SyncFailedEvent,
    SyncStartedEvent,
)
from taolib.data_sync.models import (
    FailureAction,
    SyncJobDocument,
    SyncLogDocument,
    SyncLogResponse,
    SyncMetrics,
    SyncStatus,
)
from taolib.data_sync.pipeline.extractor import MongoExtractor
from taolib.data_sync.pipeline.loader import MongoLoader
from taolib.data_sync.pipeline.protocols import (
    LoadResult,
    TransformContext,
    TransformResult,
    ValidatorProtocol,
)
from taolib.data_sync.pipeline.transformer import TransformChain
from taolib.data_sync.pipeline.utils import truncate_snapshot
from taolib.data_sync.repository.checkpoint_repo import CheckpointRepository
from taolib.data_sync.repository.failure_repo import FailureRecordRepository
from taolib.data_sync.repository.job_repo import SyncJobRepository
from taolib.data_sync.repository.log_repo import SyncLogRepository

logger = logging.getLogger(__name__)


class SyncOrchestrator:
    """同步管道编排器。

    负责协调整个 ETL 流程：
    1. 加载作业配置
    2. 连接源/目标 MongoDB
    3. 执行 Extract → Transform → Validate → Load
    4. 更新检查点
    5. 记录日志和失败
    """

    def __init__(
        self,
        job_repo: SyncJobRepository,
        log_repo: SyncLogRepository,
        checkpoint_repo: CheckpointRepository,
        failure_repo: FailureRecordRepository,
        validator: ValidatorProtocol | None = None,
    ) -> None:
        """初始化。

        Args:
            job_repo: 作业 Repository
            log_repo: 日志 Repository
            checkpoint_repo: 检查点 Repository
            failure_repo: 失败记录 Repository
            validator: 可选的数据验证器
        """
        self._job_repo = job_repo
        self._log_repo = log_repo
        self._checkpoint_repo = checkpoint_repo
        self._failure_repo = failure_repo
        self._validator = validator

    async def run_job(self, job_id: str) -> SyncLogResponse:
        """运行同步作业。

        Args:
            job_id: 作业 ID

        Returns:
            同步日志响应

        Raises:
            SyncJobNotFoundError: 作业不存在或已禁用
        """
        # 1. 加载作业
        job = await self._job_repo.get_by_id(job_id)
        if job is None or not job.enabled:
            raise SyncJobNotFoundError(f"Job not found or disabled: {job_id}")

        # 2. 创建日志记录
        log_doc = await self._create_log(job)

        # 3. 发布开始事件
        started_event = SyncStartedEvent(
            job_id=job.id,
            job_name=job.name,
            mode=job.mode,
            timestamp=datetime.now(UTC),
        )
        logger.info("sync.started: %s", started_event.to_dict())

        # 4. 执行 ETL
        try:
            await self._execute_etl(job, log_doc)
        except Exception as e:
            await self._fail_log(log_doc.id, str(e))

            # 发布失败事件
            failed_event = SyncFailedEvent(
                job_id=job.id,
                job_name=job.name,
                log_id=log_doc.id,
                error_message=str(e),
                timestamp=datetime.now(UTC),
            )
            logger.error("sync.failed: %s", failed_event.to_dict())
            raise

        # 5. 发布完成事件
        log = await self._log_repo.get_by_id(log_doc.id)
        if log:
            completed_event = SyncCompletedEvent(
                job_id=job.id,
                job_name=job.name,
                log_id=log_doc.id,
                status=SyncStatus.COMPLETED,
                metrics=log.metrics.model_dump()
                if hasattr(log.metrics, "model_dump")
                else log.metrics,
                duration_seconds=log.duration_seconds or 0.0,
                timestamp=datetime.now(UTC),
            )
            logger.info("sync.completed: %s", completed_event.to_dict())
            return log.to_response()

        return SyncLogResponse(
            _id=log_doc.id,
            job_id=log_doc.job_id,
            job_name=log_doc.job_name,
            status=log_doc.status,
            mode=log_doc.mode,
            started_at=log_doc.started_at,
            finished_at=log_doc.finished_at,
            duration_seconds=log_doc.duration_seconds,
            source_database=log_doc.source_database,
            target_database=log_doc.target_database,
            collections_synced=log_doc.collections_synced,
            metrics=log_doc.metrics,
            error_message=log_doc.error_message,
            checkpoint_snapshot=log_doc.checkpoint_snapshot,
        )

    async def _execute_etl(
        self,
        job: SyncJobDocument,
        log_doc: SyncLogDocument,
    ) -> None:
        """执行 ETL 流程。"""
        start_time = datetime.now(UTC)

        # 连接源和目标
        try:
            source_client = AsyncIOMotorClient(job.source.mongo_url)
            target_client = AsyncIOMotorClient(job.target.mongo_url)
        except Exception as e:
            raise SyncConnectionError(f"Failed to connect: {e}") from e

        try:
            source_db = source_client[job.source.database]
            target_db = target_client[job.target.database]

            # 确定要同步的集合
            collections = (
                job.source.collections or await source_db.list_collection_names()
            )

            metrics = SyncMetrics()
            collections_synced: list[str] = []

            # 对每个集合执行 ETL
            for collection_name in collections:
                logger.info(
                    "开始同步集合: %s (job=%s)",
                    collection_name,
                    job.id,
                )
                result = await self._sync_collection(
                    source_db[collection_name],
                    target_db[collection_name],
                    collection_name,
                    job,
                    log_doc.id,
                )
                metrics.total_extracted += result["extracted"]
                metrics.total_transformed += result["transformed"]
                metrics.total_loaded += result["loaded"]
                metrics.total_failed += result["failed"]
                metrics.total_skipped += result["skipped"]
                collections_synced.append(collection_name)

                logger.info(
                    "集合 %s 同步完成: extracted=%d, transformed=%d, loaded=%d, failed=%d, skipped=%d",
                    collection_name,
                    result["extracted"],
                    result["transformed"],
                    result["loaded"],
                    result["failed"],
                    result["skipped"],
                )

                # 如果设置为 abort 且有失败，则中止
                if job.failure_action == FailureAction.ABORT and result["failed"] > 0:
                    raise SyncAbortError(
                        f"Aborted due to failures in {collection_name}"
                    )

            # 更新日志
            duration = (datetime.now(UTC) - start_time).total_seconds()
            await self._log_repo.update(
                log_doc.id,
                {
                    "status": SyncStatus.COMPLETED,
                    "finished_at": datetime.now(UTC),
                    "duration_seconds": duration,
                    "collections_synced": collections_synced,
                    "metrics": metrics.model_dump(),
                },
            )

            # 更新作业最后运行状态
            await self._job_repo.update_last_run(
                job.id, SyncStatus.COMPLETED, datetime.now(UTC)
            )

        finally:
            source_client.close()
            target_client.close()

    async def _sync_collection(
        self,
        source_collection: Any,
        target_collection: Any,
        collection_name: str,
        job: SyncJobDocument,
        log_id: str,
    ) -> dict[str, int]:
        """同步单个集合。

        Returns:
            统计字典
        """
        # 获取检查点
        checkpoint = await self._checkpoint_repo.get_or_create(job.id, collection_name)

        # 初始化 pipeline 组件
        extractor = MongoExtractor(batch_size=job.batch_size)
        transformer = TransformChain(
            field_mapping=job.field_mapping,
            transform_module_path=job.transform_module,
        )
        loader = MongoLoader()

        stats = {
            "extracted": 0,
            "transformed": 0,
            "loaded": 0,
            "failed": 0,
            "skipped": 0,
        }

        # 分批处理
        context = TransformContext(
            job_id=job.id,
            collection_name=collection_name,
            field_mapping=job.field_mapping,
        )

        async for batch in extractor.extract(
            source_collection,
            checkpoint,
            job.filter_query,
            job.batch_size,
        ):
            stats["extracted"] += len(batch)

            # ---- Transform ----
            transform_result = await transformer.transform(batch, context)
            stats["transformed"] += len(transform_result.transformed)

            # Transform 失败重试
            transform_failures = transform_result.failures
            if transform_failures and job.failure_action == FailureAction.RETRY:
                retry_result = await self._retry_transform(
                    batch,
                    transform_failures,
                    transformer,
                    context,
                    job.max_retries,
                )
                stats["transformed"] += len(retry_result.transformed)
                transform_result = TransformResult(
                    transformed=transform_result.transformed + retry_result.transformed,
                    failures=retry_result.failures,
                )
                transform_failures = retry_result.failures

            stats["failed"] += len(transform_failures)

            # 记录 transform 失败
            if transform_failures:
                await self._record_failures(
                    transform_failures,
                    job.id,
                    log_id,
                    collection_name,
                    "transform",
                )

            # ---- Validate ----
            docs_to_load = transform_result.transformed
            if self._validator and docs_to_load:
                validate_result = await self._validator.validate(
                    docs_to_load,
                    context,
                )
                stats["skipped"] += len(validate_result.failures)

                # 记录 validate 失败
                if validate_result.failures:
                    await self._record_failures(
                        validate_result.failures,
                        job.id,
                        log_id,
                        collection_name,
                        "validate",
                    )

                docs_to_load = validate_result.valid

            # ---- Load ----
            if docs_to_load:
                load_result = await loader.load(target_collection, docs_to_load)
                stats["loaded"] += load_result.inserted + load_result.updated

                # Load 失败重试
                load_failures = load_result.failures
                if load_result.failed > 0 and job.failure_action == FailureAction.RETRY:
                    retry_result = await self._retry_load(
                        docs_to_load,
                        load_failures,
                        loader,
                        target_collection,
                        job.max_retries,
                    )
                    stats["loaded"] += retry_result.inserted + retry_result.updated
                    load_failures = retry_result.failures
                    stats["failed"] += retry_result.failed
                else:
                    stats["failed"] += load_result.failed

                # 记录 load 失败
                if load_failures:
                    await self._record_load_failures(
                        load_failures,
                        docs_to_load,
                        job.id,
                        log_id,
                        collection_name,
                    )

            # 更新检查点
            if batch:
                last_doc = batch[-1]
                last_ts = last_doc.get("updated_at")
                await self._checkpoint_repo.update_checkpoint(
                    job.id,
                    collection_name,
                    last_ts or datetime.now(UTC),
                    last_doc["_id"],
                    len(batch),
                )

        return stats

    async def _retry_transform(
        self,
        original_batch: list[dict[str, Any]],
        failures: list[dict[str, Any]],
        transformer: TransformChain,
        context: TransformContext,
        max_retries: int,
    ) -> TransformResult:
        """对 transform 失败的文档进行重试。

        Args:
            original_batch: 原始文档批次
            failures: 失败记录列表
            transformer: 转换器实例
            context: 转换上下文
            max_retries: 最大重试次数

        Returns:
            重试后的转换结果
        """
        # 构建失败文档 ID 到原始文档的映射
        batch_map = {doc.get("_id"): doc for doc in original_batch}
        current_failures = failures
        all_success: list[dict[str, Any]] = []

        for attempt in range(1, max_retries + 1):
            failed_ids = {f.get("document_id") for f in current_failures}
            retry_docs = [
                batch_map[doc_id] for doc_id in failed_ids if doc_id in batch_map
            ]

            if not retry_docs:
                break

            logger.debug(
                "Transform 重试第 %d/%d 次, 文档数=%d",
                attempt,
                max_retries,
                len(retry_docs),
            )

            result = await transformer.transform(retry_docs, context)
            all_success.extend(result.transformed)
            current_failures = result.failures

            if not current_failures:
                break

        # 更新 retry_count
        for f in current_failures:
            f["retry_count"] = max_retries

        return TransformResult(transformed=all_success, failures=current_failures)

    async def _retry_load(
        self,
        docs_to_load: list[dict[str, Any]],
        failures: list[dict[str, Any]],
        loader: MongoLoader,
        target_collection: Any,
        max_retries: int,
    ) -> LoadResult:
        """对 load 失败的文档进行重试。

        Args:
            docs_to_load: 原始待加载文档
            failures: 失败记录列表
            loader: 加载器实例
            target_collection: 目标集合
            max_retries: 最大重试次数

        Returns:
            重试后的加载结果
        """
        doc_map = {doc.get("_id"): doc for doc in docs_to_load}
        current_failures = failures
        total_inserted = 0
        total_updated = 0

        for attempt in range(1, max_retries + 1):
            failed_ids = {f.get("document_id") for f in current_failures}
            retry_docs = [doc_map[doc_id] for doc_id in failed_ids if doc_id in doc_map]

            if not retry_docs:
                break

            logger.debug(
                "Load 重试第 %d/%d 次, 文档数=%d",
                attempt,
                max_retries,
                len(retry_docs),
            )

            result = await loader.load(target_collection, retry_docs)
            total_inserted += result.inserted
            total_updated += result.updated
            current_failures = result.failures

            if not current_failures:
                break

        return LoadResult(
            inserted=total_inserted,
            updated=total_updated,
            failed=len(current_failures),
            failures=current_failures,
        )

    async def _record_failures(
        self,
        failures: list[dict[str, Any]],
        job_id: str,
        log_id: str,
        collection_name: str,
        phase: str,
    ) -> None:
        """记录失败到 failure_repo。

        Args:
            failures: 失败记录列表
            job_id: 作业 ID
            log_id: 日志 ID
            collection_name: 集合名称
            phase: 失败阶段
        """
        failure_records = [
            {
                "_id": f"{log_id}:{collection_name}:{phase}:{i}",
                "job_id": job_id,
                "log_id": log_id,
                "collection_name": collection_name,
                "document_id": f.get("document_id", "unknown"),
                "phase": phase,
                "error_type": f.get("error_type", "Unknown"),
                "error_message": f.get("error_message", ""),
                "document_snapshot": f.get("document_snapshot"),
                "retry_count": f.get("retry_count", 0),
                "created_at": datetime.now(UTC),
            }
            for i, f in enumerate(failures)
        ]
        await self._failure_repo.bulk_create(failure_records)

    async def _record_load_failures(
        self,
        load_failures: list[dict[str, Any]],
        docs_to_load: list[dict[str, Any]],
        job_id: str,
        log_id: str,
        collection_name: str,
    ) -> None:
        """记录 load 阶段失败到 failure_repo。

        Args:
            load_failures: 加载失败记录列表
            docs_to_load: 待加载文档列表（用于快照）
            job_id: 作业 ID
            log_id: 日志 ID
            collection_name: 集合名称
        """
        doc_map = {doc.get("_id"): doc for doc in docs_to_load}
        failure_records = [
            {
                "_id": f"{log_id}:{collection_name}:load:{i}",
                "job_id": job_id,
                "log_id": log_id,
                "collection_name": collection_name,
                "document_id": f.get("document_id", "unknown"),
                "phase": "load",
                "error_type": f.get("error_type", "BulkWriteError"),
                "error_message": f.get("error_message", ""),
                "document_snapshot": truncate_snapshot(
                    doc_map.get(f.get("document_id"), {}),
                ),
                "retry_count": f.get("retry_count", 0),
                "created_at": datetime.now(UTC),
            }
            for i, f in enumerate(load_failures)
        ]
        await self._failure_repo.bulk_create(failure_records)

    async def _create_log(self, job: SyncJobDocument) -> SyncLogDocument:
        """创建日志记录。"""
        log_id = f"{job.id}:{datetime.now(UTC).isoformat()}"
        doc_data = {
            "_id": log_id,
            "job_id": job.id,
            "job_name": job.name,
            "status": SyncStatus.RUNNING,
            "mode": job.mode,
            "started_at": datetime.now(UTC),
            "source_database": job.source.database,
            "target_database": job.target.database,
            "collections_synced": [],
            "metrics": {},
        }
        created = await self._log_repo.create(doc_data)
        return created

    async def _fail_log(self, log_id: str, error_message: str) -> None:
        """标记日志失败。"""
        await self._log_repo.update(
            log_id,
            {
                "status": SyncStatus.FAILED,
                "finished_at": datetime.now(UTC),
                "error_message": error_message,
            },
        )
