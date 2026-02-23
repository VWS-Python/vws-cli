"""``click`` options for VWS API options."""

from collections.abc import Callable
from typing import Any

import click
from beartype import beartype


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
