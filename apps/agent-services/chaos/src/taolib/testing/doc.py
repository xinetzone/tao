#!/usr/bin/env python3
"""文档构建相关任务模块。

包含文档清理、构建、国际化、测试等相关任务以及文档站点配置集合创建功能。"""

import logging
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, replace
from pathlib import Path
from shutil import rmtree
from tempfile import mkdtemp
from typing import overload

# 导入sphinx_intl模块
import sphinx_intl.basic as sphinx_intl_basic
from invoke.collection import Collection
from invoke.context import Context
from invoke.tasks import task


def _get_sphinx_paths(
    ctx: Context, source: str | None, target: str | None
) -> tuple[str, str]:
    """安全地从上下文获取 sphinx 的 source/target 路径，若没有 ctx.sphinx 则使用默认值。

    Args:
        ctx: Invoke 上下文对象，包含 sphinx 配置信息。
        source: 源目录路径，如果为 None 则使用配置值或默认值 'doc'。
        target: 目标目录路径，如果为 None 则使用配置值或默认值 'doc/_build/html'。

    Returns:
        tuple[str, str]: 包含 source 和 target 路径的元组。
    """
    sphinx_cfg = getattr(ctx, "sphinx", None)

    # 使用 SphinxConfig 数据类来结构化配置获取过程
    if sphinx_cfg:
        config = SphinxConfig(
            source=getattr(sphinx_cfg, "source", "doc"),
            target=getattr(sphinx_cfg, "target", "doc/_build/html"),
        )
    else:
        config = SphinxConfig()

    src = source or config.source
    dst = target or config.target
    return str(src), str(dst)


logger = logging.getLogger(__name__)

# 在非 Windows 平台上使用 pty
PTY = sys.platform != "win32"

# 全局 ctx 变量，用于支持测试用例中的 patch
ctx = None


@dataclass(frozen=True, slots=True)
class SphinxConfig:
    """Sphinx 配置数据类。

    用于存储 Sphinx 文档构建的配置信息，包括源代码目录和构建输出目录。
    """

    source: str = "doc"
    target: str = "doc/_build/html"


@dataclass(frozen=True, slots=True)
class ProjectConfig:
    """项目配置数据类。

    用于存储单个文档项目的配置信息，包括名称、源代码目录、构建输出目录和子文档目录。
    """

    name: str
    source: str = "doc"
    target: str = "doc/_build/html"
    children: str = ""


class ProjectConfigValidator:
    """项目配置验证器。

    用于验证和规范化文档项目配置，支持从字典或 ProjectConfig 对象创建标准化配置。
    """

    @staticmethod
    def from_dict(data: dict, index: int = 0) -> ProjectConfig:
        """从字典创建 ProjectConfig 对象。

        Args:
            data: 包含项目配置的字典，应有 name、source、target、children 键。
            index: 配置在列表中的索引，用于生成默认名称。

        Returns:
            标准化的 ProjectConfig 对象。

        Raises:
            ValueError: 当必需字段缺失或格式不合法时。
        """
        name = data.get("name", f"doc_{index + 1}")
        source = data.get("source", "doc")
        target = data.get("target", "doc/_build/html")
        children = data.get("children", "")

        # 验证字段非空
        if not name or not isinstance(name, str):
            raise ValueError(f"项目名称必须是非空字符串，得到: {name!r}")
        if not source or not isinstance(source, str):
            raise ValueError(f"源目录必须是非空字符串，得到: {source!r}")
        if not target or not isinstance(target, str):
            raise ValueError(f"目标目录必须是非空字符串，得到: {target!r}")

        return ProjectConfig(name=name, source=source, target=target, children=children)

    @staticmethod
    def normalize(config: dict | ProjectConfig, index: int = 0) -> ProjectConfig:
        """将配置标准化为 ProjectConfig 对象。

        Args:
            config: 配置对象，可以是字典或 ProjectConfig 实例。
            index: 配置在列表中的索引，用于生成默认名称。

        Returns:
            标准化的 ProjectConfig 对象。
        """
        if isinstance(config, ProjectConfig):
            return config
        elif isinstance(config, dict):
            return ProjectConfigValidator.from_dict(config, index)
        else:
            raise TypeError(f"不支持的配置类型: {type(config).__name__}")


@task
def clean(ctx: Context) -> None:
    """清除文档构建目标目录，以便下次构建是干净的。

    Args:
        ctx: Invoke 上下文对象，包含 sphinx 配置信息。
    """
    try:
        _, target = _get_sphinx_paths(ctx, None, None)
    except Exception:
        sphinx_cfg = getattr(ctx, "sphinx", None)
        target = getattr(sphinx_cfg, "target", None) if sphinx_cfg is not None else None
        if not target:
            logger.warning("无法确定 sphinx.target，跳过 clean 操作")
            return

    # 确保 target 是字符串类型
    target_str = str(target)
    output = Path(target_str)
    if output.exists():
        logger.info(f"删除 {output}")
        rmtree(output)


def _build_sphinx_opts(
    opts: str,
    language: str | None,
    nitpick: bool,
    jobs: str,
    keep_going: bool,
) -> tuple[str, str | None]:
    """构建 Sphinx 命令行选项字符串。

    Args:
        opts: 基础选项字符串。
        language: 文档语言。
        nitpick: 是否启用严格模式。
        jobs: 并行作业数。
        keep_going: 遇到错误是否继续。

    Returns:
        (opts 字符串, language 路径后缀或 None)
    """
    lang_suffix = None
    if language:
        opts = f"{opts} -D language={language}".strip()
        lang_suffix = language
    if nitpick:
        opts = f"{opts} -n -W -T".strip()
    opts = f"{opts} -j {jobs}".strip()
    if keep_going:
        opts = f"{opts} --keep-going".strip()
    return opts, lang_suffix


@task(default=True)
def build(
    ctx: Context,
    builder: str = "html",
    opts: str = "",
    language: str | None = None,
    source: str | None = None,
    target: str | None = None,
    nitpick: bool = False,
    jobs: str = "auto",
    keep_going: bool = True,
) -> None:
    """构建项目的 Sphinx 文档。

    Args:
        ctx: Invoke 上下文对象，包含 sphinx 配置信息。
        builder: Sphinx 构建器类型，默认为 'html'。
        opts: Sphinx 构建额外选项/参数。
        language: 文档语言，默认为 None。
        source: 源目录，覆盖配置设置。
        target: 输出目录，覆盖配置设置。
        nitpick: 是否启用更严格的警告/错误检查。
        jobs: 并行作业数，默认为 'auto'。
        keep_going: 遇到错误是否继续构建，默认为 True。
    """
    source, target = _get_sphinx_paths(ctx, source, target)

    opts, lang_suffix = _build_sphinx_opts(opts, language, nitpick, jobs, keep_going)
    if lang_suffix:
        target = f"{target}/{lang_suffix}"

    # 使用 python -m sphinx.cmd.build 来执行构建命令，确保在任何环境中都能找到 sphinx-build
    cmd = f"python -m sphinx.cmd.build -b {builder} {opts} {source} {target}"
    logger.info(f"{builder}@{source} => {target}")
    try:
        ctx.run(cmd, pty=PTY)
    except ValueError as e:
        if sys.platform == "win32" and "closed file" in str(e):
            logger.warning("构建被用户中断")
        else:
            raise
    except KeyboardInterrupt:
        logger.warning("构建被用户中断")
    except OSError as e:
        logger.error(f"文件系统错误: {e}")
        raise
    except Exception as e:
        logger.error(f"构建失败: {e}")
        raise


@task
def intl(ctx: Context, language: str = "en") -> None:
    """更新 POT 文件并调用 `sphinx-intl update` 命令。

    用于更新多语言文档翻译。

    Args:
        ctx: Invoke 上下文对象，包含 sphinx 配置信息。
        language: 目标语言代码，默认为 'en'（英语）。
    """
    opts = "-b gettext"
    _, configured_target = _get_sphinx_paths(ctx, None, None)
    target = Path(configured_target).parent / "gettext"

    if language == "en":
        if target.exists():
            rmtree(target)
        build(ctx, target=str(target), opts=opts)
    elif language:
        if not target.exists():
            build(ctx, target=str(target), opts=opts)
        # 使用sphinx_intl.basic.update函数代替命令行调用
        sphinx_intl_basic.update(
            locale_dir="locales",
            pot_dir=str(target),
            languages=(language,),
        )
        # 以下代码已注释掉，因为当前项目可能不需要
        # for DIR in ['pages', 'posts', 'shop']:
        #     rmtree(f'locales/{language}/LC_MESSAGES/{DIR}/')


@task
def doctest(ctx: Context) -> None:
    """运行 Sphinx 的 doctest 构建器进行文档测试。

    这将像测试运行一样，显示测试结果，如果所有测试未通过，则以非零状态退出。
    使用临时目录作为构建目标，因为唯一的输出是自动打印的文本文件。

    Args:
        ctx: Invoke 上下文对象，包含 sphinx 配置信息。
    """
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
    """显示文档目录的树形结构。

    Args:
        ctx: Invoke 上下文对象，包含 sphinx 配置信息。
    """
    ignore = ".git|*.pyc|*.swp|dist|*.egg-info|_static|_build|_templates"
    try:
        ctx.run(f'tree -Ca -I "{ignore}" {ctx.sphinx.source}', pty=PTY)
    except Exception:
        sphinx_cfg = getattr(ctx, "sphinx", None)
        root = Path(getattr(sphinx_cfg, "source", "doc") if sphinx_cfg else "doc")
        for p in sorted(root.rglob("*")):
            rel = p.relative_to(root)
            if any(part in ignore.split("|") for part in rel.parts):
                continue
            print(rel)


@task
def serve(ctx: Context, port: int = 8000) -> None:
    """启动文档预览服务器。

    Args:
        ctx: Invoke 上下文对象，包含 sphinx 配置信息。
        port: 服务器端口，默认为 8000。
    """
    _, target = _get_sphinx_paths(ctx, None, None)
    import http.server
    import os
    import socketserver
    import webbrowser

    # 切换到构建目录
    os.chdir(target)

    # 创建服务器
    Handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(("", port), Handler)

    # 打开浏览器
    url = f"http://localhost:{port}"
    print(f"文档预览服务器已启动，请在浏览器中访问: {url}")
    webbrowser.open(url)

    # 启动服务器
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器已停止")
        httpd.shutdown()


def _build_single_project(
    source: str, target: str, builder: str, opts: str
) -> tuple[str, bool, str]:
    """在子进程中构建单个 Sphinx 项目。

    Args:
        source: 文档源目录。
        target: 构建输出目录。
        builder: Sphinx 构建器类型。
        opts: Sphinx 命令行选项。

    Returns:
        (项目标识, 是否成功, 输出信息)
    """
    cmd = [
        sys.executable,
        "-m",
        "sphinx.cmd.build",
        "-b",
        builder,
        *opts.split(),
        source,
        target,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    output = result.stdout + result.stderr
    return f"{source}->{target}", result.returncode == 0, output


def build_parallel(
    project_configs: list[ProjectConfig] | dict[str, ProjectConfig],
    *,
    max_workers: int | None = None,
    builder: str = "html",
    jobs: str = "auto",
    keep_going: bool = True,
) -> dict[str, bool]:
    """并行构建多个 Sphinx 文档项目。

    使用 ThreadPoolExecutor + subprocess.run 实现并行构建，各项目在独立子进程中执行。

    Args:
        project_configs: 项目配置列表或字典。
        max_workers: 最大工作进程数，默认为 None（由系统决定）。
        builder: Sphinx 构建器类型，默认为 'html'。
        jobs: 单项目内并行作业数，默认为 'auto'。
        keep_going: 遇到错误是否继续构建，默认为 True。

    Returns:
        {project_name: success_bool} 结果字典。
    """
    # 规范化配置
    configs: list[ProjectConfig] = []
    if isinstance(project_configs, dict):
        for name, config in project_configs.items():
            if isinstance(config, ProjectConfig):
                configs.append(replace(config, name=name))
            else:
                configs.append(
                    ProjectConfigValidator.normalize({**dict(config), "name": name})
                )
    else:
        for i, config in enumerate(project_configs):
            configs.append(ProjectConfigValidator.normalize(config, i))

    if not configs:
        return {}

    opts, _ = _build_sphinx_opts("", None, False, jobs, keep_going)
    results: dict[str, bool] = {}

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(
                _build_single_project,
                cfg.source,
                cfg.target,
                builder,
                opts,
            ): cfg.name
            for cfg in configs
        }
        for future in as_completed(futures):
            name = futures[future]
            try:
                _, success, output = future.result()
                results[name] = success
                if success:
                    logger.info(f"项目 '{name}' 构建成功")
                else:
                    logger.error(f"项目 '{name}' 构建失败:\n{output}")
            except Exception as exc:
                results[name] = False
                logger.error(f"项目 '{name}' 构建异常: {exc}")

    return results


# 文档站点配置集合创建函数
# Collection is imported from invoke.collection at the top of the file


def _make_project_namespace(project_config: ProjectConfig) -> Collection:
    """为单个项目创建 Invoke 命名空间。

    Args:
        project_config: 项目配置数据类，包含名称、源目录、目标目录等。

    Returns:
        配置好的 Invoke Collection 对象，包含文档构建任务。
    """
    project_namespace = Collection(project_config.name)
    # 使用 Collection.from_module 确保传入的是一个 Collection 对象（而不是 module）
    project_namespace.add_collection(Collection.from_module(sys.modules[__name__]))
    actual_source = (
        project_config.children if project_config.children else project_config.source
    )
    project_config_dict = {
        "sphinx": {
            "source": actual_source,
            "target": f"{project_config.target}/{project_config.children}"
            if project_config.children
            else project_config.target,
        }
    }
    project_namespace.collections[__name__.split(".")[-1]].configure(
        project_config_dict
    )  # type: ignore[attr-defined]
    return project_namespace


@overload
def create_docs(
    source: str = "doc", target: str = ".temp/html", children: str = ""
) -> Collection: ...


@overload
def create_docs(
    source: list[dict[str, str]] | dict[str, dict[str, str]],
) -> Collection: ...


@overload
def create_docs(
    source: list[ProjectConfig] | dict[str, ProjectConfig],
) -> Collection: ...


def create_docs(
    source: str
    | list[dict[str, str]]
    | dict[str, dict[str, str]]
    | list[ProjectConfig]
    | dict[str, ProjectConfig]
    | None = None,
    target: str = "doc/_build/html",
    children: str = "",
) -> Collection:
    """创建文档站点配置集合。

    统一的文档站点配置创建函数，支持单个项目和多个项目的配置。

    Args:
        source: 文档源代码目录或项目配置。可以是：
            - 字符串：文档源代码目录，默认为 'doc'
            - 列表：多个项目配置的列表，每个元素是包含 source、target、name 的字典
            - 字典：多个项目配置的字典，键为项目名称，值为包含 source、target 的字典
            - 列表[ProjectConfig]：多个项目配置的数据类列表
            - 字典[str, ProjectConfig]：多个项目配置的数据类字典
            - None：使用默认值 'doc'
        target: 文档构建输出目录，仅在处理单个项目时有效，默认为 '.temp/html'。
        children: 子文档目录，仅在处理单个项目时有效，如果指定则覆盖 source。

    Returns:
        配置好的 Invoke Collection 对象，包含 doc 子命令或多个命名的 doc 子命令集合。

    Raises:
        ValueError: 当项目配置不合法时。
        TypeError: 当配置类型不支持时。
    """
    # 处理单个项目的情况
    if source is None or isinstance(source, str):
        actual_source_str = source if source is not None else "doc"
        actual_source = children if children else actual_source_str

        _config = {
            "sphinx": {
                "source": actual_source,
                "target": f"{target}/{children}" if children else target,
            }
        }

        namespace = Collection()
        namespace.add_collection(Collection.from_module(sys.modules[__name__]))
        namespace.collections[__name__.split(".")[-1]].configure(_config)  # type: ignore[attr-defined]

        return namespace

    # 处理多个项目的情况（列表或字典）
    project_configs = source  # type: ignore
    main_namespace = Collection()

    if isinstance(project_configs, list):
        for i, config in enumerate(project_configs):
            project_config = ProjectConfigValidator.normalize(config, i)
            project_namespace = _make_project_namespace(project_config)
            main_namespace.add_collection(project_namespace)
    else:
        for name, config in project_configs.items():
            if isinstance(config, ProjectConfig):
                project_config = replace(config, name=name)
            else:
                config_with_name = dict(config)
                config_with_name["name"] = name
                project_config = ProjectConfigValidator.normalize(config_with_name)
            project_namespace = _make_project_namespace(project_config)
            main_namespace.add_collection(project_namespace)

    return main_namespace


def sites(
    source: str = "doc", target: str = "doc/_build/html", children: str = ""
) -> Collection:
    """创建文档站点配置集合。

    为不同的文档站点创建配置好的 Invoke 集合，用于构建 Sphinx 文档。

    Args:
        source: 文档源代码目录，默认为 'doc'。
        target: 文档构建输出目录，默认为 '.temp/html'。
        children: 子文档目录，如果指定则覆盖 source。

    Returns:
        配置好的 Invoke Collection 对象，包含 doc 子命令。
    """
    return create_docs(source, target, children)


def multi_sites(
    project_configs: list[dict[str, str]] | dict[str, dict[str, str]],
) -> Collection:
    """创建多文档站点配置集合。

    支持同时对多个 doc 项目进行构建的功能。

    Args:
        project_configs: 项目配置列表或字典。可以是：
            - 列表形式：每个元素是包含 source、target、name 的字典
            - 字典形式：键为项目名称，值为包含 source、target 的字典

    Returns:
        配置好的 Invoke Collection 对象，包含多个命名的 doc 子命令集合。
    """
    return create_docs(project_configs)  # type: ignore


