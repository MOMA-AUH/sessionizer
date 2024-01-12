import os

from typer.testing import CliRunner

from sessionizer.main import app, bw_range_parser
from sessionizer.track_elements import BigWigRangeOption

runner = CliRunner()


def test_basic_bigwig():
    result = runner.invoke(
        app,
        [
            "--file",
            os.path.join("tests", "data", "numbers.wig"),
        ],
    )

    assert result.exit_code == 0


def test_ranges_parser_function():
    # Check result is instance of BigWigRangeOption
    result = bw_range_parser("0,0,0")
    assert isinstance(result, BigWigRangeOption)

    # Check min,mid,max case
    result = bw_range_parser("0,15,50")
    assert result.minimum == 0
    assert result.baseline == 15
    assert result.maximum == 50

    # Check min,max case
    result = bw_range_parser("0,50")
    assert result.minimum == 0
    assert result.baseline is None
    assert result.maximum == 50


def test_bigwig_with_ranges_min_mid_max():
    result = runner.invoke(
        app,
        [
            "--file",
            os.path.join("tests", "data", "numbers.wig"),
            "--bw-ranges",
            "0,15,50",
        ],
    )
    assert result.exit_code == 0


def test_bigwig_with_ranges_min_max():
    result = runner.invoke(
        app,
        [
            "--file",
            os.path.join("tests", "data", "numbers.wig"),
            "--bw-ranges",
            "0,50",
        ],
    )
    assert result.exit_code == 0


def test_bigwig_with_ranges_and_colors():
    result = runner.invoke(
        app,
        [
            "--file",
            os.path.join("tests", "data", "numbers.wig"),
            "--bw-color",
            "red",
            "--bw-negative-color",
            "blue",
            "--bw-ranges",
            "0,15,50",
        ],
    )
    assert result.exit_code == 0
