"""Pruebas de integración con un paquete XMind de referencia externo.

El fixture se descarga en CI desde una revisión fijada de sc0tfree/xmind-mcp.
Su origen no acredita por sí solo que se haya guardado con XMind Desktop:
se usa para contrastar la estructura de un archivo real, no como certificación
de compatibilidad visual.
"""

from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pytest

from xmind_md.adapters.xmind_adapter import build_xmind_content, write_xmind
from xmind_md.ir import MindMap, Relationship, Sheet, Topic

REFERENCE_FILE = Path(__file__).parent / "fixtures" / "reference.xmind"


def _read_content(path: Path) -> list[dict]:
    with zipfile.ZipFile(path) as archive:
        return json.loads(archive.read("content.json"))


@pytest.mark.skipif(
    not REFERENCE_FILE.exists(),
    reason="El fixture externo se descarga automáticamente en GitHub Actions.",
)
def test_reference_xmind_is_a_readable_modern_workbook():
    with zipfile.ZipFile(REFERENCE_FILE) as archive:
        names = set(archive.namelist())
        assert {"content.json", "metadata.json", "manifest.json"} <= names
        assert "Thumbnails/thumbnail.png" in names
        assert "content.xml" in names
        assert archive.testzip() is None
        if "mimetype" in names:
            assert archive.read("mimetype").decode("ascii") == "application/vnd.xmind.workbook"

    content = _read_content(REFERENCE_FILE)
    assert len(content) == 1
    sheet = content[0]
    assert sheet["title"] == "Mind Map"
    root = sheet["rootTopic"]
    assert root["title"] == "Central Topic"
    assert len(root["children"]["attached"]) == 4


@pytest.mark.skipif(
    not REFERENCE_FILE.exists(),
    reason="El fixture externo se descarga automáticamente en GitHub Actions.",
)
def test_generated_workbook_matches_reference_core_structure(tmp_path: Path):
    reference = _read_content(REFERENCE_FILE)[0]

    child = Topic(id="child-1", title="Child")
    root = Topic(id="root-1", title="Root", children=[child])
    mind_map = MindMap(
        id="integration-map",
        title="Integration map",
        sheet=Sheet(id="sheet-1", title="Integration map", root_topic=root),
    )

    generated_path = write_xmind(mind_map, tmp_path / "generated.xmind")
    generated = _read_content(generated_path)[0]

    assert {"id", "rootTopic"} <= set(reference)
    assert {"id", "rootTopic"} <= set(generated)
    for sheet in (reference, generated):
        topic = sheet["rootTopic"]
        assert isinstance(topic["id"], str) and topic["id"]
        assert isinstance(topic["title"], str)
        assert "attached" in topic.get("children", {})
        for child_topic in topic["children"]["attached"]:
            assert isinstance(child_topic["id"], str) and child_topic["id"]
            assert isinstance(child_topic["title"], str)


def test_generated_relationship_contains_two_model_control_points():
    root = Topic(
        id="root-1",
        title="Root",
        children=[Topic(id="child-1", title="Child")],
    )
    mind_map = MindMap(
        id="relationship-map",
        title="Relationship map",
        sheet=Sheet(
            id="sheet-1",
            title="Relationship map",
            root_topic=root,
            relationships=[
                Relationship(
                    "relation-1",
                    "root-1",
                    "child-1",
                    title="Related",
                )
            ],
        ),
    )

    relationship = build_xmind_content(mind_map)[0]["relationships"][0]
    assert relationship["end1Id"]
    assert relationship["end2Id"]
    assert set(relationship["controlPoints"]) == {"0", "1"}
    for point in relationship["controlPoints"].values():
        assert set(point) == {"x", "y"}
        assert isinstance(point["x"], (int, float))
        assert isinstance(point["y"], (int, float))
