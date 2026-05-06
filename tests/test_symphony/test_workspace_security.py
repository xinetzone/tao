"""工作区安全工具测试。"""

from pathlib import Path

import pytest

from taolib.symphony.workspace.security import (
    assert_within_root,
    canonicalize,
    sanitize_identifier,
)


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


class TestCanonicalize:
    """测试 canonicalize 逐段符号链接解析。"""

    def test_regular_path_unchanged(self, tmp_path: Path) -> None:
        """普通路径规范化后保持一致。"""
        target = tmp_path / "workspace" / "ABC-123"
        target.mkdir(parents=True)
        result = canonicalize(target)
        assert str(result) == str(target.resolve())

    def test_nonexistent_path_segments(self, tmp_path: Path) -> None:
        """不存在的路径段保持原样。"""
        target = tmp_path / "workspace" / "nonexistent"
        result = canonicalize(target)
        # 应返回解析后的路径
        assert str(result).startswith(str(tmp_path.resolve()))

    def test_symlink_resolution(self, tmp_path: Path) -> None:
        """符号链接被逐段解析。"""
        real_dir = tmp_path / "real_target"
        real_dir.mkdir()
        link = tmp_path / "link_to_real"
        try:
            link.symlink_to(real_dir, target_is_directory=True)
        except OSError:
            pytest.skip("当前环境不支持创建符号链接")

        result = canonicalize(link)
        assert result == real_dir.resolve()


class TestWorkspaceEqualsRoot:
    """测试 workspace_equals_root 检查。"""

    def test_path_equals_root_rejected(self, tmp_path: Path) -> None:
        """路径等于根目录时抛出 ValueError。"""
        root = tmp_path / "workspaces"
        root.mkdir()
        with pytest.raises(ValueError, match="等于根目录"):
            assert_within_root(root, root)

    def test_path_is_subdirectory_passes(self, tmp_path: Path) -> None:
        """路径是根目录的子目录时通过。"""
        root = tmp_path / "workspaces"
        root.mkdir()
        sub = root / "ABC-123"
        sub.mkdir()
        # 不应抛出异常
        assert_within_root(sub, root)
