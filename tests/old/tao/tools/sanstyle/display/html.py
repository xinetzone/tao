from string import Template
from urllib.parse import urlencode

element_template = Template(
    '''<${tag} class="${className}" type="${typeName}" ${config}">${content}</${tag}>''')
frame_template = Template(
    '''<${tag} class="${className}" type="${typeName}" src="${src}${params}" ${config}>''')


class Embed:
    """
    Generic class to embed an embed in an IPython notebook
    """
    _embed = """<embed type="{typeName}" class="{className}" width="{width}" height="{height}" src="{src}{params}">"""

    def __init__(self, src, height, width='100%', className='w3-card w3-pale-blue', typeName='text/html', **kwargs):
        self.typeName = typeName
        self.className = className
        self.src = src
        self.width = width
        self.height = height
        self.params = kwargs

    def _repr_html_(self):
        """return the embed iframe"""
        if self.params:
            params = "?" + urlencode(self.params)
        else:
            params = ""
        config = {
            'typeName': self.typeName,
            'src': self.src,
            'className': self.className,
            'width': self.width,
            'height': self.height,
            'params': params
        }
        return self._embed.format(**config)