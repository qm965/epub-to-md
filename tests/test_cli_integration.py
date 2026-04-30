from click.testing import CliRunner
from epub_to_md.cli import main
from tests.test_epub_parser import _build_minimal_epub
import tempfile
import os


def test_cli_converts_epub_to_md():
    """Integration test with a real temp file."""
    epub_bytes = _build_minimal_epub(
        title="CLI Test",
        creator="Tester",
        chapters=[("ch1.xhtml", "<p>CLI content</p>")],
    )
    with tempfile.NamedTemporaryFile(suffix=".epub", delete=False) as f:
        f.write(epub_bytes)
        epub_path = f.name

    out_path = epub_path.replace(".epub", ".md")
    try:
        runner = CliRunner()
        result = runner.invoke(main, [epub_path])
        assert result.exit_code == 0
        assert os.path.exists(out_path)
        with open(out_path) as f:
            content = f.read()
        assert "title: CLI Test" in content
        assert "CLI content" in content
    finally:
        os.unlink(epub_path)
        if os.path.exists(out_path):
            os.unlink(out_path)


def test_cli_custom_output():
    epub_bytes = _build_minimal_epub(
        title="Custom Out",
        creator="Tester",
        chapters=[("ch1.xhtml", "<p>Content</p>")],
    )
    with tempfile.NamedTemporaryFile(suffix=".epub", delete=False) as f:
        f.write(epub_bytes)
        epub_path = f.name

    out_path = epub_path.replace(".epub", "_custom.md")
    try:
        runner = CliRunner()
        result = runner.invoke(main, [epub_path, "-o", out_path])
        assert result.exit_code == 0
        assert os.path.exists(out_path)
        with open(out_path) as f:
            content = f.read()
        assert "title: Custom Out" in content
    finally:
        os.unlink(epub_path)
        if os.path.exists(out_path):
            os.unlink(out_path)
