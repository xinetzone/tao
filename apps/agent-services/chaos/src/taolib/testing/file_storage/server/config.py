"""服务器配置模块。

使用 pydantic-settings 管理服务器配置。
"""

from typing import Self

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """文件存储服务配置。"""

    # MongoDB
    mongo_url: str = Field(
        default="mongodb://localhost:27017", description="MongoDB 连接"
    )
    mongo_db: str = Field(default="file_storage", description="数据库名称")

    # Redis
    redis_url: str = Field(default="redis://localhost:6379", description="Redis 连接")

    # 存储后端
    storage_backend: str = Field(
        default="local", description="存储后端类型（local/s3）"
    )
    s3_endpoint_url: str | None = Field(default=None, description="S3 兼容端点")
    s3_access_key: str = Field(default="", description="S3 Access Key")
    s3_secret_key: str = Field(default="", description="S3 Secret Key")
    s3_region: str = Field(default="us-east-1", description="S3 区域")
    local_storage_path: str = Field(default="./storage", description="本地存储路径")

    # CDN
    cdn_enabled: bool = Field(default=False, description="是否启用 CDN")
    cdn_base_url: str = Field(default="", description="CDN 基础 URL")
    cdn_signing_key: str = Field(default="", description="CDN 签名密钥")

    # 签名 URL
    signed_url_secret: str = Field(
        default="", description="签名 URL 密钥（生产环境必须设置，>=32 字符）"
    )
    signed_url_default_expires: int = Field(
        default=3600, description="签名 URL 默认过期秒数"
    )

    # 上传会话
    upload_session_ttl_hours: int = Field(
        default=24, description="上传会话过期时间（小时）"
    )
    max_chunk_size_bytes: int = Field(
        default=100 * 1024 * 1024, description="最大分片大小（100MB）"
    )
    default_chunk_size_bytes: int = Field(
        default=5 * 1024 * 1024, description="默认分片大小（5MB）"
    )

    # 缩略图
    thumbnail_enabled: bool = Field(default=True, description="是否生成缩略图")

    # 服务器
    host: str = Field(default="0.0.0.0", description="监听地址")
    port: int = Field(default=8002, description="监听端口")
    debug: bool = Field(default=False, description="调试模式")
    cors_origins: list[str] = Field(
        default_factory=lambda: ["*"], description="CORS 源"
    )

    model_config = {
        "env_prefix": "FILE_STORAGE_",
        "env_file": ".env",
        "case_sensitive": False,
    }

    @model_validator(mode="after")
    def _validate_secrets(self) -> Self:
        if self.signed_url_secret and len(self.signed_url_secret) < 32:
            msg = "signed_url_secret 长度必须 >= 32 字符"
            raise ValueError(msg)
        return self


settings = Settings()


