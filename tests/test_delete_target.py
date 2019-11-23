"""
XXX
"""

import io

from click.testing import CliRunner
from mock_vws.database import VuforiaDatabase
from vws import VWS

from vws_cli import vws_group

# TODO delete without processing


def test_delete_target(
    mock_database: VuforiaDatabase,
    vws_client: VWS,
    high_quality_image: io.BytesIO,
) -> None:
    runner = CliRunner()
    target_id = vws_client.add_target(
        name='x',
        width=1,
        image=high_quality_image,
        active_flag=True,
        application_metadata=None,
    )
    assert vws_client.list_targets() == [target_id]
    commands = [
        'delete-target',
        '--target-id',
        target_id,
        '--server-access-key',
        mock_database.server_access_key,
        '--server-secret-key',
        mock_database.server_secret_key,
    ]
    vws_client.wait_for_target_processed(target_id=target_id)
    result = runner.invoke(vws_group, commands, catch_exceptions=False)
    assert result.exit_code == 0
    assert result.stdout == ''
    assert vws_client.list_targets() == []
