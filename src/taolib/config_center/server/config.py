"""应用配置模块。

使用 pydantic-settings 定义应用的所有配置项。
"""

from typing import Self

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用设置。"""

    # MongoDB 配置
    mongo_url: str = Field(
        default="mongodb://localhost:27017", description="MongoDB 连接字符串"
    )
    mongo_db: str = Field(default="config_center", description="MongoDB 数据库名称")

    # Redis 配置
    redis_url: str = Field(
        default="redis://localhost:6379", description="Redis 连接字符串"
    )

    # JWT 配置
    jwt_secret: str = Field(default="", description="JWT 密钥（生产环境必须设置，>=32 字符）")
    jwt_algorithm: str = Field(default="HS256", description="JWT 算法")
    access_token_expire_minutes: int = Field(
        default=15, description="Access Token 过期时间（分钟）"
    )
    refresh_token_expire_days: int = Field(
        default=7, description="Refresh Token 过期时间（天）"
    )

    # 服务器配置
    host: str = Field(default="0.0.0.0", description="监听地址")
    port: int = Field(default=8000, description="监听端口")
    debug: bool = Field(default=False, description="调试模式")

    # CORS 配置
    cors_origins: list[str] = Field(default=["*"], description="允许的 CORS 源")

    # 推送服务配置
    push_heartbeat_interval: int = Field(default=30, description="心跳间隔（秒）")
    push_heartbeat_timeout: int = Field(default=70, description="心跳超时（秒）")
    push_ack_timeout: int = Field(default=10, description="ACK 超时（秒）")
    push_max_retries: int = Field(default=3, description="消息最大重试次数")
    push_buffer_max_size: int = Field(default=1000, description="离线消息缓冲上限")
    push_buffer_ttl: int = Field(default=86400, description="离线消息缓冲 TTL（秒）")
    push_instance_id: str = Field(default="", description="服务实例 ID（空则自动生成）")

    @model_validator(mode="after")
    def _validate_secrets(self) -> Self:
        if self.jwt_secret and len(self.jwt_secret) < 32:
            msg = "jwt_secret 长度必须 >= 32 字符"
            raise ValueError(msg)
        return self

    model_config = SettingsConfigDict(
        env_prefix="CONFIG_CENTER_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


# 全局设置实例
settings = Settings()  # type: ignore[call-arg]
