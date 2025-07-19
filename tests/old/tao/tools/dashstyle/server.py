import logging
from dash import Dash
import socket

# def interpolate_str(template, **data):
#     s = template
#     for k, v in data.items():
#         key = "{%" + k + "%}"
#         s = s.replace(key, v)
#     return s


def get_Host_name_IP():
    try:
        host_name = socket.gethostname()
        host_ip = socket.gethostbyname(host_name)
        logging.info(f"Hostname: {host_name}\nIP: {host_ip}")
    except:
        logging.info("Unable to get Hostname and IP")
        host_ip = 'localhost'
    return host_ip


# Driver code
host_ip = get_Host_name_IP()  # Function call

# This code is conributed by "Sharad_Bhardwaj".


NAME = __name__

META_TAGS = [
    {
        'name': 'description',
        'content': 'Using AI to develop anything interesting'
    },
    # A tag that tells the browser not to scale
    # desktop widths to fit mobile screens.
    # Sets the width of the viewport (browser)
    # to the width of the device, and the zoom level
    # (initial scale) to 1.
    #
    # Necessary for "true" mobile support.
    {
        'name': 'viewport',
        'content': 'width=device-width, initial-scale=1, shrink-to-fit=no'
    }
]


def create_app(name=NAME, title='Dash', external_stylesheets=None, **kwargs):
    # external_scripts = ['https://www.google-analytics.com/analytics.js']
    external_scripts = [
        "https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-MML-AM_CHTML"]

    _external_stylesheets = ['https://xinetzone.github.io/Font-Awesome/css/all.css',
                             'https://xinetzone.github.io/w3css/4/w3.css',
                             'https://xinetzone.github.io/xinet-css/tabs.css']
    if external_stylesheets==None:
        external_stylesheets = _external_stylesheets
    kw = {
        'meta_tags': META_TAGS,
        'external_stylesheets': external_stylesheets,
        'external_scripts': external_scripts
    }
    kwargs.update(kw)
    app = Dash(name, title=title, **kwargs)
    return app


index_string_template = '''<!DOCTYPE html>
<html lang="zh">
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <article>
            {%config%}
            {%scripts%}
            {%renderer%}
        </article>
    </body>
</html>
'''


async def run_server(app, layout, host=host_ip, port=8050, mode='external', debug=True, **kw):
    # host='0.0.0.0' 、 127.0.0.1
    # app = create_app()
    app.index_string = index_string_template
    app.layout = layout
    app.run_server(mode, host=host, port=port,
                   debug=debug, use_reloader=False, **kw)
