"""Tests for the Model Target dataset commands."""

import json
import uuid
import zipfile
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from click.testing import CliRunner
from mock_vws import (
    MockVWS,
    ModelTargetGenerationFailure,
    ModelTargetGenerationWarning,
)

from vws_cli import vws_group

# The credentials which ``vws-python-mock`` accepts for the Model Target
# Web API.
_CLIENT_ID = "client-id"
_CLIENT_SECRET = "client-secret"  # noqa: S105

_CREDENTIAL_ARGS = [
    "--client-id",
    _CLIENT_ID,
    "--client-secret",
    _CLIENT_SECRET,
]

_CAD_DATA_URL = "https://example.com/model.zip"

# The exit code which ``click`` uses for a usage error.
_USAGE_ERROR_EXIT_CODE = 2


@pytest.fixture(name="model_target_mock")
def fixture_model_target_mock() -> Iterator[MockVWS]:
    """Yield a mock which generates Model Target datasets immediately."""
    with MockVWS(processing_time_seconds=0) as mock:
        yield mock


def _create_dataset(
    *,
    runner: CliRunner,
    extra_args: list[str],
) -> str:
    """Create a dataset from one model, and return the dataset UUID."""
    args = [
        "create-model-target-dataset",
        "--name",
        "my-dataset",
        "--target-sdk",
        "10.29",
        "--model-name",
        "my-model",
        "--cad-data-url",
        _CAD_DATA_URL,
        *_CREDENTIAL_ARGS,
        *extra_args,
    ]
    result = runner.invoke(
        cli=vws_group,
        args=args,
        catch_exceptions=False,
        color=True,
    )
    assert result.exit_code == 0, result.output
    return result.stdout.strip()


@pytest.mark.parametrize(
    argnames="dataset_type", argvalues=["standard", "advanced"]
)
@pytest.mark.usefixtures("model_target_mock")
def test_dataset_lifecycle(*, dataset_type: str, tmp_path: Path) -> None:
    """A dataset can be created, polled, downloaded and deleted."""
    runner = CliRunner()
    type_args = ["--dataset-type", dataset_type]
    dataset_uuid = _create_dataset(runner=runner, extra_args=type_args)
    dataset_args = [
        "--dataset-uuid",
        dataset_uuid,
        *type_args,
        *_CREDENTIAL_ARGS,
    ]

    status_result = runner.invoke(
        cli=vws_group,
        args=["get-model-target-dataset-status", *dataset_args],
        catch_exceptions=False,
        color=True,
    )
    assert status_result.exit_code == 0
    assert f"dataset_uuid: {dataset_uuid}" in status_result.stdout
    assert "status: done" in status_result.stdout

    wait_result = runner.invoke(
        cli=vws_group,
        args=["wait-for-model-target-dataset-generated", *dataset_args],
        catch_exceptions=False,
        color=True,
    )
    assert wait_result.exit_code == 0
    assert not wait_result.stderr
    assert "status: done" in wait_result.stdout

    output_file_path = tmp_path / "dataset.zip"
    download_result = runner.invoke(
        cli=vws_group,
        args=[
            "download-model-target-dataset",
            "--output",
            str(object=output_file_path),
            *dataset_args,
        ],
        catch_exceptions=False,
        color=True,
    )
    assert download_result.exit_code == 0
    assert not download_result.stdout
    assert zipfile.is_zipfile(filename=output_file_path)

    delete_result = runner.invoke(
        cli=vws_group,
        args=["delete-model-target-dataset", *dataset_args],
        catch_exceptions=False,
        color=True,
    )
    assert delete_result.exit_code == 0
    assert not delete_result.stdout

    deleted_status_result = runner.invoke(
        cli=vws_group,
        args=["get-model-target-dataset-status", *dataset_args],
        catch_exceptions=False,
        color=True,
    )
    assert deleted_status_result.exit_code == 1
    assert deleted_status_result.stderr == (
        "Error: No Model Target dataset of the given type matches the given "
        "UUID.\n"
    )


@pytest.mark.usefixtures("model_target_mock")
def test_dataset_types_share_routes() -> None:
    """A standard dataset is visible through advanced dataset routes."""
    runner = CliRunner()
    dataset_uuid = _create_dataset(runner=runner, extra_args=[])
    result = runner.invoke(
        cli=vws_group,
        args=[
            "get-model-target-dataset-status",
            "--dataset-uuid",
            dataset_uuid,
            "--dataset-type",
            "advanced",
            *_CREDENTIAL_ARGS,
        ],
        catch_exceptions=False,
        color=True,
    )
    assert result.exit_code == 0
    assert f"dataset_uuid: {dataset_uuid}" in result.stdout


@pytest.mark.usefixtures("model_target_mock")
def test_cad_data_file(*, tmp_path: Path) -> None:
    """A model's CAD data can be given as a file."""
    runner = CliRunner()
    cad_data_file_path = tmp_path / "model.obj"
    cad_data_file_path.write_bytes(data=b"\x00cad-data")
    result = runner.invoke(
        cli=vws_group,
        args=[
            "create-model-target-dataset",
            "--name",
            "my-dataset",
            "--target-sdk",
            "10.29",
            "--model-name",
            "my-model",
            "--cad-data-file",
            str(object=cad_data_file_path),
            *_CREDENTIAL_ARGS,
        ],
        catch_exceptions=False,
        color=True,
    )
    assert result.exit_code == 0
    assert result.stdout.strip()


@pytest.mark.usefixtures("model_target_mock")
def test_model_options(*, tmp_path: Path) -> None:
    """The optional model settings are sent to Vuforia."""
    runner = CliRunner()
    state_based_configuration_file_path = tmp_path / "states.json"
    state_based_configuration_file_path.write_text(
        data=json.dumps(obj={"states": {"open": {}}}),
    )
    dataset_uuid = _create_dataset(
        runner=runner,
        extra_args=[
            "--dataset-type",
            "advanced",
            "--automatic-coloring",
            "always",
            "--cad-data-format",
            "OBJ",
            "--optimize-tracking-for",
            "default",
            "--realistic-appearance",
            "auto",
            "--simplify",
            "never",
            "--state-based-configuration-file",
            str(object=state_based_configuration_file_path),
        ],
    )
    assert dataset_uuid


def _models_file(*, tmp_path: Path, models_json: object) -> Path:
    """Write a models file, and return its path."""
    models_file_path = tmp_path / "models.json"
    models_file_path.write_text(data=json.dumps(obj=models_json))
    return models_file_path


@pytest.mark.usefixtures("model_target_mock")
def test_models_file(*, tmp_path: Path) -> None:
    """Multiple models, with guide views, can be given in a file."""
    runner = CliRunner()
    models_file_path = _models_file(
        tmp_path=tmp_path,
        models_json=[
            {
                "name": "first-model",
                "cadDataUrl": _CAD_DATA_URL,
                "automaticColoring": "auto",
                "cadDataFormat": "OBJ",
                "optimizeTrackingFor": "default",
                "realisticAppearance": "true",
                "simplify": "auto",
                "stateBasedConfigurationJsonString": (
                    '{"states": {"open": {}}}'
                ),
                "views": [
                    {
                        "name": "front",
                        "guideViewPosition": {
                            "rotation": [0, 0, 0, 1],
                            "translation": [0.0, 0.0, -1.5],
                        },
                        "states": ["open"],
                    },
                ],
            },
            {
                "name": "second-model",
                "cadDataBlob": "Y2FkLWRhdGE=",
            },
        ],
    )
    result = runner.invoke(
        cli=vws_group,
        args=[
            "create-model-target-dataset",
            "--name",
            "my-dataset",
            "--target-sdk",
            "10.29",
            "--dataset-type",
            "advanced",
            "--models-file",
            str(object=models_file_path),
            *_CREDENTIAL_ARGS,
        ],
        catch_exceptions=False,
        color=True,
    )
    assert result.exit_code == 0, result.output
    assert result.stdout.strip()


@pytest.mark.usefixtures("model_target_mock")
def test_models_file_with_models_key(*, tmp_path: Path) -> None:
    """A models file may hold an object with a ``models`` array."""
    runner = CliRunner()
    models_file_path = _models_file(
        tmp_path=tmp_path,
        models_json={
            "models": [{"name": "my-model", "cadDataUrl": _CAD_DATA_URL}],
        },
    )
    result = runner.invoke(
        cli=vws_group,
        args=[
            "create-model-target-dataset",
            "--name",
            "my-dataset",
            "--target-sdk",
            "10.29",
            "--models-file",
            str(object=models_file_path),
            *_CREDENTIAL_ARGS,
        ],
        catch_exceptions=False,
        color=True,
    )
    assert result.exit_code == 0
    assert result.stdout.strip()


@pytest.mark.usefixtures("model_target_mock")
def test_models_file_with_model_options(*, tmp_path: Path) -> None:
    """``--models-file`` cannot be used with the single-model options."""
    runner = CliRunner()
    models_file_path = _models_file(
        tmp_path=tmp_path,
        models_json=[{"name": "my-model", "cadDataUrl": _CAD_DATA_URL}],
    )
    result = runner.invoke(
        cli=vws_group,
        args=[
            "create-model-target-dataset",
            "--name",
            "my-dataset",
            "--target-sdk",
            "10.29",
            "--model-name",
            "my-model",
            "--simplify",
            "never",
            "--models-file",
            str(object=models_file_path),
            *_CREDENTIAL_ARGS,
        ],
        catch_exceptions=False,
        color=True,
    )
    assert result.exit_code == _USAGE_ERROR_EXIT_CODE
    assert (
        "Error: --models-file cannot be used with --model-name, --simplify."
        in result.stderr
    )


@pytest.mark.usefixtures("model_target_mock")
def test_model_name_required() -> None:
    """A model name is required when no models file is given."""
    runner = CliRunner()
    result = runner.invoke(
        cli=vws_group,
        args=[
            "create-model-target-dataset",
            "--name",
            "my-dataset",
            "--target-sdk",
            "10.29",
            "--cad-data-url",
            _CAD_DATA_URL,
            *_CREDENTIAL_ARGS,
        ],
        catch_exceptions=False,
        color=True,
    )
    assert result.exit_code == _USAGE_ERROR_EXIT_CODE
    assert (
        "Error: --model-name is required when --models-file is not."
        in result.stderr
    )


@pytest.mark.parametrize(
    argnames="cad_data_args",
    argvalues=[
        pytest.param([], id="neither"),
        pytest.param(
            ["--cad-data-url", _CAD_DATA_URL, "--cad-data-file", __file__],
            id="both",
        ),
    ],
)
@pytest.mark.usefixtures("model_target_mock")
def test_one_cad_data_source_required(*, cad_data_args: list[str]) -> None:
    """Exactly one CAD data source is required for a single model."""
    runner = CliRunner()
    result = runner.invoke(
        cli=vws_group,
        args=[
            "create-model-target-dataset",
            "--name",
            "my-dataset",
            "--target-sdk",
            "10.29",
            "--model-name",
            "my-model",
            *cad_data_args,
            *_CREDENTIAL_ARGS,
        ],
        catch_exceptions=False,
        color=True,
    )
    assert result.exit_code == _USAGE_ERROR_EXIT_CODE
    assert (
        "Error: Exactly one of --cad-data-url and --cad-data-file is required."
        in result.stderr
    )


_VALID_POSITION: dict[str, Any] = {
    "rotation": [0, 0, 0, 1],
    "translation": [0, 0, -1],
}

_VALID_VIEW: dict[str, Any] = {
    "name": "front",
    "guideViewPosition": _VALID_POSITION,
}

_EMPTY_OBJECT: dict[str, Any] = {}

_EMPTY_ARRAY: list[Any] = []


@pytest.mark.parametrize(
    argnames=("models_json", "expected_message"),
    argvalues=[
        pytest.param(
            {"models": "my-model"},
            "/models must be an array.",
            id="models-not-an-array",
        ),
        pytest.param(
            ["my-model"],
            "/models(0) must be an object.",
            id="model-not-an-object",
        ),
        pytest.param(
            [{"cadDataUrl": _CAD_DATA_URL}],
            "/models(0)/name is required.",
            id="model-without-name",
        ),
        pytest.param(
            [{"name": "my-model", "cadData": _CAD_DATA_URL}],
            "/models(0) has unknown fields: cadData.",
            id="unknown-model-field",
        ),
        pytest.param(
            [{"name": 1}],
            "/models(0)/name must be a string.",
            id="model-name-not-a-string",
        ),
        pytest.param(
            [{"name": "my-model", "simplify": "sometimes"}],
            "/models(0)/simplify must be one of: always, auto, never.",
            id="invalid-enum-value",
        ),
        pytest.param(
            [{"name": "my-model", "views": _EMPTY_OBJECT}],
            "/models(0)/views must be an array.",
            id="views-not-an-array",
        ),
        pytest.param(
            [{"name": "my-model", "views": ["front"]}],
            "/models(0)/views(0) must be an object.",
            id="view-not-an-object",
        ),
        pytest.param(
            [{"name": "my-model", "views": [{**_VALID_VIEW, "extra": 1}]}],
            "/models(0)/views(0) has unknown fields: extra.",
            id="unknown-view-field",
        ),
        pytest.param(
            [{"name": "my-model", "views": [{"name": "front"}]}],
            "/models(0)/views(0)/guideViewPosition is required.",
            id="view-without-position",
        ),
        pytest.param(
            [
                {
                    "name": "my-model",
                    "views": [
                        {**_VALID_VIEW, "guideViewPosition": _EMPTY_ARRAY},
                    ],
                },
            ],
            "/models(0)/views(0)/guideViewPosition must be an object.",
            id="position-not-an-object",
        ),
        pytest.param(
            [
                {
                    "name": "my-model",
                    "views": [
                        {
                            **_VALID_VIEW,
                            "guideViewPosition": {
                                "rotation": [0, 0, 0, 1],
                            },
                        },
                    ],
                },
            ],
            "/models(0)/views(0)/guideViewPosition/translation is required.",
            id="position-without-translation",
        ),
        pytest.param(
            [
                {
                    "name": "my-model",
                    "views": [
                        {
                            **_VALID_VIEW,
                            "guideViewPosition": {
                                "rotation": [0, 0, 0, 1],
                                "translation": [0, 0, -1],
                                "scale": 1,
                            },
                        },
                    ],
                },
            ],
            "/models(0)/views(0)/guideViewPosition has unknown fields: scale.",
            id="unknown-position-field",
        ),
        pytest.param(
            [
                {
                    "name": "my-model",
                    "views": [
                        {
                            **_VALID_VIEW,
                            "guideViewPosition": {
                                "rotation": "0 0 0 1",
                                "translation": [0, 0, -1],
                            },
                        },
                    ],
                },
            ],
            (
                "/models(0)/views(0)/guideViewPosition/rotation must be an "
                "array of numbers."
            ),
            id="rotation-not-an-array",
        ),
        pytest.param(
            [
                {
                    "name": "my-model",
                    "views": [
                        {
                            **_VALID_VIEW,
                            "guideViewPosition": {
                                "rotation": [0, 0, 0, True],
                                "translation": [0, 0, -1],
                            },
                        },
                    ],
                },
            ],
            (
                "/models(0)/views(0)/guideViewPosition/rotation must be an "
                "array of numbers."
            ),
            id="rotation-with-a-boolean",
        ),
        pytest.param(
            [
                {
                    "name": "my-model",
                    "views": [{**_VALID_VIEW, "states": _EMPTY_OBJECT}],
                },
            ],
            "/models(0)/views(0)/states must be an array of strings.",
            id="states-not-an-array",
        ),
        pytest.param(
            [{"name": "my-model", "views": [{**_VALID_VIEW, "states": [1]}]}],
            "/models(0)/views(0)/states(0) must be a string.",
            id="state-not-a-string",
        ),
    ],
)
@pytest.mark.usefixtures("model_target_mock")
def test_invalid_models_file(
    *,
    models_json: object,
    expected_message: str,
    tmp_path: Path,
) -> None:
    """An error is shown for a models file which cannot be used."""
    runner = CliRunner()
    models_file_path = _models_file(
        tmp_path=tmp_path,
        models_json=models_json,
    )
    result = runner.invoke(
        cli=vws_group,
        args=[
            "create-model-target-dataset",
            "--name",
            "my-dataset",
            "--target-sdk",
            "10.29",
            "--models-file",
            str(object=models_file_path),
            *_CREDENTIAL_ARGS,
        ],
        catch_exceptions=False,
        color=True,
    )
    assert result.exit_code == _USAGE_ERROR_EXIT_CODE
    expected_error = (
        f"Error: Invalid value for '--models-file': {expected_message}"
    )
    assert expected_error in result.stderr


@pytest.mark.usefixtures("model_target_mock")
def test_models_file_without_models_key(*, tmp_path: Path) -> None:
    """An object models file must have a ``models`` array."""
    runner = CliRunner()
    models_file_path = _models_file(
        tmp_path=tmp_path,
        models_json={"name": "my-dataset"},
    )
    result = runner.invoke(
        cli=vws_group,
        args=[
            "create-model-target-dataset",
            "--name",
            "my-dataset",
            "--target-sdk",
            "10.29",
            "--models-file",
            str(object=models_file_path),
            *_CREDENTIAL_ARGS,
        ],
        catch_exceptions=False,
        color=True,
    )
    assert result.exit_code == _USAGE_ERROR_EXIT_CODE
    assert (
        "Error: Invalid value for '--models-file': /models is required."
        in result.stderr
    )


@pytest.mark.usefixtures("model_target_mock")
def test_models_file_is_not_json(*, tmp_path: Path) -> None:
    """An error is shown for a models file which is not JSON."""
    runner = CliRunner()
    models_file_path = tmp_path / "models.json"
    models_file_path.write_text(data="not-json")
    result = runner.invoke(
        cli=vws_group,
        args=[
            "create-model-target-dataset",
            "--name",
            "my-dataset",
            "--target-sdk",
            "10.29",
            "--models-file",
            str(object=models_file_path),
            *_CREDENTIAL_ARGS,
        ],
        catch_exceptions=False,
        color=True,
    )
    assert result.exit_code == _USAGE_ERROR_EXIT_CODE
    expected_error = (
        f"Error: Invalid value for '--models-file': {models_file_path} is "
        "not valid JSON."
    )
    assert expected_error in result.stderr


@pytest.mark.usefixtures("model_target_mock")
def test_vuforia_validation_error(*, tmp_path: Path) -> None:
    """The reasons which Vuforia gives for rejecting a request are
    shown.
    """
    runner = CliRunner()
    models_file_path = _models_file(
        tmp_path=tmp_path,
        models_json=[
            {"name": "first-model", "cadDataUrl": _CAD_DATA_URL},
            {"name": "second-model", "cadDataUrl": _CAD_DATA_URL},
        ],
    )
    result = runner.invoke(
        cli=vws_group,
        args=[
            "create-model-target-dataset",
            "--name",
            "my-dataset",
            "--target-sdk",
            "10.29",
            "--models-file",
            str(object=models_file_path),
            *_CREDENTIAL_ARGS,
        ],
        catch_exceptions=False,
        color=True,
    )
    assert result.exit_code == 1
    assert result.stderr == (
        "Error: Vuforia rejected the request.\n"
        "VALIDATION_ERROR: exactly one model should be provided\n"
    )


@pytest.mark.usefixtures("model_target_mock")
def test_authentication_failure() -> None:
    """An error is shown when the given credentials are not accepted."""
    runner = CliRunner()
    result = runner.invoke(
        cli=vws_group,
        args=[
            "create-model-target-dataset",
            "--name",
            "my-dataset",
            "--target-sdk",
            "10.29",
            "--model-name",
            "my-model",
            "--cad-data-url",
            _CAD_DATA_URL,
            "--client-id",
            _CLIENT_ID,
            "--client-secret",
            "wrong-client-secret",
        ],
        catch_exceptions=False,
        color=True,
    )
    assert result.exit_code == 1
    assert result.stderr == (
        "Error: The given client ID and client secret are not a set of Model "
        "Target Web API credentials.\n"
    )


def test_status_while_processing() -> None:
    """The status of a dataset which is being generated is shown."""
    runner = CliRunner()
    with MockVWS(processing_time_seconds=9999):
        dataset_uuid = _create_dataset(runner=runner, extra_args=[])
        result = runner.invoke(
            cli=vws_group,
            args=[
                "get-model-target-dataset-status",
                "--dataset-uuid",
                dataset_uuid,
                *_CREDENTIAL_ARGS,
            ],
            catch_exceptions=False,
            color=True,
        )

    assert result.exit_code == 0
    assert "status: processing" in result.stdout
    assert "completed_at: null" in result.stdout


def test_download_before_generated(*, tmp_path: Path) -> None:
    """An error is shown when a dataset is not ready to download."""
    runner = CliRunner()
    output_file_path = tmp_path / "dataset.zip"
    with MockVWS(processing_time_seconds=9999):
        dataset_uuid = _create_dataset(runner=runner, extra_args=[])
        result = runner.invoke(
            cli=vws_group,
            args=[
                "download-model-target-dataset",
                "--dataset-uuid",
                dataset_uuid,
                "--output",
                str(object=output_file_path),
                *_CREDENTIAL_ARGS,
            ],
            catch_exceptions=False,
            color=True,
        )

    assert result.exit_code == 1
    assert result.stderr == (
        "Error: Vuforia has not finished generating the dataset, so the "
        "dataset cannot be downloaded.\n"
    )
    assert not output_file_path.exists()


def test_wait_timeout() -> None:
    """An error is shown when waiting for a dataset times out."""
    runner = CliRunner()
    with MockVWS(processing_time_seconds=9999):
        dataset_uuid = _create_dataset(runner=runner, extra_args=[])
        result = runner.invoke(
            cli=vws_group,
            args=[
                "wait-for-model-target-dataset-generated",
                "--dataset-uuid",
                dataset_uuid,
                "--seconds-between-requests",
                "0.05",
                "--timeout-seconds",
                "0.05",
                *_CREDENTIAL_ARGS,
            ],
            catch_exceptions=False,
            color=True,
        )

    assert result.exit_code == 1
    assert result.stderr == "Timeout of 0.05 seconds reached.\n"


def test_wait_for_failed_dataset() -> None:
    """A dataset which failed to generate gives a non-zero exit code."""
    runner = CliRunner()
    failure = ModelTargetGenerationFailure(message="Generation failed")
    with MockVWS(
        processing_time_seconds=0,
        model_target_generation_failure=failure,
    ):
        dataset_uuid = _create_dataset(runner=runner, extra_args=[])
        result = runner.invoke(
            cli=vws_group,
            args=[
                "wait-for-model-target-dataset-generated",
                "--dataset-uuid",
                dataset_uuid,
                *_CREDENTIAL_ARGS,
            ],
            catch_exceptions=False,
            color=True,
        )

    assert result.exit_code == 1
    assert "status: failed" in result.stdout
    assert "message: Generation failed" in result.stdout
    assert result.stderr == "Error: Vuforia failed to generate the dataset.\n"


def test_wait_for_dataset_with_warning() -> None:
    """A warning about a generated dataset is shown."""
    runner = CliRunner()
    warning = ModelTargetGenerationWarning()
    with MockVWS(
        processing_time_seconds=0,
        model_target_generation_warning=warning,
    ):
        dataset_uuid = _create_dataset(runner=runner, extra_args=[])
        result = runner.invoke(
            cli=vws_group,
            args=[
                "wait-for-model-target-dataset-generated",
                "--dataset-uuid",
                dataset_uuid,
                *_CREDENTIAL_ARGS,
            ],
            catch_exceptions=False,
            color=True,
        )

    assert result.exit_code == 0
    assert not result.stderr
    assert "status: done" in result.stdout
    assert f"message: {warning.message}" in result.stdout


def test_unknown_dataset_uuid() -> None:
    """An error is shown for a UUID which does not match a dataset."""
    runner = CliRunner()
    with MockVWS():
        result = runner.invoke(
            cli=vws_group,
            args=[
                "delete-model-target-dataset",
                "--dataset-uuid",
                uuid.uuid4().hex,
                *_CREDENTIAL_ARGS,
            ],
            catch_exceptions=False,
            color=True,
        )

    assert result.exit_code == 1
    assert result.stderr == (
        "Error: No Model Target dataset of the given type matches the given "
        "UUID.\n"
    )
