"""Tests for OAuth token encryption."""

import pytest

from taolib.oauth.crypto.token_encryption import TokenEncryptor, generate_encryption_key


class TestGenerateEncryptionKey:
    def test_generates_valid_key(self):
        key = generate_encryption_key()
        assert isinstance(key, str)
        assert len(key) > 0

    def test_generates_unique_keys(self):
        key1 = generate_encryption_key()
        key2 = generate_encryption_key()
        assert key1 != key2


class TestTokenEncryptor:
    def test_encrypt_decrypt_roundtrip(self, encryption_key):
        encryptor = TokenEncryptor(encryption_key)
        plaintext = "my-secret-token-12345"
        encrypted = encryptor.encrypt(plaintext)
        assert encrypted != plaintext
        decrypted = encryptor.decrypt(encrypted)
        assert decrypted == plaintext

    def test_encrypt_produces_different_ciphertexts(self, encryption_key):
        encryptor = TokenEncryptor(encryption_key)
        plaintext = "same-token"
        encrypted1 = encryptor.encrypt(plaintext)
        encrypted2 = encryptor.encrypt(plaintext)
        # Fernet uses timestamp + random IV, so ciphertexts should differ
        assert encrypted1 != encrypted2

    def test_decrypt_with_wrong_key_fails(self, encryption_key):
        encryptor1 = TokenEncryptor(encryption_key)
        encrypted = encryptor1.encrypt("secret")

        other_key = generate_encryption_key()
        encryptor2 = TokenEncryptor(other_key)

        with pytest.raises(Exception):
            encryptor2.decrypt(encrypted)

    def test_encrypt_empty_string(self, encryption_key):
        encryptor = TokenEncryptor(encryption_key)
        encrypted = encryptor.encrypt("")
        decrypted = encryptor.decrypt(encrypted)
        assert decrypted == ""

    def test_encrypt_unicode(self, encryption_key):
        encryptor = TokenEncryptor(encryption_key)
        plaintext = "中文测试token-🔐"
        encrypted = encryptor.encrypt(plaintext)
        decrypted = encryptor.decrypt(encrypted)
        assert decrypted == plaintext

    def test_rotate_key(self, encryption_key):
        encryptor = TokenEncryptor(encryption_key)
        encrypted = encryptor.encrypt("my-token")

        new_key = generate_encryption_key()
        re_encrypted = TokenEncryptor.rotate_key(encryption_key, new_key, encrypted)

        new_encryptor = TokenEncryptor(new_key)
        decrypted = new_encryptor.decrypt(re_encrypted)
        assert decrypted == "my-token"
