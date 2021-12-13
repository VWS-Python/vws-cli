"""
Make PyInstaller binaries for the platform that this is being run on.
"""

import shutil
import subprocess
import sys
from pathlib import Path
from typing import Set


def remove_existing_files(scripts: Set[Path]) -> None:
    """
    Remove files created when building binaries.

    This is to stop interference with future builds.
    """
    dist_dir = Path('.') / 'dist'
    build_dir = Path('.') / 'build'
    try:
        shutil.rmtree(path=str(dist_dir))
    except FileNotFoundError:
        pass

    try:
        shutil.rmtree(path=str(build_dir))
    except FileNotFoundError:
        pass

    for script in scripts:
        path = Path(script.name + '.spec')
        try:
            path.unlink()
        except FileNotFoundError:
            pass


def create_binary(script: Path, repo_root: Path) -> None:
    """
    Use PyInstaller to create a binary from a script.

    Args:
        script: The script to create a binary for.
        repo_root: The path to the root of the repository.
    """
    # MANIFEST.in describes files that must be available which are not
    # necessarily Python files.
    # These include e.g. Dockerfiles.
    # We still need to include these in the binary.
    datas = []
    manifest = repo_root / 'MANIFEST.in'
    with manifest.open() as manifest_file:
        for line in manifest_file.readlines():
            # We do not yet have support for other MANIFEST types.
            is_include_line = line.startswith('include')
            is_recursive_include_line = line.startswith('recursive-include')
            assert is_include_line or is_recursive_include_line
            if line.startswith('recursive-include'):
                _, manifest_path, _ = line.split()
            else:
                _, manifest_path = line.split()
            if manifest_path.startswith('src/'):
                if Path(manifest_path).is_file():
                    parent = Path(manifest_path).parent
                    manifest_path = str(parent)

                src_path_length = len('src/')
                path_without_src = manifest_path[src_path_length:]
                data_item = (str(repo_root / manifest_path), path_without_src)
                datas.append(data_item)

    pyinstaller_command = [
        'pyinstaller',
        str(script.resolve()),
        '--onefile',
        '--name',
        script.name + '-' + sys.platform,
    ]
    for data in datas:
        source, destination = data
        add_data_command = ['--add-data', f'{source}:{destination}']
        pyinstaller_command += add_data_command

    subprocess.check_output(args=pyinstaller_command)


def create_binaries() -> None:
    """
    Make PyInstaller binaries for the platform that this is being run on.

    All binaries will be created in ``./dist``.
    """
    repo_root = Path(__file__).resolve().parent.parent
    script_dir = repo_root / 'bin'
    scripts = set(script_dir.iterdir())
    remove_existing_files(scripts=scripts)
    for script in scripts:
        create_binary(script=script, repo_root=repo_root)


if __name__ == '__main__':
    create_binaries()
