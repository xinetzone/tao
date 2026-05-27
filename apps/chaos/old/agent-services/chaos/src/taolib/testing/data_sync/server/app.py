"""FastAPI 应用工厂模块。

创建和配置 FastAPI 应用实例。
"""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from motor.motor_asyncio import AsyncIOMotorClient

from .api.router import api_router
from .config import settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """应用生命周期管理。"""
    # 启动时执行
    logger.info("Starting data sync server...")

    # 初始化 MongoDB
    mongo_client = AsyncIOMotorClient(settings.mongo_url)
    app.state.mongo_client = mongo_client
    app.state.db = mongo_client[settings.mongo_db]

    # 创建索引
    await app.state.db.sync_jobs.create_index("name", unique=True)
    await app.state.db.sync_jobs.create_index("enabled")
    await app.state.db.sync_logs.create_index("job_id")
    await app.state.db.sync_logs.create_index([("created_at", -1)])
    await app.state.db.sync_checkpoints.create_index(
        [("job_id", 1), ("collection_name", 1)],
        unique=True,
    )
    await app.state.db.sync_failures.create_index("job_id")
    await app.state.db.sync_failures.create_index(
        "created_at",
        expireAfterSeconds=604800,
    )  # 7 days TTL

    logger.info("Data sync server started.")

    yield

    # 关闭时执行
    logger.info("Shutting down data sync server...")
    mongo_client.close()
    logger.info("Data sync server shut down.")


def create_app() -> FastAPI:
    """创建 FastAPI 应用实例。"""
    app = FastAPI(
        title="Data Sync API",
        description="MongoDB 数据同步管理 API",
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

    # 注册静态文件路由（用于监控仪表板）
    @app.get("/dashboard", response_class=HTMLResponse)
    async def dashboard() -> str:
        """简单的监控仪表板。"""
        return _DASHBOARD_HTML

    return app


_DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Data Sync Dashboard</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 20px; }
        .header h1 { font-size: 24px; font-weight: 500; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .card { background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .card h2 { font-size: 18px; color: #333; margin-bottom: 15px; border-bottom: 1px solid #eee; padding-bottom: 10px; }
        table { width: 100%; border-collapse: collapse; }
        th, td { text-align: left; padding: 12px; border-bottom: 1px solid #eee; }
        th { background: #f8f9fa; font-weight: 500; color: #666; }
        .status { padding: 4px 8px; border-radius: 4px; font-size: 12px; }
        .status.pending { background: #fff3cd; color: #856404; }
        .status.running { background: #cce5ff; color: #004085; }
        .status.completed { background: #d4edda; color: #155724; }
        .status.failed { background: #f8d7da; color: #721c24; }
        .btn { padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; }
        .btn-primary { background: #3498db; color: white; }
        .btn-primary:hover { background: #2980b9; }
        .btn-danger { background: #e74c3c; color: white; }
        .btn-danger:hover { background: #c0392b; }
        .metric { display: flex; gap: 30px; flex-wrap: wrap; }
        .metric-item { text-align: center; min-width: 120px; }
        .metric-value { font-size: 32px; font-weight: 600; color: #3498db; }
        .metric-value.danger { color: #e74c3c; }
        .metric-label { font-size: 14px; color: #666; margin-top: 5px; }
        .refresh-btn { float: right; }
        .tabs { display: flex; gap: 8px; margin-bottom: 15px; }
        .tab { padding: 6px 16px; border: 1px solid #ddd; border-radius: 4px; cursor: pointer; background: white; }
        .tab.active { background: #3498db; color: white; border-color: #3498db; }
        .truncated { max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Data Sync Dashboard</h1>
    </div>
    <div class="container">
        <div class="card">
            <h2>Overview</h2>
            <div class="metric">
                <div class="metric-item">
                    <div class="metric-value" id="totalJobs">-</div>
                    <div class="metric-label">Total Jobs</div>
                </div>
                <div class="metric-item">
                    <div class="metric-value" id="activeJobs">-</div>
                    <div class="metric-label">Active Jobs</div>
                </div>
                <div class="metric-item">
                    <div class="metric-value" id="totalLogs">-</div>
                    <div class="metric-label">Total Runs</div>
                </div>
                <div class="metric-item">
                    <div class="metric-value danger" id="failedLogs">-</div>
                    <div class="metric-label">Failed</div>
                </div>
                <div class="metric-item">
                    <div class="metric-value danger" id="totalFailures">-</div>
                    <div class="metric-label">Failure Records</div>
                </div>
            </div>
        </div>
        <div class="card">
            <h2>
                Sync Jobs
                <button class="btn btn-primary refresh-btn" onclick="loadJobs()">Refresh</button>
            </h2>
            <table>
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Scope</th>
                        <th>Mode</th>
                        <th>Last Run</th>
                        <th>Status</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody id="jobsTable">
                    <tr><td colspan="6">Loading...</td></tr>
                </tbody>
            </table>
        </div>
        <div class="card">
            <h2>
                Recent Logs
                <button class="btn btn-primary refresh-btn" onclick="loadLogs()">Refresh</button>
            </h2>
            <table>
                <thead>
                    <tr>
                        <th>Job</th>
                        <th>Status</th>
                        <th>Started</th>
                        <th>Duration</th>
                        <th>Extracted</th>
                        <th>Loaded</th>
                        <th>Failed</th>
                    </tr>
                </thead>
                <tbody id="logsTable">
                    <tr><td colspan="7">Loading...</td></tr>
                </tbody>
            </table>
        </div>
        <div class="card">
            <h2>
                Recent Failures
                <button class="btn btn-primary refresh-btn" onclick="loadFailures()">Refresh</button>
            </h2>
            <table>
                <thead>
                    <tr>
                        <th>Document ID</th>
                        <th>Collection</th>
                        <th>Phase</th>
                        <th>Error Type</th>
                        <th>Error Message</th>
                        <th>Time</th>
                    </tr>
                </thead>
                <tbody id="failuresTable">
                    <tr><td colspan="6">Loading...</td></tr>
                </tbody>
            </table>
        </div>
    </div>
    <script>
        const API_BASE = '/api/v1';

        async function loadJobs() {
            try {
                const res = await fetch(API_BASE + '/jobs');
                const data = await res.json();
                renderJobs(data.items);
                document.getElementById('totalJobs').textContent = data.total;
                document.getElementById('activeJobs').textContent =
                    data.items.filter(j => j.enabled).length;
            } catch (e) {
                console.error('Failed to load jobs:', e);
            }
        }

        function renderJobs(jobs) {
            const tbody = document.getElementById('jobsTable');
            if (jobs.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6">No jobs found</td></tr>';
                return;
            }
            tbody.innerHTML = jobs.map(job => `
                <tr>
                    <td>${job.name}</td>
                    <td>${job.scope}</td>
                    <td>${job.mode}</td>
                    <td>${job.last_run_at
                        ? new Date(job.last_run_at).toLocaleString()
                        : '-'}</td>
                    <td><span class="status ${job.enabled ? 'completed' : 'pending'}">
                        ${job.enabled ? 'Enabled' : 'Disabled'}</span></td>
                    <td>
                        <button class="btn btn-primary" onclick="runJob('${job._id || job.id}')">
                            Run</button>
                    </td>
                </tr>
            `).join('');
        }

        async function loadLogs() {
            try {
                const res = await fetch(API_BASE + '/logs?limit=20');
                const data = await res.json();
                renderLogs(data.items);
                document.getElementById('totalLogs').textContent = data.total;
                document.getElementById('failedLogs').textContent =
                    data.items.filter(l => l.status === 'failed').length;
            } catch (e) {
                console.error('Failed to load logs:', e);
            }
        }

        function renderLogs(logs) {
            const tbody = document.getElementById('logsTable');
            if (logs.length === 0) {
                tbody.innerHTML = '<tr><td colspan="7">No logs found</td></tr>';
                return;
            }
            tbody.innerHTML = logs.map(log => {
                const m = log.metrics || {};
                return `
                <tr>
                    <td>${log.job_name}</td>
                    <td><span class="status ${log.status}">${log.status}</span></td>
                    <td>${new Date(log.started_at).toLocaleString()}</td>
                    <td>${log.duration_seconds
                        ? log.duration_seconds.toFixed(1) + 's'
                        : '-'}</td>
                    <td>${m.total_extracted || 0}</td>
                    <td>${m.total_loaded || 0}</td>
                    <td>${m.total_failed || 0}</td>
                </tr>`;
            }).join('');
        }

        async function loadFailures() {
            try {
                const res = await fetch(API_BASE + '/failures?limit=20');
                const data = await res.json();
                renderFailures(data.items);
                document.getElementById('totalFailures').textContent = data.total;
            } catch (e) {
                console.error('Failed to load failures:', e);
            }
        }

        function renderFailures(failures) {
            const tbody = document.getElementById('failuresTable');
            if (failures.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6">No failures found</td></tr>';
                return;
            }
            tbody.innerHTML = failures.map(f => `
                <tr>
                    <td class="truncated">${f.document_id || '-'}</td>
                    <td>${f.collection_name || '-'}</td>
                    <td><span class="status failed">${f.phase || '-'}</span></td>
                    <td>${f.error_type || '-'}</td>
                    <td class="truncated">${f.error_message || '-'}</td>
                    <td>${f.created_at
                        ? new Date(f.created_at).toLocaleString()
                        : '-'}</td>
                </tr>
            `).join('');
        }

        async function loadMetrics() {
            try {
                const res = await fetch(API_BASE + '/metrics');
                const data = await res.json();
                document.getElementById('totalJobs').textContent = data.total_jobs;
                document.getElementById('totalLogs').textContent = data.recent_runs;
                document.getElementById('failedLogs').textContent = data.failed;
            } catch (e) {
                // Fall back to job/log based counts
            }
        }

        async function runJob(jobId) {
            try {
                const res = await fetch(
                    API_BASE + '/jobs/' + jobId + '/run',
                    { method: 'POST' },
                );
                const data = await res.json();
                alert('Job ' + data.status + ': ' + data.message);
                loadLogs();
            } catch (e) {
                alert('Failed to run job: ' + e.message);
            }
        }

        // Load data on page load
        loadJobs();
        loadLogs();
        loadFailures();
        loadMetrics();
        setInterval(() => {
            loadJobs();
            loadLogs();
            loadFailures();
            loadMetrics();
        }, 30000); // Auto-refresh every 30s
    </script>
</body>
</html>
"""
