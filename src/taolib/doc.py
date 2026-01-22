#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""文档构建相关任务模块。

包含文档清理、构建、国际化、测试等相关任务以及文档站点配置集合创建功能。"""

from pathlib import Path
import sys
import logging
from shutil import rmtree
from tempfile import mkdtemp
from invoke.tasks import task
from invoke.context import Context
from invoke.collection import Collection


def _get_sphinx_paths(ctx: Context, source: str | None, target: str | None) -> tuple[str, str]:
    """安全地从上下文获取 sphinx 的 source/target 路径，若没有 ctx.sphinx 则使用默认值。"""
    sphinx_cfg = getattr(ctx, 'sphinx', None)
    src = source or (getattr(sphinx_cfg, "source", "doc") if sphinx_cfg else "doc")
    dst = target or (getattr(sphinx_cfg, "target", "doc/_build/html") if sphinx_cfg else "doc/_build/html")
    return str(src), str(dst)

logger = logging.getLogger(__name__)

# 在非 Windows 平台上使用 pty
PTY = sys.platform != 'win32'

@task
def clean(ctx: Context) -> None:
    """清除文档构建目标目录，以便下次构建是干净的。

    Args:
        ctx: Invoke 上下文对象，包含 sphinx 配置信息"""
    # 尝试通过 _get_sphinx_paths 获取目标（更稳健）
    try:
        _, target = _get_sphinx_paths(ctx, None, None)
    except Exception:
        # 回退到旧的属性访问方式，但要安全地处理缺失的配置
        sphinx_cfg = getattr(ctx, "sphinx", None)
        target = getattr(sphinx_cfg, "target", None) if sphinx_cfg is not None else None
        if not target:
            logger.warning("无法确定 sphinx.target，跳过 clean 操作")
            return

    output = Path(target)
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
          nitpick: bool = False,
          jobs: str = "auto",
          keep_going: bool = True) -> None:
    """构建项目的 Sphinx 文档。

    Args:
        ctx: Invoke 上下文对象，包含 sphinx 配置信息
        builder: Sphinx 构建器类型，默认为 'html'
        opts: Sphinx 构建额外选项/参数
        language: 文档语言，默认为 None
        source: 源目录，覆盖配置设置
        target: 输出目录，覆盖配置设置
        nitpick: 是否启用更严格的警告/错误检查"""
    source, target = _get_sphinx_paths(ctx, source, target)

    if language:
        opts = f"{opts} -D language={language}".strip()
        target = f"{target}/{language}"

    if nitpick:
        opts = f"{opts} -n -W -T".strip()

    opts = f"{opts} -j {jobs}".strip()
    if keep_going:
        opts = f"{opts} --keep-going".strip()

    # 执行构建命令
    cmd = f"sphinx-build -b {builder} {opts} {source} {target}"
    logger.info(f"{builder}@{source} => {target}")
    try:
        ctx.run(cmd, pty=PTY)
    except ValueError as e:
        # 在 Windows 上，Invoke 处理 KeyboardInterrupt 时可能会遇到 stdin 已关闭的情况
        # 此时会抛出 ValueError: I/O operation on closed file
        if sys.platform == 'win32' and "closed file" in str(e):
            logger.warning("构建被用户中断")
        else:
            raise
    except KeyboardInterrupt:
        logger.warning("构建被用户中断")

@task
def intl(ctx: Context, language: str = 'en') -> None:
    """更新 POT 文件并调用 `sphinx-intl update` 命令。

    用于更新多语言文档翻译。

    Args:
        ctx: Invoke 上下文对象，包含 sphinx 配置信息
        language: 目标语言代码，默认为 'en'（英语）"""
    opts = "-b gettext"
    _, configured_target = _get_sphinx_paths(ctx, None, None)
    target = Path(configured_target).parent / 'gettext'

    if language == 'en':
        if target.exists():
            rmtree(target)
        build(ctx, target=str(target), opts=opts)
    elif language:
        if not target.exists():
            build(ctx, target=str(target), opts=opts)
        ctx.run(f'sphinx-intl update -p {str(target)} -l {language}')
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
        # 使用临时目录进行 doctest 构建。不要清理常规模板输出目录以避免意外删除用户构建结果。
        logger.info(f"使用临时目录进行 doctest: {tmpdir}")
        build(ctx, target=target, opts=opts)
    finally:
        try:
            rmtree(tmpdir)
        except Exception:
            logger.warning(f"无法删除临时目录 {tmpdir}")

@task
def tree(ctx: Context) -> None:
    ignore = ".git|*.pyc|*.swp|dist|*.egg-info|_static|_build|_templates"
    try:
        ctx.run(f'tree -Ca -I "{ignore}" {ctx.sphinx.source}', pty=PTY)
    except Exception:
        sphinx_cfg = getattr(ctx, 'sphinx', None)
        root = Path(getattr(sphinx_cfg, 'source', 'doc') if sphinx_cfg else 'doc')
        for p in sorted(root.rglob("*")):
            rel = p.relative_to(root)
            if any(part in ignore.split("|") for part in rel.parts):
                continue
            print(rel)


# 文档站点配置集合创建函数
from typing import Optional, List, Dict, Union, Any, overload
# Collection is imported from invoke.collection at the top of the file


@overload
def create_docs(source: str = 'doc', target: str = '.temp/html', children: str = '') -> Collection:
    ...

@overload
def create_docs(source: Union[List[Dict[str, str]], Dict[str, Dict[str, str]]]) -> Collection:
    ...

def create_docs(
    source: Union[str, List[Dict[str, str]], Dict[str, Dict[str, str]], None] = None,
    target: str = 'doc/_build/html',
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
    # 内部 helper：生成并返回一个为单个项目配置的 Collection
    def _make_project_namespace(name: str, proj_source: str, proj_target: str, proj_children: str) -> Collection:
        project_namespace = Collection(name)
        # 使用 Collection.from_module 确保传入的是一个 Collection 对象（而不是 module）
        project_namespace.add_collection(Collection.from_module(sys.modules[__name__]))
        actual_source = proj_children if proj_children else proj_source
        project_config = {
            "sphinx": {
                "source": actual_source,
                "target": f"{proj_target}/{proj_children}" if proj_children else proj_target
            }
        }
        project_namespace.collections[__name__.split('.')[-1]].configure(project_config)  # type: ignore[attr-defined]
        return project_namespace

    # 处理单个项目的情况
    if source is None or isinstance(source, str):
        # 确保 source 有值
        actual_source_str = source if source is not None else 'doc'
        actual_source = children if children else actual_source_str

        # 创建并配置命令集合（与以前保持行为一致）
        _config = {
            "sphinx": {
                "source": actual_source,
                "target": f"{target}/{children}" if children else target
            }
        }

        namespace = Collection()
        namespace.add_collection(Collection.from_module(sys.modules[__name__]))
        namespace.collections[__name__.split('.')[-1]].configure(_config)  # type: ignore[attr-defined]

        return namespace

    # 处理多个项目的情况（列表或字典）
    project_configs = source  # type: ignore
    main_namespace = Collection()

    if isinstance(project_configs, list):
        # 列表形式：需要包含 name 字段
        for i, config in enumerate(project_configs):
            name = config.get('name', f'doc_{i+1}')
            proj_source = config.get('source', 'doc')
            proj_target = config.get('target', f'doc/_build/html/{name}')
            proj_children = config.get('children', '')

            project_namespace = _make_project_namespace(name, proj_source, proj_target, proj_children)
            main_namespace.add_collection(project_namespace)
    else:
        # 字典形式：键为项目名称
        for name, config in project_configs.items():
            proj_source = config.get('source', 'doc')
            proj_target = config.get('target', f'doc/_build/html/{name}')
            proj_children = config.get('children', '')

            project_namespace = _make_project_namespace(name, proj_source, proj_target, proj_children)
            main_namespace.add_collection(project_namespace)

    return main_namespace


def sites(source: str = 'doc', target: str = 'doc/_build/html', children: str = '') -> Collection:
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
