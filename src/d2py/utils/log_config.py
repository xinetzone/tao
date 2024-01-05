import logging


def config_logging(
    filename,
    logger_name="logger",
    filemode='a',
    filter_mod_names = [
        "matplotlib", "PIL", "asyncio", 
        "urllib3", "markdown_it",
        "ablog"
    ],
    file_formatter="%(levelname)s|%(asctime)s|%(name)s| -> %(message)s\n|==>%(module)s.%(funcName)s@: %(pathname)s:%(lineno)d",
    stream_formatter="%(levelname)s|%(asctime)s|%(name)s| -> %(message)s",
    ):
    """配置 logging

    Args:
        path: 日志保存路径
        file_formatter: 日志文件配置
        stream_formatter: 控制台打印配置
    """
    logging.basicConfig(level=logging.DEBUG,
                        format=file_formatter,
                        datefmt='%m-%d %H:%M',
                        filename=filename,
                        filemode=filemode)
    
    # 禁用一些 debug 信息
    for mod_name in filter_mod_names:
        _logger = logging.getLogger(mod_name)
        _logger.setLevel(logging.WARNING)
    
    # 创建日志级别更高的控制台处理程序
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO) # 或者 logging.ERROR
    ch_formatter = logging.Formatter(stream_formatter)
    ch.setFormatter(ch_formatter)
    logging.getLogger("").addHandler(ch)
