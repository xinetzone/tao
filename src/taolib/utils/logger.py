import logging
from logging.handlers import RotatingFileHandler

def config_logging(
    filename: str,
    logger_name: str="logger",
    filter_mod_names: set=set(),
    default_filter_mod_names: set = {
        "matplotlib", "PIL", "asyncio", 
        "urllib3", "markdown_it",
        "ablog"
    },
    file_formatter: str="%(levelname)s|%(asctime)s|%(name)s| >>> %(message)s\n|==>%(module)s.%(funcName)s@: %(pathname)s:%(lineno)d\n\n",
    stream_formatter: str="%(levelname)s|%(asctime)s|%(name)s| >>> %(message)s",
    **kwargs):
    """配置 logging

    Args:
        filename: 日志保存路径
        logger_name: 日志名称
        filemode: 写入到文件的日志写入模式
        filter_mod_names: 自定义过滤日志 debug 模式对应的模块名称列表
        default_filter_mod_names: 默认过滤日志 debug 模式对应的模块名称列表
        file_formatter: 日志文件配置
        stream_formatter: 控制台打印配置
        rich_kwargs: 富文本模式，可为空
            即开启如下模式
            ```
            >>> from rich.logging import RichHandler
            >>> ch = RichHandler(**rich_kwargs)
            ```
    """
    logger = logging.getLogger(logger_name)
    # 禁用一些 debug 信息
    for mod_name in filter_mod_names|default_filter_mod_names:
        _logger = logging.getLogger(mod_name)
        _logger.setLevel(logging.WARNING)
    logger.setLevel(logging.DEBUG)
    fh = RotatingFileHandler(filename, **kwargs)
    fh.setFormatter(logging.Formatter(file_formatter))
    # fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO) # 或者 logging.ERROR
    ch_formatter = logging.Formatter(stream_formatter)
    ch.setFormatter(ch_formatter)
    logging.getLogger("").addHandler(ch)
    