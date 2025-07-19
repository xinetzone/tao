"""
Application settings handled using essentials-configuration and Pydantic.

- essentials-configuration is used to read settings from various sources and build the
  configuration root
- Pydantic is used to validate application settings

https://github.com/Neoteroi/essentials-configuration

https://docs.pydantic.dev/latest/usage/settings/
"""
from pathlib import Path
from blacksheep.server.env import get_env, is_development
from config.common import Configuration, ConfigurationBuilder
from config.env import EnvVars
from config.user import UserSettings
from config.toml import TOMLFile
from pydantic import BaseModel


class APIInfo(BaseModel):
    title: str
    version: str


class App(BaseModel):
    show_error_details: bool


class Site(BaseModel):
    copyright: str


class Settings(BaseModel):
    app: App
    info: APIInfo
    site: Site


def default_configuration_builder(root_dir) -> ConfigurationBuilder:
    app_env = get_env() # 获取当前应用环境
    # 创建配置构建器，指定配置源及其优先级
    builder = ConfigurationBuilder(
        TOMLFile(f"{root_dir}/settings.toml"), # 1. 主配置文件
        TOMLFile(f"{root_dir}/settings.{app_env.lower()}.toml", optional=True), # 2. 环境特定配置
        EnvVars("APP_"),  # 3. 环境变量配置
    )
    # 开发环境下添加用户级配置
    if is_development():
        # for development environment, settings stored in the user folder
        # 用于开发环境的用户文件夹配置（可覆盖其他配置）
        builder.add_source(UserSettings())

    return builder


def default_configuration(root_dir: str) -> Configuration:
    builder = default_configuration_builder(root_dir)

    return builder.build()


root_dir = Path(__file__).parents[1]
def load_settings() -> Settings:
    config_root = default_configuration(root_dir)
    return config_root.bind(Settings)
