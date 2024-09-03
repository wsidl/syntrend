# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import tomli

pyproject_file = tomli.load(open('../pyproject.toml', 'rb'))
tool_config = pyproject_file['tool']

project = tool_config['poetry']['name']
project_copyright = '2024, Will Siddall'
author = 'Will Siddall'
release = tool_config['poetry']['version']

project_url = 'https://github.com/wsidl/syntrend'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.doctest',
]

templates_path = ['_templates']
exclude_patterns = []
rst_prolog = f"""
.. |git_url| replace:: {project_url}
.. |project_title| replace:: **{project}**
"""

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
