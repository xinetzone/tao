import sys
if sys.version_info >= (3, 11):
    from tomllib import load # 需要 Python3.11 及其以上版本
else:
    from tomlkit import load # 需要安装 tomlkit
from dataclasses import dataclass
from pathlib import Path
# from taolib.utils.tree import Bunch

@dataclass
class Config:
    root_dir: Path | str # 文档的根目录
    name: str = "_config.toml" # 文档目录名称

    def __post_init__(self):
        self.root_dir = Path(self.root_dir)
        # 加载文档的配置信息
        with open(self.root_dir/self.name, "rb") as f:
            self.options = load(f)
    # def write(self, name: str):
    #     return 