"""
Tests for creating binaries.
"""

import logging
from pathlib import Path

import docker
from docker.types import Mount

from admin.binaries import make_linux_binaries

LOGGER = logging.getLogger(__name__)


def test_linux_binaries() -> None:
    """
    ``make_linux_binaries`` creates a binary which can be run on Linux.
    """
    repo_root = Path(__file__).parent.parent.parent.absolute()
    binary_paths = make_linux_binaries(repo_root=repo_root)
    binary_path_names = set(path.name for path in binary_paths)
    assert binary_path_names == {'vws', 'vuforia-cloud-reco'}
    remote_repo_dir = Path('/repo')

    mounts = [
        Mount(
            source=str(repo_root),
            target=str(remote_repo_dir),
            type='bind',
        ),
    ]

    remote_paths = []
    for path in binary_paths:
        relative_path = path.relative_to(repo_root)
        remote_path = remote_repo_dir / str(relative_path)
        remote_paths.append(remote_path)

    client = docker.from_env()
    # We use the Python image because this is already pulled when building the
    # image.
    #
    # Because of a click limitation, we do not support running on containers
    # which have LANG and LC_ALL unset.
    image = 'python:3.9'
    client.images.pull(image)

    for remote_path in remote_paths:
        cmd_in_container = [
            'chmod',
            '+x',
            str(remote_path),
            '&&',
            str(remote_path),
            '--version',
            '&&',
            'rm',
            '-rf',
            str(remote_path),
        ]
        command = 'bash -c "{cmd}"'.format(cmd=' '.join(cmd_in_container))
        container = client.containers.create(
            image=image,
            mounts=mounts,
            command=command,
        )

        container.start()
        for line in container.logs(stream=True):
            line = line.decode().strip()
            LOGGER.warning(line)

        status_code = container.wait()['StatusCode']

        assert status_code == 0
        container.stop()
        container.remove(v=True)
