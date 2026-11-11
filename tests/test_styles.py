"""Pruebas de precedencia, herencia y validación de estilos."""

import pytest

from xmind_md.model import MindMap, Topic
from xmind_md.styles import StyleError, load_styles, resolve_styles


def test_style_resolution_merges_set_named_style_and_local_overrides():
    root = Topic(
        id="root",
        title="Raíz",
        level=1,
        style_set="BASE",
        style_ref="importante",
        style_overrides={"text": {"italic": True}},
    )
    mind_map = MindMap(
        title="Mapa",
        topics=[root],
        style_sets={
            "BASE": {
                "topic": {"text": {"font_size": 12, "color": "#000000"}},
                "styles": {"importante": {"topic": {"text": {"color": "#ff0000", "bold": True}}}},
            }
        },
    )

    resolve_styles(mind_map)

    assert root.resolved_style == {
        "text": {"font_size": 12, "color": "#ff0000", "bold": True, "italic": True}
    }


def test_document_definitions_override_external_definitions():
    root = Topic(id="root", title="Raíz", level=1, style_set="BASE", style_ref="normal")
    mind_map = MindMap(
        title="Mapa",
        topics=[root],
        style_sets={"BASE": {"topic": {"text": {"font_size": 14}}}},
        styles={"normal": {"topic": {"text": {"color": "red"}}}},
    )
    external = {
        "style_sets": {"BASE": {"topic": {"text": {"font_size": 10}}}},
        "styles": {"normal": {"topic": {"text": {"color": "blue"}}}},
    }

    resolve_styles(mind_map, external)

    assert root.resolved_style == {"text": {"font_size": 14, "color": "red"}}


def test_style_set_is_inherited_by_descendants():
    child = Topic(id="child", title="Hijo", level=2, style_ref="alert")
    root = Topic(id="root", title="Raíz", level=1, style_set="BASE", children=[child])
    mind_map = MindMap(
        title="Mapa",
        topics=[root],
        style_sets={"BASE": {"styles": {"alert": {"topic": {"text": {"bold": True}}}}}},
    )

    resolve_styles(mind_map)

    assert child.resolved_style == {"text": {"bold": True}}


def test_missing_style_set_or_style_is_an_error():
    root = Topic(id="root", title="Raíz", level=1, style_set="NO_EXISTE")
    with pytest.raises(StyleError, match="Conjunto"):
        resolve_styles(MindMap(title="Mapa", topics=[root]))

    root.style_set = None
    root.style_ref = "NO_EXISTE"
    with pytest.raises(StyleError, match="Estilo"):
        resolve_styles(MindMap(title="Mapa", topics=[root]))


def test_load_styles_reads_both_sections(tmp_path):
    path = tmp_path / "styles.yml"
    path.write_text(
        "style_sets:\n  BASE:\n    topic: {}\nstyles:\n  normal:\n    topic:\n      text:\n        bold: true\n",
        encoding="utf-8",
    )

    result = load_styles(path)

    assert "BASE" in result["style_sets"]
    assert result["styles"]["normal"]["topic"]["text"]["bold"] is True


def test_load_styles_rejects_duplicate_yaml_keys(tmp_path):
    path = tmp_path / "duplicate.yml"
    path.write_text(
        "style_sets:\n  BASE: {}\n  BASE: {}\n",
        encoding="utf-8",
    )
    with pytest.raises(StyleError, match="YAML de estilos inválido"):
        load_styles(path)
