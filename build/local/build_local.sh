# Build local test
conda build . --output-folder test/

#  Clean up
conda build purge
