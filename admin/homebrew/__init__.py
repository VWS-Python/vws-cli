"""
Tools for creating Homebrew recipes.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from github import UnknownObjectException
from github.ContentFile import ContentFile
from github.Repository import Repository


def _get_dependencies(requirements_file: Path) -> list[str]:
    """
    Return requirements from a requirements file.

    This expects a requirements file with no ``--find-links`` lines.
    """
    lines = requirements_file.read_text().strip().split('\n')
    return [line for line in lines if not line.startswith('#')]


def _get_class_name(homebrew_recipe_filename: str) -> str:
    """
    The Ruby class name depends on the file name.

    The first character is capitalized.
    Some characters are removed, and if a character is removed, the next
    character is capitalized.

    Returns:
        The Ruby class name to use, given a file name.
    """
    stem = Path(homebrew_recipe_filename).stem
    disallowed_characters = {'-', '.', '+'}
    class_name = ''
    for index, character in enumerate(list(stem)):
        if character in disallowed_characters:  # pragma: no cover
            pass
        else:
            if index == 0 or list(stem)[index - 1] in disallowed_characters:
                class_name += character.upper()
            else:
                class_name += character

    return class_name


def get_homebrew_formula(
    archive_url: str,
    head_url: str,
    homebrew_recipe_filename: str,
) -> str:
    """
    Return the contents of a Homebrew formula for the CLIs.
    """
    parent = Path(__file__).parent
    repository_root = parent.parent.parent
    requirements = _get_dependencies(
        requirements_file=repository_root / 'requirements/requirements.txt',
    )

    first = requirements[0]

    # This command runs on a host which we do not control the OS of.
    # We want our recipe to install on Homebrew (macOS) and Linuxbrew (Linux).
    # Some packages have OS-specific dependencies.
    # Our recipe will include the dependencies for our requirements for the OS
    # that this command runs on.
    # Some of those dependencies may error if installed on the "wrong"
    # platform.
    args = ['poet', first]
    for requirement in requirements[1:]:
        args.append('--also')
        args.append(requirement)

    result = subprocess.run(args=args, stdout=subprocess.PIPE, check=True)
    resource_stanzas = str(result.stdout.decode())
    homepage_url = ''

    class_name = _get_class_name(
        homebrew_recipe_filename=homebrew_recipe_filename,
    )
    homebrew_template_file = parent / 'homebrew_template.rb'
    homebrew_template = homebrew_template_file.read_text()
    return homebrew_template.format(
        class_name=class_name,
        resource_stanzas=resource_stanzas,
        archive_url=archive_url,
        head_url=head_url,
        homepage_url=homepage_url,
    )


def update_homebrew(
    homebrew_filename: str,
    version_str: str,
    github_repository: Repository,
    homebrew_tap_github_repository: Repository,
) -> None:
    """
    Update a Homebrew file in a given Homebrew tap with an archive from a given
    repository.
    """
    archive_url = github_repository.get_archive_link(
        archive_format='tarball',
        ref=version_str,
    )

    new_recipe_contents = get_homebrew_formula(
        archive_url=archive_url,
        head_url=github_repository.clone_url,
        homebrew_recipe_filename=homebrew_filename,
    )

    message = f'Homebrew recipe for version {version_str}'

    try:
        content_file = homebrew_tap_github_repository.get_contents(
            path=homebrew_filename,
            ref='master',
        )
    except UnknownObjectException:
        homebrew_tap_github_repository.create_file(
            path=homebrew_filename,
            message=message,
            content=new_recipe_contents,
        )
    else:
        # ``get_contents`` can return a ``ContentFile`` or a list of
        # ``ContentFile``s.
        assert isinstance(content_file, ContentFile)
        homebrew_tap_github_repository.update_file(
            path=homebrew_filename,
            message=message,
            content=new_recipe_contents,
            sha=content_file.sha,
        )
