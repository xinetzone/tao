"""邮件服务配置模块。"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """邮件服务配置。

    从环境变量加载，前缀为 EMAIL_SERVICE_。
    """

    model_config = SettingsConfigDict(
        env_prefix="EMAIL_SERVICE_", env_file=".env", case_sensitive=False
    )

    # MongoDB
    mongo_url: str = Field(default="mongodb://localhost:27017")
    mongo_db: str = Field(default="email_service")

    # Redis
    redis_url: str = Field(default="redis://localhost:6379")

    # Server
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8002)
    debug: bool = Field(default=False)
    cors_origins: list[str] = Field(default=["*"])

    # Default sender
    default_sender: str = Field(default="noreply@example.com")
    default_sender_name: str = Field(default="Email Service")
    unsubscribe_base_url: str = Field(default="http://localhost:8002")

    # SendGrid
    sendgrid_api_key: str = Field(default="")

    # Mailgun
    mailgun_api_key: str = Field(default="")
    mailgun_domain: str = Field(default="")

    # Amazon SES
    ses_region: str = Field(default="")
    ses_access_key_id: str = Field(default="")
    ses_secret_access_key: str = Field(default="")

    # SMTP
    smtp_host: str = Field(default="")
    smtp_port: int = Field(default=587)
    smtp_username: str = Field(default="")
    smtp_password: str = Field(default="")
    smtp_use_tls: bool = Field(default=True)

    # Queue
    queue_poll_interval: float = Field(default=1.0)
    queue_batch_size: int = Field(default=10)
    max_retries: int = Field(default=3)


settings = Settings()
