"""``click`` options regarding targets."""

import click

from vws_cli.options._types import ClickOptionDecorator

target_id_option: ClickOptionDecorator = click.option(
    "--target-id",
    type=str,
    help="The ID of a target in the Vuforia database.",
    required=True,
)
