from pathlib import Path
import sys
import logging
from shutil import rmtree
from tempfile import mkdtemp
from invoke import task
from invoke.context import Context

logger = logging.getLogger(__name__)

pty = sys.platform != 'win32'

@task
def clean(ctx: Context):
    """清除文档构建目标目录，以便下次构建是干净的。"""
    output = Path(ctx.sphinx.target)
    if output.exists():
        logger.info(f'删除 {output}')
        rmtree(output)


@task(default=True)
def build(ctx: Context,
          opts: str = "",
          language: str|None = None,
          source: str|None = None,
          target: str|None = None,
          nitpick: bool = False):
    """构建项目的 Sphinx 文档。
    
    Args:
        opts: Extra sphinx-build options/args
        nitpick: Build with stricter warnings/errors enabled
        source: Source directory; overrides config setting
        target: Output directory; overrides config setting
    """
    source = source or ctx.sphinx.source
    target = target or ctx.sphinx.target
    if language:
        opts = f'-D language={language}'
        target = f'{target}/{language}'
    if nitpick:
        opts += " -n -W -T"
    cmd = f"sphinx-build {opts} {source} {target}"
    logger.info(f"{source} => {target}")
    ctx.run(cmd, pty=pty)

@task
def intl(ctx: Context, language: str = 'en'):
    '''Update the POT file and invoke the `sphinx-intl update` command

    Only used with `invoke intl.update`
    '''
    opts = "-b gettext"
    target = Path(ctx.sphinx.target).parent / 'gettext'
    if language == 'en':
        clean(ctx)
        build(ctx, target=target, opts=opts)
    elif language:
        if not Path(target).exists():
            build(ctx, target=target, opts=opts)
        ctx.run(
            f'sphinx-intl update -p {target} -l {language}'
        )
        # for DIR in ['pages', 'posts', 'shop']:
        #     rmtree(f'locales/{language}/LC_MESSAGES/{DIR}/')

@task
def doctest(ctx: Context):
    """
    Run Sphinx' doctest builder.

    This will act like a test run, displaying test results & exiting nonzero if
    all tests did not pass.

    A temporary directory is used for the build target, as the only output is
    the text file which is automatically printed.
    """
    tmpdir = mkdtemp()
    try:
        opts = "-b doctest"
        target = tmpdir
        clean(ctx)
        build(ctx, target=target, opts=opts)
    finally:
        rmtree(tmpdir)

@task
def tree(ctx: Context):
    """
    Display documentation contents with the 'tree' program.
    """
    ignore = ".git|*.pyc|*.swp|dist|*.egg-info|_static|_build|_templates"
    ctx.run(f'tree -Ca -I "{ignore}" {ctx.sphinx.source}')
