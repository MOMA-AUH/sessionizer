import re
from pathlib import Path

from sessionizer.filetypes import FILE_INDEX_EXTENSIONS
from sessionizer.track_elements import BigWigRangeOption


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


def bw_range_parser(value: str):
    if not re.match(r"^\d+(\.\d+)?,\d+(\.\d+)?(,\d+(\.\d+)?)?$", value):
        raise ValueError(f"The bw_range {value} does not fit the pattern float,float (min,max) or float,float,float (min,mid,max).")

    # If range has 2 numbers: extract and set min and max
    if value.count(",") == 1:
        minimum, maximum = map(float, value.split(","))
        baseline = None
    # If range has 3 numbers: min, mid, max
    elif value.count(",") == 2:
        minimum, baseline, maximum = map(float, value.split(","))

    return BigWigRangeOption(minimum=minimum, baseline=baseline, maximum=maximum)


def filter_files_by_filetype(files, suffix_list):
    return [file for file in files for suffix in suffix_list if file.name.endswith(suffix)]
