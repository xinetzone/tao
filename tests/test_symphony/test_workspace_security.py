"""工作区安全工具测试。"""

from pathlib import Path

import pytest

from taolib.symphony.workspace.security import assert_within_root, sanitize_identifier


class TestSanitizeIdentifier:
    """测试 sanitize_identifier 标识符净化。"""

    def test_valid_chars_unchanged(self) -> None:
        """[A-Za-z0-9._-] 范围内的字符保持不变。"""
        assert sanitize_identifier("Issue-123.test_v2") == "Issue-123.test_v2"
        assert sanitize_identifier("ABC.xyz-789") == "ABC.xyz-789"

    def test_special_chars_replaced(self) -> None:
        """特殊字符被替换为 _。"""
        assert sanitize_identifier("a@b#c") == "a_b_c"
        assert sanitize_identifier("test!data") == "test_data"

    def test_path_traversal_chars(self) -> None:
        """路径遍历字符被净化。"""
        assert sanitize_identifier("../etc/passwd") == "_etc_passwd"
        assert sanitize_identifier("..\\Windows\\System") == "_Windows_System"

    def test_spaces_replaced(self) -> None:
        """空格被替换为 _。"""
        assert sanitize_identifier("my issue title") == "my_issue_title"
        assert sanitize_identifier("  leading") == "__leading"


class TestAssertWithinRoot:
    """测试 assert_within_root 路径包含检查。"""

    def test_valid_path(self, tmp_path: Path) -> None:
        """合法子路径通过验证。"""
        root = tmp_path / "workspaces"
        root.mkdir()
        target = root / "proj" / "file.txt"
        # 不创建实际文件也可以测试路径逻辑
        assert_within_root(target, root)

    def test_path_escapes_root(self, tmp_path: Path) -> None:
        """越界路径抛出 ValueError。"""
        root = tmp_path / "workspaces"
        root.mkdir()
        target = tmp_path / "outside" / "file.txt"
        with pytest.raises(ValueError):
            assert_within_root(target, root)

    def test_symlink_resolution(self, tmp_path: Path) -> None:
        """符号链接解析后验证路径越界时报错。"""
        root = tmp_path / "workspaces"
        root.mkdir()
        outside = tmp_path / "outside"
        outside.mkdir()
        symlink = root / "link"
        try:
            symlink.symlink_to(outside, target_is_directory=True)
        except OSError:
            pytest.skip("当前环境不支持创建符号链接")

        with pytest.raises(ValueError):
            assert_within_root(symlink, root)
