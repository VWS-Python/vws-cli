"""Create binaries for the CLIs."""

import logging
import uuid
from pathlib import Path

import docker
from docker.models.containers import (
    Container,
)
from docker.types import Mount

LOGGER = logging.getLogger(__name__)


def make_linux_binaries(repo_root: Path) -> None:
    """Create binaries for Linux in a Docker container.

    Args:
        repo_root: The path to the root of the repository.
    """
    client = docker.from_env()
    dist_dir = repo_root / "dist"
    assert not dist_dir.exists() or not set(dist_dir.iterdir())

    target_dir = "/" + uuid.uuid4().hex
    code_mount = Mount(
        source=str(repo_root.absolute()),
        target=target_dir,
        type="bind",
    )

    # We install in editable mode to overwrite any potential
    # ``_setuptools_scm_version.txt`` file.
    cmd_in_container = (
        "pip install --editable .[packaging] && "
        "python admin/create_pyinstaller_binaries.py"
    )
    command = f'bash -c "{cmd_in_container}"'

    container = client.containers.run(  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]
        image="python:3.12",
        mounts=[code_mount],
        command=command,
        working_dir=target_dir,
        remove=True,
        detach=True,
    )

    assert isinstance(container, Container)
    for line in container.logs(stream=True):  # pyright: ignore[reportUnknownVariableType]
        assert isinstance(line, bytes)
        warning_line = line.decode().strip()
        LOGGER.warning(warning_line)

    wait_result = container.wait()  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]
    status_code = int(wait_result["StatusCode"])  # pyright: ignore[reportUnknownArgumentType]
    assert status_code == 0
