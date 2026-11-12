"""Pruebas del parser hacia el contrato canónico IR 1.0.0."""

from pathlib import Path

import pytest

from xmind_md.ir import validate_mind_map
from xmind_md.ir.validation import IRValidationError
from xmind_md.ir_parser import parse_file_ir, parse_markdown_ir
from xmind_md.parser import parse_markdown


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


def test_constitution_example_references_a_bundled_asset():
    root = Path(__file__).resolve().parents[1]
    source = root / "examples" / "constitucion.md"
    mind_map = parse_file_ir(source)

    assert len(mind_map.assets) == 1
    asset = next(iter(mind_map.assets.values()))
    assert (source.parent / asset.path).is_file()


def test_characterization_fixture_preserves_the_complete_ir_contract():
    """Fija el resultado observable del parser antes de retirar el puente legacy."""
    root = Path(__file__).resolve().parents[1]
    fixture = root / "tests" / "fixtures" / "ir-characterization.md"
    source = fixture.read_text(encoding="utf-8")
    source_path = "tests/fixtures/ir-characterization.md"

    result = parse_markdown_ir(source, source_path=source_path)
    repeated = parse_markdown_ir(source, source_path=source_path)
    assert result.to_dict() == repeated.to_dict()
    assert validate_mind_map(result) is result

    assert result.to_dict()["ir_version"] == "1.0.0"
    assert result.id == "mapa_caracterizacion"
    assert result.title == "Mapa de caracterización"
    assert result.metadata == {
        "author": "Equipo de pruebas",
        "description": "Fixture estable para proteger la conversión Markdown a IR.",
        "style_set": "LEGISLACION",
        "extensions": {"vendor": {"source": "fixture"}},
        "source_file": source_path,
    }
    assert result.styles["destacado"]["topic"]["text"]["bold"] is True
    assert result.style_sets["LEGISLACION"]["topic"]["text"]["color"] == "#123456"

    sheet = result.sheet
    assert sheet.id == "sheet_32dd1dd1f07a5ba5"
    assert sheet.layout.structure == "mind_map"
    assert sheet.layout.direction == "balanced"
    root_topic = sheet.root_topic
    assert root_topic.id == "topic_7c08e4afc0d151cc"
    assert root_topic.source == {
        "file": source_path,
        "line_start": 25,
        "line_end": 25,
    }
    assert root_topic.style.style_set == "LEGISLACION"
    assert root_topic.content[0].type == "paragraph"
    assert root_topic.content[0].data["runs"][1]["style"] == {"bold": True}
    assert root_topic.content[0].data["runs"][3]["link"] == {
        "kind": "topic",
        "target": "articulo_1",
    }

    article = root_topic.children[0]
    assert article.id == "articulo_1"
    assert article.source["line_start"] == 43
    assert article.source["line_end"] == 43
    assert article.style.ref == "destacado"
    assert article.annotations.labels[0].text == "IMPORTANTE"
    assert article.annotations.markers[0].group == "priority"
    assert article.annotations.task == {"status": "in_progress", "progress": 50}
    assert article.links[0]["target"] == "https://www.boe.es/"
    assert [block.type for block in article.content] == [
        "paragraph",
        "list",
        "table",
        "quote",
        "divider",
        "image",
        "code",
    ]
    assert article.content[0].data["runs"][1]["style"] == {"bold": True}
    assert article.content[1].data["items"][0]["children"][0]["content"][0]["text"] == "Excepción"
    assert article.content[2].data["rows"][0]["header"] is True
    assert article.content[2].data["rows"][1]["cells"][0]["content"][0]["text"] == "Ámbito"
    assert article.content[3].data["text"] == "Cita normativa"
    assert article.content[5].data["alt"] == "Escudo"
    assert article.content[6].data["code"] == 'print("ok")'
    assert article.annotations.notes[0].content[0].data["runs"][1]["style"] == {"bold": True}

    assert len(result.assets) == 1
    asset_id = next(iter(result.assets))
    assert asset_id == "asset_2e5abc6ad3655869"
    assert result.assets[asset_id].path == "assets/escudo.svg"
    assert article.resources.images == [asset_id]
    assert article.content[5].data["asset_id"] == asset_id
    assert sheet.relationships[0].id == "rel_articulo"
    assert sheet.relationships[0].source_topic == "articulo_1"
    assert sheet.relationships[0].target_topic == root_topic.id
    assert sheet.boundaries[0].topic_ids == ["articulo_1"]
    assert sheet.boundaries[0].title == "Ámbito normativo"
    assert sheet.summaries[0].topic_ids == ["articulo_1"]
    assert sheet.summaries[0].title == "Resumen del artículo"


def test_legacy_and_ir_parsers_preserve_the_same_topic_identity_and_structure():
    root = Path(__file__).resolve().parents[1]
    fixture = root / "tests" / "fixtures" / "ir-characterization.md"
    source = fixture.read_text(encoding="utf-8")
    source_path = "tests/fixtures/ir-characterization.md"
    legacy = parse_markdown(source, source_path=source_path)
    canonical = parse_markdown_ir(source, source_path=source_path)

    def compare_topics(old_topic, ir_topic):
        assert old_topic.id == ir_topic.id
        assert old_topic.title == ir_topic.title
        assert old_topic.kind == ir_topic.kind
        assert old_topic.source == ir_topic.source
        assert old_topic.style_set == ir_topic.style.style_set
        assert old_topic.style_ref == ir_topic.style.ref
        assert old_topic.style_overrides == ir_topic.style.overrides
        assert [block["type"] for block in old_topic.content_blocks] == [
            block.type for block in ir_topic.content
        ]
        assert [item["text"] for item in old_topic.annotations.get("labels", [])] == [
            item.text for item in ir_topic.annotations.labels
        ] if old_topic.annotations.get("labels") and isinstance(
            old_topic.annotations["labels"][0], dict
        ) else [
            item for item in old_topic.annotations.get("labels", [])
        ] == [item.text for item in ir_topic.annotations.labels]
        assert [item.get("group") for item in old_topic.annotations.get("markers", [])] == [
            item.group for item in ir_topic.annotations.markers
        ]
        assert old_topic.annotations.get("task") == ir_topic.annotations.task
        assert len(old_topic.resources) == len(ir_topic.resources.images)
        assert [link["kind"] for link in old_topic.links] == [
            link["kind"] for link in ir_topic.links
        ]
        assert [link["target"] for link in old_topic.links] == [
            link["target"] for link in ir_topic.links
        ]
        assert len(old_topic.children) == len(ir_topic.children)
        for old_child, ir_child in zip(old_topic.children, ir_topic.children):
            compare_topics(old_child, ir_child)

    assert legacy.id == canonical.id
    assert legacy.title == canonical.title
    compare_topics(legacy.topics[0], canonical.sheet.root_topic)
    assert [item["id"] for item in legacy.relationships] == [
        item.id for item in canonical.sheet.relationships
    ]
    assert [item["topics"] for item in legacy.boundaries] == [
        item.topic_ids for item in canonical.sheet.boundaries
    ]
    assert [item["topics"] for item in legacy.summaries] == [
        item.topic_ids for item in canonical.sheet.summaries
    ]
