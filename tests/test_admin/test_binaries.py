"""Tests for creating binaries."""

import logging
from pathlib import Path

import docker  # type: ignore[import-untyped]
from docker.models.containers import (  # type: ignore[import-untyped]
    Container,
)
from docker.types import Mount  # type: ignore[import-untyped]

from admin.binaries import make_linux_binaries

LOGGER = logging.getLogger(__name__)


def test_linux_binaries() -> None:
    """``make_linux_binaries`` creates a binary which can be run on Linux."""
    repo_root = Path(__file__).parent.parent.parent.absolute()
    dist_dir = repo_root / "dist"
    make_linux_binaries(repo_root=repo_root)
    binary_path_names = {path.name for path in dist_dir.iterdir()}
    assert binary_path_names == {"vws-linux", "vuforia-cloud-reco-linux"}
    remote_repo_dir = Path("/repo")

    mounts = [
        Mount(
            source=str(repo_root),
            target=str(remote_repo_dir),
            type="bind",
        ),
    ]

    remote_paths: list[Path] = []
    for path in dist_dir.iterdir():
        relative_path = path.relative_to(repo_root)
        remote_path = remote_repo_dir / str(relative_path)
        remote_paths.append(remote_path)

    client = docker.from_env()  # pyright: ignore[reportUnknownMemberType]
    # We use the Python image because this is already pulled when building the
    # image.
    #
    # Because of a click limitation, we do not support running on containers
    # which have LANG and LC_ALL unset.
    image = "python:3.12"
    client.images.pull(image)  # pyright: ignore[reportUnknownMemberType]

    for remote_path in remote_paths:
        cmd_in_container = [
            "chmod",
            "+x",
            str(remote_path),
            "&&",
            str(remote_path),
            "--version",
            "&&",
            "rm",
            "-rf",
            str(remote_path),
        ]
        joined_cmd = " ".join(cmd_in_container)
        command = f'bash -c "{joined_cmd}"'
        container = client.containers.create(  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]
            image=image,
            mounts=mounts,
            command=command,
        )

        assert isinstance(container, Container)
        container.start()  # pyright: ignore[reportUnknownMemberType]
        for line in container.logs(stream=True):  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]
            assert isinstance(line, bytes)
            warning_line = line.decode().strip()
            LOGGER.warning(warning_line)

        container_wait_result = container.wait()  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]
        status_code = int(container_wait_result["StatusCode"])  # pyright: ignore[reportUnknownArgumentType]

        assert status_code == 0
        container.stop()  # pyright: ignore[reportUnknownMemberType]
        container.remove(v=True)  # pyright: ignore[reportUnknownMemberType]
