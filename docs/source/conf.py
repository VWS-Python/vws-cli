#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration for Sphinx.
"""

# pylint: disable=invalid-name

import datetime
from typing import Tuple

from pkg_resources import get_distribution

project = 'VWS-CLI'
author = 'Adam Dangoor'

extensions = [
    'sphinxcontrib.spelling',
    'sphinx_click.ext',
    'sphinx-prompt',
    'sphinx_substitution_extensions',
]

templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'

year = datetime.datetime.now().year
project_copyright = f'{year}, {author}'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# Use ``pkg_resources`` as per
# https://github.com/pypa/setuptools_scm#usage-from-sphinx.
version = get_distribution(project).version
_month, _day, _year, *_ = version.split('.')
release = f'{_month}.{_day}.{_year}'

language = None

# The name of the syntax highlighting style to use.
pygments_style = 'sphinx'
html_theme = 'alabaster'

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
#
# This is required for the alabaster theme
# refs: http://alabaster.readthedocs.io/en/latest/installation.html#sidebars
html_sidebars = {
    '**': [
        'relations.html',  # needs 'show_related': True theme option to display
        'searchbox.html',
    ],
}

# Output file base name for HTML help builder.
htmlhelp_basename = 'VWSCLIdoc'
autoclass_content = 'init'
intersphinx_mapping = {
    'python': ('https://docs.python.org/3.9', None),
}
nitpicky = True
warning_is_error = True
nitpick_ignore: list[Tuple[str, str]] = []

html_show_copyright = False
html_show_sphinx = False
html_show_sourcelink = False
autoclass_content = 'both'

html_theme_options = {
    'show_powered_by': 'false',
}

html_sidebars = {
    '**': [
        'about.html',
        'navigation.html',
        'searchbox.html',
    ],
}

# Don't check anchors because many websites use #! for AJAX magic
# http://sphinx-doc.org/config.html#confval-linkcheck_anchors
linkcheck_anchors = False
# Retry link checking to avoid transient network errors.
linkcheck_retries = 5
linkcheck_ignore = [
    # Requires login.
    r'https://developer.vuforia.com/targetmanager',
    # Only used for API calls
    r'https://cloudreco.vuforia.com',
    r'https://vws.vuforia.com',
]

spelling_word_list_filename = '../../spelling_private_dict.txt'

autodoc_member_order = 'bysource'

rst_prolog = f"""
.. |project| replace:: {project}
.. |release| replace:: {release}
.. |github-owner| replace:: VWS-Python
.. |github-repository| replace:: vws-cli
"""
