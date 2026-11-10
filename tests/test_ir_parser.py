"""Pruebas del parser hacia el contrato canónico IR 1.0.0."""
from xmind_md.ir import validate_mind_map
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
        "paragraph", "list", "table", "code", "quote", "divider"
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
        "---\\nstyle_sets:\\n  BASE:\\n    topic:\\n      text:\\n        bold: true\\n---\\n"
        ":::xmind\\nstyle_set: BASE\\n:::\\n"
        "# Raíz\\n"
        "## Hijo\\n"
    )
    result = parse_markdown_ir(source)
    root = result.sheet.root_topic
    assert root.style.style_set == "BASE"
    assert root.children[0].style.style_set is None
    assert validate_mind_map(result) is result
