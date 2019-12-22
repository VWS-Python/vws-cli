"""
A CLI for the Vuforia Cloud Recognition Service API.
"""

import click


@click.command(name='vuforia-cloud-reco')
def vuforia_cloud_reco() -> None:
    """
    Make a request to the Vuforia Cloud Recognition Service API.
    """
