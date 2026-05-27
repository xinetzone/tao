"""Symphony HTML 仪表板。

提供内嵌的 HTML+CSS+JS 仪表板页面，用于实时监控编排状态。
"""

from __future__ import annotations


def get_dashboard_html() -> str:
    """返回完整的仪表板 HTML 字符串。

    仪表板显示以下信息：
    - 运行中的 worker 列表（identifier、turn_count、tokens、last_event）
    - 重试队列
    - codex_totals（总令牌数、运行时间）
    - 每 30 秒自动刷新

    Returns:
        完整的 HTML 文档字符串。
    """
    return _DASHBOARD_HTML


_DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Symphony Dashboard</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0f172a;
            color: #e2e8f0;
        }
        .header {
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            color: white;
            padding: 20px 32px;
            border-bottom: 1px solid #334155;
        }
        .header h1 {
            font-size: 22px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .header h1 .dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #22c55e;
            display: inline-block;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.4; }
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        .card {
            background: #1e293b;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            border: 1px solid #334155;
        }
        .card h2 {
            font-size: 16px;
            color: #94a3b8;
            margin-bottom: 16px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            border-bottom: 1px solid #334155;
            padding-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .card h2 .count {
            background: #3b82f6;
            color: white;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 13px;
            font-weight: 500;
        }
        .metrics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 16px;
        }
        .metric-item {
            text-align: center;
            padding: 16px;
            background: #0f172a;
            border-radius: 8px;
            border: 1px solid #334155;
        }
        .metric-value {
            font-size: 28px;
            font-weight: 700;
            color: #60a5fa;
        }
        .metric-value.warn { color: #f59e0b; }
        .metric-value.good { color: #22c55e; }
        .metric-label {
            font-size: 12px;
            color: #64748b;
            margin-top: 6px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            text-align: left;
            padding: 10px 14px;
            border-bottom: 1px solid #1e293b;
        }
        th {
            background: #0f172a;
            font-weight: 500;
            color: #64748b;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        td {
            color: #cbd5e1;
            font-size: 14px;
            font-family: 'SF Mono', 'Fira Code', 'Cascadia Code', monospace;
        }
        tr:hover td {
            background: #1e293b;
        }
        .badge {
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
        }
        .badge.running { background: #1e3a5f; color: #60a5fa; }
        .badge.retrying { background: #3b2f0a; color: #f59e0b; }
        .badge.error { background: #3b0a0a; color: #f87171; }
        .btn {
            padding: 8px 16px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 500;
            transition: background 0.2s;
        }
        .btn-primary {
            background: #3b82f6;
            color: white;
        }
        .btn-primary:hover {
            background: #2563eb;
        }
        .refresh-info {
            font-size: 12px;
            color: #475569;
            margin-top: 12px;
            text-align: right;
        }
        .empty-state {
            text-align: center;
            padding: 40px;
            color: #475569;
        }
        .retry-error {
            color: #f87171;
            max-width: 300px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        .token-value {
            color: #60a5fa;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1><span class="dot"></span> Symphony Dashboard</h1>
    </div>
    <div class="container">
        <!-- 概览指标 -->
        <div class="card">
            <h2>
                Overview
                <button class="btn btn-primary" onclick="loadState()">Refresh</button>
            </h2>
            <div class="metrics">
                <div class="metric-item">
                    <div class="metric-value good" id="runningCount">-</div>
                    <div class="metric-label">Running</div>
                </div>
                <div class="metric-item">
                    <div class="metric-value warn" id="retryingCount">-</div>
                    <div class="metric-label">Retrying</div>
                </div>
                <div class="metric-item">
                    <div class="metric-value" id="completedCount">-</div>
                    <div class="metric-label">Completed</div>
                </div>
                <div class="metric-item">
                    <div class="metric-value" id="totalTokens">-</div>
                    <div class="metric-label">Total Tokens</div>
                </div>
                <div class="metric-item">
                    <div class="metric-value" id="runtimeSeconds">-</div>
                    <div class="metric-label">Runtime</div>
                </div>
                <div class="metric-item">
                    <div class="metric-value" id="maxConcurrent">-</div>
                    <div class="metric-label">Max Concurrent</div>
                </div>
            </div>
        </div>

        <!-- Running Workers -->
        <div class="card">
            <h2>
                Running Workers
                <span class="count" id="runningBadge">0</span>
            </h2>
            <table>
                <thead>
                    <tr>
                        <th>Identifier</th>
                        <th>Session ID</th>
                        <th>Turns</th>
                        <th>Input Tokens</th>
                        <th>Output Tokens</th>
                        <th>Total Tokens</th>
                        <th>Last Event</th>
                        <th>Started At</th>
                    </tr>
                </thead>
                <tbody id="runningTable">
                    <tr><td colspan="8" class="empty-state">Loading...</td></tr>
                </tbody>
            </table>
        </div>

        <!-- Retry Queue -->
        <div class="card">
            <h2>
                Retry Queue
                <span class="count" id="retryingBadge">0</span>
            </h2>
            <table>
                <thead>
                    <tr>
                        <th>Identifier</th>
                        <th>Attempt</th>
                        <th>Error</th>
                    </tr>
                </thead>
                <tbody id="retryTable">
                    <tr><td colspan="3" class="empty-state">Loading...</td></tr>
                </tbody>
            </table>
        </div>

        <!-- Actions -->
        <div class="card">
            <h2>Actions</h2>
            <button class="btn btn-primary" onclick="triggerRefresh()">
                Trigger Immediate Poll
            </button>
            <span id="refreshStatus" style="margin-left: 12px; font-size: 14px; color: #64748b;"></span>
        </div>

        <div class="refresh-info">
            Auto-refresh every 30s &middot; Last updated: <span id="lastUpdated">-</span>
        </div>
    </div>

    <script>
        const API_BASE = '/api/v1';

        function formatTokens(n) {
            if (n == null) return '-';
            if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M';
            if (n >= 1000) return (n / 1000).toFixed(1) + 'K';
            return String(n);
        }

        function formatRuntime(seconds) {
            if (seconds == null) return '-';
            const mins = Math.floor(seconds / 60);
            const secs = Math.floor(seconds % 60);
            if (mins >= 60) {
                const hrs = Math.floor(mins / 60);
                const remainMins = mins % 60;
                return hrs + 'h ' + remainMins + 'm';
            }
            return mins + 'm ' + secs + 's';
        }

        function formatTime(isoStr) {
            if (!isoStr) return '-';
            try {
                return new Date(isoStr).toLocaleString();
            } catch {
                return isoStr;
            }
        }

        async function loadState() {
            try {
                const res = await fetch(API_BASE + '/state');
                const data = await res.json();

                if (data.error) {
                    document.getElementById('runningCount').textContent = '!';
                    document.getElementById('retryingCount').textContent = '!';
                    document.getElementById('completedCount').textContent = '!';
                    document.getElementById('totalTokens').textContent = '!';
                    document.getElementById('runtimeSeconds').textContent = '!';
                    document.getElementById('maxConcurrent').textContent = '!';
                    document.getElementById('runningTable').innerHTML =
                        '<tr><td colspan="8" class="empty-state">' +
                        data.error.message + '</td></tr>';
                    document.getElementById('retryTable').innerHTML =
                        '<tr><td colspan="3" class="empty-state">' +
                        data.error.message + '</td></tr>';
                    return;
                }

                const running = data.running || [];
                const retrying = data.retrying || [];
                const totals = data.codex_totals || {};

                // Overview metrics
                document.getElementById('runningCount').textContent = running.length;
                document.getElementById('retryingCount').textContent = retrying.length;
                document.getElementById('completedCount').textContent = data.completed_count || 0;
                document.getElementById('totalTokens').textContent =
                    formatTokens(totals.total_tokens);
                document.getElementById('runtimeSeconds').textContent =
                    formatRuntime(totals.seconds_running);
                document.getElementById('maxConcurrent').textContent =
                    data.max_concurrent_agents || '-';

                // Running badges
                document.getElementById('runningBadge').textContent = running.length;
                document.getElementById('retryingBadge').textContent = retrying.length;

                // Running table
                const runningTbody = document.getElementById('runningTable');
                if (running.length === 0) {
                    runningTbody.innerHTML =
                        '<tr><td colspan="8" class="empty-state">' +
                        'No running workers</td></tr>';
                } else {
                    runningTbody.innerHTML = running.map(w => '<tr>' +
                        '<td><span class="badge running">' + (w.identifier || '-') + '</span></td>' +
                        '<td>' + (w.session_id || '-') + '</td>' +
                        '<td>' + (w.turn_count || 0) + '</td>' +
                        '<td class="token-value">' + formatTokens(w.tokens?.input_tokens) + '</td>' +
                        '<td class="token-value">' + formatTokens(w.tokens?.output_tokens) + '</td>' +
                        '<td class="token-value">' + formatTokens(w.tokens?.total_tokens) + '</td>' +
                        '<td>' + (w.last_event || '-') + '</td>' +
                        '<td>' + formatTime(w.started_at) + '</td>' +
                    '</tr>').join('');
                }

                // Retry table
                const retryTbody = document.getElementById('retryTable');
                if (retrying.length === 0) {
                    retryTbody.innerHTML =
                        '<tr><td colspan="3" class="empty-state">' +
                        'No retries queued</td></tr>';
                } else {
                    retryTbody.innerHTML = retrying.map(r => '<tr>' +
                        '<td><span class="badge retrying">' + (r.identifier || '-') + '</span></td>' +
                        '<td>' + (r.attempt || 0) + '</td>' +
                        '<td class="retry-error">' + (r.error || '-') + '</td>' +
                    '</tr>').join('');
                }

                document.getElementById('lastUpdated').textContent =
                    new Date().toLocaleTimeString();
            } catch (e) {
                console.error('Failed to load state:', e);
                document.getElementById('runningTable').innerHTML =
                    '<tr><td colspan="8" class="empty-state">Failed to load</td></tr>';
                document.getElementById('retryTable').innerHTML =
                    '<tr><td colspan="3" class="empty-state">Failed to load</td></tr>';
            }
        }

        async function triggerRefresh() {
            const statusEl = document.getElementById('refreshStatus');
            statusEl.textContent = 'Requesting...';
            try {
                const res = await fetch(API_BASE + '/refresh', { method: 'POST' });
                if (res.status === 202) {
                    statusEl.textContent = 'Poll triggered!';
                    setTimeout(() => { statusEl.textContent = ''; }, 3000);
                    // Refresh state after a short delay
                    setTimeout(loadState, 2000);
                } else {
                    const data = await res.json();
                    statusEl.textContent = 'Error: ' + (data.detail?.message || 'Unknown');
                    setTimeout(() => { statusEl.textContent = ''; }, 5000);
                }
            } catch (e) {
                statusEl.textContent = 'Failed: ' + e.message;
                setTimeout(() => { statusEl.textContent = ''; }, 5000);
            }
        }

        // Initial load and auto-refresh
        loadState();
        setInterval(loadState, 30000);
    </script>
</body>
</html>
"""
