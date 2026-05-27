"""应用配置模块。

使用 pydantic-settings 定义应用的所有配置项。
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用设置。"""

    model_config = SettingsConfigDict(
        env_prefix="TASK_QUEUE_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # MongoDB 配置
    mongo_url: str = Field(
        default="mongodb://localhost:27017", description="MongoDB 连接字符串"
    )
    mongo_db: str = Field(default="task_queue", description="MongoDB 数据库名称")

    # Redis 配置
    redis_url: str = Field(
        default="redis://localhost:6379/0", description="Redis 连接字符串"
    )
    redis_key_prefix: str = Field(default="tq", description="Redis 键前缀")

    # Worker 配置
    num_workers: int = Field(default=3, description="工作者数量", ge=1, le=20)

    # 服务器配置
    host: str = Field(default="0.0.0.0", description="监听地址")
    port: int = Field(default=8002, description="监听端口")
    debug: bool = Field(default=False, description="调试模式")

    # CORS 配置
    cors_origins: list[str] = Field(default=["*"], description="允许的 CORS 源")


# 全局设置实例
settings = Settings()  # type: ignore[call-arg]
