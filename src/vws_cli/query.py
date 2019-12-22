import click

from vws_cli import __version__

@click.command(name='vuforia-cloud-reco')
# We set the ``version`` parameter because in PyInstaller binaries,
# ``pkg_resources`` is not available.
#
# Click uses ``pkg_resources`` to determine the version if it is not given.
@click.version_option(version=__version__)
def vuforia_cloud_reco() -> None:
    """
    XXX
    """

