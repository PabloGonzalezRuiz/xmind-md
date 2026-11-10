import pytest

from xmind_md.parser import MarkdownParseError, parse_markdown


def test_parse_nested_headings_and_metadata():
    result = parse_markdown(
        "@conjunto(TAI_LEGISLACION)\n"
        "# Constitución\n"
        "## Título I\n"
        "@estilo(concepto_importante)\n"
        "### Artículo 14\n"
        "Texto del artículo.\n"
    )
    root = result.topics[0]
    assert result.title == "Constitución"
    assert root.style_set == "TAI_LEGISLACION"
    assert root.children[0].children[0].style_ref == "concepto_importante"
    assert root.children[0].children[0].content == ["Texto del artículo."]


def test_content_before_first_heading_fails():
    with pytest.raises(MarkdownParseError):
        parse_markdown("Texto suelto\n# Título")


def test_unknown_directive_fails():
    with pytest.raises(MarkdownParseError):
        parse_markdown("# Título\n@color(rojo)\n## Tema")
