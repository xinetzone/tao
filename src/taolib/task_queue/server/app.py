"""FastAPI 应用工厂模块。

创建和配置 FastAPI 应用实例。
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from motor.motor_asyncio import AsyncIOMotorClient
from redis.asyncio import from_url as redis_from_url

from .api.router import api_router
from .config import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """应用生命周期管理。"""
    from taolib.task_queue.queue.redis_queue import RedisTaskQueue
    from taolib.task_queue.repository.task_repo import TaskRepository
    from taolib.task_queue.worker.manager import WorkerManager
    from taolib.task_queue.worker.registry import get_default_registry

    # 启动时执行
    print("Starting task queue server...")

    # 初始化 MongoDB
    mongo_client = AsyncIOMotorClient(settings.mongo_url)
    app.state.mongo_client = mongo_client
    app.state.db = mongo_client[settings.mongo_db]

    # 初始化 Redis
    redis = redis_from_url(settings.redis_url, decode_responses=False)
    app.state.redis = redis
    app.state.redis_key_prefix = settings.redis_key_prefix

    # 创建索引
    task_repo = TaskRepository(app.state.db.tasks)
    await task_repo.create_indexes()

    # 创建队列和管理器
    redis_queue = RedisTaskQueue(redis, settings.redis_key_prefix)
    registry = get_default_registry()
    worker_manager = WorkerManager(
        redis_queue=redis_queue,
        task_repo=task_repo,
        registry=registry,
        num_workers=settings.num_workers,
    )
    app.state.worker_manager = worker_manager

    # 启动工作者
    await worker_manager.start()

    print(f"Task queue server started with {settings.num_workers} workers.")

    yield

    # 关闭时执行
    print("Shutting down task queue server...")
    await worker_manager.stop()
    await redis.aclose()
    mongo_client.close()
    print("Task queue server shut down.")


def create_app() -> FastAPI:
    """创建 FastAPI 应用实例。"""
    app = FastAPI(
        title="Task Queue API",
        description="后台任务队列管理 API",
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS 中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册 API 路由
    app.include_router(api_router)

    # 注册监控仪表板
    @app.get("/dashboard", response_class=HTMLResponse)
    async def dashboard():
        """任务队列监控仪表板。"""
        return _DASHBOARD_HTML

    return app


_DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Task Queue Dashboard</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; color: #333; }
        .header { background: #e67e22; color: white; padding: 20px; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { font-size: 24px; font-weight: 500; }
        .header button { background: rgba(255,255,255,0.2); color: white; border: 1px solid rgba(255,255,255,0.4); padding: 8px 16px; border-radius: 4px; cursor: pointer; font-size: 14px; }
        .header button:hover { background: rgba(255,255,255,0.3); }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .card { background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .card h2 { font-size: 18px; color: #333; margin-bottom: 15px; border-bottom: 1px solid #eee; padding-bottom: 10px; display: flex; justify-content: space-between; align-items: center; }
        .metrics { display: flex; gap: 20px; flex-wrap: wrap; }
        .metric-card { flex: 1; min-width: 140px; text-align: center; padding: 15px; border-radius: 8px; background: #f8f9fa; }
        .metric-value { font-size: 36px; font-weight: 700; }
        .metric-label { font-size: 13px; color: #666; margin-top: 5px; }
        .metric-card.pending .metric-value { color: #f39c12; }
        .metric-card.running .metric-value { color: #3498db; }
        .metric-card.completed .metric-value { color: #27ae60; }
        .metric-card.failed .metric-value { color: #e74c3c; }
        .queue-bars { display: flex; gap: 15px; align-items: flex-end; }
        .queue-bar { flex: 1; text-align: center; }
        .queue-bar-fill { background: #3498db; border-radius: 4px 4px 0 0; min-height: 4px; transition: height 0.3s; margin: 0 10px; }
        .queue-bar-label { font-size: 13px; color: #666; margin-top: 8px; }
        .queue-bar-value { font-size: 18px; font-weight: 600; color: #333; margin-top: 4px; }
        .queue-bar.high .queue-bar-fill { background: #e74c3c; }
        .queue-bar.normal .queue-bar-fill { background: #f39c12; }
        .queue-bar.low .queue-bar-fill { background: #27ae60; }
        table { width: 100%; border-collapse: collapse; }
        th, td { text-align: left; padding: 10px 12px; border-bottom: 1px solid #eee; font-size: 14px; }
        th { background: #f8f9fa; font-weight: 500; color: #666; }
        tr:hover { background: #f8f9fa; }
        .status { padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight: 500; display: inline-block; }
        .status.pending { background: #fff3cd; color: #856404; }
        .status.running { background: #cce5ff; color: #004085; }
        .status.completed { background: #d4edda; color: #155724; }
        .status.failed { background: #f8d7da; color: #721c24; }
        .status.retrying { background: #e2e3f1; color: #383d6e; }
        .status.cancelled { background: #e2e2e2; color: #555; }
        .priority { padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight: 500; }
        .priority.high { background: #fce4ec; color: #c62828; }
        .priority.normal { background: #fff8e1; color: #f57f17; }
        .priority.low { background: #e8f5e9; color: #2e7d32; }
        .btn { padding: 6px 12px; border: none; border-radius: 4px; cursor: pointer; font-size: 13px; }
        .btn-primary { background: #3498db; color: white; }
        .btn-primary:hover { background: #2980b9; }
        .btn-warning { background: #f39c12; color: white; }
        .btn-warning:hover { background: #e67e22; }
        .btn-sm { padding: 4px 8px; font-size: 12px; }
        .modal-overlay { display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); z-index: 100; justify-content: center; align-items: center; }
        .modal-overlay.active { display: flex; }
        .modal { background: white; border-radius: 8px; padding: 24px; max-width: 700px; width: 90%; max-height: 80vh; overflow-y: auto; }
        .modal h3 { margin-bottom: 16px; }
        .modal .close-btn { float: right; background: none; border: none; font-size: 20px; cursor: pointer; color: #666; }
        .modal pre { background: #f5f5f5; padding: 12px; border-radius: 4px; overflow-x: auto; font-size: 13px; line-height: 1.5; white-space: pre-wrap; word-break: break-all; }
        .detail-row { display: flex; padding: 8px 0; border-bottom: 1px solid #f0f0f0; }
        .detail-label { width: 120px; font-weight: 500; color: #666; flex-shrink: 0; }
        .detail-value { flex: 1; }
        .empty { text-align: center; padding: 30px; color: #999; }
        .task-id { font-family: monospace; font-size: 13px; color: #666; cursor: pointer; }
        .task-id:hover { color: #3498db; text-decoration: underline; }
        .error-text { color: #e74c3c; font-size: 13px; max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Task Queue Dashboard</h1>
        <button onclick="refreshAll()">Refresh</button>
    </div>
    <div class="container">
        <div class="card">
            <h2>Overview</h2>
            <div class="metrics">
                <div class="metric-card pending">
                    <div class="metric-value" id="metricPending">-</div>
                    <div class="metric-label">Pending</div>
                </div>
                <div class="metric-card running">
                    <div class="metric-value" id="metricRunning">-</div>
                    <div class="metric-label">Running</div>
                </div>
                <div class="metric-card completed">
                    <div class="metric-value" id="metricCompleted">-</div>
                    <div class="metric-label">Completed</div>
                </div>
                <div class="metric-card failed">
                    <div class="metric-value" id="metricFailed">-</div>
                    <div class="metric-label">Failed</div>
                </div>
            </div>
        </div>
        <div class="card">
            <h2>Queue Depths</h2>
            <div class="queue-bars" id="queueBars">
                <div class="queue-bar high">
                    <div class="queue-bar-fill" id="barHigh" style="height:4px"></div>
                    <div class="queue-bar-value" id="valHigh">0</div>
                    <div class="queue-bar-label">HIGH</div>
                </div>
                <div class="queue-bar normal">
                    <div class="queue-bar-fill" id="barNormal" style="height:4px"></div>
                    <div class="queue-bar-value" id="valNormal">0</div>
                    <div class="queue-bar-label">NORMAL</div>
                </div>
                <div class="queue-bar low">
                    <div class="queue-bar-fill" id="barLow" style="height:4px"></div>
                    <div class="queue-bar-value" id="valLow">0</div>
                    <div class="queue-bar-label">LOW</div>
                </div>
            </div>
        </div>
        <div class="card">
            <h2>Running Tasks</h2>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Type</th>
                        <th>Priority</th>
                        <th>Started</th>
                        <th>Duration</th>
                    </tr>
                </thead>
                <tbody id="runningTable">
                    <tr><td colspan="5" class="empty">Loading...</td></tr>
                </tbody>
            </table>
        </div>
        <div class="card">
            <h2>Recent Failed Tasks</h2>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Type</th>
                        <th>Error</th>
                        <th>Retries</th>
                        <th>Failed At</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody id="failedTable">
                    <tr><td colspan="6" class="empty">Loading...</td></tr>
                </tbody>
            </table>
        </div>
    </div>

    <div class="modal-overlay" id="taskModal">
        <div class="modal">
            <button class="close-btn" onclick="closeModal()">&times;</button>
            <h3>Task Detail</h3>
            <div id="taskDetail"></div>
        </div>
    </div>

    <script>
        const API = '/api/v1';

        async function loadStats() {
            try {
                const res = await fetch(API + '/stats');
                const d = await res.json();
                document.getElementById('metricPending').textContent = d.pending + (d.retrying ? '+' + d.retrying : '');
                document.getElementById('metricRunning').textContent = d.running;
                document.getElementById('metricCompleted').textContent = d.completed;
                document.getElementById('metricFailed').textContent = d.failed;
                updateBars(d.queue_high, d.queue_normal, d.queue_low);
            } catch(e) { console.error('Stats error:', e); }
        }

        function updateBars(h, n, l) {
            const max = Math.max(h, n, l, 1);
            const scale = 80;
            document.getElementById('barHigh').style.height = Math.max(4, (h/max)*scale) + 'px';
            document.getElementById('barNormal').style.height = Math.max(4, (n/max)*scale) + 'px';
            document.getElementById('barLow').style.height = Math.max(4, (l/max)*scale) + 'px';
            document.getElementById('valHigh').textContent = h;
            document.getElementById('valNormal').textContent = n;
            document.getElementById('valLow').textContent = l;
        }

        async function loadRunning() {
            try {
                const res = await fetch(API + '/tasks?status=running&limit=50');
                const d = await res.json();
                const tbody = document.getElementById('runningTable');
                if (!d.items || d.items.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="5" class="empty">No running tasks</td></tr>';
                    return;
                }
                const now = Date.now();
                tbody.innerHTML = d.items.map(t => {
                    const started = t.started_at ? new Date(t.started_at) : null;
                    const dur = started ? ((now - started.getTime())/1000).toFixed(1)+'s' : '-';
                    return `<tr>
                        <td><span class="task-id" onclick="viewTask('${t.id}')">${t.id.substring(0,12)}...</span></td>
                        <td>${t.task_type}</td>
                        <td><span class="priority ${t.priority}">${t.priority}</span></td>
                        <td>${started ? started.toLocaleTimeString() : '-'}</td>
                        <td>${dur}</td>
                    </tr>`;
                }).join('');
            } catch(e) { console.error('Running error:', e); }
        }

        async function loadFailed() {
            try {
                const res = await fetch(API + '/tasks?status=failed&limit=20');
                const d = await res.json();
                const tbody = document.getElementById('failedTable');
                if (!d.items || d.items.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="6" class="empty">No failed tasks</td></tr>';
                    return;
                }
                tbody.innerHTML = d.items.map(t => {
                    const failedAt = t.completed_at ? new Date(t.completed_at).toLocaleString() : '-';
                    const errShort = (t.error_message || '').substring(0, 60);
                    return `<tr>
                        <td><span class="task-id" onclick="viewTask('${t.id}')">${t.id.substring(0,12)}...</span></td>
                        <td>${t.task_type}</td>
                        <td class="error-text" title="${(t.error_message||'').replace(/"/g,'&quot;')}">${errShort}</td>
                        <td>${t.retry_count}/${t.max_retries}</td>
                        <td>${failedAt}</td>
                        <td><button class="btn btn-warning btn-sm" onclick="retryTask('${t.id}')">Retry</button></td>
                    </tr>`;
                }).join('');
            } catch(e) { console.error('Failed error:', e); }
        }

        async function retryTask(id) {
            try {
                const res = await fetch(API + '/tasks/' + id + '/retry', { method: 'POST' });
                if (res.ok) {
                    alert('Task re-queued for retry.');
                    refreshAll();
                } else {
                    const d = await res.json();
                    alert('Retry failed: ' + (d.detail || 'Unknown error'));
                }
            } catch(e) { alert('Retry error: ' + e.message); }
        }

        async function viewTask(id) {
            try {
                const res = await fetch(API + '/tasks/' + id);
                const t = await res.json();
                const detail = document.getElementById('taskDetail');
                detail.innerHTML = `
                    <div class="detail-row"><div class="detail-label">ID</div><div class="detail-value" style="font-family:monospace">${t.id}</div></div>
                    <div class="detail-row"><div class="detail-label">Type</div><div class="detail-value">${t.task_type}</div></div>
                    <div class="detail-row"><div class="detail-label">Status</div><div class="detail-value"><span class="status ${t.status}">${t.status}</span></div></div>
                    <div class="detail-row"><div class="detail-label">Priority</div><div class="detail-value"><span class="priority ${t.priority}">${t.priority}</span></div></div>
                    <div class="detail-row"><div class="detail-label">Retries</div><div class="detail-value">${t.retry_count}/${t.max_retries}</div></div>
                    <div class="detail-row"><div class="detail-label">Created</div><div class="detail-value">${new Date(t.created_at).toLocaleString()}</div></div>
                    <div class="detail-row"><div class="detail-label">Started</div><div class="detail-value">${t.started_at ? new Date(t.started_at).toLocaleString() : '-'}</div></div>
                    <div class="detail-row"><div class="detail-label">Completed</div><div class="detail-value">${t.completed_at ? new Date(t.completed_at).toLocaleString() : '-'}</div></div>
                    <div class="detail-row"><div class="detail-label">Tags</div><div class="detail-value">${(t.tags||[]).join(', ') || '-'}</div></div>
                    <div class="detail-row"><div class="detail-label">Params</div><div class="detail-value"><pre>${JSON.stringify(t.params, null, 2)}</pre></div></div>
                    ${t.result ? `<div class="detail-row"><div class="detail-label">Result</div><div class="detail-value"><pre>${JSON.stringify(t.result, null, 2)}</pre></div></div>` : ''}
                    ${t.error_message ? `<div class="detail-row"><div class="detail-label">Error</div><div class="detail-value" style="color:#e74c3c">${t.error_message}</div></div>` : ''}
                    ${t.error_traceback ? `<div class="detail-row"><div class="detail-label">Traceback</div><div class="detail-value"><pre>${t.error_traceback}</pre></div></div>` : ''}
                `;
                document.getElementById('taskModal').classList.add('active');
            } catch(e) { alert('Failed to load task: ' + e.message); }
        }

        function closeModal() {
            document.getElementById('taskModal').classList.remove('active');
        }

        document.getElementById('taskModal').addEventListener('click', function(e) {
            if (e.target === this) closeModal();
        });

        function refreshAll() {
            loadStats();
            loadRunning();
            loadFailed();
        }

        refreshAll();
        setInterval(refreshAll, 10000);
    </script>
</body>
</html>
"""
