"""
限流中间件集成示例

展示如何将 taolib.rate_limiter 集成到 FastAPI 应用中。
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from redis.asyncio import Redis

from taolib.testing.rate_limiter import RateLimiter, RateLimitMiddleware
from taolib.testing.rate_limiter.config import load_rate_limit_config
from taolib.testing.rate_limiter.stats import RateLimitStatsService
from taolib.testing.rate_limiter.store import RedisRateLimitStore
from taolib.testing.rate_limiter.violation_tracker import ViolationTracker


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理。

    启动时：
    1. 加载限流配置
    2. 初始化 Redis 连接
    3. 初始化 MongoDB 连接
    4. 创建限流引擎和中间件
    5. 创建违规追踪器
    6. 创建统计服务

    关闭时：
    1. 关闭 Redis 连接
    2. 关闭 MongoDB 连接
    """
    # 1. 加载配置
    config = load_rate_limit_config()

    # 2. 初始化 Redis
    redis_client = Redis.from_url(config.redis_url)
    store = RedisRateLimitStore(redis_client)

    # 3. 初始化 MongoDB
    mongo_client = AsyncIOMotorClient("mongodb://localhost:27017")
    mongo_db = mongo_client["config_center"]
    violation_collection = mongo_db[config.mongo_collection]

    # 4. 创建限流引擎
    limiter = RateLimiter(config=config, store=store)

    # 5. 创建违规追踪器
    violation_tracker = ViolationTracker(
        mongo_collection=violation_collection,
        ttl_days=config.mongo_violation_ttl_days,
    )

    # 6. 创建 MongoDB 索引
    await violation_tracker.ensure_indexes()

    # 7. 创建统计服务
    stats_service = RateLimitStatsService(
        store=store,
        mongo_collection=violation_collection,
    )

    # 8. 存储到 app.state
    app.state.rate_limiter = limiter
    app.state.violation_tracker = violation_tracker
    app.state.rate_limit_stats_service = stats_service

    yield

    # 关闭时清理资源
    await redis_client.close()
    mongo_client.close()


def create_app() -> FastAPI:
    """创建 FastAPI 应用实例。"""

    app = FastAPI(
        title="Config Center with Rate Limiting",
        version="1.0.0",
        lifespan=lifespan,
    )

    # 添加限流中间件
    app.add_middleware(
        RateLimitMiddleware,
        limiter=app.state.rate_limiter if hasattr(app.state, "rate_limiter") else None,
        violation_tracker=(
            app.state.violation_tracker
            if hasattr(app.state, "violation_tracker")
            else None
        ),
    )

    # 注册业务路由
    # from .api import router
    # app.include_router(router, prefix="/api/v1")

    # 注册限流统计路由
    from taolib.testing.rate_limiter.api.router import router as stats_router

    app.include_router(stats_router, prefix="/api/rate-limit")

    return app


# ============================================================================
# TOML 配置文件示例：rate_limit.toml
# ============================================================================
#
# [rate_limit]
# enabled = true
# default_limit = 100            # 默认每分钟 100 次请求
# window_seconds = 60            # 滑动窗口 60 秒
# redis_url = "redis://localhost:6379/1"
# mongo_violation_ttl_days = 90  # 违规记录保留 90 天
#
# [rate_limit.whitelist]
# ips = ["127.0.0.1", "10.0.0.0/8"]
# user_ids = ["admin-user-id"]
# bypass_paths = ["/health", "/docs", "/openapi.json"]
#
# [rate_limit.path_rules."/api/v1/configs"]
# limit = 50
# window_seconds = 60
# methods = ["GET"]
# description = "配置查询接口"
#
# [rate_limit.path_rules."/api/v1/auth/token"]
# limit = 5
# window_seconds = 60
# methods = ["POST"]
# description = "登录接口（防暴力破解）"
#
# ============================================================================
# 环境变量覆盖（可选）
# ============================================================================
#
# TAOLIB_RATE_LIMIT_CONFIG=/path/to/rate_limit.toml
# TAOLIB_RATE_LIMIT_ENABLED=true
# TAOLIB_RATE_LIMIT_DEFAULT_LIMIT=100
# TAOLIB_RATE_LIMIT_WINDOW_SECONDS=60
# TAOLIB_RATE_LIMIT_REDIS_URL=redis://localhost:6379/1
#
# ============================================================================
# 运行应用
# ============================================================================
#
# uvicorn example_integration:create_app --factory --host 0.0.0.0 --port 8000


