"""邮件发送和查询端点。"""

from fastapi import APIRouter, HTTPException, Query, Request

from taolib.email_service.models.email import EmailCreate, EmailResponse
from taolib.email_service.models.enums import EmailStatus, EmailType

router = APIRouter()

EMAILS_API_DESCRIPTION = """
邮件服务 API 提供邮件发送、查询和追踪功能。

## 功能特性

- **多提供商支持**：SendGrid、Mailgun、Amazon SES、SMTP
- **模板引擎**：支持 Jinja2 模板渲染
- **批量发送**：支持大批量邮件发送
- **追踪分析**：投递、打开、点击追踪
- **退订管理**：自动处理退订请求
- **失败重试**：自动重试失败的邮件

## 队列处理

邮件发送通过队列异步处理，支持：
- 优先级队列
- 失败重试
- 延迟发送
"""


@router.post(
    "",
    response_model=EmailResponse,
    status_code=201,
    summary="发送单封邮件",
    description="""
发送单封邮件。

## 请求体示例

```json
{
  "to": ["user@example.com"],
  "subject": "欢迎加入",
  "html_body": "<h1>欢迎</h1><p>感谢您的注册</p>",
  "text_body": "欢迎，感谢您的注册",
  "email_type": "transactional",
  "template_id": "welcome_email",
  "variables": {"name": "John"}
}
```

## 响应示例

```json
{
  "id": "email_abc123",
  "status": "queued",
  "to": ["user@example.com"],
  "subject": "欢迎加入",
  "created_at": "2024-01-15T10:30:00Z"
}
```
""",
    responses={
        201: {"description": "邮件已加入发送队列"},
        400: {"description": "请求参数错误"},
        503: {"description": "没有配置邮件提供商"},
    },
)
async def send_email(data: EmailCreate, request: Request):
    """发送单封邮件。"""
    if (
        not hasattr(request.app.state, "email_service")
        or request.app.state.email_service is None
    ):
        raise HTTPException(503, "No email providers configured")
    return await request.app.state.email_service.send_email(data)


@router.post(
    "/bulk",
    response_model=list[EmailResponse],
    status_code=201,
    summary="批量发送邮件",
    description="""
批量发送多封邮件。

## 请求体示例

```json
[
  {
    "to": ["user1@example.com"],
    "subject": "通知",
    "html_body": "<p>内容</p>"
  },
  {
    "to": ["user2@example.com"],
    "subject": "通知",
    "html_body": "<p>内容</p>"
  }
]
```

## 限制

单次批量发送最多 100 封邮件。
""",
    responses={
        201: {"description": "邮件已加入发送队列"},
        400: {"description": "请求数量超过限制"},
        503: {"description": "没有配置邮件提供商"},
    },
)
async def send_bulk(data: list[EmailCreate], request: Request):
    """批量发送邮件。"""
    if (
        not hasattr(request.app.state, "email_service")
        or request.app.state.email_service is None
    ):
        raise HTTPException(503, "No email providers configured")
    return await request.app.state.email_service.send_bulk(data)


@router.get(
    "",
    response_model=list[EmailResponse],
    summary="查询邮件列表",
    description="""
查询邮件列表，支持按状态和类型过滤。

## 查询参数

- `status`: 邮件状态（queued/sent/delivered/failed）
- `email_type`: 邮件类型（transactional/marketing/notification）
- `skip`: 跳过记录数（默认 0）
- `limit`: 返回数量（默认 20，最大 100）

## 响应示例

```json
[
  {
    "id": "email_abc123",
    "status": "delivered",
    "to": ["user@example.com"],
    "subject": "欢迎",
    "sent_at": "2024-01-15T10:30:00Z"
  }
]
```
""",
    responses={
        200: {"description": "成功获取邮件列表"}
    },
)
async def list_emails(
    request: Request,
    status: EmailStatus | None = Query(None),
    email_type: EmailType | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    """查询邮件列表。"""
    svc = request.app.state.email_service
    if svc is None:
        # 即使没有 provider 也可以查询
        repo = request.app.state.email_repo
        filters = {}
        if status:
            filters["status"] = str(status)
        if email_type:
            filters["email_type"] = str(email_type)
        docs = await repo.list(
            filters=filters or None, skip=skip, limit=limit, sort=[("created_at", -1)]
        )
        return [d.to_response() for d in docs]
    return await svc.list_emails(status, email_type, skip, limit)


@router.get(
    "/{email_id}",
    response_model=EmailResponse,
    summary="获取邮件详情",
    description="""
根据 ID 获取邮件的详细信息，包括发送状态、追踪事件等。

## 路径参数

- `email_id`: 邮件唯一标识符

## 响应示例

```json
{
  "id": "email_abc123",
  "status": "delivered",
  "to": ["user@example.com"],
  "subject": "欢迎加入",
  "html_body": "<h1>欢迎</h1>",
  "sent_at": "2024-01-15T10:30:00Z",
  "delivered_at": "2024-1-15T10:30:05Z"
}
```
""",
    responses={
        200: {"description": "成功获取邮件详情"},
        404: {"description": "邮件不存在"},
    },
)
async def get_email(email_id: str, request: Request):
    """获取邮件详情。"""
    doc = await request.app.state.email_repo.get_by_id(email_id)
    if doc is None:
        raise HTTPException(404, "Email not found")
    return doc.to_response()


@router.get(
    "/{email_id}/events",
    summary="获取邮件追踪事件",
    description="""
获取指定邮件的所有追踪事件，包括投递、打开、点击、退回等。

## 路径参数

- `email_id`: 邮件唯一标识符

## 响应示例

```json
[
  {
    "event_type": "delivered",
    "timestamp": "2024-01-15T10:30:05Z",
    "recipient": "user@example.com"
  },
  {
    "event_type": "opened",
    "timestamp": "2024-01-15T11:00:00Z",
    "ip_address": "192.168.1.1"
  }
]
```
""",
    responses={
        200: {"description": "成功获取追踪事件"}
    },
)
async def get_email_events(email_id: str, request: Request):
    """获取邮件的追踪事件。"""
    events = await request.app.state.tracking_service.get_events_for_email(email_id)
    return events
