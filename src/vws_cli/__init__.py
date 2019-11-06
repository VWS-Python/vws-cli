import click

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

@click.command(name='list-targets')
def list_targets():
    pass

vws_group.add_command(list_targets)
