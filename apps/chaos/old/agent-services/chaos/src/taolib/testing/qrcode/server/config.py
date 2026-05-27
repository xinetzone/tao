from pydantic_settings import BaseSettings, SettingsConfigDict


class QRCodeServerConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="QRCODE_")

    host: str = "0.0.0.0"
    port: int = 5174
    debug: bool = False
