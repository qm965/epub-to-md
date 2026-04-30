import click
from epub_to_md.orchestrator import convert
from epub_to_md.exceptions import EpubToMdError


@click.command()
@click.argument("epub_path", type=click.Path(exists=True, readable=True))
@click.option("-o", "--output", default=None, help="Output .md file path")
def main(epub_path: str, output: str | None) -> None:
    """Convert EPUB to a single Markdown file with embedded images.

    Output includes YAML metadata (title, author), full table of contents
    extracted from NCX/Nav, base64-embedded images, tables, code blocks,
    and footnotes.

    Examples:

        epub-to-md book.epub

        epub-to-md book.epub -o output.md

    Uninstall (pip):

        pip uninstall epub-to-md

    Update (pip):

        pip install --force-reinstall epub-to-md
    """
    if output is None:
        output = epub_path.replace(".epub", ".md") if epub_path.endswith(".epub") else epub_path + ".md"

    try:
        click.echo(f"Reading: {epub_path}")
        with open(epub_path, "rb") as f:
            epub_data = f.read()

        click.echo("Converting...")
        md_content = convert(epub_data)

        with open(output, "w", encoding="utf-8") as f:
            f.write(md_content)

        click.echo(f"Written: {output}")
    except EpubToMdError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    except OSError as e:
        click.echo(f"File error: {e}", err=True)
        raise SystemExit(1)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
