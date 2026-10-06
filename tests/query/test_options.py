"""Tests for `query` options commands."""

import io
import uuid
from pathlib import Path

import yaml
from click.testing import CliRunner
from mock_vws.database import CloudDatabase
from vws import VWS

from vws_cli.query import vuforia_cloud_reco


def test_max_num_results_default(
    *,
    vws_client: VWS,
    high_quality_image: io.BytesIO,
    tmp_path: Path,
    mock_database: CloudDatabase,
) -> None:
    """By default the maximum number of results is 1."""
    runner = CliRunner()
    target_id = vws_client.add_target(
        name=uuid.uuid4().hex,
        width=1,
        image=high_quality_image,
        active_flag=True,
        application_metadata=None,
    )
    target_id_2 = vws_client.add_target(
        name=uuid.uuid4().hex,
        width=1,
        image=high_quality_image,
        active_flag=True,
        application_metadata=None,
    )
    vws_client.wait_for_target_processed(target_id=target_id)
    vws_client.wait_for_target_processed(target_id=target_id_2)

    new_file = tmp_path / uuid.uuid4().hex
    image_data = high_quality_image.getvalue()
    _ = new_file.write_bytes(data=image_data)
    commands = [
        str(object=new_file),
        "--client-access-key",
        mock_database.client_access_key,
        "--client-secret-key",
        mock_database.client_secret_key,
    ]
    result = runner.invoke(
        cli=vuforia_cloud_reco,
        args=commands,
        catch_exceptions=False,
        color=True,
    )
    assert result.exit_code == 0
    result_data = yaml.safe_load(stream=result.stdout)
    assert len(result_data) == 1


def test_custom(
    *,
    vws_client: VWS,
    high_quality_image: io.BytesIO,
    tmp_path: Path,
    mock_database: CloudDatabase,
) -> None:
    """It is possible to set a custom ``--max-num-results``."""
    runner = CliRunner()
    target_id = vws_client.add_target(
        name=uuid.uuid4().hex,
        width=1,
        image=high_quality_image,
        active_flag=True,
        application_metadata=None,
    )
    target_id_2 = vws_client.add_target(
        name=uuid.uuid4().hex,
        width=1,
        image=high_quality_image,
        active_flag=True,
        application_metadata=None,
    )
    target_id_3 = vws_client.add_target(
        name=uuid.uuid4().hex,
        width=1,
        image=high_quality_image,
        active_flag=True,
        application_metadata=None,
    )
    vws_client.wait_for_target_processed(target_id=target_id)
    vws_client.wait_for_target_processed(target_id=target_id_2)
    vws_client.wait_for_target_processed(target_id=target_id_3)

    new_file = tmp_path / uuid.uuid4().hex
    image_data = high_quality_image.getvalue()
    _ = new_file.write_bytes(data=image_data)
    max_num_results = 2
    commands = [
        str(object=new_file),
        "--max-num-results",
        str(object=max_num_results),
        "--client-access-key",
        mock_database.client_access_key,
        "--client-secret-key",
        mock_database.client_secret_key,
    ]
    result = runner.invoke(
        cli=vuforia_cloud_reco,
        args=commands,
        catch_exceptions=False,
        color=True,
    )
    assert result.exit_code == 0
    result_data = yaml.safe_load(stream=result.stdout)
    assert len(result_data) == max_num_results


def test_out_of_range(
    *,
    high_quality_image: io.BytesIO,
    tmp_path: Path,
    mock_database: CloudDatabase,
) -> None:
    """``--max-num-results`` must be between 1 and 50."""
    runner = CliRunner()
    new_file = tmp_path / uuid.uuid4().hex
    image_data = high_quality_image.getvalue()
    _ = new_file.write_bytes(data=image_data)
    commands = [
        str(object=new_file),
        "--max-num-results",
        str(object=0),
        "--client-access-key",
        mock_database.client_access_key,
        "--client-secret-key",
        mock_database.client_secret_key,
    ]
    result = runner.invoke(
        cli=vuforia_cloud_reco,
        args=commands,
        catch_exceptions=False,
        color=True,
    )
    expected_result_code = 2
    assert result.exit_code == expected_result_code
    expected_stderr_substring = (
        "Error: Invalid value for '--max-num-results': 0 is not in the "
        "range 1<=x<=50."
    )
    assert expected_stderr_substring in result.stderr


def test_include_target_data_default(
    *,
    vws_client: VWS,
    high_quality_image: io.BytesIO,
    tmp_path: Path,
    mock_database: CloudDatabase,
) -> None:
    """By default, target data is only returned in the top match."""
    runner = CliRunner()
    target_id = vws_client.add_target(
        name=uuid.uuid4().hex,
        width=1,
        image=high_quality_image,
        active_flag=True,
        application_metadata=None,
    )
    target_id_2 = vws_client.add_target(
        name=uuid.uuid4().hex,
        width=1,
        image=high_quality_image,
        active_flag=True,
        application_metadata=None,
    )
    vws_client.wait_for_target_processed(target_id=target_id)
    vws_client.wait_for_target_processed(target_id=target_id_2)
    new_file = tmp_path / uuid.uuid4().hex
    image_data = high_quality_image.getvalue()
    _ = new_file.write_bytes(data=image_data)
    commands = [
        str(object=new_file),
        "--max-num-results",
        str(object=2),
        "--client-access-key",
        mock_database.client_access_key,
        "--client-secret-key",
        mock_database.client_secret_key,
    ]
    result = runner.invoke(
        cli=vuforia_cloud_reco,
        args=commands,
        catch_exceptions=False,
        color=True,
    )
    assert result.exit_code == 0
    matches = yaml.safe_load(stream=result.stdout)
    top_match, second_match = matches
    assert top_match["target_data"] is not None
    assert second_match["target_data"] is None


def test_top(
    *,
    vws_client: VWS,
    high_quality_image: io.BytesIO,
    tmp_path: Path,
    mock_database: CloudDatabase,
) -> None:
    """
    When 'top' is given, target data is only returned in the top
    match.
    """
    runner = CliRunner()
    target_id = vws_client.add_target(
        name=uuid.uuid4().hex,
        width=1,
        image=high_quality_image,
        active_flag=True,
        application_metadata=None,
    )
    target_id_2 = vws_client.add_target(
        name=uuid.uuid4().hex,
        width=1,
        image=high_quality_image,
        active_flag=True,
        application_metadata=None,
    )
    vws_client.wait_for_target_processed(target_id=target_id)
    vws_client.wait_for_target_processed(target_id=target_id_2)
    new_file = tmp_path / uuid.uuid4().hex
    image_data = high_quality_image.getvalue()
    _ = new_file.write_bytes(data=image_data)
    commands = [
        str(object=new_file),
        "--max-num-results",
        str(object=2),
        "--include-target-data",
        "top",
        "--client-access-key",
        mock_database.client_access_key,
        "--client-secret-key",
        mock_database.client_secret_key,
    ]
    result = runner.invoke(
        cli=vuforia_cloud_reco,
        args=commands,
        catch_exceptions=False,
        color=True,
    )
    assert result.exit_code == 0
    matches = yaml.safe_load(stream=result.stdout)
    top_match, second_match = matches
    assert top_match["target_data"] is not None
    assert second_match["target_data"] is None


def test_none(
    *,
    vws_client: VWS,
    high_quality_image: io.BytesIO,
    tmp_path: Path,
    mock_database: CloudDatabase,
) -> None:
    """
    When 'none' is given, target data is not returned in any
    match.
    """
    runner = CliRunner()
    target_id = vws_client.add_target(
        name=uuid.uuid4().hex,
        width=1,
        image=high_quality_image,
        active_flag=True,
        application_metadata=None,
    )
    target_id_2 = vws_client.add_target(
        name=uuid.uuid4().hex,
        width=1,
        image=high_quality_image,
        active_flag=True,
        application_metadata=None,
    )
    vws_client.wait_for_target_processed(target_id=target_id)
    vws_client.wait_for_target_processed(target_id=target_id_2)
    new_file = tmp_path / uuid.uuid4().hex
    image_data = high_quality_image.getvalue()
    _ = new_file.write_bytes(data=image_data)
    commands = [
        str(object=new_file),
        "--max-num-results",
        str(object=2),
        "--include-target-data",
        "none",
        "--client-access-key",
        mock_database.client_access_key,
        "--client-secret-key",
        mock_database.client_secret_key,
    ]
    result = runner.invoke(
        cli=vuforia_cloud_reco,
        args=commands,
        catch_exceptions=False,
        color=True,
    )
    assert result.exit_code == 0
    matches = yaml.safe_load(stream=result.stdout)
    top_match, second_match = matches
    assert top_match["target_data"] is None
    assert second_match["target_data"] is None


def test_all(
    *,
    vws_client: VWS,
    high_quality_image: io.BytesIO,
    tmp_path: Path,
    mock_database: CloudDatabase,
) -> None:
    """When 'all' is given, target data is returned in all matches."""
    runner = CliRunner()
    target_id = vws_client.add_target(
        name=uuid.uuid4().hex,
        width=1,
        image=high_quality_image,
        active_flag=True,
        application_metadata=None,
    )
    target_id_2 = vws_client.add_target(
        name=uuid.uuid4().hex,
        width=1,
        image=high_quality_image,
        active_flag=True,
        application_metadata=None,
    )
    vws_client.wait_for_target_processed(target_id=target_id)
    vws_client.wait_for_target_processed(target_id=target_id_2)
    new_file = tmp_path / uuid.uuid4().hex
    image_data = high_quality_image.getvalue()
    _ = new_file.write_bytes(data=image_data)

    commands = [
        str(object=new_file),
        "--max-num-results",
        str(object=2),
        "--include-target-data",
        "all",
        "--client-access-key",
        mock_database.client_access_key,
        "--client-secret-key",
        mock_database.client_secret_key,
    ]
    result = runner.invoke(
        cli=vuforia_cloud_reco,
        args=commands,
        catch_exceptions=False,
        color=True,
    )
    assert result.exit_code == 0
    matches = yaml.safe_load(stream=result.stdout)
    top_match, second_match = matches
    assert top_match["target_data"] is not None
    assert second_match["target_data"] is not None


def test_other(
    *,
    high_quality_image: io.BytesIO,
    tmp_path: Path,
    mock_database: CloudDatabase,
) -> None:
    """
    When a string other than 'top', 'all', or 'none' is given, an
    error is
    shown.
    """
    runner = CliRunner()
    new_file = tmp_path / uuid.uuid4().hex
    image_data = high_quality_image.getvalue()
    _ = new_file.write_bytes(data=image_data)
    commands = [
        str(object=new_file),
        "--max-num-results",
        str(object=2),
        "--include-target-data",
        "other",
        "--client-access-key",
        mock_database.client_access_key,
        "--client-secret-key",
        mock_database.client_secret_key,
    ]
    result = runner.invoke(
        cli=vuforia_cloud_reco,
        args=commands,
        catch_exceptions=False,
        color=True,
    )
    expected_result_code = 2
    assert result.exit_code == expected_result_code
    expected_stderr = (
        "'--include-target-data': 'other' is not one of 'top', 'none', 'all'."
    )
    assert expected_stderr in result.stderr
