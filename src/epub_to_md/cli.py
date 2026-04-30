import click


@click.command()
@click.argument("epub_path", type=click.Path(exists=True, readable=True))
@click.option("-o", "--output", default=None, help="Output .md file path")
def main(epub_path: str, output: str | None) -> None:
    """Convert EPUB to a single Markdown file."""
    click.echo(f"Input: {epub_path}")
    click.echo(f"Output: {output or epub_path.replace('.epub', '.md')}")


if __name__ == "__main__":
    main()
