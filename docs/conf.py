# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys
from setuptools_scm import get_version

sys.path.insert(0, os.path.abspath('../ldlm'))

project = 'py-ldlm'
copyright = '2024, Ian Moore'
author = 'Ian Moore'
release = get_version(root=os.path.abspath('../'))

extensions = [
    'myst_parser',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
]

autodoc_default_options = {
    'member-order': 'bysource',
}

autoclass_content = "both"

templates_path = []
exclude_patterns = []

#jhtml_theme = 'furo'  #'sphinx_rtd_theme'
html_theme = 'sphinx_rtd_theme'
#html_static_path = ['_static']
#templates_path = ['_templates']

#html_sidebars = { '**': ['globaltoc.html', 'relations.html', 'sourcelink.html', 'searchbox.html'], }
