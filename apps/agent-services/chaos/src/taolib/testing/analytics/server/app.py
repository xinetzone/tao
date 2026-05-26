"""FastAPI 应用工厂模块。

创建和配置分析服务的 FastAPI 应用实例。
"""

import importlib.resources
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, Response
from motor.motor_asyncio import AsyncIOMotorClient

from .api.router import api_router
from .config import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """应用生命周期管理。"""
    print("Starting analytics server...")

    mongo_client = AsyncIOMotorClient(settings.mongo_url)
    app.state.mongo_client = mongo_client
    app.state.db = mongo_client[settings.mongo_db]

    # 事件集合索引
    events_col = app.state.db.analytics_events
    await events_col.create_index([("app_id", 1), ("timestamp", -1)])
    await events_col.create_index([("app_id", 1), ("event_type", 1)])
    await events_col.create_index([("session_id", 1), ("timestamp", 1)])
    await events_col.create_index(
        [("app_id", 1), ("event_type", 1), ("metadata.feature_name", 1)],
        sparse=True,
    )
    await events_col.create_index(
        "timestamp",
        expireAfterSeconds=settings.event_ttl_days * 24 * 3600,
    )

    # 会话集合索引
    sessions_col = app.state.db.analytics_sessions
    await sessions_col.create_index([("app_id", 1), ("started_at", -1)])
    await sessions_col.create_index([("app_id", 1), ("user_id", 1)], sparse=True)
    await sessions_col.create_index(
        "started_at",
        expireAfterSeconds=settings.session_ttl_days * 24 * 3600,
    )

    print("Analytics server started.")
    yield

    print("Shutting down analytics server...")
    mongo_client.close()
    print("Analytics server shut down.")


def _load_sdk_js() -> str:
    """加载 JavaScript SDK 文件内容。"""
    sdk_path = importlib.resources.files("taolib.testing.analytics.sdk") / "analytics.js"
    return sdk_path.read_text(encoding="utf-8")


def create_app() -> FastAPI:
    """创建 FastAPI 应用实例。"""
    app = FastAPI(
        title="Analytics API",
        description="用户行为分析 API",
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

    @app.get("/sdk/analytics.js")
    async def serve_sdk():
        """提供 JavaScript SDK 文件。"""
        content = _load_sdk_js()
        return Response(content=content, media_type="application/javascript")

    @app.get("/dashboard", response_class=HTMLResponse)
    async def dashboard():
        """分析仪表板。"""
        return _DASHBOARD_HTML

    return app


_DASHBOARD_HTML = """\
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Analytics Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        *{box-sizing:border-box;margin:0;padding:0}
        body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#f5f5f5;color:#333}
        .header{background:#2c3e50;color:#fff;padding:20px;display:flex;justify-content:space-between;align-items:center}
        .header h1{font-size:24px;font-weight:500}
        .hc{display:flex;gap:12px;align-items:center}
        .hc select,.hc input{padding:6px 10px;border:1px solid #4a6785;border-radius:4px;background:#34495e;color:#fff;font-size:13px}
        .container{max-width:1400px;margin:0 auto;padding:20px}
        .metrics{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:16px;margin-bottom:20px}
        .mc{background:#fff;border-radius:8px;padding:20px;text-align:center;box-shadow:0 2px 4px rgba(0,0,0,.1)}
        .mv{font-size:32px;font-weight:600;color:#3498db}
        .ml{font-size:14px;color:#666;margin-top:5px}
        .grid{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:20px}
        .card{background:#fff;border-radius:8px;padding:20px;box-shadow:0 2px 4px rgba(0,0,0,.1)}
        .card-full{grid-column:1/-1}
        .card h2{font-size:16px;color:#333;margin-bottom:15px;padding-bottom:10px;border-bottom:1px solid #eee}
        .cc{position:relative;height:300px}
        table{width:100%;border-collapse:collapse;font-size:14px}
        th,td{text-align:left;padding:10px 12px;border-bottom:1px solid #eee}
        th{background:#f8f9fa;font-weight:500;color:#666}
        .bar{display:inline-block;height:20px;background:#3498db;border-radius:3px;min-width:4px}
        .fs{display:flex;align-items:center;margin-bottom:8px}
        .fb{height:36px;background:linear-gradient(90deg,#3498db,#2ecc71);border-radius:4px;display:flex;align-items:center;padding:0 12px;color:#fff;font-size:13px;font-weight:500;transition:width .5s}
        .fl{min-width:120px;font-size:13px;margin-right:12px}
        .fc{margin-left:12px;color:#666;font-size:13px}
        .dr{color:#e74c3c;font-size:12px;margin-left:8px}
        .btn{padding:6px 14px;border:none;border-radius:4px;cursor:pointer;font-size:13px}
        .btn-p{background:#3498db;color:#fff}
        .btn-p:hover{background:#2980b9}
        .ig{display:flex;gap:8px;margin-bottom:12px}
        .ig input{flex:1;padding:6px 10px;border:1px solid #ddd;border-radius:4px;font-size:13px}
        .empty{text-align:center;color:#999;padding:40px}
        @media(max-width:768px){.grid{grid-template-columns:1fr}}
    </style>
</head>
<body>
<div class="header">
    <h1>Analytics Dashboard</h1>
    <div class="hc">
        <input type="text" id="appId" placeholder="App ID" value="">
        <select id="timeRange">
            <option value="1">Last 24h</option>
            <option value="7" selected>Last 7 days</option>
            <option value="30">Last 30 days</option>
            <option value="90">Last 90 days</option>
        </select>
        <button class="btn btn-p" onclick="loadAll()">Refresh</button>
    </div>
</div>
<div class="container">
    <div class="metrics">
        <div class="mc"><div class="mv" id="totalEvents">-</div><div class="ml">Total Events</div></div>
        <div class="mc"><div class="mv" id="uniqueSessions">-</div><div class="ml">Sessions</div></div>
        <div class="mc"><div class="mv" id="uniqueUsers">-</div><div class="ml">Users</div></div>
        <div class="mc"><div class="mv" id="avgDuration">-</div><div class="ml">Avg Duration</div></div>
        <div class="mc"><div class="mv" id="bounceRate">-</div><div class="ml">Bounce Rate</div></div>
    </div>
    <div class="grid">
        <div class="card">
            <h2>Conversion Funnel</h2>
            <div class="ig">
                <input type="text" id="funnelSteps" placeholder="Steps (comma-separated, e.g. /home,/signup,/dashboard)">
                <button class="btn btn-p" onclick="loadFunnel()">Analyze</button>
            </div>
            <div id="funnelChart"></div>
        </div>
        <div class="card">
            <h2>Top Features</h2>
            <div class="cc"><canvas id="featuresChart"></canvas></div>
        </div>
        <div class="card">
            <h2>User Flow (Top Paths)</h2>
            <table><thead><tr><th>From</th><th>To</th><th>Count</th><th></th></tr></thead>
            <tbody id="pathsTable"><tr><td colspan="4" class="empty">Enter App ID and click Refresh</td></tr></tbody></table>
        </div>
        <div class="card">
            <h2>Time on Section</h2>
            <div class="cc"><canvas id="retentionChart"></canvas></div>
        </div>
        <div class="card card-full">
            <h2>Drop-off Analysis</h2>
            <div class="ig">
                <input type="text" id="dropOffSteps" placeholder="Flow steps (comma-separated, e.g. /cart,/checkout,/payment,/confirm)">
                <button class="btn btn-p" onclick="loadDropOff()">Analyze</button>
            </div>
            <div id="dropOffChart"></div>
        </div>
        <div class="card">
            <h2>Top Pages</h2>
            <table><thead><tr><th>Page</th><th>Views</th><th></th></tr></thead>
            <tbody id="pagesTable"><tr><td colspan="3" class="empty">No data</td></tr></tbody></table>
        </div>
        <div class="card">
            <h2>Event Distribution</h2>
            <div class="cc"><canvas id="eventTypesChart"></canvas></div>
        </div>
    </div>
</div>
<script>
const A='/api/v1';
let fCI=null,rCI=null,eCI=null;
function gP(){const a=document.getElementById('appId').value.trim(),d=parseInt(document.getElementById('timeRange').value),e=new Date().toISOString(),s=new Date(Date.now()-d*864e5).toISOString();return{appId:a,start:s,end:e}}
function fmt(n){if(n==null)return'-';if(n>=1e6)return(n/1e6).toFixed(1)+'M';if(n>=1e3)return(n/1e3).toFixed(1)+'K';return String(n)}
function fmtD(s){if(!s)return'-';return s<60?s.toFixed(0)+'s':(s/60).toFixed(1)+'m'}
async function api(p){const r=await fetch(A+p);if(!r.ok)return null;return await r.json()}
async function loadOverview(){const p=gP();if(!p.appId)return;const d=await api('/analytics/overview?app_id='+encodeURIComponent(p.appId)+'&start='+p.start+'&end='+p.end);if(!d)return;
document.getElementById('totalEvents').textContent=fmt(d.total_events);
document.getElementById('uniqueSessions').textContent=fmt(d.unique_sessions);
document.getElementById('uniqueUsers').textContent=fmt(d.unique_users);
document.getElementById('avgDuration').textContent=fmtD(d.avg_duration_seconds);
document.getElementById('bounceRate').textContent=d.bounce_rate!=null?(d.bounce_rate*100).toFixed(1)+'%':'-';
const pb=document.getElementById('pagesTable');
if(d.top_pages&&d.top_pages.length>0){const mx=d.top_pages[0].count;pb.innerHTML=d.top_pages.map(p=>'<tr><td>'+p.page+'</td><td>'+p.count+'</td><td><span class="bar" style="width:'+(p.count/mx*100)+'px"></span></td></tr>').join('')}else{pb.innerHTML='<tr><td colspan="3" class="empty">No data</td></tr>'}
if(d.event_types&&d.event_types.length>0){const ctx=document.getElementById('eventTypesChart').getContext('2d');if(eCI)eCI.destroy();eCI=new Chart(ctx,{type:'doughnut',data:{labels:d.event_types.map(e=>e.type),datasets:[{data:d.event_types.map(e=>e.count),backgroundColor:['#3498db','#2ecc71','#e74c3c','#f39c12','#9b59b6','#1abc9c','#e67e22','#34495e']}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'right'}}}})}}
async function loadFeatures(){const p=gP();if(!p.appId)return;const d=await api('/analytics/features?app_id='+encodeURIComponent(p.appId)+'&start='+p.start+'&end='+p.end+'&limit=15');if(!d||!d.features||!d.features.length)return;
const ctx=document.getElementById('featuresChart').getContext('2d');if(fCI)fCI.destroy();fCI=new Chart(ctx,{type:'bar',data:{labels:d.features.map(f=>f.name||'unknown'),datasets:[{label:'Usage',data:d.features.map(f=>f.count),backgroundColor:'#3498db'},{label:'Users',data:d.features.map(f=>f.unique_users),backgroundColor:'#2ecc71'}]},options:{responsive:true,maintainAspectRatio:false,indexAxis:'y',plugins:{legend:{position:'top'}},scales:{x:{beginAtZero:true}}}})}
async function loadPaths(){const p=gP();if(!p.appId)return;const d=await api('/analytics/paths?app_id='+encodeURIComponent(p.appId)+'&start='+p.start+'&end='+p.end+'&limit=20');if(!d||!d.paths)return;
const tb=document.getElementById('pathsTable');if(!d.paths.length){tb.innerHTML='<tr><td colspan="4" class="empty">No navigation data</td></tr>';return}
const mx=d.paths[0].value;tb.innerHTML=d.paths.map(p=>'<tr><td>'+p.source+'</td><td>'+p.target+'</td><td>'+p.value+'</td><td><span class="bar" style="width:'+(p.value/mx*80)+'px"></span></td></tr>').join('')}
async function loadRetention(){const p=gP();if(!p.appId)return;const d=await api('/analytics/retention?app_id='+encodeURIComponent(p.appId)+'&start='+p.start+'&end='+p.end);if(!d||!d.sections||!d.sections.length)return;
const ctx=document.getElementById('retentionChart').getContext('2d');if(rCI)rCI.destroy();rCI=new Chart(ctx,{type:'bar',data:{labels:d.sections.map(s=>s.section_id||'unknown'),datasets:[{label:'Avg Duration (ms)',data:d.sections.map(s=>s.avg_duration_ms),backgroundColor:'#9b59b6'}]},options:{responsive:true,maintainAspectRatio:false,indexAxis:'y',plugins:{legend:{display:false}},scales:{x:{beginAtZero:true}}}})}
async function loadFunnel(){const p=gP();if(!p.appId)return;const st=document.getElementById('funnelSteps').value.trim();if(!st)return;
const d=await api('/analytics/funnel?app_id='+encodeURIComponent(p.appId)+'&steps='+encodeURIComponent(st)+'&start='+p.start+'&end='+p.end);if(!d||!d.steps)return;
const c=document.getElementById('funnelChart');if(!d.steps.length){c.innerHTML='<div class="empty">No funnel data</div>';return}
const mx=Math.max(...d.steps.map(s=>s.count),1);c.innerHTML=d.steps.map((s,i)=>{const w=Math.max(s.count/mx*100,5);const r=i===0?'':'<span class="dr">'+(s.conversion_rate*100).toFixed(1)+'% from prev</span>';return'<div class="fs"><span class="fl">'+s.name+'</span><div class="fb" style="width:'+w+'%">'+s.count+'</div>'+r+'</div>'}).join('')+'<div style="margin-top:8px;font-size:13px;color:#666">Overall: <strong>'+(d.overall_conversion*100).toFixed(1)+'%</strong></div>'}
async function loadDropOff(){const p=gP();if(!p.appId)return;const st=document.getElementById('dropOffSteps').value.trim();if(!st)return;
const d=await api('/analytics/drop-off?app_id='+encodeURIComponent(p.appId)+'&steps='+encodeURIComponent(st)+'&start='+p.start+'&end='+p.end);if(!d||!d.steps)return;
const c=document.getElementById('dropOffChart');if(!d.steps.length){c.innerHTML='<div class="empty">No drop-off data</div>';return}
const mx=Math.max(...d.steps.map(s=>Math.max(s.entered,s.completed)),1);c.innerHTML='<table><thead><tr><th>Step</th><th>Entered</th><th>Completed</th><th>Drop-off</th><th></th></tr></thead><tbody>'+d.steps.map(s=>{const dp=(s.drop_off_rate*100).toFixed(1),bw=Math.max(s.completed/mx*200,4);return'<tr><td>'+s.name+'</td><td>'+s.entered+'</td><td>'+s.completed+'</td><td class="dr">'+dp+'%</td><td><span class="bar" style="width:'+bw+'px;background:'+(s.drop_off_rate>.3?'#e74c3c':'#2ecc71')+'"></span></td></tr>'}).join('')+'</tbody></table>'}
function loadAll(){loadOverview();loadFeatures();loadPaths();loadRetention()}
loadAll();setInterval(loadAll,30000);
</script>
</body>
</html>
"""


