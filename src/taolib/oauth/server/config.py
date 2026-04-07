"""OAuth 应用配置模块。

使用 pydantic-settings 定义 OAuth 服务的所有配置项。
"""

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class OAuthSettings(BaseSettings):
    """OAuth 服务设置。"""

    model_config = SettingsConfigDict(
        env_prefix="OAUTH_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # MongoDB 配置
    mongo_url: str = Field(
        default="mongodb://localhost:27017", description="MongoDB 连接字符串"
    )
    mongo_db: str = Field(default="taolib_oauth", description="MongoDB 数据库名称")

    # Redis 配置
    redis_url: str = Field(
        default="redis://localhost:6379", description="Redis 连接字符串"
    )

    # JWT 配置（应与 config_center 共享）
    jwt_secret: str = Field(default="", description="JWT 密钥（生产环境必须设置，>=32 字符）")
    jwt_algorithm: str = Field(default="HS256", description="JWT 算法")
    access_token_expire_minutes: int = Field(
        default=15, description="Access Token 过期时间（分钟）"
    )
    refresh_token_expire_days: int = Field(
        default=7, description="Refresh Token 过期时间（天）"
    )

    # 加密配置
    encryption_key: str = Field(
        default="", description="Fernet 加密密钥（必须在生产环境设置）"
    )

    # OAuth 流程配置
    state_ttl_seconds: int = Field(default=600, description="CSRF State 有效期（秒）")
    session_ttl_hours: int = Field(default=24, description="会话有效期（小时）")
    default_redirect_uri: str = Field(
        default="http://localhost:8002/api/v1/oauth/callback",
        description="默认回调 URI",
    )

    # 引导凭证（用于首次部署）
    google_client_id: str = Field(default="", description="Google Client ID")
    google_client_secret: str = Field(default="", description="Google Client Secret")
    github_client_id: str = Field(default="", description="GitHub Client ID")
    github_client_secret: str = Field(default="", description="GitHub Client Secret")

    # 服务器配置
    host: str = Field(default="0.0.0.0", description="监听地址")
    port: int = Field(default=8002, description="监听端口")
    debug: bool = Field(default=False, description="调试模式")

    # CORS 配置
    cors_origins: list[str] = Field(default=["*"], description="允许的 CORS 源")

    @model_validator(mode="after")
    def _validate_secrets(self) -> OAuthSettings:
        if self.jwt_secret and len(self.jwt_secret) < 32:
            msg = "jwt_secret 长度必须 >= 32 字符"
            raise ValueError(msg)
        return self


# 全局设置实例
settings = OAuthSettings()  # type: ignore[call-arg]
