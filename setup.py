"""
Setup script for DC/OS End to End tests.
"""

from pathlib import Path
from setuptools import find_packages, setup
from typing import List


def _get_dependencies(requirements_file: Path) -> List[str]:
    """
    Return requirements from a requirements file.

    This expects a requirements file with no ``--find-links`` lines.
    """
    lines = requirements_file.read_text().strip().split('\n')
    return [line for line in lines if not line.startswith('#')]


_DIRECT_REQUIRES = _get_dependencies(
    requirements_file=Path('requirements.txt'),
)

INSTALL_REQUIRES = _DIRECT_REQUIRES
DEV_REQUIRES = _get_dependencies(
    requirements_file=Path('dev-requirements.txt'),
)
PACKAGING_REQUIRES = _get_dependencies(
    requirements_file=Path('packaging-requirements.txt'),
)

LONG_DESCRIPTION = Path('README.rst').read_text()

setup(
    name='TODO',
    author='Adam Dangoor',
    author_email='todo',
    description='todo.',
    long_description=LONG_DESCRIPTION,
    packages=find_packages(where='src'),
    zip_safe=False,
    package_dir={'': 'src'},
    install_requires=INSTALL_REQUIRES,
    include_package_data=True,
    license='TODO',
    keywords='todo',
    url='https://github.com/adamtheturtle/vws-cli',
    extras_require={
        'dev': DEV_REQUIRES,
        'packaging': PACKAGING_REQUIRES,
    },
    classifiers=[
        'Operating System :: POSIX',
        'Environment :: Web Environment',
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: MIT',
        'Development Status :: 5 - Production/Stable',
    ],
    # Avoid dependency links because they are not supported by Read The Docs.
    #
    # Also, they require users to use ``--process-dependency-links``.
    dependency_links=[],
    entry_points="""
        [console_scripts]
        vws=vws_cli:vws_group
    """,
)
