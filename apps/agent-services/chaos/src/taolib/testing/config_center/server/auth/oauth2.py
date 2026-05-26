"""OAuth2 认证模块。

配置 OAuth2 Password Bearer 认证方案。
"""

from fastapi.security import OAuth2PasswordBearer

# OAuth2 Password Bearer 配置
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


