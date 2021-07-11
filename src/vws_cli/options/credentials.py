"""
``click`` options regarding credentials.
"""

from __future__ import annotations

from typing import Callable

import click


def server_access_key_option(
    command: Callable[..., None] | None = None,
) -> Callable[..., None]:
    """
    An option decorator for the Vuforia server access key.
    """
    click_option_function: Callable[
        [Callable[..., None]],
        Callable[..., None],
    ] = click.option(
        '--server-access-key',
        type=str,
        help=(
            'A Vuforia server access key to use to access the Vuforia Web '
            'Services API.'
        ),
        required=True,
        envvar='VUFORIA_SERVER_ACCESS_KEY',
        show_envvar=True,
    )
    assert command is not None
    function: Callable[..., None] = click_option_function(command)
    return function


def server_secret_key_option(
    command: Callable[..., None] | None = None,
) -> Callable[..., None]:
    """
    An option decorator for the Vuforia server secret key.
    """
    click_option_function: Callable[
        [Callable[..., None]],
        Callable[..., None],
    ] = click.option(
        '--server-secret-key',
        type=str,
        help=(
            'A Vuforia server secret key to use to access the Vuforia Web '
            'Services API.'
        ),
        required=True,
        envvar='VUFORIA_SERVER_SECRET_KEY',
        show_envvar=True,
    )
    assert command is not None
    function: Callable[..., None] = click_option_function(command)
    return function


def client_access_key_option(
    command: Callable[..., None] | None = None,
) -> Callable[..., None]:
    """
    An option decorator for the Vuforia client access key.
    """
    click_option_function: Callable[
        [Callable[..., None]],
        Callable[..., None],
    ] = click.option(
        '--client-access-key',
        type=str,
        help=(
            'A Vuforia client access key to use to access the Vuforia '
            'Cloud Recognition API.'
        ),
        required=True,
        envvar='VUFORIA_CLIENT_ACCESS_KEY',
        show_envvar=True,
    )
    assert command is not None
    function: Callable[..., None] = click_option_function(command)
    return function


def client_secret_key_option(
    command: Callable[..., None] | None = None,
) -> Callable[..., None]:
    """
    An option decorator for the Vuforia client secret key.
    """
    click_option_function: Callable[
        [Callable[..., None]],
        Callable[..., None],
    ] = click.option(
        '--client-secret-key',
        type=str,
        help=(
            'A Vuforia client secret key to use to access the Vuforia '
            'Cloud Recognition API.'
        ),
        required=True,
        envvar='VUFORIA_CLIENT_SECRET_KEY',
        show_envvar=True,
    )
    assert command is not None
    function: Callable[..., None] = click_option_function(command)
    return function
