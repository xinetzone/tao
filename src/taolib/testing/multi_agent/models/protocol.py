"""智能体间通信协议。

定义智能体之间通信的标准协议和消息格式。
"""

from datetime import UTC, datetime
from typing import Any
from enum import StrEnum
from uuid import uuid4

from pydantic import BaseModel, Field

from taolib.testing.multi_agent.models.enums import MessageType


class ProtocolVersion(StrEnum):
    """协议版本。"""

    V1 = "1.0.0"


class ProtocolHeader(BaseModel):
    """协议头部。"""

    version: ProtocolVersion = Field(default=ProtocolVersion.V1, description="协议版本")
    message_id: str = Field(default_factory=lambda: str(uuid4()), description="消息唯一标识")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC), description="消息时间戳")
    ttl: int = Field(default=30, description="消息生存时间（秒）", ge=1)


class ProtocolMessage(BaseModel):
    """协议消息。"""

    header: ProtocolHeader = Field(default_factory=ProtocolHeader, description="消息头部")
    message_type: MessageType = Field(default=MessageType.TEXT, description="消息类型")
    sender: str = Field(..., description="发送者标识", min_length=1, max_length=255)
    receiver: str | None = Field(default=None, description="接收者标识（None 表示广播）")
    body: dict[str, Any] = Field(default_factory=dict, description="消息体")
    metadata: dict[str, Any] = Field(default_factory=dict, description="元数据")

    def is_expired(self) -> bool:
        """检查消息是否已过期。"""
        now = datetime.now(UTC)
        age = (now - self.header.timestamp).total_seconds()
        return age > self.header.ttl

    def to_dict(self) -> dict[str, Any]:
        """转换为字典格式。"""
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ProtocolMessage":
        """从字典创建协议消息。"""
        return cls(**data)


class TaskRequestPayload(BaseModel):
    """任务请求载荷。"""

    task_id: str = Field(..., description="任务 ID")
    task_description: str = Field(..., description="任务描述")
    required_skills: list[str] = Field(default_factory=list, description="所需技能")
    parameters: dict[str, Any] = Field(default_factory=dict, description="任务参数")
    deadline: datetime | None = Field(default=None, description="截止时间")


class TaskResponsePayload(BaseModel):
    """任务响应载荷。"""

    task_id: str = Field(..., description="任务 ID")
    status: str = Field(..., description="任务状态")
    result: dict[str, Any] | None = Field(default=None, description="任务结果")
    error: str | None = Field(default=None, description="错误信息")
    progress: float = Field(default=0.0, description="进度（0-1）", ge=0.0, le=1.0)


class SkillRequestPayload(BaseModel):
    """技能请求载荷。"""

    skill_id: str = Field(..., description="技能 ID")
    skill_name: str = Field(..., description="技能名称")
    input_data: dict[str, Any] = Field(default_factory=dict, description="输入数据")


class SkillResponsePayload(BaseModel):
    """技能响应载荷。"""

    skill_id: str = Field(..., description="技能 ID")
    success: bool = Field(..., description="是否成功")
    output_data: dict[str, Any] | None = Field(default=None, description="输出数据")
    error: str | None = Field(default=None, description="错误信息")


class StatusUpdatePayload(BaseModel):
    """状态更新载荷。"""

    agent_id: str = Field(..., description="智能体 ID")
    status: str = Field(..., description="状态")
    current_task: str | None = Field(default=None, description="当前任务 ID")
    resources: dict[str, Any] = Field(default_factory=dict, description="资源使用情况")


class HeartbeatPayload(BaseModel):
    """心跳载荷。"""

    agent_id: str = Field(..., description="智能体 ID")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    load: float = Field(default=0.0, description="负载（0-1）", ge=0.0, le=1.0)
    status: str = Field(default="idle", description="状态")


def create_task_request(
    sender: str,
    receiver: str | None,
    task_id: str,
    task_description: str,
    required_skills: list[str] | None = None,
    parameters: dict[str, Any] | None = None,
    deadline: datetime | None = None,
) -> ProtocolMessage:
    """创建任务请求消息。"""
    payload = TaskRequestPayload(
        task_id=task_id,
        task_description=task_description,
        required_skills=required_skills or [],
        parameters=parameters or {},
        deadline=deadline,
    )
    return ProtocolMessage(
        message_type=MessageType.TASK_REQUEST,
        sender=sender,
        receiver=receiver,
        body=payload.model_dump(),
    )


def create_task_response(
    sender: str,
    receiver: str,
    task_id: str,
    status: str,
    result: dict[str, Any] | None = None,
    error: str | None = None,
    progress: float = 0.0,
) -> ProtocolMessage:
    """创建任务响应消息。"""
    payload = TaskResponsePayload(
        task_id=task_id,
        status=status,
        result=result,
        error=error,
        progress=progress,
    )
    return ProtocolMessage(
        message_type=MessageType.TASK_RESPONSE,
        sender=sender,
        receiver=receiver,
        body=payload.model_dump(),
    )


def create_heartbeat(
    agent_id: str,
    load: float = 0.0,
    status: str = "idle",
) -> ProtocolMessage:
    """创建心跳消息。"""
    payload = HeartbeatPayload(
        agent_id=agent_id,
        load=load,
        status=status,
    )
    return ProtocolMessage(
        message_type=MessageType.HEARTBEAT,
        sender=agent_id,
        receiver=None,
        body=payload.model_dump(),
    )
