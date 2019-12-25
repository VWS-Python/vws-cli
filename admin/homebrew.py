from pathlib import Path
import subprocess


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
        if character not in disallowed_characters:
            if index == 0:
                class_name += character.upper()
            elif list(stem)[index - 1] in disallowed_characters:
                class_name += character.upper()
            else:
                class_name += character

    return class_name


def get_homebrew_formula(
    archive_url: str,
    head_url: str,
    homebrew_recipe_filename: str,
    description: str,
    homepage: str,
    package_name: str,
) -> str:
    """
    Return the contents of a Homebrew formula for the CLIs.
    """
    class_name = _get_class_name(
        homebrew_recipe_filename=homebrew_recipe_filename,
    )

    args = [
        'pybrew',
        '--formula-name',
        class_name,
        '--description',
        description,
        '--homepage',
        homepage,
        '--git-repo',
        head_url,
        '--release-url',
        archive_url,
        '--verbose',
        package_name,
        homebrew_recipe_filename,
    ]

    result = subprocess.run(args=args, stdout=subprocess.PIPE, check=True)
    recipe = str(result.stdout.decode())
    return recipe
