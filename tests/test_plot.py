"""Tests for taolib.plot module."""

from pathlib import Path
from unittest.mock import patch


class TestConfigureMatplotlibFonts:
    """Tests for configure_matplotlib_fonts function."""

    def test_configure_with_default_params(self):
        """Test configuration with default parameters."""
        from taolib.plot.configs.matplotlib_font import configure_matplotlib_fonts

        with (
            patch("matplotlib.font_manager.findSystemFonts") as mock_find,
            patch("matplotlib.font_manager.fontManager.addfont") as mock_add,
            patch("matplotlib.pyplot.rcParams") as mock_rcParams,
            patch.object(Path, "exists", return_value=True),
        ):
            mock_find.return_value = ["/path/to/font.ttf"]

            result = configure_matplotlib_fonts()

            assert result is True
            mock_add.assert_called_once()
            assert mock_rcParams.__setitem__.call_count >= 1

    def test_configure_with_custom_font_directory(self, tmp_path: Path):
        """Test configuration with custom font directory."""
        from taolib.plot.configs.matplotlib_font import configure_matplotlib_fonts

        font_dir = tmp_path / "fonts"
        font_dir.mkdir()

        with (
            patch("matplotlib.font_manager.findSystemFonts") as mock_find,
            patch("matplotlib.font_manager.fontManager.addfont") as mock_add,
            patch("matplotlib.pyplot.rcParams") as mock_rcParams,
        ):
            mock_find.return_value = [str(font_dir / "test.ttf")]

            result = configure_matplotlib_fonts(
                font_directory=str(font_dir),
                target_fonts=["Custom Font"]
            )

            assert result is True
            mock_find.assert_called_once_with(fontpaths=[str(font_dir)])

    def test_configure_nonexistent_directory(self):
        """Test configuration with non-existent directory."""
        from taolib.plot.configs.matplotlib_font import configure_matplotlib_fonts

        with patch.object(Path, "exists", return_value=False):
            result = configure_matplotlib_fonts(font_directory="/nonexistent/path")

            assert result is False

    def test_configure_empty_font_directory(self, tmp_path: Path):
        """Test configuration with empty font directory."""
        from taolib.plot.configs.matplotlib_font import configure_matplotlib_fonts

        font_dir = tmp_path / "empty_fonts"
        font_dir.mkdir()

        with (
            patch("matplotlib.font_manager.findSystemFonts") as mock_find,
            patch.object(Path, "exists", return_value=True),
        ):
            mock_find.return_value = []

            result = configure_matplotlib_fonts(font_directory=str(font_dir))

            assert result is False

    def test_configure_handles_font_load_error(self):
        """Test that font load errors are handled gracefully."""
        from taolib.plot.configs.matplotlib_font import configure_matplotlib_fonts

        with (
            patch("matplotlib.font_manager.findSystemFonts") as mock_find,
            patch("matplotlib.font_manager.fontManager.addfont") as mock_add,
            patch("matplotlib.pyplot.rcParams"),
            patch.object(Path, "exists", return_value=True),
        ):
            mock_find.return_value = ["/path/to/font1.ttf", "/path/to/font2.ttf"]
            mock_add.side_effect = [Exception("Load error"), None]

            result = configure_matplotlib_fonts()

            assert result is True
            assert mock_add.call_count == 2

    def test_configure_with_custom_target_fonts(self):
        """Test configuration with custom target fonts."""
        from taolib.plot.configs.matplotlib_font import configure_matplotlib_fonts

        custom_fonts = ["Font A", "Font B"]

        with (
            patch("matplotlib.font_manager.findSystemFonts") as mock_find,
            patch("matplotlib.font_manager.fontManager.addfont"),
            patch("matplotlib.pyplot.rcParams") as mock_rcParams,
            patch.object(Path, "exists", return_value=True),
        ):
            mock_find.return_value = ["/path/to/font.ttf"]

            result = configure_matplotlib_fonts(target_fonts=custom_fonts)

            assert result is True
            mock_rcParams.__setitem__.assert_called()
