"""
Release the next version of VWS CLI.
"""

import datetime
import os
import subprocess
from pathlib import Path
from typing import List

from dulwich.porcelain import add, commit, push, tag_list
from dulwich.repo import Repo
from github import Github, Repository, UnknownObjectException

from homebrew import get_homebrew_formula


def get_version() -> str:
    """
    Return the next version of VWS CLI.
    This is today’s date in the format ``YYYY.MM.DD.MICRO``.
    ``MICRO`` refers to the number of releases created on this date,
    starting from ``0``.
    """
    utc_now = datetime.datetime.utcnow()
    date_format = '%Y.%m.%d'
    date_str = utc_now.strftime(date_format)
    local_repository = Repo('.')
    tag_labels = tag_list(repo=local_repository)
    tag_labels = [item.decode() for item in tag_labels]
    today_tag_labels = [
        item for item in tag_labels if item.startswith(date_str)
    ]
    micro = int(len(today_tag_labels))
    return '{date}.{micro}'.format(date=date_str, micro=micro)


def update_changelog(version: str, changelog: Path) -> None:
    """
    Add a version title to the changelog.
    """
    changelog_contents = changelog.read_text()
    new_changelog_contents = changelog_contents.replace(
        'Next\n----',
        'Next\n----\n\n{version}\n------------'.format(version=version),
    )
    changelog.write_text(new_changelog_contents)


def create_github_release(
    repository: Repository,
    version: str,
) -> None:
    """
    Create a tag and release on GitHub.
    """
    changelog_url = ('https://vws-cli.readthedocs.io/en/latest/changelog.html')
    repository.create_git_tag_and_release(
        tag=version,
        tag_message='Release ' + version,
        release_name='Release ' + version,
        release_message='See ' + changelog_url,
        type='commit',
        object=repository.get_commits()[0].sha,
    )


def update_homebrew(
    homebrew_file: Path,
    version_str: str,
    repository: Repository,
) -> None:
    """
    Update the Homebrew file.
    """
    archive_url = repository.get_archive_link(
        archive_format='tarball',
        ref=version_str,
    )

    homebrew_formula_contents = get_homebrew_formula(
        archive_url=archive_url,
        head_url=repository.clone_url,
        homebrew_recipe_filename=homebrew_file.name,
    )
    homebrew_file.write_text(homebrew_formula_contents)


def commit_and_push(
    version: str,
    repository: Repository,
    paths: List[Path],
) -> None:
    """
    Commit and push all changes.
    """
    local_repository = Repo('.')
    _, ignored = add(paths=[str(path) for path in paths])
    assert not ignored
    message = b'Update for release ' + version.encode('utf-8')
    commit(message=message)
    branch_name = 'master'
    push(
        repo=local_repository,
        remote_location=repository.ssh_url,
        refspecs=branch_name.encode('utf-8'),
    )


def get_repo(github_token: str, github_owner: str) -> Repository:
    """
    Get a GitHub repository.
    """
    github_client = Github(github_token)
    try:
        github_user_or_org = github_client.get_organization(github_owner)
    except UnknownObjectException:
        github_user_or_org = github_client.get_user(github_owner)

    return github_user_or_org.get_repo('vws-cli')


def upload_to_pypi() -> None:
    """
    Build source and binary distributions.
    """
    for args in (
        ['git', 'fetch'],
        ['rm', '-rf', 'build'],
        ['python', 'setup.py', 'sdist', 'bdist_wheel'],
        ['twine', 'upload', '-r', 'pypi', 'dist/*'],
    ):
        subprocess.run(args=args, check=True)


def main() -> None:
    """
    Perform a release.
    """
    github_token = os.environ['GITHUB_TOKEN']
    github_owner = os.environ['GITHUB_OWNER']
    repository = get_repo(github_token=github_token, github_owner=github_owner)
    version_str = get_version()
    homebrew_file = Path('vws.rb')
    changelog = Path('CHANGELOG.rst')
    update_changelog(version=version_str, changelog=changelog)
    update_homebrew(
        homebrew_file=homebrew_file,
        version_str=version_str,
        repository=repository,
    )
    paths = [homebrew_file, changelog]
    commit_and_push(version=version_str, repository=repository, paths=paths)
    create_github_release(
        repository=repository,
        version=version_str,
    )
    upload_to_pypi()


if __name__ == '__main__':
    main()
