"""任务型事务辅助函数"""
import asyncio
# import logging
import textwrap

async def communicate_cmd(cmd: str, cwd: str|None=None, indent: int=2,  **kwds)->str:
    """运行命令行执行任务

    Args:
        cmd: 命令行任务
        cwd: 当前工作目录
        indent: 命令行打印信息缩进位数

    Return:
        返回命令任务执行的打印信息
    """
    _ = lambda text: textwrap.indent(text, prefix=" "*indent) # 美化打印信息
    proc = await asyncio.create_subprocess_shell(
        cmd, 
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=cwd, **kwds)
    stdout, stderr = await proc.communicate(input=None)
    std_data = f'[{cmd!r} 退出状态码 {proc.returncode}]\n'
    if stdout:
        std_data += f'[stdout]:\n{_(stdout.decode())}\n' 
    if stderr:
        std_data += f'[stdinfo]:\n{_(stderr.decode())}\n'
    return std_data

# async def log_cmd(cmd: str, cwd: str|None=None, indent: int=2, logger_name="run", **kwds)->str:
#     """运行命令行执行任务，并记录打印信息

#     Args:
#         cmd: 命令行任务
#         cwd: 当前工作目录
#         indent: 命令行打印信息缩进位数

#     Return:
#         返回命令任务执行的打印信息
#     """
#     logger = logger = logging.getLogger(logger_name)
#     hd = logging.StreamHandler()
#     hd.setFormatter(logging.Formatter("%(message)s"))
#     logger.addHandler(hd)
#     proc = await asyncio.create_subprocess_shell(
#         cmd, 
#         stdin=asyncio.subprocess.PIPE,
#         stdout=asyncio.subprocess.PIPE,
#         stderr=asyncio.subprocess.PIPE,
#         cwd=cwd, **kwds)
#     # 获取实时输出/错误信息
#     if not proc.stdout.at_eof():
#         for line in iter(proc.stdout.readline, b''):
#             line = await line
#             logger.info(line.decode())
#             if proc.stdout.at_eof():
#                 break
#     if not proc.stderr.at_eof():
#         for line in iter(proc.stderr.readline, b''):
#             line = await line
#             logger.info(line.decode())
#             if proc.stderr.at_eof():
#                 break
#     # 等待命令执行完成
#     proc.wait()