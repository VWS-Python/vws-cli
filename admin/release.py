"""
Release the next version.
"""

import os
import subprocess
from pathlib import Path

from binaries import make_linux_binaries  # pylint: disable=import-error
from github import Github
from github.GitRelease import GitRelease
from homebrew import update_homebrew  # pylint: disable=import-error


def add_binaries_to_github_release(github_release: GitRelease) -> None:
    """
    Add binaries to a GitHub release.
    """
    # We need to make the artifacts just after creating a tag so that the
    # --version output is exactly the one of the tag.
    # We fetch the latest tags, including the one which was just created.
    for args in (
        ['git', 'fetch', '--tags'],
        ['git', 'merge', 'origin/master'],
        ['git', 'status'],
    ):
        subprocess.run(args=args, check=True)

    linux_artifacts = make_linux_binaries(repo_root=Path('.'))
    for installer_path in linux_artifacts:
        github_release.upload_asset(
            path=str(installer_path),
            label=installer_path.name + '-linux',
        )


def main() -> None:
    """
    Perform a release.
    """
    github_token = os.environ['GITHUB_TOKEN']
    version_str = os.environ['NEXT_VERSION']
    homebrew_tap_github_token = os.environ['HOMEBREW_TAP_GITHUB_TOKEN']
    github_repository_name = os.environ['GITHUB_REPOSITORY']
    github_client = Github(github_token)
    homebrew_tap_github_client = Github(homebrew_tap_github_token)
    github_repository = github_client.get_repo(
        full_name_or_id=github_repository_name,
    )
    update_homebrew(
        homebrew_filename='vws-cli.rb',
        version_str=version_str,
        github_repository=github_repository,
        homebrew_tap_github_repository=homebrew_tap_github_client.get_repo(
            full_name_or_id='VWS-Python/homebrew-vws',
        ),
    )
    github_release = github_repository.get_latest_release()
    add_binaries_to_github_release(github_release=github_release)


if __name__ == '__main__':
    main()
