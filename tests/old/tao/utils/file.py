from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def mkdir(root: str|Path, mode=0o755, parents=True, exist_ok=True):
    """创建文件夹"""
    root = Path(root)
    if not root.exists():
        root.mkdir(mode=mode, parents=parents, exist_ok=exist_ok)
        logger.info(f"{root} 创建成功")
    else:
        logger.info(f"{root} 已存在无需创建")
