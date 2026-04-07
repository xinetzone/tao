"""应用配置模块。

使用 pydantic-settings 定义应用的所有配置项。
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用设置。"""

    model_config = SettingsConfigDict(
        env_prefix="DATA_SYNC_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # MongoDB 配置
    mongo_url: str = Field(
        default="mongodb://localhost:27017", description="MongoDB 连接字符串"
    )
    mongo_db: str = Field(default="data_sync", description="MongoDB 数据库名称")

    # JWT 配置（可选，用于 API 认证）
    jwt_secret: str = Field(default="", description="JWT 密钥（留空则禁用认证）")
    jwt_algorithm: str = Field(default="HS256", description="JWT 算法")

    # 服务器配置
    host: str = Field(default="0.0.0.0", description="监听地址")
    port: int = Field(default=8001, description="监听端口")
    debug: bool = Field(default=False, description="调试模式")

    # CORS 配置
    cors_origins: list[str] = Field(default=["*"], description="允许的 CORS 源")


# 全局设置实例
settings = Settings()  # type: ignore[call-arg]
