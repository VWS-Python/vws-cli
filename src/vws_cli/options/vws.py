"""``click`` options for VWS API options."""

from collections.abc import Callable
from typing import Any

import click
from beartype import beartype


@beartype
def database_id_option(
    command: Callable[..., Any],
) -> Callable[..., Any]:
    """An option decorator for the Vuforia database ID."""
    return click.option(
        "--database-id",
        type=str,
        help=(
            "The ID of the Vuforia database which the given server keys "
            "belong to. This is shown in the Vuforia target manager."
        ),
        required=True,
        envvar="VUFORIA_DATABASE_ID",
        show_envvar=True,
    )(command)


@beartype
def base_vws_url_option(
    command: Callable[..., Any],
) -> Callable[..., Any]:
    """An option decorator for choosing the base VWS URL."""
    return click.option(
        "--base-vws-url",
        type=click.STRING,
        default="https://vws.vuforia.com",
        help="The base URL for the VWS API.",
        show_default=True,
    )(command)
