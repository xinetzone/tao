"""数据同步测试 fixtures。"""

import pytest

from taolib.testing.data_sync.models import (
    FailureAction,
    SyncConnectionConfig,
    SyncJobCreate,
    SyncMode,
    SyncScope,
    SyncStatus,
)


@pytest.fixture
def sample_source_config() -> SyncConnectionConfig:
    """源数据库配置。"""
    return SyncConnectionConfig(
        mongo_url="mongodb://source:27017",
        database="source_db",
        collections=["users", "configs"],
    )


@pytest.fixture
def sample_target_config() -> SyncConnectionConfig:
    """目标数据库配置。"""
    return SyncConnectionConfig(
        mongo_url="mongodb://target:27017",
        database="target_db",
    )


@pytest.fixture
def sample_job_create(
    sample_source_config: SyncConnectionConfig,
    sample_target_config: SyncConnectionConfig,
) -> SyncJobCreate:
    """示例作业创建数据。"""
    return SyncJobCreate(
        name="test-sync-job",
        description="Test sync job",
        scope=SyncScope.DATABASE,
        mode=SyncMode.INCREMENTAL,
        source=sample_source_config,
        target=sample_target_config,
        batch_size=500,
        failure_action=FailureAction.SKIP,
        max_retries=3,
        tags=["test", "sync"],
    )


@pytest.fixture
def sample_sync_status() -> SyncStatus:
    """示例同步状态。"""
    return SyncStatus.PENDING



