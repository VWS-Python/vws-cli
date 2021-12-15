"""
Release the next version.
"""

import os
from pathlib import Path

from binaries import make_linux_binaries  # pylint: disable=import-error


def main() -> None:
    """
    Perform a release.
    """
    make_linux_binaries(repo_root=Path('.'))


if __name__ == '__main__':
    main()
