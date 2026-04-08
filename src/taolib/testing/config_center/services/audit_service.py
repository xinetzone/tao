"""审计日志服务模块。

实现审计日志的异步写入和查询功能。
"""

from typing import Any

from ..models.audit import AuditLogResponse
from ..models.enums import AuditAction, AuditStatus
from ..repository.audit_repo import AuditLogRepository


class AuditService:
    """审计日志业务服务。"""

    def __init__(self, audit_repo: AuditLogRepository) -> None:
        """初始化审计服务。

        Args:
            audit_repo: 审计日志 Repository
        """
        self._audit_repo = audit_repo

    async def log_action(
        self,
        action: AuditAction,
        resource_type: str,
        resource_id: str,
        resource_key: str,
        actor_id: str,
        actor_name: str = "",
        actor_ip: str = "",
        old_value: Any = None,
        new_value: Any = None,
        metadata: dict[str, Any] | None = None,
        status: AuditStatus = AuditStatus.SUCCESS,
    ) -> AuditLogResponse:
        """记录审计日志。

        Args:
            action: 操作类型
            resource_type: 资源类型
            resource_id: 资源 ID
            resource_key: 资源标识
            actor_id: 操作人 ID
            actor_name: 操作人名称
            actor_ip: 操作人 IP
            old_value: 变更前值
            new_value: 变更后值
            metadata: 附加元数据
            status: 操作状态

        Returns:
            创建的审计日志响应
        """
        document = {
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "resource_key": resource_key,
            "actor_id": actor_id,
            "actor_name": actor_name,
            "actor_ip": actor_ip,
            "old_value": old_value,
            "new_value": new_value,
            "metadata": metadata or {},
            "status": status,
        }

        log = await self._audit_repo.create_log(document)
        return log.to_response()

    async def query_logs(
        self,
        resource_type: str | None = None,
        resource_id: str | None = None,
        actor_id: str | None = None,
        action: str | None = None,
        time_from=None,
        time_to=None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[AuditLogResponse]:
        """查询审计日志。

        Args:
            resource_type: 资源类型过滤
            resource_id: 资源 ID 过滤
            actor_id: 操作人 ID 过滤
            action: 操作类型过滤
            time_from: 起始时间
            time_to: 结束时间
            skip: 跳过记录数
            limit: 限制记录数

        Returns:
            审计日志响应列表
        """
        logs = await self._audit_repo.query_logs(
            resource_type=resource_type,
            resource_id=resource_id,
            actor_id=actor_id,
            action=action,
            time_from=time_from,
            time_to=time_to,
            skip=skip,
            limit=limit,
        )
        return [log.to_response() for log in logs]


