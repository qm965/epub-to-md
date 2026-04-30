import click
from epub_to_md.orchestrator import convert


@click.command()
@click.argument("epub_path", type=click.Path(exists=True, readable=True))
@click.option("-o", "--output", default=None, help="Output .md file path")
def main(epub_path: str, output: str | None) -> None:
    """Convert EPUB to a single Markdown file."""
    if output is None:
        output = epub_path.replace(".epub", ".md") if epub_path.endswith(".epub") else epub_path + ".md"

    click.echo(f"Reading: {epub_path}")
    with open(epub_path, "rb") as f:
        epub_data = f.read()

    click.echo("Converting...")
    md_content = convert(epub_data)

    with open(output, "w", encoding="utf-8") as f:
        f.write(md_content)

    click.echo(f"Written: {output}")


if __name__ == "__main__":
    main()
