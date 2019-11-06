import click
from typing import Callable

_CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(name='vws', context_settings=_CONTEXT_SETTINGS)
# We set the ``version`` parameter because in PyInstaller binaries,
# ``pkg_resources`` is not available.
#
# Click uses ``pkg_resources`` to determine the version if it is not given.
#@click.version_option(version=vws_cli.__version__)
@click.version_option(version='0')
def vws_group() -> None:
    """
    Manage VWS.
    """

def server_access_key_option(
    command: Callable[..., None],
) -> Callable[..., None]:
    """
    An option decorator for XXX.
    """
    click_option_function: Callable[[Callable[..., None]], Callable[..., None]] = click.option(
        '--server-access-key',
        type=str,
        help='XXX',
    )
    function: Callable[..., None] = click_option_function(command)
    return function

def server_secret_key_option(
    command: Callable[..., None],
) -> Callable[..., None]:
    """
    An option decorator for XXX.
    """
    click_option_function: Callable[[Callable[..., None]], Callable[..., None]] = click.option(
        '--server-secret-key',
        type=str,
        help='XXX',
    )
    function: Callable[..., None] = click_option_function(command)
    return function


@click.command(name='list-targets')
@server_access_key_option
@server_secret_key_option
def list_targets(
    server_access_key: str,
    server_secret_key: str,
):
    pass

vws_group.add_command(list_targets)
