import os
from pathlib import Path

FILE_INDEX_EXTENSIONS = {
    "bam": ".bai",
    "cram": ".crai",
    "vcf": ".tbi",
    "vcf.gz": ".tbi",
    "fasta": ".fai",
    "FASTA": ".fai",
    "bed": ".tbi",
    "bed.gz": ".tbi",
}


def generate_symlink(shortcut_dir: Path, file: Path):
    symlink = os.path.join(shortcut_dir, os.path.basename(file))
    try:
        os.symlink(src=file, dst=symlink)
    except FileExistsError:
        pass

    # Handle index files if they exist (https://igvteam.github.io/igv-webapp/fileFormats.html)
    file_type = file.suffix
    if file_type in FILE_INDEX_EXTENSIONS:
        file_index = file + FILE_INDEX_EXTENSIONS[file_type]
        if os.path.exists(file_index):
            try:
                file_index_symlink = os.path.join(shortcut_dir, os.path.basename(file_index))
                os.symlink(file_index, file_index_symlink)
            except FileExistsError:
                pass

    return symlink
