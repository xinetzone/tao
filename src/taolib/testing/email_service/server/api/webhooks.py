"""提供商 Webhook 端点。

接收各提供商的投递通知（delivered/opened/clicked/bounced/complained）。
"""

from fastapi import APIRouter, Request

from taolib.testing.email_service.models.enums import BounceType, TrackingEventType

router = APIRouter()


@router.post("/sendgrid")
async def sendgrid_webhook(request: Request):
    """处理 SendGrid Event Webhook。"""
    events = await request.json()
    if not isinstance(events, list):
        events = [events]

    for event in events:
        email_id = event.get("custom_args", {}).get("email_id") or event.get(
            "sg_message_id", ""
        )
        recipient = event.get("email", "")
        event_name = event.get("event", "")

        mapping = {
            "delivered": TrackingEventType.DELIVERED,
            "open": TrackingEventType.OPENED,
            "click": TrackingEventType.CLICKED,
            "bounce": TrackingEventType.BOUNCED,
            "spamreport": TrackingEventType.COMPLAINED,
        }
        event_type = mapping.get(event_name)
        if not event_type:
            continue

        if event_type == TrackingEventType.BOUNCED:
            bounce_type = (
                BounceType.HARD if event.get("type") == "bounce" else BounceType.SOFT
            )
            await request.app.state.bounce_handler.handle_bounce(
                email_id=email_id,
                bounce_type=bounce_type,
                reason=event.get("reason", ""),
                recipient=recipient,
                provider="sendgrid",
                raw_payload=event,
            )
        elif event_type == TrackingEventType.COMPLAINED:
            await request.app.state.bounce_handler.handle_complaint(
                email_id=email_id,
                recipient=recipient,
                provider="sendgrid",
                raw_payload=event,
            )
        else:
            await request.app.state.tracking_service.record_event(
                email_id=email_id,
                event_type=event_type,
                recipient=recipient,
                provider="sendgrid",
                ip_address=event.get("ip"),
                user_agent=event.get("useragent"),
                click_url=event.get("url"),
                raw_payload=event,
            )

    return {"status": "ok"}


@router.post("/mailgun")
async def mailgun_webhook(request: Request):
    """处理 Mailgun Webhook。"""
    data = await request.json()
    event_data = data.get("event-data", data)
    event_name = event_data.get("event", "")
    recipient = event_data.get("recipient", "")
    message_id = event_data.get("message", {}).get("headers", {}).get("message-id", "")

    mapping = {
        "delivered": TrackingEventType.DELIVERED,
        "opened": TrackingEventType.OPENED,
        "clicked": TrackingEventType.CLICKED,
        "failed": TrackingEventType.BOUNCED,
        "complained": TrackingEventType.COMPLAINED,
    }
    event_type = mapping.get(event_name)
    if not event_type:
        return {"status": "ignored"}

    if event_type == TrackingEventType.BOUNCED:
        severity = event_data.get("severity", "permanent")
        bounce_type = BounceType.HARD if severity == "permanent" else BounceType.SOFT
        await request.app.state.bounce_handler.handle_bounce(
            email_id=message_id,
            bounce_type=bounce_type,
            reason=event_data.get("delivery-status", {}).get("message", ""),
            recipient=recipient,
            provider="mailgun",
            raw_payload=event_data,
        )
    elif event_type == TrackingEventType.COMPLAINED:
        await request.app.state.bounce_handler.handle_complaint(
            email_id=message_id,
            recipient=recipient,
            provider="mailgun",
            raw_payload=event_data,
        )
    else:
        await request.app.state.tracking_service.record_event(
            email_id=message_id,
            event_type=event_type,
            recipient=recipient,
            provider="mailgun",
            ip_address=event_data.get("ip"),
            user_agent=event_data.get("client-info", {}).get("user-agent"),
            click_url=event_data.get("url"),
            raw_payload=event_data,
        )

    return {"status": "ok"}


@router.post("/ses")
async def ses_webhook(request: Request):
    """处理 Amazon SES SNS 通知。"""
    data = await request.json()
    notification_type = data.get("notificationType", data.get("Type", ""))

    if notification_type == "Bounce":
        bounce = data.get("bounce", {})
        for recipient in bounce.get("bouncedRecipients", []):
            bounce_type = (
                BounceType.HARD
                if bounce.get("bounceType") == "Permanent"
                else BounceType.SOFT
            )
            await request.app.state.bounce_handler.handle_bounce(
                email_id=data.get("mail", {}).get("messageId", ""),
                bounce_type=bounce_type,
                reason=recipient.get("diagnosticCode", ""),
                recipient=recipient.get("emailAddress", ""),
                provider="ses",
                raw_payload=data,
            )
    elif notification_type == "Complaint":
        complaint = data.get("complaint", {})
        for recipient in complaint.get("complainedRecipients", []):
            await request.app.state.bounce_handler.handle_complaint(
                email_id=data.get("mail", {}).get("messageId", ""),
                recipient=recipient.get("emailAddress", ""),
                provider="ses",
                raw_payload=data,
            )
    elif notification_type == "Delivery":
        delivery = data.get("delivery", {})
        for recipient in delivery.get("recipients", []):
            await request.app.state.tracking_service.record_event(
                email_id=data.get("mail", {}).get("messageId", ""),
                event_type=TrackingEventType.DELIVERED,
                recipient=recipient,
                provider="ses",
                raw_payload=data,
            )

    return {"status": "ok"}


@router.post("/generic")
async def generic_webhook(request: Request):
    """通用 Webhook（SMTP bounce 通知等）。"""
    data = await request.json()
    event_type_str = data.get("event_type", "")
    mapping = {
        "delivered": TrackingEventType.DELIVERED,
        "bounced": TrackingEventType.BOUNCED,
        "complained": TrackingEventType.COMPLAINED,
    }
    event_type = mapping.get(event_type_str)
    if not event_type:
        return {"status": "ignored"}

    await request.app.state.tracking_service.record_event(
        email_id=data.get("email_id", ""),
        event_type=event_type,
        recipient=data.get("recipient", ""),
        provider=data.get("provider", "generic"),
        raw_payload=data,
    )
    return {"status": "ok"}


