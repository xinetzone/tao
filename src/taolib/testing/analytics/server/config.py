"""应用配置模块。

使用 pydantic-settings 定义分析服务的所有配置项。
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用设置。"""

    model_config = SettingsConfigDict(
        env_prefix="ANALYTICS_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # MongoDB 配置
    mongo_url: str = Field(
        default="mongodb://localhost:27017", description="MongoDB 连接字符串"
    )
    mongo_db: str = Field(default="analytics", description="MongoDB 数据库名称")

    # 服务器配置
    host: str = Field(default="0.0.0.0", description="监听地址")
    port: int = Field(default=8002, description="监听端口")
    debug: bool = Field(default=False, description="调试模式")

    # CORS 配置
    cors_origins: list[str] = Field(default=["*"], description="允许的 CORS 源")

    # API Key 认证（空列表 = 不启用认证）
    api_keys: list[str] = Field(
        default_factory=list, description="允许的 API Key 列表（空 = 不启用认证）"
    )

    # 数据保留配置
    event_ttl_days: int = Field(default=90, description="事件 TTL（天）")
    session_ttl_days: int = Field(default=180, description="会话 TTL（天）")

    # 批量摄入限制
    max_batch_size: int = Field(default=1000, description="单次批量事件最大数量")


# 全局设置实例
settings = Settings()  # type: ignore[call-arg]


