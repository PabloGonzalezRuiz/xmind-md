"""Pruebas del adaptador JSON IR 1.x."""

import json

import pytest

from xmind_md.adapters.json_adapter import write_json
from xmind_md.ir import (
    ContentBlock,
    MindMap,
    Sheet,
    Topic,
    TopicStructure,
    TreeTableCell,
    TreeTableRow,
)


def make_map() -> MindMap:
    root = Topic(
        id="root-1",
        title="Raíz",
        content=[ContentBlock("paragraph", {"text": "Contenido"})],
        children=[Topic(id="child-1", title="Hijo")],
    )
    return MindMap(
        id="map-1",
        title="Mapa",
        sheet=Sheet(id="sheet-1", title="Hoja principal", root_topic=root),
    )


def test_write_json_serializes_the_canonical_ir_shape(tmp_path):
    destination = tmp_path / "nested" / "map.json"
    write_json(make_map(), destination)
    result = json.loads(destination.read_text(encoding="utf-8"))
    assert result["ir_version"] == "1.0.0"
    assert result["sheet"]["title"] == "Hoja principal"
    assert result["sheet"]["root_topic"]["children"][0]["title"] == "Hijo"
    assert "topics" not in result
    assert result["sheet"]["root_topic"]["content"][0] == {
        "type": "paragraph",
        "text": "Contenido",
    }


def test_write_json_preserves_unicode_and_adds_final_newline(tmp_path):
    destination = tmp_path / "map.json"
    write_json(make_map(), destination)
    content = destination.read_text(encoding="utf-8")
    assert "Raíz" in content
    assert content.endswith("\n")


def test_write_json_rejects_legacy_model():
    from xmind_md.model import MindMap as LegacyMindMap

    with pytest.raises(TypeError, match="MindMap IR"):
        write_json(LegacyMindMap(title="legacy"), "unused.json")


def test_write_json_rejects_non_finite_numbers():
    mind_map = make_map()
    mind_map.metadata["invalid"] = float("nan")

    with pytest.raises(ValueError, match="Out of range float values"):
        write_json(mind_map, "unused.json")


def test_write_json_serializes_ir_1_1_semantic_structure(tmp_path):
    mind_map = make_map()
    mind_map.ir_version = "1.1.0"
    root = mind_map.sheet.root_topic
    root.semantic_role = "legal.article"
    root.children[0].semantic_role = "table.body_cell"
    root.structure = TopicStructure(
        "tree_table",
        [TreeTableRow([TreeTableCell("child-1")])],
    )
    destination = tmp_path / "map-1.1.json"

    write_json(mind_map, destination)

    result = json.loads(destination.read_text(encoding="utf-8"))
    assert result["ir_version"] == "1.1.0"
    assert result["sheet"]["root_topic"]["semantic_role"] == "legal.article"
    assert result["sheet"]["root_topic"]["structure"]["rows"][0]["cells"] == [
        {"topic_id": "child-1"}
    ]
