# Configuration file for the Sphinx documentation builder.

project = 'ai-dao-agents'
copyright = '2026, AI Dao'
author = 'AI Dao'
release = '0.1.0'

# -- General configuration ---------------------------------------------------

extensions = [
    'myst_parser',
]

source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

master_doc = 'index'

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
