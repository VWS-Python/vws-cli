"""``click`` commands for the Vuforia Model Target Web API."""

import base64
import contextlib
import dataclasses
import json
import sys
from collections.abc import Generator, Sequence
from enum import StrEnum
from pathlib import Path
from typing import Any

import click
import yaml
from beartype import beartype
from vws import ModelTargetService
from vws.exceptions.custom_exceptions import ServerError
from vws.exceptions.model_target_exceptions import (
    ModelTargetDatasetTimeoutError,
    ModelTargetError,
    ModelTargetOAuth2Error,
)
from vws.exceptions.vws_exceptions import TooManyRequestsError
from vws.model_target_datasets import (
    AutomaticColoring,
    CadDataFormat,
    GuideViewPosition,
    ModelTargetDatasetType,
    ModelTargetModel,
    ModelTargetView,
    MotionHint,
    OptimizeTrackingFor,
    RealisticAppearance,
    Simplify,
    TrackingMode,
)
from vws.reports import (
    ModelTargetDatasetStatuses,
    ModelTargetDatasetStatusReport,
)

from vws_cli._error_handling import get_model_target_error_message
from vws_cli.options.model_targets import (
    client_id_option,
    client_secret_option,
    dataset_type_option,
    dataset_uuid_option,
)
from vws_cli.options.timeout import (
    connection_timeout_seconds_option,
    read_timeout_seconds_option,
)
from vws_cli.options.vws import base_vws_url_option

_SECONDS_BETWEEN_REQUESTS_DEFAULT = 0.2

_SECONDS_BETWEEN_REQUESTS_HELP = (
    "The number of seconds to wait between requests made while polling the "
    "dataset status. "
    f"We wait {_SECONDS_BETWEEN_REQUESTS_DEFAULT} seconds by default, rather "
    "than less, than that to decrease the number of calls made to the API, to "
    "decrease the likelihood of hitting the request quota."
)

_TIMEOUT_SECONDS_HELP = (
    "The maximum number of seconds to wait for the dataset to be generated."
)


@beartype
@contextlib.contextmanager
def _handle_model_target_exceptions() -> Generator[None]:
    """Show error messages and catch exceptions from ``VWS-Python``."""
    error_message = ""
    error_stream = sys.stderr

    try:
        yield
    except (
        ModelTargetError,
        ModelTargetOAuth2Error,
        ServerError,
        TooManyRequestsError,
    ) as exc:
        error_message = get_model_target_error_message(exc=exc)
    else:
        return

    click.echo(message=error_message, file=error_stream)
    sys.exit(1)


@beartype
def _model_target_client(
    *,
    client_id: str,
    client_secret: str,
    base_vws_url: str,
    connection_timeout_seconds: float,
    read_timeout_seconds: float,
) -> ModelTargetService:
    """Get a client for the Model Target Web API."""
    return ModelTargetService(
        client_id=client_id,
        client_secret=client_secret,
        base_vws_url=base_vws_url,
        request_timeout_seconds=(
            connection_timeout_seconds,
            read_timeout_seconds,
        ),
    )


@beartype
def _status_report_yaml(*, report: ModelTargetDatasetStatusReport) -> str:
    """Get a YAML representation of a dataset status report."""
    report_dict = dataclasses.asdict(obj=report)
    report_dict["status"] = report.status.value
    for key in ("created_at", "eta", "completed_at"):
        value = report_dict[key]
        report_dict[key] = None if value is None else str(object=value)
    return yaml.dump(data=report_dict)


_MODELS_FILE_HINT = "'--models-file'"

_MODEL_STRING_FIELDS = {
    "cadDataBlob": "cad_data_blob",
    "cadDataUrl": "cad_data_url",
    "name": "name",
    "stateBasedConfigurationJsonString": (
        "state_based_configuration_json_string"
    ),
}

_MODEL_ENUM_FIELDS: dict[str, tuple[str, type[StrEnum]]] = {
    "automaticColoring": ("automatic_coloring", AutomaticColoring),
    "cadDataFormat": ("cad_data_format", CadDataFormat),
    "motionHint": ("motion_hint", MotionHint),
    "optimizeTrackingFor": ("optimize_tracking_for", OptimizeTrackingFor),
    "realisticAppearance": ("realistic_appearance", RealisticAppearance),
    "simplify": ("simplify", Simplify),
    "trackingMode": ("tracking_mode", TrackingMode),
}

_MODEL_FIELDS = frozenset(
    {*_MODEL_STRING_FIELDS, *_MODEL_ENUM_FIELDS, "views"},
)

_VIEW_FIELDS = frozenset({"guideViewPosition", "name", "states"})

_POSITION_FIELDS = frozenset({"rotation", "translation"})


@beartype
def _models_file_error(*, message: str) -> click.BadParameter:
    """Get an error to raise for an invalid models file."""
    return click.BadParameter(message=message, param_hint=_MODELS_FILE_HINT)


@beartype
def _is_json_object(*, value: object) -> bool:
    """Get whether a value from a models file is an object."""
    return isinstance(value, dict)


@beartype
def _is_json_array(*, value: object) -> bool:
    """Get whether a value from a models file is an array."""
    return isinstance(value, list)


@beartype
def _as_json_object(*, value: object) -> dict[str, Any] | None:
    """Get an object from a models file, or ``None``."""
    if not _is_json_object(value=value):
        return None
    # The value goes through a variable which is typed as ``Any`` so that
    # the keys and values of the returned object are not unknown types.
    value_any: Any = value
    value_dict: dict[str, Any] = value_any
    return value_dict


@beartype
def _json_object(*, value: object, message: str) -> dict[str, Any]:
    """Get an object from a models file, or raise an error."""
    value_dict = _as_json_object(value=value)
    if value_dict is None:
        raise _models_file_error(message=message)
    return value_dict


@beartype
def _json_array(*, value: object, message: str) -> list[Any]:
    """Get an array from a models file, or raise an error."""
    if not _is_json_array(value=value):
        raise _models_file_error(message=message)
    # The value goes through a variable which is typed as ``Any`` so that
    # the items of the returned array are not unknown types.
    value_any: Any = value
    value_list: list[Any] = value_any
    return value_list


@beartype
def _checked_object(
    *,
    value: object,
    known_fields: frozenset[str],
    required_fields: Sequence[str],
    path: str,
) -> dict[str, Any]:
    """Get an object with known and required fields, or raise an error."""
    value_dict = _json_object(
        value=value,
        message=f"{path} must be an object.",
    )
    unknown_fields = sorted(set(value_dict) - known_fields)
    if unknown_fields:
        message = f"{path} has unknown fields: {', '.join(unknown_fields)}."
        raise _models_file_error(message=message)

    for required_field in required_fields:
        if required_field not in value_dict:
            message = f"{path}/{required_field} is required."
            raise _models_file_error(message=message)

    return value_dict


@beartype
def _string_value(*, value: object, path: str) -> str:
    """Get a string from a models file, or raise an error."""
    if not isinstance(value, str):
        message = f"{path} must be a string."
        raise _models_file_error(message=message)
    return value


@beartype
def _enum_value(
    *,
    value: object,
    enum_type: type[StrEnum],
    path: str,
) -> StrEnum:
    """Get an enumeration member from a models file, or raise an error."""
    string_value = _string_value(value=value, path=path)
    try:
        return enum_type(value=string_value)
    except ValueError as exc:
        allowed = ", ".join(sorted(member.value for member in enum_type))
        message = f"{path} must be one of: {allowed}."
        raise _models_file_error(message=message) from exc


@beartype
def _number_sequence(*, value: object, path: str) -> Sequence[float]:
    """Get a sequence of numbers from a models file, or raise an error."""
    message = f"{path} must be an array of numbers."
    items = _json_array(value=value, message=message)
    for item in items:
        if isinstance(item, bool) or not isinstance(item, int | float):
            raise _models_file_error(message=message)

    return [float(item) for item in items]


@beartype
def _guide_view_position_from_json(
    *,
    value: object,
    path: str,
) -> GuideViewPosition:
    """Get a guide view position from a models file, or raise an error."""
    position_dict = _checked_object(
        value=value,
        known_fields=_POSITION_FIELDS,
        required_fields=("rotation", "translation"),
        path=path,
    )
    return GuideViewPosition(
        rotation=_number_sequence(
            value=position_dict["rotation"],
            path=f"{path}/rotation",
        ),
        translation=_number_sequence(
            value=position_dict["translation"],
            path=f"{path}/translation",
        ),
    )


@beartype
def _view_from_json(*, value: object, path: str) -> ModelTargetView:
    """Get a guide view from a models file, or raise an error."""
    view_dict = _checked_object(
        value=value,
        known_fields=_VIEW_FIELDS,
        required_fields=("guideViewPosition", "name"),
        path=path,
    )

    states: Sequence[str] | None = None
    if "states" in view_dict:
        states_items = _json_array(
            value=view_dict["states"],
            message=f"{path}/states must be an array of strings.",
        )
        states = [
            _string_value(value=state, path=f"{path}/states({index})")
            for index, state in enumerate(iterable=states_items)
        ]

    return ModelTargetView(
        name=_string_value(value=view_dict["name"], path=f"{path}/name"),
        guide_view_position=_guide_view_position_from_json(
            value=view_dict["guideViewPosition"],
            path=f"{path}/guideViewPosition",
        ),
        states=states,
    )


@beartype
def _model_from_json(*, value: object, path: str) -> ModelTargetModel:
    """Get a model from a models file, or raise an error."""
    model_dict = _checked_object(
        value=value,
        known_fields=_MODEL_FIELDS,
        required_fields=("name",),
        path=path,
    )

    model_kwargs: dict[str, Any] = {
        field_name: _string_value(
            value=model_dict[json_field],
            path=f"{path}/{json_field}",
        )
        for json_field, field_name in _MODEL_STRING_FIELDS.items()
        if json_field in model_dict
    }

    for json_field, (field_name, enum_type) in _MODEL_ENUM_FIELDS.items():
        if json_field in model_dict:
            model_kwargs[field_name] = _enum_value(
                value=model_dict[json_field],
                enum_type=enum_type,
                path=f"{path}/{json_field}",
            )

    model_kwargs["views"] = []
    if "views" in model_dict:
        views_items = _json_array(
            value=model_dict["views"],
            message=f"{path}/views must be an array.",
        )
        model_kwargs["views"] = [
            _view_from_json(value=view_json, path=f"{path}/views({index})")
            for index, view_json in enumerate(iterable=views_items)
        ]

    return ModelTargetModel(**model_kwargs)


@beartype
def _models_from_file(
    *,
    models_file_path: Path,
) -> Sequence[ModelTargetModel]:
    """Get the models described by a models file, or raise an error."""
    try:
        file_json: object = json.loads(s=models_file_path.read_text())
    except json.JSONDecodeError as exc:
        message = f"{models_file_path} is not valid JSON."
        raise _models_file_error(message=message) from exc

    models_json: object = file_json
    file_dict = _as_json_object(value=file_json)
    if file_dict is not None:
        if "models" not in file_dict:
            message = "/models is required."
            raise _models_file_error(message=message)
        models_json = file_dict["models"]

    models_items = _json_array(
        value=models_json,
        message="/models must be an array.",
    )
    return [
        _model_from_json(value=model_json, path=f"/models({index})")
        for index, model_json in enumerate(iterable=models_items)
    ]


@click.command(name="create-model-target-dataset")
@click.option(
    "--name",
    type=str,
    required=True,
    help="The name of the Model Target dataset.",
)
@click.option(
    "--target-sdk",
    type=str,
    required=True,
    help=(
        "The Vuforia Engine version to generate the dataset for, for example "
        '"10.29".'
    ),
)
@dataset_type_option
@click.option(
    "--model-name",
    type=str,
    help=(
        "The name of the model to generate the dataset from. This is "
        "required unless --models-file is given."
    ),
)
@click.option(
    "--cad-data-url",
    type=str,
    help="A URL which Vuforia downloads the model's CAD data from.",
)
@click.option(
    "--cad-data-file",
    "cad_data_file_path",
    type=click.Path(
        exists=True,
        dir_okay=False,
        path_type=Path,
    ),
    help=(
        "The path to a file with the model's CAD data. The file is sent to "
        "Vuforia as base64 encoded data."
    ),
)
@click.option(
    "--automatic-coloring",
    type=click.Choice(choices=AutomaticColoring, case_sensitive=False),
    help="Whether Vuforia colors the model automatically.",
)
@click.option(
    "--cad-data-format",
    type=click.Choice(choices=CadDataFormat, case_sensitive=False),
    help="The format of the model's CAD data.",
)
@click.option(
    "--motion-hint",
    type=click.Choice(choices=MotionHint, case_sensitive=False),
    help="How the object which the model represents moves.",
)
@click.option(
    "--optimize-tracking-for",
    type=click.Choice(choices=OptimizeTrackingFor, case_sensitive=False),
    help="What Vuforia optimizes tracking of the model for.",
)
@click.option(
    "--realistic-appearance",
    type=click.Choice(choices=RealisticAppearance, case_sensitive=False),
    help=(
        "Whether the model looks like the object it represents. This is "
        "documented for advanced datasets only."
    ),
)
@click.option(
    "--simplify",
    type=click.Choice(choices=Simplify, case_sensitive=False),
    help="Whether Vuforia simplifies the model.",
)
@click.option(
    "--tracking-mode",
    type=click.Choice(choices=TrackingMode, case_sensitive=False),
    help="The tracking mode to generate the dataset for.",
)
@click.option(
    "--state-based-configuration-file",
    "state_based_configuration_file_path",
    type=click.Path(
        exists=True,
        dir_okay=False,
        path_type=Path,
    ),
    help=(
        "The path to a JSON file with the model's State-Based Model Target "
        "configuration."
    ),
)
@click.option(
    "--models-file",
    "models_file_path",
    type=click.Path(
        exists=True,
        dir_okay=False,
        path_type=Path,
    ),
    help=(
        "The path to a JSON file which describes the models to generate the "
        "dataset from, in the form which the Model Target Web API takes. The "
        "file holds either an array of models or an object with a "
        '"models" array. This is the only way to give multiple models, or '
        "to give guide views, and it cannot be used with the other model "
        "options."
    ),
)
@client_id_option
@client_secret_option
@base_vws_url_option
@connection_timeout_seconds_option
@read_timeout_seconds_option
@_handle_model_target_exceptions()
@beartype
def create_model_target_dataset(
    *,
    client_id: str,
    client_secret: str,
    name: str,
    target_sdk: str,
    dataset_type: ModelTargetDatasetType,
    model_name: str | None,
    cad_data_url: str | None,
    cad_data_file_path: Path | None,
    automatic_coloring: AutomaticColoring | None,
    cad_data_format: CadDataFormat | None,
    motion_hint: MotionHint | None,
    optimize_tracking_for: OptimizeTrackingFor | None,
    realistic_appearance: RealisticAppearance | None,
    simplify: Simplify | None,
    tracking_mode: TrackingMode | None,
    state_based_configuration_file_path: Path | None,
    models_file_path: Path | None,
    base_vws_url: str,
    connection_timeout_seconds: float,
    read_timeout_seconds: float,
) -> None:
    """Create a Model Target dataset.

    Vuforia generates the dataset in the background, so the dataset is not
    available to download immediately. The UUID of the new dataset is shown.

    \b
    See
    https://developer.vuforia.com/library/vuforia-engine/web-api/model-target-web-api/
    """
    model_option_values: dict[str, object] = {
        "--automatic-coloring": automatic_coloring,
        "--cad-data-file": cad_data_file_path,
        "--cad-data-format": cad_data_format,
        "--cad-data-url": cad_data_url,
        "--model-name": model_name,
        "--motion-hint": motion_hint,
        "--optimize-tracking-for": optimize_tracking_for,
        "--realistic-appearance": realistic_appearance,
        "--simplify": simplify,
        "--state-based-configuration-file": (
            state_based_configuration_file_path
        ),
        "--tracking-mode": tracking_mode,
    }

    if models_file_path is not None:
        given_model_options = sorted(
            option_name
            for option_name, value in model_option_values.items()
            if value is not None
        )
        if given_model_options:
            message = (
                "--models-file cannot be used with "
                f"{', '.join(given_model_options)}."
            )
            raise click.UsageError(message=message)
        models = _models_from_file(models_file_path=models_file_path)
    else:
        if model_name is None:
            message = "--model-name is required when --models-file is not."
            raise click.UsageError(message=message)

        if (cad_data_url is None) == (cad_data_file_path is None):
            message = (
                "Exactly one of --cad-data-url and --cad-data-file is "
                "required."
            )
            raise click.UsageError(message=message)

        cad_data_blob: str | None = None
        if cad_data_file_path is not None:
            cad_data_blob = base64.b64encode(
                s=cad_data_file_path.read_bytes(),
            ).decode(encoding="ascii")

        state_based_configuration_json_string: str | None = None
        if state_based_configuration_file_path is not None:
            state_based_configuration_json_string = (
                state_based_configuration_file_path.read_text()
            )

        models = [
            ModelTargetModel(
                name=model_name,
                cad_data_url=cad_data_url,
                cad_data_blob=cad_data_blob,
                automatic_coloring=automatic_coloring,
                cad_data_format=cad_data_format,
                motion_hint=motion_hint,
                optimize_tracking_for=optimize_tracking_for,
                realistic_appearance=realistic_appearance,
                simplify=simplify,
                tracking_mode=tracking_mode,
                state_based_configuration_json_string=(
                    state_based_configuration_json_string
                ),
                views=[],
            ),
        ]

    model_target_client = _model_target_client(
        client_id=client_id,
        client_secret=client_secret,
        base_vws_url=base_vws_url,
        connection_timeout_seconds=connection_timeout_seconds,
        read_timeout_seconds=read_timeout_seconds,
    )

    dataset_uuid = model_target_client.create_dataset(
        name=name,
        target_sdk=target_sdk,
        models=models,
        dataset_type=dataset_type,
    )

    click.echo(message=dataset_uuid)


@click.command(name="get-model-target-dataset-status")
@dataset_uuid_option
@dataset_type_option
@client_id_option
@client_secret_option
@base_vws_url_option
@connection_timeout_seconds_option
@read_timeout_seconds_option
@_handle_model_target_exceptions()
@beartype
def get_model_target_dataset_status(
    *,
    client_id: str,
    client_secret: str,
    dataset_uuid: str,
    dataset_type: ModelTargetDatasetType,
    base_vws_url: str,
    connection_timeout_seconds: float,
    read_timeout_seconds: float,
) -> None:
    """Get the status of a Model Target dataset.

    \b
    See
    https://developer.vuforia.com/library/vuforia-engine/web-api/model-target-web-api/
    """
    model_target_client = _model_target_client(
        client_id=client_id,
        client_secret=client_secret,
        base_vws_url=base_vws_url,
        connection_timeout_seconds=connection_timeout_seconds,
        read_timeout_seconds=read_timeout_seconds,
    )

    report = model_target_client.get_dataset_status(
        dataset_uuid=dataset_uuid,
        dataset_type=dataset_type,
    )

    click.echo(message=_status_report_yaml(report=report))


@click.command(name="wait-for-model-target-dataset-generated")
@click.option(
    "--seconds-between-requests",
    type=click.FloatRange(min=0.05),
    default=_SECONDS_BETWEEN_REQUESTS_DEFAULT,
    help=_SECONDS_BETWEEN_REQUESTS_HELP,
    show_default=True,
)
@click.option(
    "--timeout-seconds",
    type=click.FloatRange(min=0.05),
    default=300,
    help=_TIMEOUT_SECONDS_HELP,
    show_default=True,
)
@dataset_uuid_option
@dataset_type_option
@client_id_option
@client_secret_option
@base_vws_url_option
@connection_timeout_seconds_option
@read_timeout_seconds_option
@_handle_model_target_exceptions()
@beartype
def wait_for_model_target_dataset_generated(
    *,
    client_id: str,
    client_secret: str,
    dataset_uuid: str,
    dataset_type: ModelTargetDatasetType,
    seconds_between_requests: float,
    timeout_seconds: float,
    base_vws_url: str,
    connection_timeout_seconds: float,
    read_timeout_seconds: float,
) -> None:
    """Wait for Vuforia to finish generating a Model Target dataset.

    This is done by polling the Model Target Web API. The status of the
    dataset is shown once Vuforia has finished with it. A dataset which
    failed to generate is also finished, and gives a non-zero exit code.
    """
    model_target_client = _model_target_client(
        client_id=client_id,
        client_secret=client_secret,
        base_vws_url=base_vws_url,
        connection_timeout_seconds=connection_timeout_seconds,
        read_timeout_seconds=read_timeout_seconds,
    )

    try:
        report = model_target_client.wait_for_dataset_generated(
            dataset_uuid=dataset_uuid,
            dataset_type=dataset_type,
            seconds_between_requests=seconds_between_requests,
            timeout_seconds=timeout_seconds,
        )
    except ModelTargetDatasetTimeoutError:
        click.echo(
            message=f"Timeout of {timeout_seconds} seconds reached.",
            err=True,
        )
        sys.exit(1)

    click.echo(message=_status_report_yaml(report=report))

    if report.status == ModelTargetDatasetStatuses.FAILED:
        click.echo(
            message="Error: Vuforia failed to generate the dataset.",
            err=True,
        )
        sys.exit(1)


@click.command(name="download-model-target-dataset")
@click.option(
    "--output",
    "output_file_path",
    type=click.Path(
        dir_okay=False,
        writable=True,
        path_type=Path,
    ),
    required=True,
    help="The path to write the generated dataset zip file to.",
)
@dataset_uuid_option
@dataset_type_option
@client_id_option
@client_secret_option
@base_vws_url_option
@connection_timeout_seconds_option
@read_timeout_seconds_option
@_handle_model_target_exceptions()
@beartype
def download_model_target_dataset(
    *,
    client_id: str,
    client_secret: str,
    dataset_uuid: str,
    dataset_type: ModelTargetDatasetType,
    output_file_path: Path,
    base_vws_url: str,
    connection_timeout_seconds: float,
    read_timeout_seconds: float,
) -> None:
    """Download a generated Model Target dataset.

    \b
    See
    https://developer.vuforia.com/library/vuforia-engine/web-api/model-target-web-api/
    """
    model_target_client = _model_target_client(
        client_id=client_id,
        client_secret=client_secret,
        base_vws_url=base_vws_url,
        connection_timeout_seconds=connection_timeout_seconds,
        read_timeout_seconds=read_timeout_seconds,
    )

    dataset = model_target_client.download_dataset(
        dataset_uuid=dataset_uuid,
        dataset_type=dataset_type,
    )

    output_file_path.write_bytes(data=dataset)


@click.command(name="delete-model-target-dataset")
@dataset_uuid_option
@dataset_type_option
@client_id_option
@client_secret_option
@base_vws_url_option
@connection_timeout_seconds_option
@read_timeout_seconds_option
@_handle_model_target_exceptions()
@beartype
def delete_model_target_dataset(
    *,
    client_id: str,
    client_secret: str,
    dataset_uuid: str,
    dataset_type: ModelTargetDatasetType,
    base_vws_url: str,
    connection_timeout_seconds: float,
    read_timeout_seconds: float,
) -> None:
    """Delete a Model Target dataset.

    \b
    See
    https://developer.vuforia.com/library/vuforia-engine/web-api/model-target-web-api/
    """
    model_target_client = _model_target_client(
        client_id=client_id,
        client_secret=client_secret,
        base_vws_url=base_vws_url,
        connection_timeout_seconds=connection_timeout_seconds,
        read_timeout_seconds=read_timeout_seconds,
    )

    model_target_client.delete_dataset(
        dataset_uuid=dataset_uuid,
        dataset_type=dataset_type,
    )
