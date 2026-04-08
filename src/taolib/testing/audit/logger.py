"""审计日志记录器。

提供审计日志的记录功能，支持多种存储后端。
"""

import json
import logging
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

from .errors import AuditStorageError
from .models import AuditLog, AuditLogFilter, AuditLogResponse

if TYPE_CHECKING:
    from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)


@runtime_checkable
class AuditStorageProtocol(Protocol):
    """审计日志存储后端协议。

    定义审计日志存储后端需要实现的所有操作。
    """

    async def save(self, log: AuditLog) -> None:
        """保存审计日志。

        Args:
            log: 审计日志实例
        """
        ...

    async def save_batch(self, logs: Sequence[AuditLog]) -> None:
        """批量保存审计日志。

        Args:
            logs: 审计日志列表
        """
        ...

    async def query(self, filter_params: AuditLogFilter) -> list[AuditLogResponse]:
        """查询审计日志。

        Args:
            filter_params: 查询过滤器

        Returns:
            匹配的审计日志列表
        """
        ...

    async def count(self, filter_params: AuditLogFilter) -> int:
        """统计审计日志数量。

        Args:
            filter_params: 查询过滤器

        Returns:
            匹配的日志数量
        """
        ...

    async def delete_old_logs(self, before: datetime) -> int:
        """删除旧日志。

        Args:
            before: 删除此时间之前的日志

        Returns:
            删除的日志数量
        """
        ...


class InMemoryAuditStorage:
    """内存审计日志存储。

    适用于测试和开发环境。

    Attributes:
        _logs: 日志存储列表
        _max_size: 最大存储数量
    """

    def __init__(self, max_size: int = 10000) -> None:
        """初始化内存存储。

        Args:
            max_size: 最大存储数量，超过时删除最旧的日志
        """
        self._logs: list[AuditLog] = []
        self._max_size = max_size

    async def save(self, log: AuditLog) -> None:
        """保存审计日志。

        Args:
            log: 审计日志实例
        """
        self._logs.append(log)
        if len(self._logs) > self._max_size:
            self._logs = self._logs[-self._max_size :]

    async def save_batch(self, logs: Sequence[AuditLog]) -> None:
        """批量保存审计日志。

        Args:
            logs: 审计日志列表
        """
        self._logs.extend(logs)
        if len(self._logs) > self._max_size:
            self._logs = self._logs[-self._max_size :]

    async def query(self, filter_params: AuditLogFilter) -> list[AuditLogResponse]:
        """查询审计日志。

        Args:
            filter_params: 查询过滤器

        Returns:
            匹配的审计日志列表
        """
        results = []
        for log in reversed(self._logs):
            if self._match_filter(log, filter_params):
                results.append(AuditLogResponse.model_validate(log))
                if len(results) >= filter_params.limit:
                    break
        return results

    async def count(self, filter_params: AuditLogFilter) -> int:
        """统计审计日志数量。

        Args:
            filter_params: 查询过滤器

        Returns:
            匹配的日志数量
        """
        return sum(1 for log in self._logs if self._match_filter(log, filter_params))

    async def delete_old_logs(self, before: datetime) -> int:
        """删除旧日志。

        Args:
            before: 删除此时间之前的日志

        Returns:
            删除的日志数量
        """
        original_size = len(self._logs)
        self._logs = [log for log in self._logs if log.timestamp >= before]
        return original_size - len(self._logs)

    def _match_filter(self, log: AuditLog, filter_params: AuditLogFilter) -> bool:
        """检查日志是否匹配过滤器。

        Args:
            log: 审计日志
            filter_params: 过滤器

        Returns:
            是否匹配
        """
        if filter_params.user_id and log.user_id != filter_params.user_id:
            return False
        if filter_params.action and log.action != filter_params.action:
            return False
        if filter_params.resource_type and log.resource_type != filter_params.resource_type:
            return False
        if filter_params.resource_id and log.resource_id != filter_params.resource_id:
            return False
        if filter_params.status and log.status != filter_params.status:
            return False
        if filter_params.start_time and log.timestamp < filter_params.start_time:
            return False
        if filter_params.end_time and log.timestamp > filter_params.end_time:
            return False
        return not (filter_params.ip_address and log.ip_address != filter_params.ip_address)


class FileAuditStorage:
    """文件审计日志存储。

    将审计日志保存到 JSON 文件中。

    Attributes:
        _file_path: 日志文件路径
        _max_size: 最大存储数量
    """

    def __init__(self, file_path: str | Path, max_size: int = 100000) -> None:
        """初始化文件存储。

        Args:
            file_path: 日志文件路径
            max_size: 最大存储数量
        """
        self._file_path = Path(file_path)
        self._max_size = max_size
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """确保日志文件存在。"""
        self._file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self._file_path.exists():
            self._file_path.write_text("[]", encoding="utf-8")

    def _read_logs(self) -> list[AuditLog]:
        """读取所有日志。

        Returns:
            日志列表
        """
        try:
            content = self._file_path.read_text(encoding="utf-8")
            data = json.loads(content)
            return [AuditLog.model_validate(item) for item in data]
        except (json.JSONDecodeError, Exception):
            logger.exception("Failed to read audit logs from file")
            return []

    def _write_logs(self, logs: list[AuditLog]) -> None:
        """写入所有日志。

        Args:
            logs: 日志列表
        """
        data = [log.model_dump(mode="json") for log in logs]
        content = json.dumps(data, ensure_ascii=False, indent=2, default=str)
        self._file_path.write_text(content, encoding="utf-8")

    async def save(self, log: AuditLog) -> None:
        """保存审计日志。

        Args:
            log: 审计日志实例
        """
        logs = self._read_logs()
        logs.append(log)
        if len(logs) > self._max_size:
            logs = logs[-self._max_size :]
        self._write_logs(logs)

    async def save_batch(self, logs: Sequence[AuditLog]) -> None:
        """批量保存审计日志。

        Args:
            logs: 审计日志列表
        """
        existing_logs = self._read_logs()
        existing_logs.extend(logs)
        if len(existing_logs) > self._max_size:
            existing_logs = existing_logs[-self._max_size :]
        self._write_logs(existing_logs)

    async def query(self, filter_params: AuditLogFilter) -> list[AuditLogResponse]:
        """查询审计日志。

        Args:
            filter_params: 查询过滤器

        Returns:
            匹配的审计日志列表
        """
        logs = self._read_logs()
        results = []
        for log in reversed(logs):
            if self._match_filter(log, filter_params):
                results.append(AuditLogResponse.model_validate(log))
                if len(results) >= filter_params.limit:
                    break
        return results

    async def count(self, filter_params: AuditLogFilter) -> int:
        """统计审计日志数量。

        Args:
            filter_params: 查询过滤器

        Returns:
            匹配的日志数量
        """
        logs = self._read_logs()
        return sum(1 for log in logs if self._match_filter(log, filter_params))

    async def delete_old_logs(self, before: datetime) -> int:
        """删除旧日志。

        Args:
            before: 删除此时间之前的日志

        Returns:
            删除的日志数量
        """
        logs = self._read_logs()
        original_size = len(logs)
        logs = [log for log in logs if log.timestamp >= before]
        self._write_logs(logs)
        return original_size - len(logs)

    def _match_filter(self, log: AuditLog, filter_params: AuditLogFilter) -> bool:
        """检查日志是否匹配过滤器。"""
        if filter_params.user_id and log.user_id != filter_params.user_id:
            return False
        if filter_params.action and log.action != filter_params.action:
            return False
        if filter_params.resource_type and log.resource_type != filter_params.resource_type:
            return False
        if filter_params.resource_id and log.resource_id != filter_params.resource_id:
            return False
        if filter_params.status and log.status != filter_params.status:
            return False
        if filter_params.start_time and log.timestamp < filter_params.start_time:
            return False
        if filter_params.end_time and log.timestamp > filter_params.end_time:
            return False
        return not (filter_params.ip_address and log.ip_address != filter_params.ip_address)


class MongoDBAuditStorage:
    """MongoDB 审计日志存储。

    使用 MongoDB 作为审计日志存储后端。

    Attributes:
        _client: MongoDB 客户端
        _database_name: 数据库名称
        _collection_name: 集合名称
    """

    def __init__(
        self,
        client: AsyncIOMotorClient,
        database_name: str = "audit",
        collection_name: str = "logs",
    ) -> None:
        """初始化 MongoDB 存储。

        Args:
            client: Motor 异步 MongoDB 客户端
            database_name: 数据库名称
            collection_name: 集合名称
        """
        self._client = client
        self._database_name = database_name
        self._collection_name = collection_name
        self._collection = client[database_name][collection_name]

    async def save(self, log: AuditLog) -> None:
        """保存审计日志。

        Args:
            log: 审计日志实例
        """
        doc = log.model_dump(mode="json")
        doc["_id"] = str(log.id)
        try:
            await self._collection.insert_one(doc)
        except Exception as e:
            raise AuditStorageError(f"Failed to save audit log: {e}") from e

    async def save_batch(self, logs: Sequence[AuditLog]) -> None:
        """批量保存审计日志。

        Args:
            logs: 审计日志列表
        """
        if not logs:
            return
        docs = []
        for log in logs:
            doc = log.model_dump(mode="json")
            doc["_id"] = str(log.id)
            docs.append(doc)
        try:
            await self._collection.insert_many(docs)
        except Exception as e:
            raise AuditStorageError(f"Failed to save audit logs: {e}") from e

    async def query(self, filter_params: AuditLogFilter) -> list[AuditLogResponse]:
        """查询审计日志。

        Args:
            filter_params: 查询过滤器

        Returns:
            匹配的审计日志列表
        """
        query = self._build_query(filter_params)
        cursor = (
            self._collection.find(query)
            .sort("timestamp", -1)
            .skip(filter_params.offset)
            .limit(filter_params.limit)
        )
        results = []
        async for doc in cursor:
            doc["id"] = doc.pop("_id")
            results.append(AuditLogResponse.model_validate(doc))
        return results

    async def count(self, filter_params: AuditLogFilter) -> int:
        """统计审计日志数量。

        Args:
            filter_params: 查询过滤器

        Returns:
            匹配的日志数量
        """
        query = self._build_query(filter_params)
        return await self._collection.count_documents(query)

    async def delete_old_logs(self, before: datetime) -> int:
        """删除旧日志。

        Args:
            before: 删除此时间之前的日志

        Returns:
            删除的日志数量
        """
        result = await self._collection.delete_many({"timestamp": {"$lt": before}})
        return result.deleted_count

    async def create_indexes(self) -> None:
        """创建索引。"""
        await self._collection.create_index("timestamp")
        await self._collection.create_index("user_id")
        await self._collection.create_index("action")
        await self._collection.create_index("resource_type")
        await self._collection.create_index([("timestamp", -1), ("user_id", 1)])

    def _build_query(self, filter_params: AuditLogFilter) -> dict[str, Any]:
        """构建 MongoDB 查询条件。

        Args:
            filter_params: 过滤器

        Returns:
            MongoDB 查询字典
        """
        query: dict[str, Any] = {}
        if filter_params.user_id:
            query["user_id"] = filter_params.user_id
        if filter_params.action:
            query["action"] = filter_params.action.value
        if filter_params.resource_type:
            query["resource_type"] = filter_params.resource_type
        if filter_params.resource_id:
            query["resource_id"] = filter_params.resource_id
        if filter_params.status:
            query["status"] = filter_params.status.value
        if filter_params.ip_address:
            query["ip_address"] = filter_params.ip_address
        if filter_params.start_time or filter_params.end_time:
            query["timestamp"] = {}
            if filter_params.start_time:
                query["timestamp"]["$gte"] = filter_params.start_time
            if filter_params.end_time:
                query["timestamp"]["$lte"] = filter_params.end_time
        return query


class AuditLogger:
    """审计日志记录器。

    提供审计日志的记录功能，支持同步和异步操作。

    Attributes:
        _storage: 存储后端
        _default_user_id: 默认用户 ID
        _default_ip_address: 默认 IP 地址
    """

    def __init__(
        self,
        storage: AuditStorageProtocol,
        default_user_id: str | None = None,
        default_ip_address: str | None = None,
    ) -> None:
        """初始化审计日志记录器。

        Args:
            storage: 存储后端实例
            default_user_id: 默认用户 ID
            default_ip_address: 默认 IP 地址
        """
        self._storage = storage
        self._default_user_id = default_user_id
        self._default_ip_address = default_ip_address

    async def log(
        self,
        action: str,
        resource_type: str,
        resource_id: str | None = None,
        user_id: str | None = None,
        details: dict[str, Any] | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        status: str = "success",
        error_message: str | None = None,
    ) -> AuditLog:
        """记录审计日志。

        Args:
            action: 操作类型
            resource_type: 资源类型
            resource_id: 资源 ID
            user_id: 用户 ID
            details: 操作详情
            ip_address: IP 地址
            user_agent: User-Agent
            status: 操作状态
            error_message: 错误信息

        Returns:
            创建的审计日志实例
        """
        from .models import AuditAction, AuditStatus

        try:
            action_enum = AuditAction(action)
        except ValueError:
            action_enum = AuditAction.EXECUTE

        try:
            status_enum = AuditStatus(status)
        except ValueError:
            status_enum = AuditStatus.FAILED

        log_entry = AuditLog(
            user_id=user_id or self._default_user_id,
            action=action_enum,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
            ip_address=ip_address or self._default_ip_address,
            user_agent=user_agent,
            status=status_enum,
            error_message=error_message,
        )

        await self._storage.save(log_entry)
        logger.debug("Audit log saved: %s - %s", action, resource_type)

        return log_entry

    async def log_create(
        self,
        resource_type: str,
        resource_id: str,
        user_id: str | None = None,
        details: dict[str, Any] | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> AuditLog:
        """记录创建操作。

        Args:
            resource_type: 资源类型
            resource_id: 资源 ID
            user_id: 用户 ID
            details: 操作详情
            ip_address: IP 地址
            user_agent: User-Agent

        Returns:
            创建的审计日志实例
        """
        return await self.log(
            action="create",
            resource_type=resource_type,
            resource_id=resource_id,
            user_id=user_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
        )

    async def log_update(
        self,
        resource_type: str,
        resource_id: str,
        user_id: str | None = None,
        details: dict[str, Any] | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> AuditLog:
        """记录更新操作。

        Args:
            resource_type: 资源类型
            resource_id: 资源 ID
            user_id: 用户 ID
            details: 操作详情
            ip_address: IP 地址
            user_agent: User-Agent

        Returns:
            创建的审计日志实例
        """
        return await self.log(
            action="update",
            resource_type=resource_type,
            resource_id=resource_id,
            user_id=user_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
        )

    async def log_delete(
        self,
        resource_type: str,
        resource_id: str,
        user_id: str | None = None,
        details: dict[str, Any] | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> AuditLog:
        """记录删除操作。

        Args:
            resource_type: 资源类型
            resource_id: 资源 ID
            user_id: 用户 ID
            details: 操作详情
            ip_address: IP 地址
            user_agent: User-Agent

        Returns:
            创建的审计日志实例
        """
        return await self.log(
            action="delete",
            resource_type=resource_type,
            resource_id=resource_id,
            user_id=user_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
        )

    async def log_login(
        self,
        user_id: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
        success: bool = True,
        error_message: str | None = None,
    ) -> AuditLog:
        """记录登录操作。

        Args:
            user_id: 用户 ID
            ip_address: IP 地址
            user_agent: User-Agent
            success: 是否成功
            error_message: 错误信息

        Returns:
            创建的审计日志实例
        """
        return await self.log(
            action="login" if success else "login.failed",
            resource_type="session",
            resource_id=user_id,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            status="success" if success else "failed",
            error_message=error_message,
        )

    async def log_logout(
        self,
        user_id: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> AuditLog:
        """记录登出操作。

        Args:
            user_id: 用户 ID
            ip_address: IP 地址
            user_agent: User-Agent

        Returns:
            创建的审计日志实例
        """
        return await self.log(
            action="logout",
            resource_type="session",
            resource_id=user_id,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )

    async def query(self, filter_params: AuditLogFilter) -> list[AuditLogResponse]:
        """查询审计日志。

        Args:
            filter_params: 查询过滤器

        Returns:
            匹配的审计日志列表
        """
        return await self._storage.query(filter_params)

    async def count(self, filter_params: AuditLogFilter) -> int:
        """统计审计日志数量。

        Args:
            filter_params: 查询过滤器

        Returns:
            匹配的日志数量
        """
        return await self._storage.count(filter_params)

    async def delete_old_logs(self, days: int = 90) -> int:
        """删除旧日志。

        Args:
            days: 保留天数

        Returns:
            删除的日志数量
        """
        before = datetime.now(UTC).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        from datetime import timedelta

        before = before - timedelta(days=days)
        return await self._storage.delete_old_logs(before)


