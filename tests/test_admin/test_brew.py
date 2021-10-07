"""
Tests for Homebrew and Linuxbrew.
"""

import logging
import shutil
import subprocess
from pathlib import Path

import docker
from docker.types import Mount

from admin.homebrew import get_homebrew_formula

LOGGER = logging.getLogger(__name__)


def _create_archive(directory: Path) -> Path:
    # Homebrew requires the archive name to look like a valid version.
    version = '1'
    archive_name = '{version}.tar.gz'.format(version=version)
    repository_copy_dir = directory / 'repository_copy_dir'
    repo_root = Path(__file__).parent.parent.parent
    shutil.copytree(src=repo_root, dst=repository_copy_dir)
    archive_file = directory / archive_name
    archive_file.touch()
    # setuptools_scm only works with archives of tagged commits.
    # Therefore we make this repository copy look in a way like a GitHub
    # archive looks after a tag.
    repository_copy_git_archival = repository_copy_dir / '.git_archival.txt'
    # Expected pattern is from
    # https://pypi.org/project/setuptools-scm-git-archive/.
    git_archival_pattern = 'ref-names: $Format:%D$\n'
    assert repository_copy_git_archival.read_text() == git_archival_pattern

    # This is taken from the ``.git_archival.txt`` file from a real GitHub
    # release.
    fake_subsitution = 'ref-names: HEAD -> master, tag: 2019.12.30.1'
    repository_copy_git_archival.write_text(fake_subsitution)

    # A Git archive does not include uncommitted changes.
    # Therefore we commit changes.
    add_args = ['git', 'add', '.git_archival.txt']
    commit_args = [
        'git',
        '-c',
        'user.email="fake@gmail.com"',
        '-c',
        'user.name="fakename"',
        'commit',
        '-m',
        'Fake git archival',
    ]

    # We do not use ``dulwich.porcelain.archive`` because it has no option to
    # use a gzip format.
    archive_args = [
        'git',
        'archive',
        '--format',
        'tar.gz',
        '-o',
        str(archive_file),
        '--prefix',
        '{version}/'.format(version=version),
        'HEAD',
        str(repository_copy_dir),
    ]
    for args in (add_args, commit_args, archive_args):
        subprocess.run(args=args, check=True, cwd=repository_copy_dir)
    return archive_file


def test_create_local_brewfile(tmp_path: Path) -> None:
    """
    Show that it is at least possible to write some brew file, whether that
    actually installs or not.
    """
    archive_file = _create_archive(directory=tmp_path)
    # The path needs to look like a versioned artifact to Homebrew/Linuxbrew.
    local_archive_url = 'file://' + str(archive_file)
    head_url = 'file://' + str(Path('.').absolute())
    homebrew_filename = 'vws.rb'

    homebrew_formula_contents = get_homebrew_formula(
        archive_url=local_archive_url,
        head_url=head_url,
        homebrew_recipe_filename=homebrew_filename,
    )

    homebrew_file = tmp_path / homebrew_filename
    homebrew_file.write_text(homebrew_formula_contents)
    # For local testing:
    # import pyperclip; pyperclip.copy(str(homebrew_file))
    # import pdb; pdb.set_trace()
    #
    # Then:
    # $ brew install --debug <PASTE>


def test_brew(tmp_path: Path) -> None:
    """
    It is possible to create a Homebrew formula and to install this with
    Linuxbrew.

    This requires ``pip install docker`` and for Docker to be running.
    """
    archive_file = _create_archive(directory=tmp_path)

    client = docker.from_env()
    linuxbrew_image = 'linuxbrew/brew'
    # The path needs to look like a versioned artifact to Linuxbrew.
    container_archive_path = '/' + archive_file.stem
    container_archive_url = 'file://' + container_archive_path
    head_url = 'file://' + str(Path('.').absolute())
    homebrew_filename = 'vws.rb'

    homebrew_formula_contents = get_homebrew_formula(
        archive_url=container_archive_url,
        head_url=head_url,
        homebrew_recipe_filename=homebrew_filename,
    )

    homebrew_file = tmp_path / homebrew_filename
    homebrew_file.write_text(homebrew_formula_contents)
    container_homebrew_file_path = '/' + homebrew_filename

    archive_mount = Mount(
        source=str(archive_file.resolve().absolute()),
        target=container_archive_path,
        type='bind',
    )

    homebrew_file_mount = Mount(
        source=str(homebrew_file.resolve().absolute()),
        target=container_homebrew_file_path,
        type='bind',
    )

    mounts = [archive_mount, homebrew_file_mount]
    client.images.pull(repository=linuxbrew_image, tag='latest')
    # Locally it is useful to run ``brew install`` with ``-v`` to expose
    # issues.
    # However, this produces a log which is too long for Travis CI.
    #
    # We see
    # "The job exceeded the maximum log length, and has been terminated.".
    command_list = [
        'brew',
        'install',
        container_homebrew_file_path,
        '&&',
        'vws',
        '--version',
    ]

    command = '/bin/bash -c "{command}"'.format(
        command=' '.join(command_list),
    )

    container = client.containers.create(
        image=linuxbrew_image,
        mounts=mounts,
        command=command,
        user='linuxbrew',
        environment={'HOMEBREW_NO_AUTO_UPDATE': 1},
    )

    container.start()
    for line in container.logs(stream=True):
        line = line.decode().strip()
        LOGGER.warning(line)

    status_code = container.wait()['StatusCode']
    assert status_code == 0
    container.remove(force=True)
