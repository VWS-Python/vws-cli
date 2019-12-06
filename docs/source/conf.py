#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration for Sphinx.
"""

# pylint: disable=invalid-name

import datetime
import os
import sys
from email import message_from_string

import pkg_resources

import vws_cli

sys.path.insert(0, os.path.abspath('.'))

key_package = vws_cli

extensions = [
    'sphinxcontrib.spelling',
    'sphinx_click.ext',
]

templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'

package_name = key_package.__name__
# Normalize as per https://www.python.org/dev/peps/pep-0440/.
normalized_package_name = package_name.replace('_', '-').lower()
distributions = {v.key: v for v in set(pkg_resources.working_set)}
distribution = distributions[normalized_package_name]
project_name = distribution.project_name

pkg_info = distribution.get_metadata('PKG-INFO')
pkg_info_as_message = message_from_string(pkg_info)

project = pkg_info_as_message['Name']
author = pkg_info_as_message['Author']
year = datetime.datetime.now().year
copyright = f'{year}, {author}'  # pylint: disable=redefined-builtin

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
version = key_package.__version__
release = version.split('+')[0]

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
nitpick_ignore = []

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
]

spelling_word_list_filename = '../../spelling_private_dict.txt'

autodoc_member_order = 'bysource'

rst_prolog = f"""
.. |project| replace:: {project}
"""
