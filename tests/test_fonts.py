"""taolib.fonts 的三闸行为测试。"""

import shutil
from pathlib import Path

import pytest

matplotlib = pytest.importorskip("matplotlib")

from matplotlib import font_manager, rcParams  # noqa: E402
from taolib.fonts import (  # noqa: E402
    FontConfigError,
    configure_matplotlib_fonts,
    iter_font_files,
    register_font_directory,
)


@pytest.fixture(autouse=True)
def _restore_rcparams():
    """每个用例结束后还原 rcParams，避免污染同进程的其他用例。"""
    with matplotlib.rc_context():
        yield


@pytest.fixture
def font_dir(tmp_path: Path) -> Path:
    """准备一个只含 DejaVuSans.ttf 副本的临时字体目录。"""
    source = Path(matplotlib.get_data_path()) / "fonts" / "ttf" / "DejaVuSans.ttf"
    if not source.is_file():
        pytest.skip("当前 matplotlib 安装缺少 DejaVuSans.ttf")
    target = tmp_path / "fonts"
    target.mkdir()
    shutil.copy2(source, target / "DejaVuSans.ttf")
    return target


def test_register_returns_new_files_only(font_dir: Path) -> None:
    added = register_font_directory(font_dir)

    assert added == [font_dir / "DejaVuSans.ttf"]
    installed = [
        entry
        for entry in font_manager.fontManager.ttflist
        if Path(entry.fname).resolve() == (font_dir / "DejaVuSans.ttf").resolve()
    ]
    assert len(installed) == 1


def test_register_is_idempotent(font_dir: Path) -> None:
    assert len(register_font_directory(font_dir)) == 1
    assert register_font_directory(font_dir) == []


def test_missing_directory_raises(tmp_path: Path) -> None:
    with pytest.raises(FontConfigError, match="不存在或不是目录"):
        register_font_directory(tmp_path / "absent")


def test_directory_without_fonts_raises(tmp_path: Path) -> None:
    empty = tmp_path / "empty"
    empty.mkdir()

    with pytest.raises(FontConfigError, match="没有字体文件"):
        register_font_directory(empty)


def test_iter_font_files_is_recursive_and_sorted(font_dir: Path) -> None:
    nested = font_dir / "cn" / "deep"
    nested.mkdir(parents=True)
    shutil.copy2(font_dir / "DejaVuSans.ttf", nested / "Copy.TTF")
    (font_dir / "readme.txt").write_text("非字体文件", encoding="utf-8")

    files = iter_font_files(font_dir)

    assert set(files) == {font_dir / "DejaVuSans.ttf", nested / "Copy.TTF"}
    assert iter_font_files(font_dir) == files  # 同一目录多次扫描顺序稳定


def test_iter_font_files_rejects_bad_directory(tmp_path: Path) -> None:
    with pytest.raises(FontConfigError, match="不存在或不是目录"):
        iter_font_files(tmp_path / "absent")

    empty = tmp_path / "empty"
    empty.mkdir()
    with pytest.raises(FontConfigError, match="没有字体文件"):
        iter_font_files(empty)


def test_configure_sets_rcparams(font_dir: Path) -> None:
    resolved = configure_matplotlib_fonts(font_dir, ["DejaVu Sans"])

    assert resolved == ("DejaVu Sans",)
    assert rcParams["font.family"] == ["sans-serif"]
    assert rcParams["font.sans-serif"] == ["DejaVu Sans"]
    assert rcParams["axes.unicode_minus"] is False


def test_unicode_minus_can_be_kept(font_dir: Path) -> None:
    configure_matplotlib_fonts(font_dir, ["DejaVu Sans"], unicode_minus=True)

    assert rcParams["axes.unicode_minus"] is True


def test_unresolvable_family_raises_without_touching_rcparams(font_dir: Path) -> None:
    before = list(rcParams["font.sans-serif"])

    with pytest.raises(FontConfigError, match="无法解析"):
        configure_matplotlib_fonts(font_dir, ["绝不存在的字体 XYZ"])

    assert list(rcParams["font.sans-serif"]) == before


def test_none_directory_uses_installed_fonts() -> None:
    assert configure_matplotlib_fonts(None, ["DejaVu Sans"]) == ("DejaVu Sans",)
