# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import os
import sys

sys.path.insert(0, os.path.abspath('../ldlm'))

project = 'py-ldlm'
copyright = '2024, Google LLC'
author = 'Ian Moore'
release = os.getenv("READTHEDOCS_VERSION_NAME", "latest")

extensions = [
    'myst_parser',
    'sphinx_copybutton',
    'sphinx.ext.autosectionlabel',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
]

autodoc_default_options = {
    'member-order': 'bysource',
}

autoclass_content = "both"
autosectionlabel_prefix_document = True

templates_path = []
exclude_patterns = []

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_theme_options = {}
html_favicon = 'favicon.ico'
