"""Tests for `query` timeouts commands."""

import datetime
import io
import uuid
from pathlib import Path

import pytest
import requests
from click.testing import CliRunner
from freezegun import freeze_time
from mock_vws import MockVWS
from mock_vws.database import CloudDatabase

from vws_cli.query import vuforia_cloud_reco


@pytest.mark.parametrize(
    argnames=("response_delay_seconds", "expect_timeout"),
    argvalues=[(29, False), (31, True)],
)
def test_default_timeout(
    *,
    high_quality_image: io.BytesIO,
    tmp_path: Path,
    response_delay_seconds: int,
    expect_timeout: bool,
) -> None:
    """At 29 seconds there is no error; at 31 seconds there is a
    timeout.
    """
    runner = CliRunner()
    new_file = tmp_path / uuid.uuid4().hex
    image_data = high_quality_image.getvalue()
    _ = new_file.write_bytes(data=image_data)
    with (
        freeze_time() as frozen_datetime,
        MockVWS(
            response_delay_seconds=response_delay_seconds,
            sleep_fn=lambda seconds: (
                frozen_datetime.tick(
                    delta=datetime.timedelta(seconds=seconds),
                ),
                None,
            )[1],
        ) as mock,
    ):
        database = CloudDatabase()
        mock.add_cloud_database(cloud_database=database)
        commands = [
            str(object=new_file),
            "--client-access-key",
            database.client_access_key,
            "--client-secret-key",
            database.client_secret_key,
        ]

        if expect_timeout:
            with pytest.raises(
                expected_exception=requests.exceptions.Timeout,
            ):
                _ = runner.invoke(
                    cli=vuforia_cloud_reco,
                    args=commands,
                    catch_exceptions=False,
                    color=True,
                )
        else:
            result = runner.invoke(
                cli=vuforia_cloud_reco,
                args=commands,
                catch_exceptions=False,
                color=True,
            )
            assert result.exit_code == 0


def test_custom_timeout(
    *,
    high_quality_image: io.BytesIO,
    tmp_path: Path,
) -> None:
    """Custom connection and read timeouts are respected."""
    runner = CliRunner()
    new_file = tmp_path / uuid.uuid4().hex
    image_data = high_quality_image.getvalue()
    _ = new_file.write_bytes(data=image_data)
    with (
        freeze_time() as frozen_datetime,
        MockVWS(
            response_delay_seconds=5,
            sleep_fn=lambda seconds: (
                frozen_datetime.tick(
                    delta=datetime.timedelta(seconds=seconds),
                ),
                None,
            )[1],
        ) as mock,
    ):
        database = CloudDatabase()
        mock.add_cloud_database(cloud_database=database)
        commands = [
            str(object=new_file),
            "--client-access-key",
            database.client_access_key,
            "--client-secret-key",
            database.client_secret_key,
            "--read-timeout-seconds",
            "1",
        ]

        with pytest.raises(
            expected_exception=requests.exceptions.Timeout,
        ):
            _ = runner.invoke(
                cli=vuforia_cloud_reco,
                args=commands,
                catch_exceptions=False,
                color=True,
            )


def test_custom_timeout_no_error(
    *,
    high_quality_image: io.BytesIO,
    tmp_path: Path,
) -> None:
    """A sufficiently large timeout does not cause an error."""
    runner = CliRunner()
    new_file = tmp_path / uuid.uuid4().hex
    image_data = high_quality_image.getvalue()
    _ = new_file.write_bytes(data=image_data)
    with (
        freeze_time() as frozen_datetime,
        MockVWS(
            response_delay_seconds=5,
            sleep_fn=lambda seconds: (
                frozen_datetime.tick(
                    delta=datetime.timedelta(seconds=seconds),
                ),
                None,
            )[1],
        ) as mock,
    ):
        database = CloudDatabase()
        mock.add_cloud_database(cloud_database=database)
        commands = [
            str(object=new_file),
            "--client-access-key",
            database.client_access_key,
            "--client-secret-key",
            database.client_secret_key,
            "--read-timeout-seconds",
            "60",
        ]

        result = runner.invoke(
            cli=vuforia_cloud_reco,
            args=commands,
            catch_exceptions=False,
            color=True,
        )
        assert result.exit_code == 0
