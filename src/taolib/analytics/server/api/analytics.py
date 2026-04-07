"""分析查询路由。"""

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Query, Request

router = APIRouter()

ANALYTICS_API_DESCRIPTION = """
分析查询 API 提供用户行为分析和统计功能。

## 功能模块

- **概览统计**：PV、UV、会话数等核心指标
- **转化漏斗**：分析用户转化路径
- **功能排名**：功能使用热度排行
- **导航路径**：用户行为轨迹分析
- **停留分析**：区域停留时间统计
- **流失分析**：用户流失点识别

## 时间范围

所有接口支持通过 `start` 和 `end` 参数指定时间范围，格式为 ISO 8601。
默认查询最近 7 天的数据。
"""


def _parse_time_range(start: str | None, end: str | None) -> tuple[datetime, datetime]:
    """解析时间范围参数，默认最近 7 天。"""
    now = datetime.now(UTC)
    end_dt = datetime.fromisoformat(end) if end else now
    start_dt = datetime.fromisoformat(start) if start else end_dt - timedelta(days=7)

    # 确保时区
    if start_dt.tzinfo is None:
        start_dt = start_dt.replace(tzinfo=UTC)
    if end_dt.tzinfo is None:
        end_dt = end_dt.replace(tzinfo=UTC)

    return start_dt, end_dt


def get_analytics_service(request: Request):
    """获取 AnalyticsService 实例。"""
    from ...repository.event_repo import EventRepository
    from ...repository.session_repo import SessionRepository
    from ...services.analytics_service import AnalyticsService

    event_repo = EventRepository(request.app.state.db.analytics_events)
    session_repo = SessionRepository(request.app.state.db.analytics_sessions)
    return AnalyticsService(event_repo, session_repo)


@router.get(
    "/overview",
    summary="获取概览统计",
    description="""
获取应用的核心统计指标概览。

## 查询参数

- `app_id`: 应用标识（必填）
- `start`: 开始时间（ISO 格式，可选）
- `end`: 结束时间（ISO 格式，可选）

## 响应示例

```json
{
  "pv": 125000,
  "uv": 15000,
  "sessions": 8500,
  "avg_session_duration": 180,
  "bounce_rate": 0.35,
  "new_users": 1200
}
```
""",
    responses={
        200: {
            "description": "成功获取概览统计",
            "content": {
                "application/json": {
                    "example": {
                        "pv": 125000,
                        "uv": 15000,
                        "sessions": 8500,
                        "avg_session_duration": 180,
                    }
                }
            },
        }
    },
)
async def get_overview(
    request: Request,
    app_id: str = Query(..., description="应用标识"),
    start: str | None = Query(None, description="开始时间 (ISO 格式)"),
    end: str | None = Query(None, description="结束时间 (ISO 格式)"),
):
    """获取概览统计。"""
    start_dt, end_dt = _parse_time_range(start, end)
    service = get_analytics_service(request)
    return await service.get_overview(app_id, start_dt, end_dt)


@router.get(
    "/funnel",
    summary="获取转化漏斗分析",
    description="""
分析用户在指定步骤间的转化率。

## 查询参数

- `app_id`: 应用标识（必填）
- `steps`: 漏斗步骤，逗号分隔（必填）
- `start`: 开始时间（可选）
- `end`: 结束时间（可选）

## 请求示例

```
GET /funnel?app_id=myapp&steps=view_product,add_cart,checkout,payment
```

## 响应示例

```json
{
  "steps": [
    {"name": "view_product", "count": 10000, "rate": 1.0},
    {"name": "add_cart", "count": 3000, "rate": 0.3},
    {"name": "checkout", "count": 1500, "rate": 0.15},
    {"name": "payment", "count": 800, "rate": 0.08}
  ],
  "total_conversion": 0.08
}
```
""",
    responses={
        200: {
            "description": "成功获取漏斗分析",
            "content": {
                "application/json": {
                    "example": {
                        "steps": [
                            {"name": "step1", "count": 10000, "rate": 1.0},
                            {"name": "step2", "count": 5000, "rate": 0.5},
                        ]
                    }
                }
            },
        }
    },
)
async def get_funnel(
    request: Request,
    app_id: str = Query(..., description="应用标识"),
    steps: str = Query(..., description="漏斗步骤（逗号分隔）"),
    start: str | None = Query(None, description="开始时间 (ISO 格式)"),
    end: str | None = Query(None, description="结束时间 (ISO 格式)"),
):
    """获取转化漏斗分析。"""
    start_dt, end_dt = _parse_time_range(start, end)
    step_list = [s.strip() for s in steps.split(",") if s.strip()]
    service = get_analytics_service(request)
    return await service.get_funnel(app_id, step_list, start_dt, end_dt)


@router.get(
    "/features",
    summary="获取功能使用排名",
    description="""
获取应用功能的使用热度排名。

## 查询参数

- `app_id`: 应用标识（必填）
- `start`: 开始时间（可选）
- `end`: 结束时间（可选）
- `limit`: 返回数量（默认 20，最大 100）

## 响应示例

```json
{
  "features": [
    {"name": "search", "count": 50000, "unique_users": 8000},
    {"name": "export", "count": 25000, "unique_users": 5000},
    {"name": "share", "count": 15000, "unique_users": 3000}
  ]
}
```
""",
    responses={
        200: {"description": "成功获取功能排名"}
    },
)
async def get_features(
    request: Request,
    app_id: str = Query(..., description="应用标识"),
    start: str | None = Query(None, description="开始时间 (ISO 格式)"),
    end: str | None = Query(None, description="结束时间 (ISO 格式)"),
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
):
    """获取功能使用排名。"""
    start_dt, end_dt = _parse_time_range(start, end)
    service = get_analytics_service(request)
    return await service.get_feature_ranking(app_id, start_dt, end_dt, limit)


@router.get(
    "/paths",
    summary="获取用户导航路径",
    description="""
分析用户在应用内的导航轨迹。

## 查询参数

- `app_id`: 应用标识（必填）
- `start`: 开始时间（可选）
- `end`: 结束时间（可选）
- `limit`: 返回数量（默认 50，最大 200）

## 响应示例

```json
{
  "paths": [
    {
      "sequence": ["home", "product", "cart", "checkout"],
      "count": 1500,
      "avg_duration": 180
    }
  ]
}
```
""",
    responses={
        200: {"description": "成功获取导航路径"}
    },
)
async def get_paths(
    request: Request,
    app_id: str = Query(..., description="应用标识"),
    start: str | None = Query(None, description="开始时间 (ISO 格式)"),
    end: str | None = Query(None, description="结束时间 (ISO 格式)"),
    limit: int = Query(50, ge=1, le=200, description="返回数量"),
):
    """获取用户导航路径。"""
    start_dt, end_dt = _parse_time_range(start, end)
    service = get_analytics_service(request)
    return await service.get_navigation_paths(app_id, start_dt, end_dt, limit)


@router.get(
    "/retention",
    summary="获取停留时间分析",
    description="""
分析用户在各个区域的平均停留时间。

## 查询参数

- `app_id`: 应用标识（必填）
- `start`: 开始时间（可选）
- `end`: 结束时间（可选）

## 响应示例

```json
{
  "areas": [
    {"name": "product_detail", "avg_duration": 120, "visits": 5000},
    {"name": "checkout", "avg_duration": 180, "visits": 2000}
  ]
}
```
""",
    responses={
        200: {"description": "成功获取停留分析"}
    },
)
async def get_retention(
    request: Request,
    app_id: str = Query(..., description="应用标识"),
    start: str | None = Query(None, description="开始时间 (ISO 格式)"),
    end: str | None = Query(None, description="结束时间 (ISO 格式)"),
):
    """获取区域停留时间分析。"""
    start_dt, end_dt = _parse_time_range(start, end)
    service = get_analytics_service(request)
    return await service.get_retention(app_id, start_dt, end_dt)


@router.get(
    "/drop-off",
    summary="获取流失点分析",
    description="""
分析用户在流程中的流失点。

## 查询参数

- `app_id`: 应用标识（必填）
- `steps`: 流程步骤，逗号分隔（必填）
- `start`: 开始时间（可选）
- `end`: 结束时间（可选）

## 请求示例

```
GET /drop-off?app_id=myapp&steps=landing,signup,verify,complete
```

## 响应示例

```json
{
  "drop_offs": [
    {"step": "signup", "drop_count": 3000, "drop_rate": 0.3},
    {"step": "verify", "drop_count": 1500, "drop_rate": 0.15}
  ]
}
```
""",
    responses={
        200: {"description": "成功获取流失分析"}
    },
)
async def get_drop_off(
    request: Request,
    app_id: str = Query(..., description="应用标识"),
    steps: str = Query(..., description="流程步骤（逗号分隔）"),
    start: str | None = Query(None, description="开始时间 (ISO 格式)"),
    end: str | None = Query(None, description="结束时间 (ISO 格式)"),
):
    """获取流失点分析。"""
    start_dt, end_dt = _parse_time_range(start, end)
    step_list = [s.strip() for s in steps.split(",") if s.strip()]
    service = get_analytics_service(request)
    return await service.get_drop_off(app_id, step_list, start_dt, end_dt)
