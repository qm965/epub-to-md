from epub_to_md.converter import html_to_md


def test_simple_table():
    html = """<table>
<tr><th>Name</th><th>Age</th></tr>
<tr><td>Alice</td><td>30</td></tr>
</table>"""
    result = html_to_md(html)
    assert "| Name" in result
    assert "| Alice" in result


def test_footnotes():
    """Epub footnote links like <a href="#note1" epub:type="noteref">[1]</a>."""
    html = '<p>Text<sup><a href="#note1" id="noteref1">[1]</a></sup></p>'
    result = html_to_md(html)
    assert "[1]" in result


def test_mathml_simple():
    """MathML gets converted to LaTeX-style notation."""
    html = """<p><math xmlns="http://www.w3.org/1998/Math/MathML">
<msup><mi>x</mi><mn>2</mn></msup>
</math></p>"""
    result = html_to_md(html)
    assert "x^2" in result or "x²" in result or "x^{2}" in result


def test_encoding_special_chars():
    html = "<p>café &amp; résumé — «élève» → 中文</p>"
    result = html_to_md(html).strip()
    assert "café" in result
    assert "résumé" in result
    assert "中文" in result


def test_empty_body():
    assert html_to_md("<html><body></body></html>").strip() == ""


def test_only_whitespace():
    assert html_to_md("<body>   </body>").strip() == ""


def test_nested_blockquote():
    html = "<blockquote><p>Level 1</p><blockquote><p>Level 2</p></blockquote></blockquote>"
    result = html_to_md(html)
    assert "> Level 1" in result
    assert "> > Level 2" in result


def test_definition_list():
    """DL/DT/DD should render as plain text."""
    html = "<dl><dt>Term</dt><dd>Definition</dd></dl>"
    result = html_to_md(html)
    assert "Term" in result
    assert "Definition" in result
