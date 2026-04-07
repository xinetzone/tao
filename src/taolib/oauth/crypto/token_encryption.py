"""Token 加密模块。

使用 Fernet 对称加密安全存储 OAuth Token。
"""

from cryptography.fernet import Fernet, InvalidToken

from ..errors import OAuthTokenDecryptionError


def generate_encryption_key() -> str:
    """生成新的 Fernet 加密密钥。

    Returns:
        Base64 编码的 32 字节密钥字符串
    """
    return Fernet.generate_key().decode()


class TokenEncryptor:
    """Token 加密器。

    使用 Fernet 对称加密对 OAuth Token 进行加密和解密。

    Args:
        encryption_key: Fernet 兼容的加密密钥（Base64 编码的 32 字节）
    """

    def __init__(self, encryption_key: str) -> None:
        """初始化加密器。

        Args:
            encryption_key: Fernet 兼容的加密密钥
        """
        self._fernet = Fernet(encryption_key.encode())

    def encrypt(self, plaintext: str) -> str:
        """加密明文。

        Args:
            plaintext: 要加密的明文字符串

        Returns:
            Base64 编码的密文字符串
        """
        return self._fernet.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        """解密密文。

        Args:
            ciphertext: Base64 编码的密文字符串

        Returns:
            解密后的明文字符串

        Raises:
            OAuthTokenDecryptionError: 解密失败
        """
        try:
            return self._fernet.decrypt(ciphertext.encode()).decode()
        except (InvalidToken, Exception) as e:
            raise OAuthTokenDecryptionError(f"Token 解密失败: {e}")

    @staticmethod
    def rotate_key(old_key: str, new_key: str, ciphertext: str) -> str:
        """密钥轮换：用旧密钥解密后用新密钥重新加密。

        Args:
            old_key: 旧的加密密钥
            new_key: 新的加密密钥
            ciphertext: 用旧密钥加密的密文

        Returns:
            用新密钥加密的密文

        Raises:
            OAuthTokenDecryptionError: 用旧密钥解密失败
        """
        old_encryptor = TokenEncryptor(old_key)
        new_encryptor = TokenEncryptor(new_key)
        plaintext = old_encryptor.decrypt(ciphertext)
        return new_encryptor.encrypt(plaintext)
