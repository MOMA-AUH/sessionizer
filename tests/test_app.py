import os
import tempfile

from typer.testing import CliRunner

from sessionizer.main import app

runner = CliRunner()


def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0


def test_basic_run():
    result = runner.invoke(
        app,
        [
            "--file",
            os.path.join(
                "tests",
                "data",
                "alignment.sam",
            ),
        ],
    )
    assert result.exit_code == 0
