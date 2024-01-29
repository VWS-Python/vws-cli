"""Create binaries for the CLIs."""

import logging
import uuid
from pathlib import Path

import docker  # type: ignore[import-untyped]
from docker.models.containers import (  # type: ignore[import-untyped]
    Container,
)
from docker.types import Mount  # type: ignore[import-untyped]

LOGGER = logging.getLogger(__name__)


def make_linux_binaries(repo_root: Path) -> None:
    """Create binaries for Linux in a Docker container.

    Args:
        repo_root: The path to the root of the repository.
    """
    client = docker.from_env()  # pyright: ignore[reportUnknownMemberType]
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
    for line in container.logs(stream=True):  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]
        assert isinstance(line, bytes)
        warning_line = line.decode().strip()
        LOGGER.warning(warning_line)

    status_code = int(container.wait()["StatusCode"])  # pyright: ignore[reportUnknownArgumentType, reportUnknownMemberType]
    assert status_code == 0
