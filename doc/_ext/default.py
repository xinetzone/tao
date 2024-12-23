import sys
if sys.platform == 'win32':
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
from docutils import nodes

from sphinx.application import Sphinx
from sphinx.util.docutils import SphinxDirective, SphinxRole
from sphinx.util.typing import ExtensionMetadata


def setup(app: Sphinx) -> ExtensionMetadata:
    app.add_config_value('xxx', False, 'html')
    app.setup_extension('myst_nb')
    # app.config.xxx = True
    print(app.config)
    return {
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
