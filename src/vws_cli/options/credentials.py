"""
``click`` options regarding credentials.
"""

from typing import Callable

import click


def server_access_key_option(command: Callable[..., None],
                             ) -> Callable[..., None]:
    """
    An option decorator for the Vuforia server access key.
    """
    click_option_function: Callable[
        [Callable[..., None]], Callable[..., None]] = click.option(
            '--server-access-key',
            type=str,
            help=(
                'A Vuforia server access key to use to access the Vuforia Web '
                'Services API'
            ),
            required=True,
        )
    function: Callable[..., None] = click_option_function(command)
    return function


def server_secret_key_option(command: Callable[..., None],
                             ) -> Callable[..., None]:
    """
    An option decorator for the Vuforia server secret key.
    """
    click_option_function: Callable[
        [Callable[..., None]], Callable[..., None]] = click.option(
            '--server-secret-key',
            type=str,
            help=(
                'A Vuforia server secret key to use to access the Vuforia Web '
                'Services API'
            ),
            required=True,
        )
    function: Callable[..., None] = click_option_function(command)
    return function
