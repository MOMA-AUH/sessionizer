import os

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


def generate_symlink(shortcut_dir, file):
    symlink = os.path.join(shortcut_dir, os.path.basename(file))
    os.symlink(src=file, dst=symlink)

    # Handle index files if they exist (https://igvteam.github.io/igv-webapp/fileFormats.html)
    file_type = file.split(".")[-1]
    if file_type in FILE_INDEX_EXTENSIONS:
        file_index = file + FILE_INDEX_EXTENSIONS[file_type]
        if os.path.exists(file_index):
            file_index_symlink = os.path.join(shortcut_dir, os.path.basename(file_index))
            os.symlink(file_index, file_index_symlink)

    return symlink
