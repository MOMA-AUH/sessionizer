import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from typer.testing import CliRunner

from sessionizer.colors import RGBColorOption
from sessionizer.main import app


class TestAppHelp(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def test_help(self):
        result = self.runner.invoke(app, ["--help"])
        assert result.exit_code == 0


class TestAppAlignment(unittest.TestCase):
    def setUp(self):
        # Runner for app
        self.runner = CliRunner()

        # Set up temporary directories and files for testing
        self.temp_dir = TemporaryDirectory()
        self.test_dir = Path(self.temp_dir.name)

        self.input_dir = self.test_dir / "input"
        self.input_dir.mkdir()

        # BAM file
        # Input files
        self.input_bam = self.input_dir / "input.bam"

        with open(self.input_bam, "w", encoding="utf-8") as f:
            f.write("test content")

        # Custom genome
        self.custom_genome = self.test_dir / "custom_genome.fasta"

        with open(self.custom_genome, "w", encoding="utf-8") as f:
            f.write("test content")

    def test_basic_alignment(self):
        result = self.runner.invoke(
            app,
            ["--file", self.input_bam],
        )
        assert result.exit_code == 0

    def test_alignment_to_custom_genome(self):
        result = self.runner.invoke(
            app,
            [
                "--file",
                self.input_bam,
                "--genome",
                "custom",
                "--genome-path",
                self.custom_genome,
            ],
        )

        assert result.exit_code == 0

    def test_alignment_group_by(self):
        result = self.runner.invoke(
            app,
            [
                "--file",
                self.input_bam,
                "--bam-group-by",
                "phase",
            ],
        )

        assert result.exit_code == 0
        assert 'groupBy="PHASE"' in result.output

        result = self.runner.invoke(
            app,
            [
                "--file",
                self.input_bam,
                "--bam-group-by",
                "base_at_position",
            ],
        )

        assert result.exit_code == 0
        assert 'groupBy="BASE_AT_POS"' in result.output

    def test_multiple_files(self):
        result = self.runner.invoke(
            app,
            [
                "--file",
                self.input_bam,
                "--file",
                self.input_bam,
                "--bam-group-by",
                "phase",
            ],
        )
        assert result.exit_code == 0

        result = self.runner.invoke(
            app,
            [
                "--file",
                self.input_bam,
                "--file",
                self.input_bam,
                "--bam-group-by",
                "phase",
                "--bam-group-by",
                "phase",
            ],
        )
        assert result.exit_code == 0

        result = self.runner.invoke(
            app,
            [
                "--file",
                self.input_bam,
                "--file",
                self.input_bam,
                "--bam-group-by",
                "phase",
                "--bam-group-by",
                "phase",
                "--bam-group-by",
                "phase",
            ],
        )
        assert result.exit_code == 1


class TestAppVcf(unittest.TestCase):
    """Test cases for app function"""

    def setUp(self):
        """Set up temporary directories and files for testing"""
        self.temp_dir = TemporaryDirectory()
        self.test_dir = Path(self.temp_dir.name)

        self.input_dir = self.test_dir / "input"
        self.input_dir.mkdir()

        # VCF file
        self.input_vcf = self.input_dir / "input.vcf.gz"

        with open(self.input_vcf, "w", encoding="utf-8") as f:
            f.write("test content")

        self.runner = CliRunner()

    def tearDown(self):
        """Clean up temporary directories and files after testing"""
        self.temp_dir.cleanup()

    def test_app_vcf_basic(self):
        """Test running the app with a VCF file"""

        with open(self.input_vcf, "w", encoding="utf-8") as f:
            f.write("test content")

        result = self.runner.invoke(
            app,
            [
                "--file",
                self.input_vcf,
            ],
        )
        assert result.exit_code == 0

        result = self.runner.invoke(
            app,
            [
                "--file",
                self.input_vcf,
                "--vcf-show-genotypes",
            ],
        )
        assert result.exit_code == 0
        assert 'showGenotypes="true"' in result.output

        result = self.runner.invoke(
            app,
            [
                "--file",
                self.input_vcf,
                "--no-vcf-show-genotypes",
            ],
        )
        assert result.exit_code == 0
        assert 'showGenotypes="false"' in result.output


class TestAppGtf(unittest.TestCase):
    """Test cases for app function"""

    def setUp(self):
        """Set up temporary directories and files for testing"""

        self.runner = CliRunner()

        self.temp_dir = TemporaryDirectory()
        self.test_dir = Path(self.temp_dir.name)

        self.input_dir = self.test_dir / "input"
        self.input_dir.mkdir()

        # GTF file
        self.input_gtf = self.input_dir / "input.gtf.gz"

    def tearDown(self):
        """Clean up temporary directories and files after testing"""
        self.temp_dir.cleanup()

    def test_app_gtf_basic(self):
        """Test running the app with a GTF file"""

        with open(self.input_gtf, "w", encoding="utf-8") as f:
            f.write("test content")

        result = self.runner.invoke(
            app,
            [
                "--file",
                self.input_gtf,
            ],
        )
        assert result.exit_code == 0

        result = self.runner.invoke(
            app,
            [
                "--file",
                self.input_gtf,
                "--gtf-display-mode",
                "expanded",
            ],
        )
        assert result.exit_code == 0
        assert 'displayMode="EXPANDED"' in result.output


class TestAppBigWig(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

        self.temp_dir = TemporaryDirectory()
        self.test_dir = Path(self.temp_dir.name)

        self.input_dir = self.test_dir / "input"
        self.input_dir.mkdir()

        # bigwig file
        self.input_bw = self.input_dir / "input.bigwig"

        with open(self.input_bw, "w", encoding="utf-8") as f:
            f.write("test content")

    def test_basic_bigwig(self):
        result = self.runner.invoke(
            app,
            [
                "--file",
                self.input_bw,
            ],
        )

        assert result.exit_code == 0

    def test_bigwig_with_ranges_min_mid_max(self):
        result = self.runner.invoke(
            app,
            [
                "--file",
                self.input_bw,
                "--bw-ranges",
                "0,15,50",
            ],
        )
        assert result.exit_code == 0
        assert 'minimum="0.0"' in result.output
        assert 'baseline="15.0"' in result.output
        assert 'maximum="50.0"' in result.output

    def test_bigwig_with_ranges_min_max(self):
        result = self.runner.invoke(
            app,
            [
                "--file",
                self.input_bw,
                "--bw-ranges",
                "3,11",
            ],
        )
        assert result.exit_code == 0
        assert 'minimum="3.0"' in result.output
        assert 'maximum="11.0"' in result.output

    def test_bigwig_with_ranges_and_colors(self):
        result = self.runner.invoke(
            app,
            [
                "--file",
                self.input_bw,
                "--bw-color",
                "red",
                "--bw-negative-color",
                "blue",
                "--bw-ranges",
                "0.1,0.2,0.33",
            ],
        )
        assert result.exit_code == 0
        assert f'color="{RGBColorOption.RED.rgb_values()}"' in result.output
        assert f'altColor="{RGBColorOption.BLUE.rgb_values()}"' in result.output
