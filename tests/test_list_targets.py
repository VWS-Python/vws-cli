"""
XXX
"""

import io
from textwrap import dedent

from click.testing import CliRunner
from mock_vws.database import VuforiaDatabase
from vws import VWS

from vws_cli import vws_group


def test_list_targets(
    mock_database: VuforiaDatabase,
    vws_client: VWS,
    high_quality_image: io.BytesIO,
) -> None:
    runner = CliRunner()
    target_id_1 = vws_client.add_target(
        name='x1',
        width=1,
        image=high_quality_image,
        active_flag=True,
        application_metadata=None,
    )
    target_id_2 = vws_client.add_target(
        name='x2',
        width=1,
        image=high_quality_image,
        active_flag=True,
        application_metadata=None,
    )
    commands = [
        'list-targets',
        '--server-access-key',
        mock_database.server_access_key,
        '--server-secret-key',
        mock_database.server_secret_key,
    ]
    result = runner.invoke(vws_group, commands, catch_exceptions=False)
    assert result.exit_code == 0
    expected = dedent(
        f"""\
        {target_id_1}
        {target_id_2}
        """,
    )
    assert result.stdout == expected
