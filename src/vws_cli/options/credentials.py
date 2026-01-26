"""``click`` options regarding credentials."""

from collections.abc import Callable
from typing import Any

import click
from beartype import beartype


@beartype
def server_access_key_option(
    command: Callable[..., Any],
) -> Callable[..., Any]:
    """An option decorator for the Vuforia server access key."""
    return click.option(
        "--server-access-key",
        type=str,
        help=(
            "A Vuforia server access key to use to access the Vuforia Web "
            "Services API."
        ),
        required=True,
        envvar="VUFORIA_SERVER_ACCESS_KEY",
        show_envvar=True,
    )(command)


@beartype
def server_secret_key_option(
    command: Callable[..., Any],
) -> Callable[..., Any]:
    """An option decorator for the Vuforia server secret key."""
    return click.option(
        "--server-secret-key",
        type=str,
        help=(
            "A Vuforia server secret key to use to access the Vuforia Web "
            "Services API."
        ),
        required=True,
        envvar="VUFORIA_SERVER_SECRET_KEY",
        show_envvar=True,
    )(command)


@beartype
def client_access_key_option(
    command: Callable[..., Any],
) -> Callable[..., Any]:
    """An option decorator for the Vuforia client access key."""
    return click.option(
        "--client-access-key",
        type=str,
        help=(
            "A Vuforia client access key to use to access the Vuforia "
            "Cloud Recognition API."
        ),
        required=True,
        envvar="VUFORIA_CLIENT_ACCESS_KEY",
        show_envvar=True,
    )(command)


@beartype
def client_secret_key_option(
    command: Callable[..., Any],
) -> Callable[..., Any]:
    """An option decorator for the Vuforia client secret key."""
    return click.option(
        "--client-secret-key",
        type=str,
        help=(
            "A Vuforia client secret key to use to access the Vuforia "
            "Cloud Recognition API."
        ),
        required=True,
        envvar="VUFORIA_CLIENT_SECRET_KEY",
        show_envvar=True,
    )(command)
