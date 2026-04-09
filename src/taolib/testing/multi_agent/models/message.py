"""消息数据模型。

定义智能体间通信的消息模型。
"""

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from taolib.testing.multi_agent.models.enums import MessageType


class MessagePayload(BaseModel):
    """消息载荷。"""

    task_id: str | None = Field(None, description="关联的任务ID")
    agent_id: str | None = Field(None, description="关联的智能体ID")
    skill_id: str | None = Field(None, description="关联的技能ID")
    data: dict[str, Any] = Field(default_factory=dict, description="消息数据")
    metadata: dict[str, Any] = Field(default_factory=dict, description="元数据")


class Message(BaseModel):
    """智能体间通信消息。"""

    id: str = Field(..., description="消息ID")
    message_type: MessageType = Field(..., description="消息类型")
    sender_id: str = Field(..., description="发送者ID")
    receiver_id: str | None = Field(None, description="接收者ID(None表示广播)")
    payload: MessagePayload = Field(default_factory=MessagePayload, description="消息载荷")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC), description="时间戳")
    priority: int = Field(default=5, ge=1, le=10, description="优先级(1-10)")
    requires_response: bool = Field(default=False, description="是否需要响应")
    response_to: str | None = Field(None, description="响应的消息ID")
