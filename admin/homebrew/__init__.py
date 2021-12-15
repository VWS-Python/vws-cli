"""
Tools for creating Homebrew recipes.
"""

from __future__ import annotations

import subprocess
from pathlib import Path


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
