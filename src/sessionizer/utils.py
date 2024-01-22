from pathlib import Path

from sessionizer.filetypes import FILE_INDEX_EXTENSIONS


def generate_symlink(shortcut_dir: Path, file: Path) -> Path:
    symlink = shortcut_dir / file.name

    # If symlink already exists, remove it
    if symlink.is_symlink():
        symlink.unlink()

    # Create symlink
    symlink.symlink_to(file)

    # Handle index files if they exist (https://igvteam.github.io/igv-webapp/fileFormats.html)
    extension = next((key for key in FILE_INDEX_EXTENSIONS if file.name.endswith(key)), None)
    if extension:
        file_index = file.parent / (file.name + FILE_INDEX_EXTENSIONS[extension])
        if file_index.exists():
            generate_symlink(shortcut_dir, file_index)

    return symlink
