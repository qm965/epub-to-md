import pytest
from click.testing import CliRunner
from epub_to_md.cli import main
import tempfile
import os


def test_cli_with_nonexistent_file():
    runner = CliRunner()
    result = runner.invoke(main, ["/nonexistent/file.epub"])
    assert result.exit_code != 0


def test_cli_with_invalid_file():
    with tempfile.NamedTemporaryFile(suffix=".epub", delete=False) as f:
        f.write(b"not a real epub")
        path = f.name
    try:
        runner = CliRunner()
        result = runner.invoke(main, [path])
        assert result.exit_code != 0
    finally:
        os.unlink(path)


def test_cli_with_non_epub_extension():
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
        f.write(b"some text")
        path = f.name
    try:
        runner = CliRunner()
        result = runner.invoke(main, [path])
        assert result.exit_code != 0
    finally:
        os.unlink(path)
