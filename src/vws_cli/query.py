import click

from vws_cli import __version__

def image_argument(
    command: Optional[Callable[..., None]] = None,
) -> Callable[..., None]:
    """
    An argument decorator for choosing a query image.
    """
    click_option_function = click.argument(
        type=click_pathlib.Path(
            exists=True,
            file_okay=True,
            dir_okay=False,
        ),
        help='The path to an image to upload and set as the target image.',
        required=required,
    )

    return click_option_function(command)


@click.command(name='vuforia-cloud-reco')
# We set the ``version`` parameter because in PyInstaller binaries,
# ``pkg_resources`` is not available.
#
# Click uses ``pkg_resources`` to determine the version if it is not given.
@click.
@click.version_option(version=__version__)
def vuforia_cloud_reco() -> None:
    """
    XXX
    """
