"""
matplotlib 字体配置模块

此模块提供了配置 matplotlib 中文字体显示的功能，自动加载指定目录下的字体文件
并设置 matplotlib 使用中文字体，确保图表中的中文能正确显示。
"""

import logging
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import font_manager

logger = logging.getLogger(__name__)


def configure_matplotlib_fonts(
    font_directory: str | None = None,
    target_fonts: list[str] | None = None,
) -> bool:
    """
    配置 matplotlib 的字体设置

    参数:
        font_directory: 字体文件所在目录路径，如果为 None 则使用默认路径
        target_fonts: 要设置的目标字体名称

    返回:
        bool: 配置是否成功
    """
    if target_fonts is None:
        target_fonts = ["Maple Mono NF CN"]

    try:
        if font_directory is None:
            root_dir = Path(__file__).resolve().parents[0]
            font_directory = str(root_dir / "fonts")

        font_dir_path = Path(font_directory)
        if not font_dir_path.exists():
            logger.warning(f"字体目录不存在: {font_directory}")
            return False

        font_files = font_manager.findSystemFonts(fontpaths=[font_directory])

        if not font_files:
            logger.warning(f"在 {font_directory} 中未找到任何字体文件")
            return False

        for font_file in font_files:
            try:
                font_manager.fontManager.addfont(font_file)
                logger.debug(f"成功加载字体: {font_file}")
            except Exception as e:
                logger.error(f"加载字体失败 {font_file}: {e}")

        plt.rcParams["font.family"] = target_fonts
        logger.debug(f"已成功配置 matplotlib 使用字体: {target_fonts}")

        return True

    except Exception as e:
        logger.error(f"配置 matplotlib 字体时发生错误: {e}")
        return False


if __name__ == "__main__":
    configure_matplotlib_fonts()
