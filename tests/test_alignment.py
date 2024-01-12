import os

from typer.testing import CliRunner

from sessionizer.main import app

runner = CliRunner()


def test_basic_alignment():
    result = runner.invoke(
        app,
        [
            "--file",
            os.path.join("tests", "data", "alignment.sam"),
        ],
    )
    assert result.exit_code == 0


def test_alignment_to_custom_genome():
    result = runner.invoke(
        app,
        [
            "--file",
            os.path.join("tests", "data", "alignment.sam"),
            "--genome",
            "custom",
            "--genome-path",
            os.path.join("tests", "data", "genome.fasta"),
        ],
    )

    assert result.exit_code == 0


def test_alignment_group_by():
    result = runner.invoke(
        app,
        [
            "--file",
            os.path.join("tests", "data", "alignment.sam"),
            "--bam-group-by",
            "phase",
        ],
    )

    assert result.exit_code == 0

    result = runner.invoke(
        app,
        [
            "--file",
            os.path.join("tests", "data", "alignment.sam"),
            "--bam-group-by",
            "base_at_position",
        ],
    )

    assert result.exit_code == 0


def test_multiple_files():
    result = runner.invoke(
        app,
        [
            "--file",
            os.path.join("tests", "data", "alignment.sam"),
            "--file",
            os.path.join("tests", "data", "alignment_other.sam"),
            "--bam-group-by",
            "phase",
        ],
    )
    assert result.exit_code == 0

    result = runner.invoke(
        app,
        [
            "--file",
            os.path.join("tests", "data", "alignment.sam"),
            "--file",
            os.path.join("tests", "data", "alignment_other.sam"),
            "--bam-group-by",
            "phase",
            "--bam-group-by",
            "phase",
        ],
    )
    assert result.exit_code == 0

    result = runner.invoke(
        app,
        [
            "--file",
            os.path.join("tests", "data", "alignment.sam"),
            "--file",
            os.path.join("tests", "data", "alignment_other.sam"),
            "--bam-group-by",
            "phase" "--bam-group-by",
            "phase" "--bam-group-by",
            "phase",
        ],
    )
    assert result.exit_code == 2
