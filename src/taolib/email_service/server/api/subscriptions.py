"""订阅管理端点。"""

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import HTMLResponse

from taolib.email_service.errors import SubscriptionError
from taolib.email_service.models.enums import SubscriptionStatus

router = APIRouter()


@router.get("")
async def list_subscriptions(
    request: Request,
    status: SubscriptionStatus | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    """查询订阅列表。"""
    filters = {}
    if status:
        filters["status"] = str(status)
    docs = await request.app.state.subscription_repo.list(
        filters=filters or None, skip=skip, limit=limit
    )
    return [d.to_response() for d in docs]


@router.get("/{email}")
async def get_subscription(email: str, request: Request):
    """获取邮箱订阅状态。"""
    doc = await request.app.state.subscription_repo.find_by_email(email)
    if doc is None:
        return {"email": email, "status": "active", "subscribed": True}
    return doc.to_response()


@router.post("/{email}/resubscribe")
async def resubscribe(email: str, request: Request):
    """重新订阅。"""
    try:
        return await request.app.state.subscription_service.resubscribe(email)
    except SubscriptionError as e:
        raise HTTPException(400, str(e))


# --- 公开退订端点 (无需认证) ---


@router.get("/unsubscribe", response_class=HTMLResponse)
async def unsubscribe_page(
    token: str = Query(...),
    email: str = Query(...),
):
    """退订确认页面。"""
    return f"""<!DOCTYPE html>
<html lang="zh"><head><meta charset="UTF-8"><title>退订确认</title>
<style>body{{font-family:sans-serif;display:flex;justify-content:center;padding:60px;background:#f9fafb}}
.box{{background:#fff;border-radius:12px;padding:40px;max-width:480px;box-shadow:0 2px 8px rgba(0,0,0,.08);text-align:center}}
h2{{margin-bottom:16px;color:#1f2937}}p{{color:#6b7280;margin-bottom:24px}}
button{{background:#dc2626;color:#fff;border:none;padding:12px 32px;border-radius:8px;
font-size:16px;cursor:pointer}}button:hover{{background:#b91c1c}}
</style></head><body><div class="box">
<h2>确认退订</h2><p>您确定要退订 <b>{email}</b> 的邮件订阅吗？</p>
<form method="POST" action="/api/v1/subscriptions/unsubscribe">
<input type="hidden" name="token" value="{token}">
<input type="hidden" name="email" value="{email}">
<button type="submit">确认退订</button></form></div></body></html>"""


@router.post("/unsubscribe")
async def process_unsubscribe(
    request: Request,
    token: str = Query(None),
    email: str = Query(None),
):
    """处理退订请求。"""
    # 支持表单提交和查询参数
    if token is None:
        form = await request.form()
        token = form.get("token", "")
        _email = form.get("email", "")

    if not token:
        raise HTTPException(400, "Missing unsubscribe token")

    try:
        await request.app.state.subscription_service.unsubscribe(token)
        return HTMLResponse("""<!DOCTYPE html>
<html lang="zh"><head><meta charset="UTF-8"><title>退订成功</title>
<style>body{font-family:sans-serif;display:flex;justify-content:center;padding:60px;background:#f9fafb}
.box{background:#fff;border-radius:12px;padding:40px;max-width:480px;box-shadow:0 2px 8px rgba(0,0,0,.08);text-align:center}
h2{color:#059669}p{color:#6b7280}</style></head><body><div class="box">
<h2>退订成功</h2><p>您已成功退订邮件。如需重新订阅，请联系管理员。</p>
</div></body></html>""")
    except SubscriptionError as e:
        raise HTTPException(400, str(e))
