from epub_to_md.converter import html_to_md


def test_paragraph():
    assert html_to_md("<p>Hello world</p>").strip() == "Hello world"


def test_headings():
    html = "<h1>A</h1><h2>B</h2><h3>C</h3>"
    result = html_to_md(html).strip()
    assert "# A" in result
    assert "## B" in result
    assert "### C" in result


def test_bold_and_italic():
    html = "<p><b>bold</b> and <i>italic</i></p>"
    result = html_to_md(html).strip()
    assert "**bold**" in result
    assert "*italic*" in result


def test_unordered_list():
    html = "<ul><li>One</li><li>Two</li></ul>"
    result = html_to_md(html).strip()
    assert "- One" in result
    assert "- Two" in result


def test_ordered_list():
    html = "<ol><li>First</li><li>Second</li></ol>"
    result = html_to_md(html).strip()
    assert "1. First" in result
    assert "2. Second" in result


def test_links():
    html = '<p>Visit <a href="https://example.com">Example</a></p>'
    result = html_to_md(html).strip()
    assert "[Example](https://example.com)" in result


def test_code_block():
    html = '<pre><code class="language-python">print("hi")</code></pre>'
    result = html_to_md(html).strip()
    assert "```python" in result
    assert 'print("hi")' in result
    assert "```" in result


def test_image_tag_placeholder():
    """Image tags emit a placeholder that gets resolved later."""
    html = '<img src="images/photo.png" alt="Photo"/>'
    result = html_to_md(html)
    assert "![Photo](images/photo.png)" in result


def test_nested_list():
    html = "<ul><li>One<ul><li>Nested</li></ul></li></ul>"
    result = html_to_md(html).strip()
    assert "- One" in result
    assert "  - Nested" in result


def test_blockquote():
    html = "<blockquote><p>Quote</p></blockquote>"
    result = html_to_md(html).strip()
    assert "> Quote" in result
