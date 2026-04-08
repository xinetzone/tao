"""SyncOrchestrator 集成测试。"""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from taolib.testing.data_sync.errors import SyncJobNotFoundError
from taolib.testing.data_sync.models import (
    FailureAction,
    SyncConnectionConfig,
    SyncJobCreate,
    SyncJobDocument,
    SyncLogDocument,
    SyncMetrics,
    SyncMode,
    SyncScope,
    SyncStatus,
)
from taolib.testing.data_sync.services.orchestrator import SyncOrchestrator


def create_sample_job(
    job_id: str = "test-job-1",
    name: str = "test-sync-job",
    enabled: bool = True,
) -> SyncJobDocument:
    """创建示例作业文档。"""
    job_create = SyncJobCreate(
        name=name,
        description="Test sync job",
        scope=SyncScope.DATABASE,
        mode=SyncMode.INCREMENTAL,
        source=SyncConnectionConfig(
            mongo_url="mongodb://source:27017",
            database="source_db",
            collections=["users"],
        ),
        target=SyncConnectionConfig(
            mongo_url="mongodb://target:27017",
            database="target_db",
        ),
        batch_size=100,
        failure_action=FailureAction.SKIP,
    )
    return SyncJobDocument(
        _id=job_id,
        name=job_create.name,
        description=job_create.description,
        scope=job_create.scope,
        mode=job_create.mode,
        source=job_create.source,
        target=job_create.target,
        field_mapping={},
        filter_query=None,
        transform_module=None,
        batch_size=job_create.batch_size,
        failure_action=job_create.failure_action,
        enabled=enabled,
        max_retries=3,
        schedule_cron=None,
        tags=["test"],
        created_by="test",
        updated_by="test",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


def create_sample_log(
    log_id: str = "test-job-1:2024-01-01T00:00:00Z",
    job_id: str = "test-job-1",
) -> SyncLogDocument:
    """创建示例日志文档。"""
    return SyncLogDocument(
        _id=log_id,
        job_id=job_id,
        job_name="test-sync-job",
        status=SyncStatus.RUNNING,
        mode=SyncMode.INCREMENTAL,
        started_at=datetime.now(UTC),
        source_database="source_db",
        target_database="target_db",
        collections_synced=[],
        metrics=SyncMetrics().model_dump(),
        finished_at=None,
        duration_seconds=None,
        error_message=None,
        checkpoint_snapshot=None,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


class TestSyncOrchestrator:
    """SyncOrchestrator 测试。"""

    @pytest.fixture
    def mock_job_repo(self) -> MagicMock:
        """Mock 作业 Repository。"""
        return MagicMock()

    @pytest.fixture
    def mock_log_repo(self) -> MagicMock:
        """Mock 日志 Repository。"""
        return MagicMock()

    @pytest.fixture
    def mock_checkpoint_repo(self) -> MagicMock:
        """Mock 检查点 Repository。"""
        return MagicMock()

    @pytest.fixture
    def mock_failure_repo(self) -> MagicMock:
        """Mock 失败记录 Repository。"""
        return MagicMock()

    @pytest.fixture
    def orchestrator(
        self,
        mock_job_repo: MagicMock,
        mock_log_repo: MagicMock,
        mock_checkpoint_repo: MagicMock,
        mock_failure_repo: MagicMock,
    ) -> SyncOrchestrator:
        """创建 Orchestrator 实例。"""
        return SyncOrchestrator(
            job_repo=mock_job_repo,
            log_repo=mock_log_repo,
            checkpoint_repo=mock_checkpoint_repo,
            failure_repo=mock_failure_repo,
        )

    def test_init(
        self,
        orchestrator: SyncOrchestrator,
        mock_job_repo: MagicMock,
        mock_log_repo: MagicMock,
        mock_checkpoint_repo: MagicMock,
        mock_failure_repo: MagicMock,
    ) -> None:
        """测试初始化。"""
        assert orchestrator._job_repo == mock_job_repo
        assert orchestrator._log_repo == mock_log_repo
        assert orchestrator._checkpoint_repo == mock_checkpoint_repo
        assert orchestrator._failure_repo == mock_failure_repo

    @pytest.mark.asyncio
    async def test_run_job_not_found(
        self,
        orchestrator: SyncOrchestrator,
        mock_job_repo: MagicMock,
    ) -> None:
        """测试作业不存在时抛出异常。"""
        mock_job_repo.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(SyncJobNotFoundError):
            await orchestrator.run_job("nonexistent-job")

    @pytest.mark.asyncio
    async def test_run_job_disabled(
        self,
        orchestrator: SyncOrchestrator,
        mock_job_repo: MagicMock,
    ) -> None:
        """测试禁用的作业抛出异常。"""
        disabled_job = create_sample_job(enabled=False)
        mock_job_repo.get_by_id = AsyncMock(return_value=disabled_job)

        with pytest.raises(SyncJobNotFoundError):
            await orchestrator.run_job("test-job-1")

    @pytest.mark.asyncio
    async def test_run_job_success(
        self,
        orchestrator: SyncOrchestrator,
        mock_job_repo: MagicMock,
        mock_log_repo: MagicMock,
        mock_checkpoint_repo: MagicMock,
        mock_failure_repo: MagicMock,
    ) -> None:
        """测试成功执行作业。"""
        job = create_sample_job()
        log = create_sample_log()
        checkpoint = MagicMock()
        checkpoint.last_synced_timestamp = None

        # Mock repositories
        mock_job_repo.get_by_id = AsyncMock(return_value=job)
        mock_log_repo.create = AsyncMock(return_value=log)
        mock_log_repo.update = AsyncMock(return_value=MagicMock())
        mock_log_repo.get_by_id = AsyncMock(return_value=log)
        mock_checkpoint_repo.get_or_create = AsyncMock(return_value=checkpoint)
        mock_checkpoint_repo.update_checkpoint = AsyncMock(return_value=MagicMock())
        mock_failure_repo.bulk_create = AsyncMock(return_value=0)
        mock_job_repo.update_last_run = AsyncMock(return_value=MagicMock())

        # Mock MongoDB clients
        mock_source_collection = MagicMock()
        mock_target_collection = MagicMock()

        # Mock cursor with async iterator
        mock_cursor = MagicMock()
        mock_cursor.__aiter__ = lambda self: self
        mock_cursor.__anext__ = AsyncMock(
            side_effect=[
                {"_id": "1", "updated_at": datetime.now(UTC)},
                StopAsyncIteration(),
            ]
        )

        mock_source_collection.find.return_value.sort.return_value = mock_cursor

        mock_source_db = MagicMock()
        mock_source_db.__getitem__ = MagicMock(return_value=mock_source_collection)
        mock_source_db.list_collection_names = AsyncMock(return_value=["users"])

        mock_target_db = MagicMock()
        mock_target_db.__getitem__ = MagicMock(return_value=mock_target_collection)

        mock_source_client = MagicMock()
        mock_source_client.__getitem__ = MagicMock(return_value=mock_source_db)

        mock_target_client = MagicMock()
        mock_target_client.__getitem__ = MagicMock(return_value=mock_target_db)

        # Mock bulk_write result
        mock_bulk_result = MagicMock()
        mock_bulk_result.inserted = 1
        mock_bulk_result.updated = 0
        mock_bulk_result.failed = 0
        mock_target_collection.bulk_write = AsyncMock(return_value=mock_bulk_result)

        with patch(
            "taolib.testing.data_sync.services.orchestrator.AsyncIOMotorClient"
        ) as mock_client:
            mock_client.side_effect = [mock_source_client, mock_target_client]

            result = await orchestrator.run_job("test-job-1")

        assert result.job_id == "test-job-1"
        assert mock_log_repo.create.called
        assert mock_job_repo.update_last_run.called

    @pytest.mark.asyncio
    async def test_run_job_with_connection_error(
        self,
        orchestrator: SyncOrchestrator,
        mock_job_repo: MagicMock,
        mock_log_repo: MagicMock,
    ) -> None:
        """测试连接错误时抛出异常。"""
        from taolib.testing.data_sync.errors import SyncConnectionError

        job = create_sample_job()
        log = create_sample_log()

        mock_job_repo.get_by_id = AsyncMock(return_value=job)
        mock_log_repo.create = AsyncMock(return_value=log)
        mock_log_repo.update = AsyncMock(return_value=MagicMock())

        with patch(
            "taolib.testing.data_sync.services.orchestrator.AsyncIOMotorClient"
        ) as mock_client:
            mock_client.side_effect = Exception("Connection refused")

            with pytest.raises(SyncConnectionError):
                await orchestrator.run_job("test-job-1")


class TestSyncOrchestratorExecuteETL:
    """ETL 执行流程测试。"""

    @pytest.fixture
    def mock_job_repo(self) -> MagicMock:
        repo = MagicMock()
        repo.update_last_run = AsyncMock(return_value=MagicMock())
        return repo

    @pytest.fixture
    def mock_log_repo(self) -> MagicMock:
        repo = MagicMock()
        repo.create = AsyncMock(return_value=MagicMock())
        repo.update = AsyncMock(return_value=MagicMock())
        return repo

    @pytest.fixture
    def mock_checkpoint_repo(self) -> MagicMock:
        repo = MagicMock()
        repo.get_or_create = AsyncMock(return_value=MagicMock())
        repo.update_checkpoint = AsyncMock(return_value=MagicMock())
        return repo

    @pytest.fixture
    def mock_failure_repo(self) -> MagicMock:
        repo = MagicMock()
        repo.bulk_create = AsyncMock(return_value=0)
        return repo

    @pytest.fixture
    def orchestrator(
        self,
        mock_job_repo: MagicMock,
        mock_log_repo: MagicMock,
        mock_checkpoint_repo: MagicMock,
        mock_failure_repo: MagicMock,
    ) -> SyncOrchestrator:
        return SyncOrchestrator(
            job_repo=mock_job_repo,
            log_repo=mock_log_repo,
            checkpoint_repo=mock_checkpoint_repo,
            failure_repo=mock_failure_repo,
        )

    @pytest.mark.asyncio
    async def test_execute_etl_empty_collection(
        self,
        orchestrator: SyncOrchestrator,
        mock_job_repo: MagicMock,
        mock_log_repo: MagicMock,
        mock_checkpoint_repo: MagicMock,
        mock_failure_repo: MagicMock,
    ) -> None:
        """测试空集合处理。"""
        job = create_sample_job()
        log = create_sample_log()

        mock_log_repo.create = AsyncMock(return_value=log)
        mock_log_repo.update = AsyncMock(return_value=MagicMock())
        mock_job_repo.update_last_run = AsyncMock(return_value=MagicMock())

        # Mock empty cursor
        mock_cursor = MagicMock()
        mock_cursor.__aiter__ = lambda self: self
        mock_cursor.__anext__ = AsyncMock(side_effect=StopAsyncIteration())

        mock_source_collection = MagicMock()
        mock_source_collection.find.return_value.sort.return_value = mock_cursor

        mock_source_db = MagicMock()
        mock_source_db.__getitem__ = MagicMock(return_value=mock_source_collection)
        mock_source_db.list_collection_names = AsyncMock(return_value=["users"])

        mock_target_collection = MagicMock()

        mock_source_client = MagicMock()
        mock_source_client.__getitem__ = MagicMock(return_value=mock_source_db)
        mock_source_client.close = MagicMock()

        mock_target_client = MagicMock()
        mock_target_client.__getitem__ = MagicMock(return_value=mock_target_collection)
        mock_target_client.close = MagicMock()

        with patch(
            "taolib.testing.data_sync.services.orchestrator.AsyncIOMotorClient"
        ) as mock_client:
            mock_client.side_effect = [mock_source_client, mock_target_client]

            await orchestrator._execute_etl(job, log)

        # 验证日志更新被调用
        assert mock_log_repo.update.called
        # 验证客户端关闭
        mock_source_client.close.assert_called_once()
        mock_target_client.close.assert_called_once()


class TestSyncOrchestratorErrorHandling:
    """错误处理测试。"""

    @pytest.fixture
    def mock_job_repo(self) -> MagicMock:
        return MagicMock()

    @pytest.fixture
    def mock_log_repo(self) -> MagicMock:
        repo = MagicMock()
        repo.create = AsyncMock(return_value=MagicMock())
        repo.update = AsyncMock(return_value=MagicMock())
        return repo

    @pytest.fixture
    def mock_checkpoint_repo(self) -> MagicMock:
        return MagicMock()

    @pytest.fixture
    def mock_failure_repo(self) -> MagicMock:
        return MagicMock()

    @pytest.fixture
    def orchestrator(
        self,
        mock_job_repo: MagicMock,
        mock_log_repo: MagicMock,
        mock_checkpoint_repo: MagicMock,
        mock_failure_repo: MagicMock,
    ) -> SyncOrchestrator:
        return SyncOrchestrator(
            job_repo=mock_job_repo,
            log_repo=mock_log_repo,
            checkpoint_repo=mock_checkpoint_repo,
            failure_repo=mock_failure_repo,
        )

    @pytest.mark.asyncio
    async def test_create_log(self, orchestrator: SyncOrchestrator) -> None:
        """测试创建日志。"""
        job = create_sample_job()

        log = await orchestrator._create_log(job)

        assert orchestrator._log_repo.create.called
        call_args = orchestrator._log_repo.create.call_args[0][0]
        assert call_args["job_id"] == job.id
        assert call_args["job_name"] == job.name
        assert call_args["status"] == SyncStatus.RUNNING

    @pytest.mark.asyncio
    async def test_fail_log(self, orchestrator: SyncOrchestrator) -> None:
        """测试标记日志失败。"""
        await orchestrator._fail_log("log-123", "Test error message")

        assert orchestrator._log_repo.update.called
        call_args = orchestrator._log_repo.update.call_args
        assert call_args[0][0] == "log-123"
        update_data = call_args[0][1]
        assert update_data["status"] == SyncStatus.FAILED
        assert update_data["error_message"] == "Test error message"


class TestOrchestratorRetry:
    """重试机制测试。"""

    @pytest.fixture
    def mock_repos(self):
        return {
            "job_repo": MagicMock(),
            "log_repo": MagicMock(
                create=AsyncMock(return_value=MagicMock()),
                update=AsyncMock(return_value=MagicMock()),
            ),
            "checkpoint_repo": MagicMock(
                get_or_create=AsyncMock(
                    return_value=MagicMock(last_synced_timestamp=None)
                ),
                update_checkpoint=AsyncMock(return_value=MagicMock()),
            ),
            "failure_repo": MagicMock(
                bulk_create=AsyncMock(return_value=0),
            ),
        }

    @pytest.mark.asyncio
    async def test_retry_transform_recovers(self, mock_repos) -> None:
        """Transform 重试后恢复。"""
        from taolib.testing.data_sync.pipeline.protocols import (
            TransformContext,
            TransformResult,
        )
        from taolib.testing.data_sync.pipeline.transformer import TransformChain

        orchestrator = SyncOrchestrator(**mock_repos)

        # 第一次失败，第二次成功
        failures = [
            {"document_id": "2", "error_type": "ValueError", "error_message": "bad"}
        ]
        batch = [{"_id": "1"}, {"_id": "2"}]

        call_count = 0

        async def mock_transform(self, documents, context):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                # 第一次重试：doc "2" 仍然失败
                return TransformResult(
                    transformed=[],
                    failures=[
                        {
                            "document_id": "2",
                            "error_type": "ValueError",
                            "error_message": "bad",
                        }
                    ],
                )
            # 第二次重试：成功
            return TransformResult(transformed=[{"_id": "2"}], failures=[])

        with patch.object(TransformChain, "transform", mock_transform):
            transformer = TransformChain()
            context = TransformContext(job_id="j1", collection_name="c1")
            result = await orchestrator._retry_transform(
                batch,
                failures,
                transformer,
                context,
                max_retries=2,
            )

        assert len(result.transformed) == 1  # doc "2" recovered
        assert len(result.failures) == 0

    @pytest.mark.asyncio
    async def test_retry_exhausted_records_failures(self, mock_repos) -> None:
        """重试耗尽后记录失败。"""
        from taolib.testing.data_sync.pipeline.protocols import (
            TransformContext,
            TransformResult,
        )
        from taolib.testing.data_sync.pipeline.transformer import TransformChain

        orchestrator = SyncOrchestrator(**mock_repos)
        failures = [
            {"document_id": "2", "error_type": "ValueError", "error_message": "bad"}
        ]
        batch = [{"_id": "2"}]

        async def always_fail(self, documents, context):
            return TransformResult(
                transformed=[],
                failures=[
                    {
                        "document_id": "2",
                        "error_type": "ValueError",
                        "error_message": "bad",
                    }
                ],
            )

        with patch.object(TransformChain, "transform", always_fail):
            transformer = TransformChain()
            context = TransformContext(job_id="j1", collection_name="c1")
            result = await orchestrator._retry_transform(
                batch,
                failures,
                transformer,
                context,
                max_retries=2,
            )

        assert len(result.failures) == 1
        assert result.failures[0]["retry_count"] == 2


class TestOrchestratorValidation:
    """验证阶段测试。"""

    @pytest.mark.asyncio
    async def test_validator_filters_invalid_docs(self) -> None:
        """验证阶段过滤无效文档。"""
        from taolib.testing.data_sync.pipeline.protocols import TransformContext
        from taolib.testing.data_sync.pipeline.validator import DataValidator

        validator = DataValidator()
        validator.register(lambda doc, ctx: ["invalid"] if doc.get("bad") else [])

        mock_repos = {
            "job_repo": MagicMock(),
            "log_repo": MagicMock(
                create=AsyncMock(return_value=MagicMock()),
                update=AsyncMock(return_value=MagicMock()),
            ),
            "checkpoint_repo": MagicMock(
                get_or_create=AsyncMock(
                    return_value=MagicMock(last_synced_timestamp=None)
                ),
                update_checkpoint=AsyncMock(return_value=MagicMock()),
            ),
            "failure_repo": MagicMock(
                bulk_create=AsyncMock(return_value=0),
            ),
        }

        orchestrator = SyncOrchestrator(**mock_repos, validator=validator)
        assert orchestrator._validator is not None

        context = TransformContext(job_id="j1", collection_name="c1")
        result = await validator.validate(
            [{"_id": "1", "ok": True}, {"_id": "2", "bad": True}],
            context,
        )
        assert len(result.valid) == 1
        assert len(result.failures) == 1


class TestOrchestratorEvents:
    """事件发布测试。"""

    @pytest.mark.asyncio
    async def test_events_logged_on_success(self) -> None:
        """成功时记录开始和完成事件。"""
        job = create_sample_job()
        log = create_sample_log()

        mock_repos = {
            "job_repo": MagicMock(
                get_by_id=AsyncMock(return_value=job),
                update_last_run=AsyncMock(return_value=MagicMock()),
            ),
            "log_repo": MagicMock(
                create=AsyncMock(return_value=log),
                update=AsyncMock(return_value=MagicMock()),
                get_by_id=AsyncMock(return_value=log),
            ),
            "checkpoint_repo": MagicMock(
                get_or_create=AsyncMock(
                    return_value=MagicMock(last_synced_timestamp=None)
                ),
                update_checkpoint=AsyncMock(return_value=MagicMock()),
            ),
            "failure_repo": MagicMock(
                bulk_create=AsyncMock(return_value=0),
            ),
        }

        orchestrator = SyncOrchestrator(**mock_repos)

        # Mock empty cursor
        mock_cursor = MagicMock()
        mock_cursor.__aiter__ = lambda self: self
        mock_cursor.__anext__ = AsyncMock(side_effect=StopAsyncIteration())

        mock_source_collection = MagicMock()
        mock_source_collection.find.return_value.sort.return_value = mock_cursor

        mock_source_db = MagicMock()
        mock_source_db.__getitem__ = MagicMock(return_value=mock_source_collection)

        mock_target_db = MagicMock()
        mock_target_db.__getitem__ = MagicMock(return_value=MagicMock())

        mock_source_client = MagicMock()
        mock_source_client.__getitem__ = MagicMock(return_value=mock_source_db)
        mock_source_client.close = MagicMock()

        mock_target_client = MagicMock()
        mock_target_client.__getitem__ = MagicMock(return_value=mock_target_db)
        mock_target_client.close = MagicMock()

        with (
            patch(
                "taolib.testing.data_sync.services.orchestrator.AsyncIOMotorClient"
            ) as mock_client,
            patch("taolib.testing.data_sync.services.orchestrator.logger") as mock_logger,
        ):
            mock_client.side_effect = [mock_source_client, mock_target_client]

            await orchestrator.run_job("test-job-1")

        # 验证 started 和 completed 事件都被记录
        info_calls = [str(c) for c in mock_logger.info.call_args_list]
        assert any("sync.started" in c for c in info_calls)
        assert any("sync.completed" in c for c in info_calls)



