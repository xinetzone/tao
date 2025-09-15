#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""文档构建相关任务模块。

包含文档清理、构建、国际化、测试等相关任务以及文档站点配置集合创建功能。"""

from pathlib import Path
import sys
import logging
from shutil import rmtree
from tempfile import mkdtemp
from invoke import task, Context

logger = logging.getLogger(__name__)

# 在非 Windows 平台上使用 pty
PTY = sys.platform != 'win32'

@task
def clean(ctx: Context) -> None:
    """清除文档构建目标目录，以便下次构建是干净的。
    
    Args:
        ctx: Invoke 上下文对象，包含 sphinx 配置信息"""
    output = Path(ctx.sphinx.target)
    if output.exists():
        logger.info(f'删除 {output}')
        rmtree(output)


@task(default=True)
def build(ctx: Context,
          builder: str = "html",
          opts: str = "",
          language: str | None = None,
          source: str | None = None,
          target: str | None = None,
          nitpick: bool = False) -> None:
    """构建项目的 Sphinx 文档。
    
    Args:
        ctx: Invoke 上下文对象，包含 sphinx 配置信息
        builder: Sphinx 构建器类型，默认为 'html'
        opts: Sphinx 构建额外选项/参数
        language: 文档语言，默认为 None
        source: 源目录，覆盖配置设置
        target: 输出目录，覆盖配置设置
        nitpick: 是否启用更严格的警告/错误检查"""
    source = source or ctx.sphinx.source
    target = target or ctx.sphinx.target
    
    # 处理语言选项
    if language:
        opts = f'-D language={language}'
        target = f'{target}/{language}'
        
    # 处理严格模式选项
    if nitpick:
        opts += " -n -W -T"
        
    # 执行构建命令
    cmd = f"sphinx-build -b {builder} {opts} {source} {target}"
    logger.info(f"{builder}@{source} => {target}")
    ctx.run(cmd, pty=PTY)

@task
def intl(ctx: Context, language: str = 'en') -> None:
    """更新 POT 文件并调用 `sphinx-intl update` 命令。
    
    用于更新多语言文档翻译。
    
    Args:
        ctx: Invoke 上下文对象，包含 sphinx 配置信息
        language: 目标语言代码，默认为 'en'（英语）"""
    opts = "-b gettext"
    target = Path(ctx.sphinx.target).parent / 'gettext'
    
    if language == 'en':
        # 英语是源语言，需要重新生成 POT 文件
        clean(ctx)
        build(ctx, target=target, opts=opts)
    elif language:
        # 确保 POT 文件已生成
        if not Path(target).exists():
            build(ctx, target=target, opts=opts)
        # 更新指定语言的翻译
        ctx.run(f'sphinx-intl update -p {target} -l {language}')
        # 以下代码已注释掉，因为当前项目可能不需要
        # for DIR in ['pages', 'posts', 'shop']:
        #     rmtree(f'locales/{language}/LC_MESSAGES/{DIR}/')

@task
def doctest(ctx: Context) -> None:
    """运行 Sphinx 的 doctest 构建器进行文档测试。
    
    这将像测试运行一样，显示测试结果，如果所有测试未通过，则以非零状态退出。
    使用临时目录作为构建目标，因为唯一的输出是自动打印的文本文件。
    
    Args:
        ctx: Invoke 上下文对象，包含 sphinx 配置信息"""
    tmpdir = mkdtemp()
    try:
        opts = "-b doctest"
        target = tmpdir
        clean(ctx)
        build(ctx, target=target, opts=opts)
    finally:
        rmtree(tmpdir)

@task
def tree(ctx: Context) -> None:
    """使用 'tree' 程序显示文档内容结构。
    
    Args:
        ctx: Invoke 上下文对象，包含 sphinx 配置信息"""
    # 定义需要忽略的文件和目录模式
    ignore = ".git|*.pyc|*.swp|dist|*.egg-info|_static|_build|_templates"
    ctx.run(f'tree -Ca -I "{ignore}" {ctx.sphinx.source}')


# 文档站点配置集合创建函数
from typing import Optional, List, Dict, Union, Any, overload
from invoke import Collection


@overload
def create_docs(source: str = 'doc', target: str = '.temp/html', children: str = '') -> Collection:
    ...

@overload
def create_docs(project_configs: Union[List[Dict[str, str]], Dict[str, Dict[str, str]]]) -> Collection:
    ...

def create_docs(
    source: Union[str, List[Dict[str, str]], Dict[str, Dict[str, str]], None] = None, 
    target: str = '.temp/html', 
    children: str = ''
) -> Collection:
    """创建文档站点配置集合。
    
    统一的文档站点配置创建函数，支持单个项目和多个项目的配置。
    
    Args:
        source: 文档源代码目录或项目配置。可以是：
            - 字符串：文档源代码目录，默认为 'doc'
            - 列表：多个项目配置的列表，每个元素是包含 source、target、name 的字典
            - 字典：多个项目配置的字典，键为项目名称，值为包含 source、target 的字典
            - None：使用默认值 'doc'
        target: 文档构建输出目录，仅在处理单个项目时有效，默认为 '.temp/html'
        children: 子文档目录，仅在处理单个项目时有效，如果指定则覆盖 source
        
    Returns:
        配置好的 Invoke Collection 对象，包含 doc 子命令或多个命名的 doc 子命令集合"""
    # 处理单个项目的情况
    if source is None or isinstance(source, str):
        # 确保source有值
        actual_source_str = source if source is not None else 'doc'
        # 确定实际使用的源目录
        actual_source = children if children else actual_source_str
        
        # 创建 Sphinx 配置
        _config = {
            "sphinx": {
                "source": actual_source,
                "target": f"{target}/{children}" if children else target
            }
        }
        
        # 创建并配置命令集合
        namespace = Collection()
        namespace.add_collection(sys.modules[__name__])
        namespace.collections[__name__.split('.')[-1]].configure(_config)
        
        return namespace
    
    # 处理多个项目的情况（列表或字典）
    project_configs = source  # type: ignore
    main_namespace = Collection()
    
    if isinstance(project_configs, list):
        # 列表形式：需要包含 name 字段
        for i, config in enumerate(project_configs):
            # 获取项目配置，提供默认值
            name = config.get('name', f'doc_{i+1}')
            proj_source = config.get('source', 'doc')
            proj_target = config.get('target', f'.temp/html/{name}')
            proj_children = config.get('children', '')
            
            # 创建项目特定的子命令集合
            project_namespace = Collection(name)
            project_namespace.add_collection(sys.modules[__name__])
            
            # 确定实际使用的源目录
            actual_source = proj_children if proj_children else proj_source
            
            # 创建并应用配置
            project_config = {
                "sphinx": {
                    "source": actual_source,
                    "target": f"{proj_target}/{proj_children}" if proj_children else proj_target
                }
            }
            project_namespace.collections[__name__.split('.')[-1]].configure(project_config)
            
            # 添加到主命令集合
            main_namespace.add_collection(project_namespace)
    else:
        # 字典形式：键为项目名称
        for name, config in project_configs.items():
            # 获取项目配置
            proj_source = config.get('source', 'doc')
            proj_target = config.get('target', f'.temp/html/{name}')
            proj_children = config.get('children', '')
            
            # 创建项目特定的子命令集合
            project_namespace = Collection(name)
            project_namespace.add_collection(sys.modules[__name__])
            
            # 确定实际使用的源目录
            actual_source = proj_children if proj_children else proj_source
            
            # 创建并应用配置
            project_config = {
                "sphinx": {
                    "source": actual_source,
                    "target": f"{proj_target}/{proj_children}" if proj_children else proj_target
                }
            }
            project_namespace.collections[__name__.split('.')[-1]].configure(project_config)
            
            # 添加到主命令集合
            main_namespace.add_collection(project_namespace)
    
    return main_namespace


def sites(source: str = 'doc', target: str = '.temp/html', children: str = '') -> Collection:
    """创建文档站点配置集合。
    
    为不同的文档站点创建配置好的 Invoke 集合，用于构建 Sphinx 文档。
    
    Args:
        source: 文档源代码目录，默认为 'doc'
        target: 文档构建输出目录，默认为 '.temp/html'
        children: 子文档目录，如果指定则覆盖 source
        
    Returns:
        配置好的 Invoke Collection 对象，包含 doc 子命令"""
    return create_docs(source, target, children)


def multi_sites(project_configs: Union[List[Dict[str, str]], Dict[str, Dict[str, str]]]) -> Collection:
    """创建多文档站点配置集合。
    
    支持同时对多个 doc 项目进行构建的功能。
    
    Args:
        project_configs: 项目配置列表或字典。可以是：
            - 列表形式：每个元素是包含 source、target、name 的字典
            - 字典形式：键为项目名称，值为包含 source、target 的字典
        
    Returns:
        配置好的 Invoke Collection 对象，包含多个命名的 doc 子命令集合"""
    return create_docs(project_configs)  # type: ignore
