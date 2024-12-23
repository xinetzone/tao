from pathlib import Path
from shutil import rmtree
from invoke import task


@task
def clean(c):
    output = Path(c.sphinx.target)
    if output.exists():
        print(f'delete {output}')
        rmtree(output)


@task(
    default=True,
    help={
        "opts": "Extra sphinx-build options/args",
        "nitpick": "Build with stricter warnings/errors enabled",
        "source": "Source directory; overrides config setting",
        "target": "Output directory; overrides config setting",
    },
)
def build(c,
          opts=None,
          language=None,
          source=None,
          target=None,
          nitpick=False):
    """
    Build the project's Sphinx docs.
    """
    if opts is None:
        opts = ""
    source = source or c.sphinx.source
    target = target or c.sphinx.target
    if language:
        opts = f'-D language={language}'
        target = f'{target}/{language}'
    if nitpick:
        opts += " -n -W -T"
    cmd = f"sphinx-build {opts} {source} {target}"
    print(source, target)
    c.run(cmd)


@task
def update(c, language='en'):
    '''Update the POT file and invoke the `sphinx-intl` `update` command

    Only used with `invoke intl.update`
    '''
    opts = "-b gettext"
    target = Path(c.sphinx.target).parent / 'gettext'
    if language == 'en':
        clean(c)
        build(c, target=target, opts=opts)
    else:
        if not Path(target).exists():
            build(c, target=target, opts=opts)
        c.run(
            f'sphinx-intl update -p {target} -l {language}'
        )
        # for DIR in ['pages', 'posts', 'shop']:
        #     rmtree(f'locales/{language}/LC_MESSAGES/{DIR}/')
