"""
Create binaries for the CLIs.
"""

import logging
import uuid
from pathlib import Path
from typing import Set

import docker
from docker.types import Mount

LOGGER = logging.getLogger(__name__)


def make_linux_binaries(repo_root: Path) -> Set[Path]:
    """
    Create binaries for Linux in a Docker container.

    Args:
        repo_root: The path to the root of the repository.

    Returns:
        A set of paths to the built binaries.
    """
    client = docker.from_env()
    dist_dir = repo_root / 'dist'
    assert not dist_dir.exists() or not set(dist_dir.iterdir())

    target_dir = '/' + uuid.uuid4().hex
    code_mount = Mount(
        source=str(repo_root.absolute()),
        target=target_dir,
        type='bind',
    )

    # We install in editable mode to overwrite any potential
    # ``_setuptools_scm_version.txt`` file.
    cmd_in_container = [
        'pip',
        'install',
        '--editable',
        '.[packaging]',
        '&&',
        'python',
        'admin/create_pyinstaller_binaries.py',
    ]
    command = 'bash -c "{cmd}"'.format(cmd=' '.join(cmd_in_container))

    container = client.containers.run(
        image='python:3.9',
        mounts=[code_mount],
        command=command,
        working_dir=target_dir,
        remove=True,
        detach=True,
    )
    for line in container.logs(stream=True):
        line = line.decode().strip()
        LOGGER.warning(line)

    status_code = container.wait()['StatusCode']
    assert status_code == 0
    return set(dist_dir.iterdir())
