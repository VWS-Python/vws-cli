#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration for Sphinx.
"""

# pylint: disable=invalid-name

import datetime
from typing import List, Tuple

import vws_cli

project = 'VWS-CLI'
author = 'Adam Dangoor'

extensions = [
    'sphinxcontrib.spelling',
    'sphinx_click.ext',
    'sphinx_substitution_extensions',
]

templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'

year = datetime.datetime.now().year
copyright = f'{year}, {author}'  # pylint: disable=redefined-builtin

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
version = vws_cli.__version__
release = version.split('+')[0]

substitutions = [
    ('|release|', release),
    ('|github-owner|', 'adamtheturtle'),
    ('|github-repository|', 'vws-cli'),
]

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
    'python': ('https://docs.python.org/3.7', None),
}
nitpicky = True
warning_is_error = True
nitpick_ignore: List[Tuple[str, str]] = []

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
"""
