"""``click`` options regarding timeouts."""

from collections.abc import Callable
from typing import Any

import click
from beartype import beartype


@beartype
def connection_timeout_seconds_option(
    command: Callable[..., Any],
) -> Callable[..., Any]:
    """An option decorator for the connection timeout."""
    return click.option(
        "--connection-timeout-seconds",
        type=click.FloatRange(min=0.05),
        default=30,
        help="The connection timeout for HTTP requests, in seconds.",
        show_default=True,
    )(command)


@beartype
def read_timeout_seconds_option(
    command: Callable[..., Any],
) -> Callable[..., Any]:
    """An option decorator for the read timeout."""
    return click.option(
        "--read-timeout-seconds",
        type=click.FloatRange(min=0.05),
        default=30,
        help="The read timeout for HTTP requests, in seconds.",
        show_default=True,
    )(command)
