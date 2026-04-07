"""file_storage Settings 配置测试。"""

import sys
from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

# server/__init__.py 导入 create_app 会触发 FastAPI 路由注册链，
# 需要先 mock 掉 server.app 模块以避免不相关的导入错误。
_app_key = "taolib.file_storage.server.app"
_had_app = _app_key in sys.modules
if not _had_app:
    sys.modules[_app_key] = MagicMock()

from taolib.file_storage.server.config import Settings  # noqa: E402


class TestSignedUrlSecret:
    """签名 URL 密钥校验测试。"""

    def test_empty_secret_allowed(self):
        """空密钥（开发/测试模式）应正常创建。"""
        settings = Settings(signed_url_secret="")
        assert settings.signed_url_secret == ""

    def test_default_secret_is_empty(self):
        """默认密钥应为空字符串。"""
        settings = Settings()
        assert settings.signed_url_secret == ""

    def test_short_secret_raises(self):
        """短密钥（非空但 <32 字符）应抛出 ValidationError。"""
        with pytest.raises(ValidationError, match="signed_url_secret"):
            Settings(signed_url_secret="short")

    def test_valid_secret_32_chars(self):
        """32 字符密钥应正常通过。"""
        secret = "a" * 32
        settings = Settings(signed_url_secret=secret)
        assert settings.signed_url_secret == secret

    def test_valid_secret_long(self):
        """长密钥应正常通过。"""
        secret = "x" * 64
        settings = Settings(signed_url_secret=secret)
        assert settings.signed_url_secret == secret
