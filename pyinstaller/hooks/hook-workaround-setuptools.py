"""
A PyInstaller hook to work around
https://github.com/pypa/setuptools/issues/1963.
"""

from PyInstaller.utils.hooks import collect_submodules

hiddenimports = collect_submodules('pkg_resources')
