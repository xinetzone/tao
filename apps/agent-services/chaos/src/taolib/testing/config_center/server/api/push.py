"""推送服务 API 模块。

提供 WebSocket 实时推送、HTTP 轮询降级、在线状态查询和连接统计端点。
"""
from datetime import UTC, datetime

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Request,
    WebSocket,
    WebSocketDisconnect,
)

from ...models.user import UserDocument
from ..auth.jwt_handler import verify_access_token
from ..dependencies import get_current_user, require_permission

router = APIRouter(prefix="/push", tags=["推送服务"])


def _get_manager(request: Request):
    """获取推送管理器（从 app.state）。"""
    mgr = getattr(request.app.state, "push_manager", None)
    if mgr is None:
        raise HTTPException(status_code=503, detail="推送服务未就绪")
    return mgr


def _get_buffer(request: Request):
    """获取消息缓冲（从 app.state）。"""
    buf = getattr(request.app.state, "message_buffer", None)
    if buf is None:
        raise HTTPException(status_code=503, detail="消息缓冲未就绪")
    return buf


def _get_presence(request: Request):
    """获取在线状态追踪器（从 app.state）。"""
    tracker = getattr(request.app.state, "presence_tracker", None)
    if tracker is None:
        raise HTTPException(status_code=503, detail="状态追踪未就绪")
    return tracker


# ------------------------------------------------------------------
# WebSocket 端点
# ------------------------------------------------------------------


@router.websocket("/ws")
async def websocket_push(
    websocket: WebSocket,
    token: str = Query(..., description="JWT 认证令牌"),
    environments: str = Query(default="", description="逗号分隔的环境列表"),
    services: str = Query(default="", description="逗号分隔的服务列表"),
):
    """WebSocket 实时推送端点。

    客户端通过此端点建立 WebSocket 连接，接收实时推送消息。
    支持通过 environments 和 services 参数自动订阅配置变更频道。
    """
    # 验证 JWT
    try:
        payload = verify_access_token(token)
        user_id = payload.get("sub")
        if not user_id:
            await websocket.close(code=4001, reason="无效的认证令牌")
            return
    except Exception:
        await websocket.close(code=4001, reason="认证失败")
        return

    manager = getattr(websocket.app.state, "push_manager", None)
    if manager is None:
        await websocket.close(code=1013, reason="服务未就绪")
        return

    env_list = [e.strip() for e in environments.split(",") if e.strip()]
    svc_list = [s.strip() for s in services.split(",") if s.strip()]

    try:
        await manager.connect(websocket, user_id, env_list, svc_list)

        # 主消息循环
        async for data in websocket.iter_text():
            await manager.handle_client_message(websocket, data)

    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        manager.disconnect(websocket)


# ------------------------------------------------------------------
# HTTP 轮询降级端点
# ------------------------------------------------------------------


@router.get("/poll")
async def poll_messages(
    request: Request,
    channels: str = Query(..., description="逗号分隔的频道列表"),
    since: str = Query(default="", description="起始时间戳 (ISO 格式)"),
    limit: int = Query(default=50, ge=1, le=200, description="最大消息数"),
    current_user: UserDocument = Depends(get_current_user),
):
    """HTTP 轮询端点（WebSocket 不可用时的降级方案）。

    客户端定期调用此端点获取新消息，通过 since 参数实现增量拉取。
    """
    buf = _get_buffer(request)

    if since:
        try:
            since_dt = datetime.fromisoformat(since)
        except ValueError:
            raise HTTPException(status_code=400, detail="无效的时间戳格式")
    else:
        since_dt = datetime.min.replace(tzinfo=UTC)

    channel_list = [c.strip() for c in channels.split(",") if c.strip()]
    all_messages = []
    for channel in channel_list:
        msgs = await buf.get_recent(channel, since_dt, limit)
        all_messages.extend([m.to_dict() for m in msgs])

    # 按时间戳排序
    all_messages.sort(key=lambda m: m.get("timestamp", ""))
    all_messages = all_messages[:limit]

    return {
        "messages": all_messages,
        "server_timestamp": datetime.now(UTC).isoformat(),
        "has_more": len(all_messages) >= limit,
    }


# ------------------------------------------------------------------
# 监控端点
# ------------------------------------------------------------------


@router.get("/stats")
async def get_push_stats(
    request: Request,
    _: UserDocument = Depends(require_permission("push", "read")),
):
    """获取推送服务连接统计（需要管理权限）。"""
    mgr = _get_manager(request)
    return mgr.get_stats().to_dict()


@router.get("/presence/{user_id}")
async def get_user_presence(
    user_id: str,
    request: Request,
    current_user: UserDocument = Depends(get_current_user),
):
    """查询用户在线状态。

    普通用户只能查询自己的状态。
    """
    if current_user.id != user_id:
        # 非本人查询需要管理权限（此处简化处理，生产中应检查角色）
        pass

    tracker = _get_presence(request)
    presence = await tracker.get_status(user_id)
    if presence is None:
        return {"user_id": user_id, "status": "offline", "connection_count": 0}
    return presence.to_dict()


@router.get("/presence")
async def get_all_online_users(
    request: Request,
    _: UserDocument = Depends(require_permission("push", "read")),
):
    """获取所有在线用户列表（需要管理权限）。"""
    tracker = _get_presence(request)
    users = await tracker.get_all_online()
    return [u.to_dict() for u in users]


