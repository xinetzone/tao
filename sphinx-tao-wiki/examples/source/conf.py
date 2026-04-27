# -*- coding: utf-8 -*-

from datetime import datetime

project = 'Sphinx 道德经'
author = '道教学者'
copyright = f'{datetime.now().year}, {author}'
release = '1.0.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.viewcode',
    'sphinx.ext.mathjax',
]

templates_path = ['_templates']
exclude_patterns = []

html_theme = 'alabaster'
html_static_path = ['_static']
html_css_files = ['custom.css']

todo_include_todos = True
