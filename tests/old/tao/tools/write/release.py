'''代码，可能改变'''

from invoke import task


@task
def install(ctx, name='doc'):
    # --use-feature=in-tree-build
    ctx.run(f'pip install .[{name}] ')


# namespace = Collection(docs, deploy)
