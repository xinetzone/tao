"""FastAPI 应用工厂模块。"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import redis.asyncio as aioredis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from motor.motor_asyncio import AsyncIOMotorClient

from taolib.email_service.providers.failover import ProviderFailoverManager
from taolib.email_service.providers.mailgun import MailgunProvider
from taolib.email_service.providers.sendgrid import SendGridProvider
from taolib.email_service.providers.ses import SESProvider
from taolib.email_service.providers.smtp import SMTPProvider
from taolib.email_service.queue.redis_queue import RedisEmailQueue
from taolib.email_service.repository.email_repo import EmailRepository
from taolib.email_service.repository.subscription_repo import SubscriptionRepository
from taolib.email_service.repository.template_repo import TemplateRepository
from taolib.email_service.repository.tracking_repo import TrackingRepository
from taolib.email_service.services.bounce_handler import BounceHandler
from taolib.email_service.services.email_service import EmailService
from taolib.email_service.services.queue_processor import QueueProcessor
from taolib.email_service.services.subscription_service import SubscriptionService
from taolib.email_service.services.template_service import TemplateService
from taolib.email_service.services.tracking_service import TrackingService
from taolib.email_service.template.engine import TemplateEngine

from .api.router import api_router
from .config import settings


def _build_providers() -> list[tuple]:
    """根据配置构建提供商列表。"""
    providers = []
    priority = 1

    if settings.sendgrid_api_key:
        providers.append(
            (
                SendGridProvider(
                    api_key=settings.sendgrid_api_key,
                    sender_email=settings.default_sender,
                    sender_name=settings.default_sender_name,
                ),
                priority,
            )
        )
        priority += 1

    if settings.mailgun_api_key and settings.mailgun_domain:
        providers.append(
            (
                MailgunProvider(
                    api_key=settings.mailgun_api_key,
                    domain=settings.mailgun_domain,
                ),
                priority,
            )
        )
        priority += 1

    if settings.ses_region and settings.ses_access_key_id:
        providers.append(
            (
                SESProvider(
                    region=settings.ses_region,
                    access_key_id=settings.ses_access_key_id,
                    secret_access_key=settings.ses_secret_access_key,
                ),
                priority,
            )
        )
        priority += 1

    if settings.smtp_host:
        providers.append(
            (
                SMTPProvider(
                    host=settings.smtp_host,
                    port=settings.smtp_port,
                    username=settings.smtp_username or None,
                    password=settings.smtp_password or None,
                    use_tls=settings.smtp_use_tls,
                ),
                priority,
            )
        )

    return providers


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """应用生命周期管理。"""
    print("Starting email service server...")

    # MongoDB
    mongo_client = AsyncIOMotorClient(settings.mongo_url)
    app.state.mongo_client = mongo_client
    app.state.db = mongo_client[settings.mongo_db]

    # Redis
    redis_client = aioredis.from_url(settings.redis_url, decode_responses=False)
    app.state.redis = redis_client

    # Repositories
    db = app.state.db
    app.state.email_repo = EmailRepository(db.emails)
    app.state.template_repo = TemplateRepository(db.templates)
    app.state.tracking_repo = TrackingRepository(db.tracking_events)
    app.state.subscription_repo = SubscriptionRepository(db.subscriptions)

    # Create indexes
    await app.state.email_repo.create_indexes()
    await app.state.template_repo.create_indexes()
    await app.state.tracking_repo.create_indexes()
    await app.state.subscription_repo.create_indexes()

    # Template engine
    app.state.template_engine = TemplateEngine(
        unsubscribe_base_url=settings.unsubscribe_base_url
    )

    # Providers
    provider_list = _build_providers()
    app.state.provider_manager = (
        ProviderFailoverManager(providers=provider_list) if provider_list else None
    )

    # Queue
    app.state.queue = RedisEmailQueue(redis_client)

    # Services
    app.state.template_service = TemplateService(
        app.state.template_repo, app.state.template_engine
    )
    app.state.subscription_service = SubscriptionService(app.state.subscription_repo)
    app.state.tracking_service = TrackingService(
        app.state.tracking_repo, app.state.email_repo
    )
    app.state.bounce_handler = BounceHandler(
        app.state.tracking_service,
        app.state.subscription_service,
        app.state.email_repo,
    )

    if app.state.provider_manager:
        app.state.email_service = EmailService(
            email_repo=app.state.email_repo,
            template_service=app.state.template_service,
            subscription_service=app.state.subscription_service,
            provider_manager=app.state.provider_manager,
            queue=app.state.queue,
            tracking_service=app.state.tracking_service,
        )

        # Queue processor
        app.state.queue_processor = QueueProcessor(
            queue=app.state.queue,
            email_repo=app.state.email_repo,
            send_callback=app.state.email_service._send_now,
            poll_interval=settings.queue_poll_interval,
            batch_size=settings.queue_batch_size,
        )
        await app.state.queue_processor.start()

    print("Email service server started.")
    yield

    # Shutdown
    print("Shutting down email service server...")
    if hasattr(app.state, "queue_processor"):
        await app.state.queue_processor.stop()
    await redis_client.aclose()
    mongo_client.close()


def create_app() -> FastAPI:
    """创建 FastAPI 应用。"""
    app = FastAPI(
        title="Email Service",
        description="事务性邮件和营销邮件服务系统",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router)

    @app.get("/dashboard", response_class=HTMLResponse)
    async def dashboard():
        """监控仪表板。"""
        return _DASHBOARD_HTML

    return app


_DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Email Service Dashboard</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#f0f2f5;color:#1f2937}
.header{background:#1e40af;color:#fff;padding:20px 32px;display:flex;justify-content:space-between;align-items:center}
.header h1{font-size:22px}
.container{max-width:1200px;margin:24px auto;padding:0 16px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:16px;margin-bottom:24px}
.card{background:#fff;border-radius:8px;padding:20px;box-shadow:0 1px 3px rgba(0,0,0,.1)}
.card .label{font-size:13px;color:#6b7280;margin-bottom:4px}
.card .value{font-size:28px;font-weight:700}
.card .value.green{color:#059669}.card .value.red{color:#dc2626}
.card .value.blue{color:#2563eb}.card .value.amber{color:#d97706}
.section{background:#fff;border-radius:8px;padding:20px;box-shadow:0 1px 3px rgba(0,0,0,.1);margin-bottom:24px}
.section h2{font-size:16px;margin-bottom:12px;padding-bottom:8px;border-bottom:1px solid #e5e7eb}
table{width:100%;border-collapse:collapse;font-size:14px}
th,td{padding:10px 12px;text-align:left;border-bottom:1px solid #f3f4f6}
th{font-weight:600;color:#6b7280;font-size:12px;text-transform:uppercase}
.badge{display:inline-block;padding:2px 8px;border-radius:12px;font-size:12px;font-weight:500}
.badge.sent{background:#dbeafe;color:#1e40af}.badge.delivered{background:#d1fae5;color:#065f46}
.badge.opened{background:#fef3c7;color:#92400e}.badge.failed{background:#fee2e2;color:#991b1b}
.badge.queued{background:#f3f4f6;color:#4b5563}.badge.bounced{background:#fce7f3;color:#9d174d}
.badge.healthy{background:#d1fae5;color:#065f46}.badge.unhealthy{background:#fee2e2;color:#991b1b}
.refresh{font-size:12px;color:rgba(255,255,255,.7)}
</style>
</head>
<body>
<div class="header"><h1>Email Service Dashboard</h1><span class="refresh" id="lastUpdate"></span></div>
<div class="container">
  <div class="cards" id="statsCards"></div>
  <div class="section"><h2>Provider Status</h2><div id="providerStatus">Loading...</div></div>
  <div class="section"><h2>Queue Status</h2><div id="queueStatus">Loading...</div></div>
  <div class="section"><h2>Recent Emails</h2><table><thead><tr>
    <th>ID</th><th>Subject</th><th>Recipients</th><th>Status</th><th>Created</th>
  </tr></thead><tbody id="emailsTable"></tbody></table></div>
</div>
<script>
const API='/api/v1';
function badge(status){return `<span class="badge ${status}">${status}</span>`}
function shortId(id){return id?id.substring(0,8)+'...':'—'}
function fmtDate(d){return d?new Date(d).toLocaleString('zh-CN'):'—'}
async function fetchJSON(url){try{const r=await fetch(url);return await r.json()}catch{return null}}
async function refresh(){
  document.getElementById('lastUpdate').textContent='Updated: '+new Date().toLocaleString('zh-CN');
  const [health,emails,analytics]=await Promise.all([
    fetchJSON(API+'/health'),fetchJSON(API+'/emails?limit=20'),
    fetchJSON(API+'/tracking/analytics?days=7')
  ]);
  if(analytics){
    document.getElementById('statsCards').innerHTML=`
      <div class="card"><div class="label">Total Sent</div><div class="value blue">${analytics.total_sent||0}</div></div>
      <div class="card"><div class="label">Delivery Rate</div><div class="value green">${(analytics.delivery_rate||0).toFixed(1)}%</div></div>
      <div class="card"><div class="label">Open Rate</div><div class="value amber">${(analytics.open_rate||0).toFixed(1)}%</div></div>
      <div class="card"><div class="label">Click Rate</div><div class="value blue">${(analytics.click_rate||0).toFixed(1)}%</div></div>
      <div class="card"><div class="label">Bounce Rate</div><div class="value red">${(analytics.bounce_rate||0).toFixed(1)}%</div></div>`;
  }
  if(health){
    const ps=(health.providers||[]).map(p=>`<span class="badge ${p.is_healthy?'healthy':'unhealthy'}">${p.provider_name}: ${p.is_healthy?'Healthy':'Down'}</span> `).join('');
    document.getElementById('providerStatus').innerHTML=ps||'No providers configured';
    const q=health.queue||{};
    document.getElementById('queueStatus').innerHTML=`High: <b>${q.high||0}</b> | Normal: <b>${q.normal||0}</b> | Low: <b>${q.low||0}</b>`;
  }
  if(Array.isArray(emails)){
    document.getElementById('emailsTable').innerHTML=emails.map(e=>`<tr>
      <td>${shortId(e.id||e._id)}</td><td>${e.subject||'—'}</td>
      <td>${(e.recipients||[]).map(r=>r.email||r).join(', ')}</td>
      <td>${badge(e.status)}</td><td>${fmtDate(e.created_at)}</td></tr>`).join('');
  }
}
refresh();setInterval(refresh,30000);
</script>
</body></html>"""
