# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import tomli
from sphinx.application import Sphinx

pyproject_file = tomli.load(open('../pyproject.toml', 'rb'))
project_config = pyproject_file['project']
tool_config = pyproject_file['tool']

project = project_config['name']
project_copyright = '2024, Will Siddall'
author = ', '.join([author['name'] for author in project_config['authors']])
release = project_config['version']

repo_url = project_config['urls']['Repository']
doc_url = project_config['urls']['Homepage']

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.doctest',
    'sphinx.ext.graphviz',
    'matplotlib.sphinxext.plot_directive',
]

templates_path = ['_templates']
exclude_patterns = []
rst_prolog = f"""
.. |git_url| replace:: {repo_url}
.. |project_title| replace:: **{project}**
"""

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']


def setup(_app: Sphinx):
    pass
