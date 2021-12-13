"""
Release the next version.
"""

import os
import subprocess
from pathlib import Path

from binaries import make_linux_binaries  # pylint: disable=import-error
from github import Github
from github.ContentFile import ContentFile
from github.GitRelease import GitRelease
from github.Repository import Repository
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
        ['git', 'rebase', 'origin/master'],
        ['git', 'status'],
    ):
        subprocess.run(args=args, check=True)

    linux_artifacts = make_linux_binaries(repo_root=Path('.'))
    for installer_path in linux_artifacts:
        github_release.upload_asset(
            path=str(installer_path),
            label=installer_path.name + '-linux',
        )


def update_changelog(version: str, github_repository: Repository) -> None:
    """
    Add a version title to the changelog.
    """
    changelog_path = Path('CHANGELOG.rst')
    branch = 'master'
    changelog_content_file = github_repository.get_contents(
        path=str(changelog_path),
        ref=branch,
    )
    # ``get_contents`` can return a ``ContentFile`` or a list of
    # ``ContentFile``s.
    assert isinstance(changelog_content_file, ContentFile)
    changelog_bytes = changelog_content_file.decoded_content
    changelog_contents = changelog_bytes.decode('utf-8')
    new_changelog_contents = changelog_contents.replace(
        'Next\n----',
        f'Next\n----\n\n{version}\n------------',
    )
    github_repository.update_file(
        path=str(changelog_path),
        message=f'Update for release {version}',
        content=new_changelog_contents,
        sha=changelog_content_file.sha,
    )


def main() -> None:
    """
    Perform a release.
    """
    github_token = os.environ['GITHUB_TOKEN']
    homebrew_tap_github_token = os.environ['HOMEBREW_TAP_GITHUB_TOKEN']
    github_repository_name = os.environ['GITHUB_REPOSITORY']
    github_client = Github(github_token)
    homebrew_tap_github_client = Github(homebrew_tap_github_token)
    github_repository = github_client.get_repo(
        full_name_or_id=github_repository_name,
    )
    version_str = os.environ['NEXT_VERSION']
    update_changelog(version=version_str, github_repository=github_repository)
    update_homebrew(
        homebrew_filename='vws-cli.rb',
        version_str=version_str,
        github_repository=github_repository,
        homebrew_tap_github_repository=homebrew_tap_github_client.get_repo(
            full_name_or_id='VWS-Python/homebrew-vws',
        ),
    )
    github_release = github_repository.create_git_tag_and_release(
        tag=version_str,
        tag_message='Release ' + version_str,
        release_name='Release ' + version_str,
        release_message='See CHANGELOG.rst',
        type='commit',
        object=github_repository.get_commits()[0].sha,
    )

    add_binaries_to_github_release(github_release=github_release)


if __name__ == '__main__':
    main()
