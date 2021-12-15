"""
Release the next version.
"""

import os
from pathlib import Path

from binaries import make_linux_binaries  # pylint: disable=import-error
from github import Github
from homebrew import get_homebrew_formula  # pylint: disable=import-error


def main() -> None:
    """
    Perform a release.
    """
    github_token = os.environ['GITHUB_TOKEN']
    github_repository_name = os.environ['GITHUB_REPOSITORY']
    github_client = Github(github_token)
    github_repository = github_client.get_repo(
        full_name_or_id=github_repository_name,
    )
    homebrew_recipe_filename = 'vws-cli.rb'
    version_str = os.environ['NEXT_VERSION']
    archive_url = github_repository.get_archive_link(
        archive_format='tarball',
        ref=version_str,
    )

    new_recipe_contents = get_homebrew_formula(
        archive_url=archive_url,
        head_url=github_repository.clone_url,
        homebrew_recipe_filename=homebrew_recipe_filename,
    )

    homebrew_recipe_file = Path(homebrew_recipe_filename)
    homebrew_recipe_file.write_text(new_recipe_contents, encoding='utf-8')
    make_linux_binaries(repo_root=Path('.'))


if __name__ == '__main__':
    main()
