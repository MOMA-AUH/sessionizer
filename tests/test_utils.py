import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from sessionizer.utils import generate_symlink


class TestGenerateSymlink(unittest.TestCase):
    """Test cases for generate_symlink function"""

    def setUp(self):
        """Set up temporary directories and files for testing"""
        self.temp_dir = TemporaryDirectory()
        self.test_dir = Path(self.temp_dir.name)

        self.input_dir = self.test_dir / "input"
        self.input_dir.mkdir()
        self.shortcut_dir = self.test_dir / "shortcut"
        self.shortcut_dir.mkdir()

        # BAM file
        # Input files
        self.input_file = self.input_dir / "input.bam"
        self.input_file_index = self.input_dir / "input.bam.bai"

        # Shortcut files
        self.link = self.shortcut_dir / "input.bam"
        self.link_index = self.shortcut_dir / "input.bam.bai"

        # VCF file
        # Input files
        self.vcf_file = self.input_dir / "input.vcf.gz"
        self.vcf_file_index = self.input_dir / "input.vcf.gz.tbi"

        # Shortcut files
        self.link_vcf = self.shortcut_dir / "input.vcf.gz"
        self.link_vcf_index = self.shortcut_dir / "input.vcf.gz.tbi"

    def tearDown(self):
        """Clean up temporary directories and files after testing"""
        self.temp_dir.cleanup()

    def test_generate_symlink_simple_case(self):
        """Test generating symlink for a simple case"""
        with open(self.input_file, "w", encoding="utf-8") as f:
            f.write("test content")
        generate_symlink(shortcut_dir=self.shortcut_dir, file=self.input_file)
        self.assertTrue(self.link.is_symlink())

    def test_generate_symlink_bam_with_index_file(self):
        """Test generating symlink for a BAM with an index file"""
        # Create input file and index file
        with open(self.input_file, "w", encoding="utf-8") as f:
            f.write("test content")
        with open(self.input_file_index, "w", encoding="utf-8") as f:
            f.write("index content")

        generate_symlink(self.shortcut_dir, self.input_file)

        self.assertTrue(self.link.is_symlink())
        self.assertTrue(self.link_index.is_symlink())

    def test_generate_symlink_vcf_with_index_file(self):
        """Test generating symlink for a VCF with an index file"""
        # Create input file and index file
        with open(self.vcf_file, "w", encoding="utf-8") as f:
            f.write("test content")
        with open(self.vcf_file_index, "w", encoding="utf-8") as f:
            f.write("index content")

        generate_symlink(self.shortcut_dir, self.vcf_file)

        self.assertTrue(self.link_vcf.is_symlink())
        self.assertTrue(self.link_vcf_index.is_symlink())
