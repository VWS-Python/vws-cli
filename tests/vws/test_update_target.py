"""Tests for `vws` update target commands."""

import base64
import io
import secrets
import uuid
from pathlib import Path
from textwrap import dedent

from click.testing import CliRunner
from mock_vws.database import CloudDatabase
from vws import VWS, CloudRecoService

from vws_cli import vws_group


def test_update_target(
    *,
    mock_database: CloudDatabase,
    vws_client: VWS,
    high_quality_image: io.BytesIO,
    tmp_path: Path,
    cloud_reco_client: CloudRecoService,
    different_high_quality_image: io.BytesIO,
) -> None:
    """It is possible to update a target."""
    runner = CliRunner()
    old_name = uuid.uuid4().hex
    old_width = secrets.choice(seq=range(1, 5000)) / 100
    target_id = vws_client.add_target(
        name=old_name,
        width=old_width,
        image=high_quality_image,
        active_flag=True,
        application_metadata=None,
    )
    vws_client.wait_for_target_processed(target_id=target_id)
    new_application_metadata = base64.b64encode(s=b"a").decode(
        encoding="ascii",
    )
    new_name = uuid.uuid4().hex
    new_width = secrets.choice(seq=range(1, 5000)) / 100
    new_image_file = tmp_path / uuid.uuid4().hex
    new_image_data = different_high_quality_image.getvalue()
    _ = new_image_file.write_bytes(data=new_image_data)

    commands = [
        "update-target",
        "--target-id",
        target_id,
        "--name",
        new_name,
        "--width",
        str(object=new_width),
        "--image",
        str(object=new_image_file),
        "--active-flag",
        "true",
        "--application-metadata",
        new_application_metadata,
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
    assert not bool(result.stdout)

    vws_client.wait_for_target_processed(target_id=target_id)
    [
        matching_target,
    ] = cloud_reco_client.query(image=different_high_quality_image)
    assert matching_target.target_id == target_id
    query_target_data = matching_target.target_data
    assert query_target_data is not None
    query_metadata = query_target_data.application_metadata
    assert query_metadata == new_application_metadata

    commands = [
        "update-target",
        "--target-id",
        target_id,
        "--active-flag",
        "false",
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
    assert not bool(result.stdout)
    target_details = vws_client.get_target_record(target_id=target_id)
    target_record = target_details.target_record
    assert not target_record.active_flag
    assert target_record.name == new_name
    assert target_record.width == new_width
    assert not target_record.active_flag


def test_no_fields_given(
    *,
    mock_database: CloudDatabase,
    vws_client: VWS,
    high_quality_image: io.BytesIO,
) -> None:
    """It is possible to give no update fields."""
    runner = CliRunner()
    old_name = uuid.uuid4().hex
    old_width = secrets.choice(seq=range(1, 5000)) / 100
    target_id = vws_client.add_target(
        name=old_name,
        width=old_width,
        image=high_quality_image,
        active_flag=True,
        application_metadata=None,
    )
    vws_client.wait_for_target_processed(target_id=target_id)

    commands = [
        "update-target",
        "--target-id",
        target_id,
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
    assert not bool(result.stdout)


def test_image_file_does_not_exist(
    *,
    mock_database: CloudDatabase,
    vws_client: VWS,
    high_quality_image: io.BytesIO,
    tmp_path: Path,
) -> None:
    """
    An appropriate error is given if the given image file does not
    exist.
    """
    target_id = vws_client.add_target(
        name="x",
        width=1,
        image=high_quality_image,
        active_flag=True,
        application_metadata=None,
    )
    vws_client.wait_for_target_processed(target_id=target_id)
    runner = CliRunner()
    does_not_exist_file = tmp_path / uuid.uuid4().hex
    commands = [
        "update-target",
        "--target-id",
        target_id,
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
            Usage: vws update-target [OPTIONS]
            Try 'vws update-target --help' for help.

            Error: Invalid value for '--image': File '{does_not_exist_file}' does not exist.
            """,
    ).replace("\\", "\\\\")
    assert result.stderr == expected_stderr


def test_image_file_is_dir(
    *,
    mock_database: CloudDatabase,
    vws_client: VWS,
    high_quality_image: io.BytesIO,
    tmp_path: Path,
) -> None:
    """
    An appropriate error is given if the given image file path
    points to a
    directory.
    """
    target_id = vws_client.add_target(
        name="x",
        width=1,
        image=high_quality_image,
        active_flag=True,
        application_metadata=None,
    )
    vws_client.wait_for_target_processed(target_id=target_id)
    runner = CliRunner()
    commands = [
        "update-target",
        "--target-id",
        target_id,
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
            Usage: vws update-target [OPTIONS]
            Try 'vws update-target --help' for help.

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
    target_id = vws_client.add_target(
        name="x",
        width=1,
        image=high_quality_image,
        active_flag=True,
        application_metadata=None,
    )
    vws_client.wait_for_target_processed(target_id=target_id)
    new_filename = uuid.uuid4().hex
    original_image_file = tmp_path / "foo"
    image_data = high_quality_image.getvalue()
    _ = original_image_file.write_bytes(data=image_data)
    commands = [
        "update-target",
        "--target-id",
        target_id,
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
