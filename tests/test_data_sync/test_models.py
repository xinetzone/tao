"""数据同步模型测试。"""


import pytest

from taolib.data_sync.models import (
    FailureAction,
    SyncCheckpoint,
    SyncConnectionConfig,
    SyncJobCreate,
    SyncJobDocument,
    SyncMetrics,
    SyncMode,
    SyncScope,
    SyncStatus,
)


class TestEnums:
    """枚举测试。"""

    def test_sync_status_values(self) -> None:
        assert SyncStatus.PENDING == "pending"
        assert SyncStatus.RUNNING == "running"
        assert SyncStatus.COMPLETED == "completed"
        assert SyncStatus.FAILED == "failed"
        assert SyncStatus.CANCELLED == "cancelled"

    def test_sync_scope_values(self) -> None:
        assert SyncScope.CONFIG_CENTER == "config_center"
        assert SyncScope.DATABASE == "database"
        assert SyncScope.FULL == "full"

    def test_sync_mode_values(self) -> None:
        assert SyncMode.FULL == "full"
        assert SyncMode.INCREMENTAL == "incremental"

    def test_failure_action_values(self) -> None:
        assert FailureAction.SKIP == "skip"
        assert FailureAction.RETRY == "retry"
        assert FailureAction.ABORT == "abort"


class TestSyncConnectionConfig:
    """连接配置测试。"""

    def test_default_values(self) -> None:
        config = SyncConnectionConfig(database="test_db")
        assert config.mongo_url == "mongodb://localhost:27017"
        assert config.database == "test_db"
        assert config.collections is None

    def test_custom_values(self) -> None:
        config = SyncConnectionConfig(
            mongo_url="mongodb://custom:27017",
            database="custom_db",
            collections=["users", "configs"],
        )
        assert config.mongo_url == "mongodb://custom:27017"
        assert config.collections == ["users", "configs"]


class TestSyncJobCreate:
    """作业创建测试。"""

    def test_valid_job_create(
        self, sample_job_create: SyncJobCreate
    ) -> None:
        assert sample_job_create.name == "test-sync-job"
        assert sample_job_create.batch_size == 500
        assert sample_job_create.failure_action == FailureAction.SKIP

    def test_job_name_required(self) -> None:
        with pytest.raises(Exception):  # Pydantic 验证错误
            SyncJobCreate(
                name="",  # 空名称
                source=SyncConnectionConfig(database="src"),
                target=SyncConnectionConfig(database="tgt"),
            )


class TestSyncJobDocument:
    """作业文档测试。"""

    def test_to_response(self) -> None:
        doc = SyncJobDocument(
            id="test-job",
            name="Test Job",
            source=SyncConnectionConfig(database="src"),
            target=SyncConnectionConfig(database="tgt"),
            created_by="admin",
            updated_by="admin",
        )
        response = doc.to_response()
        assert response.id == "test-job"
        assert response.name == "Test Job"
        assert response.created_by == "admin"


class TestSyncMetrics:
    """指标测试。"""

    def test_default_values(self) -> None:
        metrics = SyncMetrics()
        assert metrics.total_extracted == 0
        assert metrics.total_transformed == 0
        assert metrics.total_loaded == 0
        assert metrics.total_failed == 0


class TestSyncCheckpoint:
    """检查点测试。"""

    def test_checkpoint_fields(self) -> None:
        checkpoint = SyncCheckpoint(
            id="job1:users",
            job_id="job1",
            collection_name="users",
            total_synced=100,
        )
        assert checkpoint.job_id == "job1"
        assert checkpoint.collection_name == "users"
        assert checkpoint.total_synced == 100
