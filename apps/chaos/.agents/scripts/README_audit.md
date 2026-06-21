# 审计功能模块 — EU AI Act Article 12 合规实现

本模块提供完整的审计日志记录功能，满足 EU AI Act Article 12（记录留存）要求。

## 模块组成

```
.agents/scripts/
├── audit_logger.py              # 核心审计日志记录器
├── cleanup_audit_logs.py        # 日志清理脚本
└── audit_integration_example.py # 集成示例
```

## 快速开始

### 1. 基础用法

```python
from audit_logger import create_audit_logger

# 创建审计日志记录器
audit = create_audit_logger()

# 记录 Agent 操作
audit.log_action(
    agent_id="code-review-agent",
    action="review_pull_request",
    input_data={"pr_id": 123},
    output_data={"approved": True},
    user_id="developer@company.com",
)
```

### 2. 集成到 Agent 执行流程

```python
from audit_logger import create_audit_logger

# 创建审计日志记录器和执行器
audit = create_audit_logger()
executor = AuditedAgentExecutor(audit)

# 执行 Agent（自动记录审计日志）
result = executor.execute(agent, task, user_id="user@example.com")
```

### 3. 使用装饰器

```python
from audit_logger import create_audit_logger, with_audit

audit = create_audit_logger()

@with_audit(audit)
def execute_task(agent, task):
    return agent.run(task)

# 自动记录审计日志
result = execute_task(agent, task)
```

## 核心功能

### AuditLogger 类

**主要方法**:

| 方法 | 说明 |
|------|------|
| `log_action()` | 记录 Agent 操作 |
| `log_error()` | 记录错误 |
| `log_approval()` | 记录审批操作 |
| `query()` | 查询审计日志 |
| `get_statistics()` | 获取统计信息 |
| `start_session()` | 开始审计会话 |
| `end_session()` | 结束审计会话 |
| `cleanup_old_logs()` | 清理过期日志 |
| `export_logs()` | 导出审计日志 |

**配置参数**:

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `log_dir` | `.agents/audit_logs` | 日志目录路径 |
| `retention_days` | 365 | 日志保留天数 |
| `max_file_size_mb` | 100 | 单个日志文件最大大小 |
| `compress_after_days` | 30 | 多少天后压缩日志 |

### 审计日志格式

每条审计日志包含以下字段：

```json
{
  "timestamp": "2026-06-22T00:17:04.123456",
  "agent_id": "code-review-agent",
  "action": "review_pull_request",
  "input_hash": "a1b2c3d4e5f6g7h8",
  "output_hash": "i9j0k1l2m3n4o5p6",
  "human_approved": false,
  "metadata": {},
  "level": "INFO",
  "session_id": "session_20260622001704",
  "user_id": "developer@company.com",
  "duration_ms": 150
}
```

**字段说明**:

- `timestamp`: 时间戳（ISO 8601 格式）
- `agent_id`: Agent 标识符
- `action`: 操作类型
- `input_hash`: 输入数据哈希（SHA-256 前 16 位，避免存储敏感数据）
- `output_hash`: 输出数据哈希
- `human_approved`: 是否经过人工审批
- `metadata`: 元数据
- `level`: 日志级别（INFO, WARNING, ERROR, CRITICAL）
- `session_id`: 会话 ID（用于关联同一会话的多个操作）
- `user_id`: 用户 ID
- `duration_ms`: 操作耗时（毫秒）

## 使用场景

### 场景 1: 记录 Agent 操作

```python
audit = create_audit_logger()

# 记录代码审查操作
audit.log_action(
    agent_id="code-review-agent",
    action="review_pull_request",
    input_data={
        "pr_id": 123,
        "files": ["src/main.py", "src/utils.py"],
    },
    output_data={
        "approved": True,
        "comments": ["LGTM"],
    },
    user_id="developer@company.com",
)
```

### 场景 2: 记录审批流程

```python
audit = create_audit_logger()

# 记录审批请求
request_id = "req_001"
audit.log_action(
    agent_id="approval-workflow",
    action="approval_requested",
    input_data={"action": "production_deploy"},
    metadata={"approver_role": "Tech Lead"},
)

# 记录审批决策
audit.log_approval(
    request_id=request_id,
    action="production_deploy",
    approver="tech-lead@company.com",
    approved=True,
    comment="代码已审查，可以部署",
)
```

### 场景 3: 批量任务执行

```python
audit = create_audit_logger()
batch_executor = BatchExecutor(audit)

# 开始会话
session_id = audit.start_session()

# 批量执行任务
tasks = [
    Task(action="task_1", input_data={"id": 1}),
    Task(action="task_2", input_data={"id": 2}),
    Task(action="task_3", input_data={"id": 3}),
]

results = batch_executor.execute_batch(agent, tasks, user_id="batch-user")

# 结束会话
audit.end_session()

# 查询会话日志
entries = audit.query(session_id=session_id)
```

### 场景 4: 查询审计日志

```python
from datetime import datetime, timedelta

audit = create_audit_logger()

# 查询最近 7 天的日志
start_time = datetime.now() - timedelta(days=7)
entries = audit.query(start_time=start_time, limit=100)

# 查询特定 Agent 的日志
entries = audit.query(agent_id="code-review-agent", limit=50)

# 查询特定操作的日志
entries = audit.query(action="production_deploy", limit=20)
```

### 场景 5: 获取统计信息

```python
audit = create_audit_logger()

# 获取统计信息
stats = audit.get_statistics()

print(f"总操作数: {stats['total_actions']}")
print(f"唯一 Agent 数: {stats['unique_agents']}")
print(f"人工审批率: {stats['human_approval_rate']:.2%}")
print(f"错误率: {stats['error_rate']:.2%}")
```

## 日志清理

### 手动清理

```bash
# 基础清理（默认保留 365 天）
uv run python .agents/scripts/cleanup_audit_logs.py

# 指定保留天数
uv run python .agents/scripts/cleanup_audit_logs.py --retention-days 180

# 干运行（预览）
uv run python .agents/scripts/cleanup_audit_logs.py --dry-run --verbose
```

### 定时清理（Cron）

```bash
# 每天凌晨 2 点清理
0 2 * * * cd /path/to/project && uv run python .agents/scripts/cleanup_audit_logs.py
```

## 日志导出

```python
from datetime import datetime, timedelta

audit = create_audit_logger()

# 导出最近 30 天的日志（JSON 格式）
start_time = datetime.now() - timedelta(days=30)
count = audit.export_logs(
    output_path="audit_export.json",
    start_time=start_time,
    format="json",
)

print(f"导出 {count} 条记录")

# 导出为 CSV 格式
count = audit.export_logs(
    output_path="audit_export.csv",
    start_time=start_time,
    format="csv",
)
```

## 合规性验证

### 运行合规检查

```bash
# 检查 EU AI Act 合规性
uv run python .agents/scripts/check_eu_ai_act.py --verbose
```

### 预期结果

整改完成后，应该看到：

```
Art 12
----------------------------------------------------------------------
[OK] 满足 [HIGH] 所有 AI Agent 操作必须可审计
   键: constraints.strong.audit_all_actions
   详情: 已启用全量审计
[OK] 满足 [MED] 审计日志必须保留足够时长
   键: constraints.strong.audit_retention_days
   详情: 日志保留 365 天（>= 365 天）
```

## 性能考虑

### 日志文件轮转

- 单个日志文件最大 100 MB
- 按月自动轮转
- 旧日志自动压缩（30 天后）

### 数据哈希

- 输入/输出数据使用 SHA-256 哈希
- 只存储前 16 位，避免日志过大
- 敏感数据不直接存储

### 查询优化

- 日志按时间倒序查询
- 支持多条件过滤
- 支持压缩文件查询

## 故障排查

### 问题 1: 日志文件未创建

**检查**:
```bash
ls -la .agents/audit_logs/
```

**解决**:
```bash
# 手动创建目录
mkdir -p .agents/audit_logs
```

### 问题 2: 权限错误

**检查**:
```bash
# 检查目录权限
ls -ld .agents/audit_logs/
```

**解决**:
```bash
# 修改权限
chmod 755 .agents/audit_logs/
```

### 问题 3: 日志查询慢

**优化**:
- 减少查询时间范围
- 使用更具体的过滤条件
- 定期清理旧日志

## 最佳实践

1. **会话管理**: 使用 `start_session()` 和 `end_session()` 关联相关操作
2. **错误记录**: 使用 `log_error()` 记录异常，包含完整错误信息
3. **审批记录**: 使用 `log_approval()` 记录审批决策
4. **定期清理**: 设置定时任务定期清理过期日志
5. **数据脱敏**: 输入/输出数据自动哈希，避免存储敏感信息
6. **性能监控**: 使用 `duration_ms` 记录操作耗时

## 相关文档

- [EU AI Act 合规整改清单](../docs/tech/eu-ai-act-remediation-checklist.md)
- [AGENTS.md 实施路线图](../docs/tech/agents-md-implementation-roadmap.md)
- [constraints.toml 配置示例](../constraints.toml)

## 版本历史

- **v1.0** (2026-06-22): 初始版本，实现核心审计功能
