# Build package from git
BUILD_DIR="/faststorage/project/MomaReference/BACKUP/nanopore/software/conda"
conda build . --output-folder $BUILD_DIR

# Clean up
conda build purge