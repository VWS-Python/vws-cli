"""
XXX
"""

from typing import Callable, Optional
from pathlib import Path
import click_pathlib
import click

from vws_cli import __version__

def image_argument(
    command: Optional[Callable[..., None]] = None,
) -> Callable[..., None]:
    """
    An argument decorator for choosing a query image.
    """
    click_option_function = click.argument(
        'image',
        type=click_pathlib.Path(
            exists=True,
            file_okay=True,
            dir_okay=False,
        ),
    )

    return click_option_function(command)


@click.command(name='vuforia-cloud-reco')
# We set the ``version`` parameter because in PyInstaller binaries,
# ``pkg_resources`` is not available.
#
# Click uses ``pkg_resources`` to determine the version if it is not given.
@image_argument
@click.version_option(version=__version__)
def vuforia_cloud_reco(image: Path) -> None:
    """
    XXX
    """
