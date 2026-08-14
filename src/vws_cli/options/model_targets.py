"""``click`` options regarding Model Target datasets."""

from collections.abc import Callable
from typing import Any

import click
from beartype import beartype
from vws.model_target_datasets import ModelTargetDatasetType


@beartype
def client_id_option(
    command: Callable[..., Any],
) -> Callable[..., Any]:
    """An option decorator for the Model Target Web API client ID."""
    return click.option(
        "--client-id",
        type=str,
        help=(
            "A Vuforia OAuth2 client ID to use to access the Model Target "
            "Web API."
        ),
        required=True,
        envvar="VUFORIA_MODEL_TARGET_CLIENT_ID",
        show_envvar=True,
    )(command)


@beartype
def client_secret_option(
    command: Callable[..., Any],
) -> Callable[..., Any]:
    """An option decorator for the Model Target Web API client secret."""
    return click.option(
        "--client-secret",
        type=str,
        help=(
            "A Vuforia OAuth2 client secret to use to access the Model "
            "Target Web API."
        ),
        required=True,
        envvar="VUFORIA_MODEL_TARGET_CLIENT_SECRET",
        show_envvar=True,
    )(command)


@beartype
def dataset_type_option(
    command: Callable[..., Any],
) -> Callable[..., Any]:
    """An option decorator for the kind of Model Target dataset."""
    return click.option(
        "--dataset-type",
        type=click.Choice(
            choices=ModelTargetDatasetType,
            case_sensitive=False,
        ),
        default=ModelTargetDatasetType.STANDARD.value,
        help=(
            "The kind of Model Target dataset. Standard and advanced "
            "datasets are separate resources, so a dataset created as one "
            "type is not visible to requests for the other type."
        ),
        show_default=True,
    )(command)


@beartype
def dataset_uuid_option(
    command: Callable[..., Any],
) -> Callable[..., Any]:
    """An option decorator for the UUID of a Model Target dataset."""
    return click.option(
        "--dataset-uuid",
        type=str,
        help=(
            "The UUID of a Model Target dataset, as given when the dataset "
            "was created."
        ),
        required=True,
    )(command)
