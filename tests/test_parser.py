"""Pruebas de la gramática Markdown enriquecida y su validación."""
from pathlib import Path

import pytest

from xmind_md.parser import MarkdownParseError, parse_file, parse_markdown


def test_legacy_heading_and_directives_remain_supported():
    result = parse_markdown(
        "@conjunto(TAI_LEGISLACION)\n# Constitución\n"
        "## Título I\n@estilo(concepto_importante)\n### Artículo 14\nTexto.\n"
    )
    root = result.topics[0]
    assert root.style_set == "TAI_LEGISLACION"
    assert root.children[0].children[0].style_ref == "concepto_importante"
    assert root.children[0].children[0].content == ["Texto."]


def test_front_matter_and_structured_content():
    source = (
        "---\ntitle: Mapa de prueba\nid: mapa_1\n---\n"
        "# Raíz\nPárrafo **importante**.\n\n- Uno\n- Dos\n"
        "\n| A | B |\n|---|---|\n| 1 | 2 |\n"
        "\n" + chr(96) * 3 + "python\nprint('ok')\n" + chr(96) * 3 + "\n"
    )
    result = parse_markdown(source)
    root = result.topics[0]
    assert result.title == "Mapa de prueba"
    assert result.id == "mapa_1"
    assert [block["type"] for block in root.content_blocks] == [
        "paragraph", "list", "table", "code"
    ]


def test_topic_directive_is_consumed_by_next_heading_only():
    result = parse_markdown(
        "# Raíz\n:::xmind\nid: hijo_1\nlabels: [IMPORTANTE]\n:::\n"
        "## Hijo\n## Hermano\n"
    )
    child, sibling = result.topics[0].children
    assert child.id == "hijo_1"
    assert child.annotations["labels"] == ["IMPORTANTE"]
    assert sibling.id != child.id


def test_fenced_code_does_not_create_headings_or_directives():
    tick = chr(96) * 3
    result = parse_markdown("# Raíz\n" + tick + "md\n## No es tema\n:::xmind\n" + tick + "\n")
    assert len(result.topics[0].children) == 0
    assert result.topics[0].content_blocks[0]["type"] == "code"


def test_relationship_references_are_validated_after_parse():
    result = parse_markdown(
        "# Raíz\n:::xmind\nid: a\n:::\n## A\n"
        ":::xmind\nid: b\n:::\n## B\n"
        ":::xmind-relationship\nid: r1\nsource: a\ntarget: b\n:::\n"
    )
    assert result.relationships[0]["source"] == "a"


@pytest.mark.parametrize("source", [
    "Texto sin raíz",
    "# Uno\n# Dos",
    "# Raíz\n:::xmind\nid: pendiente\n:::",
    "# Raíz\n:::xmind-unknown\nx: y\n:::",
    "# Raíz\n:::xmind-relationship\nid: r\nsource: no\ntarget: tampoco\n:::",
])
def test_invalid_documents_fail(source):
    with pytest.raises(MarkdownParseError):
        parse_markdown(source)


def test_note_directive_keeps_markdown_body():
    result = parse_markdown(
        "# Raíz\n:::xmind-note\nNota con **énfasis** y texto.\n:::\n"
    )
    assert result.topics[0].annotations["notes"] == ["Nota con **énfasis** y texto."]


def test_yaml_dates_are_normalized_to_json_strings():
    result = parse_markdown(
        "# Raíz\n:::xmind\ntask:\n  due_date: 2026-12-15\n:::\n## Hijo\n"
    )
    assert result.topics[0].children[0].annotations["task"]["due_date"] == "2026-12-15"


def test_repository_example_parses_as_complete_document():
    example = Path(__file__).parents[1] / "examples" / "constitucion.md"
    result = parse_file(example)
    assert result.title == "Constitución Española"
    assert len(result.topics) == 1
    assert len(result.relationships) == 1
    assert len(result.boundaries) == 1
    assert len(result.summaries) == 1
    assert result.assets[0]["src"] == "assets/escudo.png"


def test_generated_topic_ids_do_not_depend_on_line_numbers():
    first = parse_markdown("# Raíz\n## Rama\n")
    second = parse_markdown("# Raíz\n\nPárrafo añadido.\n\n## Rama\n")
    assert first.topics[0].id == second.topics[0].id
    assert first.topics[0].children[0].id == second.topics[0].children[0].id



def test_nested_lists_keep_recursive_structure():
    result = parse_markdown(
        "# Raíz\n- Uno\n  - Uno A\n    - Uno A.1\n  - Uno B\n- Dos\n"
    )
    block = result.topics[0].content_blocks[0]
    assert len(block["items"]) == 2
    assert len(block["items"][0]["children"]) == 2
    assert len(block["items"][0]["children"][0]["children"]) == 1


def test_duplicate_yaml_keys_are_rejected():
    with pytest.raises(MarkdownParseError, match="YAML inválido"):
        parse_markdown("# Raíz\n:::xmind\nlabels: [A]\nlabels: [B]\n:::\n## Hijo\n")


@pytest.mark.parametrize("bad_id", ["", "con espacios", "ámbito", "id/incorrecto"])
def test_invalid_explicit_topic_ids_are_rejected(bad_id):
    with pytest.raises(MarkdownParseError, match="ID"):
        parse_markdown(f"# Raíz\n:::xmind\nid: '{bad_id}'\n:::\n## Hijo\n")


def test_front_matter_style_fields_must_be_mappings():
    with pytest.raises(MarkdownParseError, match="styles"):
        parse_markdown("---\nstyles: texto\n---\n# Raíz\n")



def test_table_rows_must_match_header_width():
    with pytest.raises(MarkdownParseError, match="Fila de tabla"):
        parse_markdown("# Raíz\n| A | B |\n|---|---|\n| solo una |\n")


def test_table_separator_must_match_header_width():
    with pytest.raises(MarkdownParseError, match="Separador de tabla"):
        parse_markdown("# Raíz\n| A | B |\n|---|\n")


def test_tab_indented_nested_list_is_preserved():
    result = parse_markdown("# Raíz\n- Padre\n\t- Hijo\n")
    assert len(result.topics[0].content_blocks[0]["items"][0]["children"]) == 1
