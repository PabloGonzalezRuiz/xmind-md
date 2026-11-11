"""Pruebas del parser hacia el contrato canónico IR 1.0.0."""

import pytest

from xmind_md.ir import validate_mind_map
from xmind_md.ir.validation import IRValidationError
from xmind_md.ir_parser import parse_file_ir, parse_markdown_ir


def test_parser_builds_one_sheet_and_one_root_topic():
    result = parse_markdown_ir("# Raíz\n## Rama\n### Hoja\n")
    assert result.sheet.title == "Raíz"
    assert result.sheet.root_topic.title == "Raíz"
    assert result.sheet.root_topic.children[0].children[0].title == "Hoja"
    assert result.to_dict()["ir_version"] == "1.0.0"
    assert validate_mind_map(result) is result


def test_parser_converts_structured_content_to_ir_blocks():
    source = (
        "---\ntitle: Mapa IR\nid: mapa_ir\n---\n"
        "# Raíz\nTexto **importante**.\n\n- Uno\n- Dos\n"
        "\n| A | B |\n|---|---|\n| 1 | 2 |\n"
        "\n" + chr(96) * 3 + "python\nprint('ok')\n" + chr(96) * 3 + "\n"
        "\n> Cita\n\n---\n"
    )
    result = parse_markdown_ir(source)
    blocks = result.sheet.root_topic.content
    assert [block.type for block in blocks] == [
        "paragraph",
        "list",
        "table",
        "code",
        "quote",
        "divider",
    ]
    assert blocks[0].data["text"] == "Texto importante."
    assert blocks[1].data["items"][0]["content"][0]["type"] == "paragraph"
    assert blocks[2].data["rows"][0]["header"] is True
    assert blocks[3].data["code"] == "print('ok')"


def test_parser_indexes_images_as_assets_and_topic_resources():
    result = parse_markdown_ir("# Raíz\n![Escudo](assets/escudo.png)\n")
    root = result.sheet.root_topic
    assert len(result.assets) == 1
    asset_id = next(iter(result.assets))
    assert result.assets[asset_id].path == "assets/escudo.png"
    assert root.resources.images == [asset_id]
    assert root.content[0].data["asset_id"] == asset_id


def test_parser_converts_annotations_styles_and_links():
    source = (
        "---\nstyles:\n  destacado:\n    topic:\n      text:\n        color: '#fff'\n---\n"
        "# Raíz\n"
        ":::xmind\nstyle: destacado\nstyle_overrides:\n  text:\n    color: '#fff'\n"
        "labels: [IMPORTANTE]\nmarkers:\n  - group: priority\n    value: 1\n"
        "task:\n  progress: 25\nlinks:\n  - kind: web\n    target: https://example.com\n"
        ":::\n## Hijo\n"
    )
    root = parse_markdown_ir(source).sheet.root_topic.children[0]
    assert root.style.ref == "destacado"
    assert root.style.overrides["text"]["color"] == "#fff"
    assert root.annotations.labels[0].text == "IMPORTANTE"
    assert root.annotations.markers[0].value == 1
    assert root.annotations.task["progress"] == 25
    assert root.links[0]["kind"] == "web"


def test_parser_places_relationships_boundaries_and_summaries_in_sheet():
    source = (
        "# Raíz\n:::xmind\nid: a\n:::\n## A\n"
        ":::xmind\nid: b\n:::\n## B\n"
        ":::xmind-relationship\nid: r1\nsource: a\ntarget: b\n:::\n"
        ":::xmind-boundary\nid: bd1\ntopics: [a, b]\n:::\n"
        ":::xmind-summary\nid: sm1\ntopics: [a, b]\n:::\n"
    )
    sheet = parse_markdown_ir(source).sheet
    assert sheet.relationships[0].source_topic == "a"
    assert sheet.relationships[0].target_topic == "b"
    assert sheet.boundaries[0].topic_ids == ["a", "b"]
    assert sheet.summaries[0].topic_ids == ["a", "b"]


def test_parse_file_ir_uses_source_file_metadata(tmp_path):
    source = tmp_path / "mapa.md"
    source.write_text("# Raíz\n", encoding="utf-8")
    result = parse_file_ir(source)
    assert result.metadata["source_file"] == source.as_posix()


def test_parser_preserves_topic_style_set_reference_in_ir():
    source = (
        "---\nstyle_sets:\n  BASE:\n    topic:\n      text:\n        bold: true\n---\n"
        ":::xmind\nstyle_set: BASE\n:::\n"
        "# Raíz\n"
        "## Hijo\n"
    )
    result = parse_markdown_ir(source)
    root = result.sheet.root_topic
    assert root.style.style_set == "BASE"
    assert root.children[0].style.style_set is None
    assert validate_mind_map(result) is result


def test_parser_preserves_document_level_style_set():
    source = (
        "---\ntitle: Mapa\nstyle_set: GLOBAL\n"
        "style_sets:\n  GLOBAL:\n    topic:\n      text:\n        bold: true\n---\n"
        "# Raíz\n"
    )
    result = parse_markdown_ir(source)
    assert result.metadata["style_set"] == "GLOBAL"
    assert validate_mind_map(result) is result


def test_parser_preserves_internal_topic_links_and_validates_target():
    source = (
        "# Raíz\n:::xmind\nid: destino\n:::\n## Destino\nReferencia a [destino](topic:destino).\n"
    )
    result = parse_markdown_ir(source)
    runs = result.sheet.root_topic.children[0].content[0].data["runs"]
    assert runs[1]["link"] == {"kind": "topic", "target": "destino"}


def test_parser_preserves_inline_strikethrough_and_note_formatting():
    source = "# Raíz\nTexto ~~obsoleto~~.\n:::xmind-note\nNota **importante**.\n:::\n"
    root = parse_markdown_ir(source).sheet.root_topic
    assert root.content[0].data["runs"][1]["style"] == {"strikethrough": True}
    note_runs = root.annotations.notes[0].content[0].data["runs"]
    assert note_runs[1]["style"] == {"bold": True}


def test_parser_preserves_content_block_source_ranges():
    result = parse_markdown_ir("# Raíz\nPrimera línea.\nSegunda línea.\n")
    block = result.sheet.root_topic.content[0]
    assert block.data["source"] == {"file": "<string>", "line_start": 2, "line_end": 3}


def test_internal_topic_link_to_missing_target_is_rejected():
    with pytest.raises(IRValidationError, match="tema enlazado inexistente"):
        parse_markdown_ir("# Raíz\n[no existe](topic:ausente)\n")


def test_all_primary_content_blocks_keep_inclusive_source_ranges():
    source = (
        "# Raíz\n"
        "Texto.\n\n"
        "- Uno\n\n"
        "| A |\n|---|\n| B |\n\n"
        "```python\nprint('ok')\n```\n\n"
        "> Cita\n\n"
        "---\n\n"
        "![Imagen](assets/imagen.png)\n"
    )
    result = parse_markdown_ir(source, source_path="ejemplo.md")
    blocks = result.sheet.root_topic.content
    assert [block.type for block in blocks] == [
        "paragraph",
        "list",
        "table",
        "code",
        "quote",
        "divider",
        "image",
    ]
    expected = [(2, 2), (4, 4), (6, 8), (10, 12), (14, 14), (16, 16), (18, 18)]
    assert [
        (block.data["source"]["line_start"], block.data["source"]["line_end"]) for block in blocks
    ] == expected
    assert all(block.data["source"]["file"] == "ejemplo.md" for block in blocks)

def test_ir_parser_preserves_map_and_global_entity_extensions():
    source = (
        "---\nextensions: {vendor: {map_flag: true}}\n---\n"
        "# Raíz\n"
        ":::xmind\nid: a\n:::\n## A\n"
        ":::xmind\nid: b\n:::\n## B\n"
        ":::xmind-relationship\nid: rel\nsource: a\ntarget: b\n"
        "extensions: {vendor: {relation_flag: true}}\n:::\n"
        ":::xmind-boundary\nid: boundary\ntopics: [a, b]\n"
        "extensions: {vendor: {boundary_flag: true}}\n:::\n"
        ":::xmind-summary\nid: summary\ntopics: [a, b]\n"
        "extensions: {vendor: {summary_flag: true}}\n:::\n"
    )
    result = parse_markdown_ir(source)
    assert result.metadata["extensions"] == {"vendor": {"map_flag": True}}
    assert result.sheet.relationships[0].extensions == {"vendor": {"relation_flag": True}}
    assert result.sheet.boundaries[0].extensions == {"vendor": {"boundary_flag": True}}
    assert result.sheet.summaries[0].extensions == {"vendor": {"summary_flag": True}}
