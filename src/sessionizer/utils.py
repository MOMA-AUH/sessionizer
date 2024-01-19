import os
from pathlib import Path

from sessionizer.filetypes import FILE_INDEX_EXTENSIONS


def generate_symlink(shortcut_dir: Path, file: Path):
    symlink = os.path.join(shortcut_dir, os.path.basename(file))

    # If symlink already exists, remove it
    if os.path.islink(symlink):
        os.unlink(symlink)

    # Create symlink
    os.symlink(src=file, dst=symlink)

    # Handle index files if they exist (https://igvteam.github.io/igv-webapp/fileFormats.html)
    if any([file.name.endswith(extension) for extension in FILE_INDEX_EXTENSIONS]):
        file_index = file.parent / (file.name + FILE_INDEX_EXTENSIONS[file.suffix])
        if os.path.exists(file_index):
            generate_symlink(shortcut_dir, file_index)

    return symlink
