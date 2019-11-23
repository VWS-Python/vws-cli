import sys
from typing import Any, Callable, Dict, Tuple

import click
import wrapt
from vws.exceptions import UnknownTarget


@wrapt.decorator
def handle_unknown_target(
    wrapped: Callable[..., str],
    instance: Any,
    args: Tuple,
    kwargs: Dict,
) -> None:
    try:
        wrapped(*args, **kwargs)
    except UnknownTarget as exc:
        click.echo(f'Target "{exc.target_id}" does not exist.', err=True)
        sys.exit(1)
