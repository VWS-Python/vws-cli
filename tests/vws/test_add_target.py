"""Tests for `vws` add target commands."""

import base64
import io
import secrets
import uuid
from pathlib import Path
from textwrap import dedent

import pytest
from click.testing import CliRunner
from mock_vws.database import CloudDatabase
from vws import VWS, CloudRecoService

from vws_cli import vws_group


def test_add_target(
    *,
    mock_database: CloudDatabase,
    vws_client: VWS,
    high_quality_image: io.BytesIO,
    tmp_path: Path,
    cloud_reco_client: CloudRecoService,
) -> None:
    """It is possible to add a target."""
    runner = CliRunner()
    new_file = tmp_path / uuid.uuid4().hex
    name = uuid.uuid4().hex
    image_data = high_quality_image.getvalue()
    _ = new_file.write_bytes(data=image_data)
    width = secrets.choice(seq=range(1, 5000)) / 100
    commands = [
        "add-target",
        "--name",
        name,
        "--width",
        str(object=width),
        "--image",
        str(object=new_file),
        "--server-access-key",
        mock_database.server_access_key,
        "--server-secret-key",
        mock_database.server_secret_key,
    ]
    result = runner.invoke(
        cli=vws_group,
        args=commands,
        catch_exceptions=False,
        color=True,
    )
    assert result.exit_code == 0, result.output

    target_id = result.stdout.strip()
    target_details = vws_client.get_target_record(target_id=target_id)
    target_record = target_details.target_record
    assert target_record.name == name
    assert target_record.width == width
    assert target_record.active_flag is True
    vws_client.wait_for_target_processed(target_id=target_id)

    [query_result] = cloud_reco_client.query(image=high_quality_image)
    assert query_result.target_id == target_id
    target_data = query_result.target_data
    assert target_data is not None
    assert target_data.application_metadata is None


def test_image_file_does_not_exist(
    *,
    mock_database: CloudDatabase,
    tmp_path: Path,
) -> None:
    """
    An appropriate error is given if the given image file does not
    exist.
    """
    runner = CliRunner()
    does_not_exist_file = tmp_path / uuid.uuid4().hex
    commands = [
        "add-target",
        "--name",
        "foo",
        "--width",
        "1",
        "--image",
        str(object=does_not_exist_file),
        "--server-access-key",
        mock_database.server_access_key,
        "--server-secret-key",
        mock_database.server_secret_key,
    ]
    result = runner.invoke(
        cli=vws_group,
        args=commands,
        catch_exceptions=False,
        color=True,
    )
    expected_result_code = 2
    assert result.exit_code == expected_result_code
    assert not bool(result.stdout)
    expected_stderr = dedent(
        text=f"""\
            Usage: vws add-target [OPTIONS]
            Try 'vws add-target --help' for help.

            Error: Invalid value for '--image': File '{does_not_exist_file}' does not exist.
            """,
    ).replace("\\", "\\\\")
    assert result.stderr == expected_stderr


def test_image_file_is_dir(
    *,
    mock_database: CloudDatabase,
    tmp_path: Path,
) -> None:
    """
    An appropriate error is given if the given image file path
    points to a
    directory.
    """
    runner = CliRunner()
    commands = [
        "add-target",
        "--name",
        "foo",
        "--width",
        "1",
        "--image",
        str(object=tmp_path),
        "--server-access-key",
        mock_database.server_access_key,
        "--server-secret-key",
        mock_database.server_secret_key,
    ]
    result = runner.invoke(
        cli=vws_group,
        args=commands,
        catch_exceptions=False,
        color=True,
    )
    expected_result_code = 2
    assert result.exit_code == expected_result_code
    assert not bool(result.stdout)
    expected_stderr = dedent(
        text=f"""\
            Usage: vws add-target [OPTIONS]
            Try 'vws add-target --help' for help.

            Error: Invalid value for '--image': File '{tmp_path}' is a directory.
            """,
    ).replace("\\", "\\\\")
    assert result.stderr == expected_stderr


def test_relative_path(
    *,
    mock_database: CloudDatabase,
    vws_client: VWS,
    high_quality_image: io.BytesIO,
    tmp_path: Path,
) -> None:
    """Image file paths are resolved."""
    runner = CliRunner()
    new_filename = uuid.uuid4().hex
    original_image_file = tmp_path / "foo"
    image_data = high_quality_image.getvalue()
    _ = original_image_file.write_bytes(data=image_data)
    name = uuid.uuid4().hex
    commands = [
        "add-target",
        "--name",
        name,
        "--width",
        "1",
        "--image",
        new_filename,
        "--server-access-key",
        mock_database.server_access_key,
        "--server-secret-key",
        mock_database.server_secret_key,
    ]
    with runner.isolated_filesystem():
        new_file = Path(new_filename)
        new_file.symlink_to(target=original_image_file)
        result = runner.invoke(
            cli=vws_group,
            args=commands,
            catch_exceptions=False,
            color=True,
        )
    assert result.exit_code == 0
    target_id = result.stdout.strip()
    target_record = vws_client.get_target_record(target_id=target_id)
    assert target_record.target_record.name == name


def test_custom_metadata(
    *,
    mock_database: CloudDatabase,
    cloud_reco_client: CloudRecoService,
    vws_client: VWS,
    tmp_path: Path,
    high_quality_image: io.BytesIO,
) -> None:
    """Custom metadata can be given."""
    runner = CliRunner()
    new_file = tmp_path / uuid.uuid4().hex
    name = uuid.uuid4().hex
    image_data = high_quality_image.getvalue()
    _ = new_file.write_bytes(data=image_data)
    application_metadata = uuid.uuid4().hex
    metadata_bytes = application_metadata.encode(encoding="ascii")
    base64_encoded_metadata_bytes = base64.b64encode(s=metadata_bytes)
    base64_encoded_metadata = base64_encoded_metadata_bytes.decode(
        encoding="ascii",
    )
    commands = [
        "add-target",
        "--name",
        name,
        "--width",
        "0.1",
        "--image",
        str(object=new_file),
        "--application-metadata",
        base64_encoded_metadata,
        "--server-access-key",
        mock_database.server_access_key,
        "--server-secret-key",
        mock_database.server_secret_key,
    ]
    result = runner.invoke(
        cli=vws_group,
        args=commands,
        catch_exceptions=False,
        color=True,
    )
    assert result.exit_code == 0
    target_id = result.stdout.strip()
    vws_client.wait_for_target_processed(target_id=target_id)
    [query_result] = cloud_reco_client.query(image=high_quality_image)
    assert query_result.target_id == target_id
    target_data = query_result.target_data
    assert target_data is not None
    assert target_data.application_metadata == base64_encoded_metadata


@pytest.mark.parametrize(
    argnames=("active_flag_given", "active_flag_expected"),
    argvalues=[
        ("true", True),
        ("false", False),
    ],
)
def test_custom_active_flag(
    *,
    mock_database: CloudDatabase,
    vws_client: VWS,
    high_quality_image: io.BytesIO,
    tmp_path: Path,
    active_flag_given: str,
    active_flag_expected: bool,
) -> None:
    """The Active Flag of the new target can be chosen."""
    runner = CliRunner()
    new_file = tmp_path / uuid.uuid4().hex
    image_data = high_quality_image.getvalue()
    _ = new_file.write_bytes(data=image_data)
    commands = [
        "add-target",
        "--name",
        "foo",
        "--width",
        "0.1",
        "--image",
        str(object=new_file),
        "--active-flag",
        active_flag_given,
        "--server-access-key",
        mock_database.server_access_key,
        "--server-secret-key",
        mock_database.server_secret_key,
    ]
    result = runner.invoke(
        cli=vws_group,
        args=commands,
        catch_exceptions=False,
        color=True,
    )
    assert result.exit_code == 0

    target_id = result.stdout.strip()
    target_details = vws_client.get_target_record(target_id=target_id)
    active_flag = target_details.target_record.active_flag
    assert active_flag is active_flag_expected
