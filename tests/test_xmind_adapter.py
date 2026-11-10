"""Pruebas del adaptador XMind moderno."""
import json
import uuid
import zipfile

import pytest

from xmind_md.adapters.xmind_adapter import (
    MIMETYPE,
    XMindAdapterError,
    build_xmind_content,
    write_xmind,
)
from xmind_md.model import MindMap, Topic


def make_map() -> MindMap:
    child = Topic(
        id="topic_child",
        title="Hijo",
        level=2,
        annotations={
            "labels": ["IMPORTANTE"],
            "markers": [{"group": "priority", "value": "1"}],
            "notes": ["Nota adicional"],
        },
        content_blocks=[
            {"type": "paragraph", "runs": [{"text": "Texto "}, {"text": "del hijo"}]}
        ],
        links=[{"url": "https://example.com"}],
        resolved_style={
            "shape": "org.xmind.topicShape.roundRect",
            "text": {"font_size": 14, "bold": True, "color": "#123456"},
            "background": {"color": "#ffffff"},
            "border": {"color": "#000000", "width": 2},
        },
    )
    root = Topic(
        id="topic_root",
        title="Raíz",
        level=1,
        children=[child],
    )
    return MindMap(
        id="map_test",
        title="Mapa de prueba",
        topics=[root],
        relationships=[
            {"id": "rel_1", "source": "topic_root", "target": "topic_child", "title": "Conecta"}
        ],
    )


def test_build_content_creates_one_sheet_and_recursive_topic_tree():
    content = build_xmind_content(make_map())

    assert len(content) == 1
    sheet = content[0]
    assert sheet["class"] == "sheet"
    assert sheet["title"] == "Mapa de prueba"
    root = sheet["rootTopic"]
    child = root["children"]["attached"][0]
    assert root["title"] == "Raíz"
    assert child["title"] == "Hijo"
    assert uuid.UUID(root["id"])
    assert uuid.UUID(child["id"])
    assert root["id"] != child["id"]


def test_build_content_maps_labels_markers_notes_links_and_styles():
    child = build_xmind_content(make_map())[0]["rootTopic"]["children"]["attached"][0]

    assert child["labels"] == ["IMPORTANTE"]
    assert child["markers"] == [{"markerId": "priority-1"}]
    assert child["notes"]["plain"]["content"] == "Texto del hijo\n\nNota adicional"
    assert child["href"] == "https://example.com"
    assert child["style"]["properties"] == {
        "shape-class": "org.xmind.topicShape.roundRect",
        "fo:font-size": "14",
        "fo:font-weight": "bold",
        "fo:color": "#123456",
        "svg:fill": "#ffffff",
        "line-color": "#000000",
        "line-width": "2",
    }


def test_build_content_maps_relationship_endpoints_to_xmind_ids():
    sheet = build_xmind_content(make_map())[0]
    root = sheet["rootTopic"]
    child = root["children"]["attached"][0]
    relationship = sheet["relationships"][0]

    assert relationship["class"] == "relationship"
    assert relationship["end1Id"] == root["id"]
    assert relationship["end2Id"] == child["id"]
    assert relationship["controlPoints"] == {
        "0": {"x": 0, "y": 0},
        "1": {"x": 0, "y": 0},
    }
    assert relationship["title"] == "Conecta"


def test_generated_ids_are_deterministic():
    first = build_xmind_content(make_map())
    second = build_xmind_content(make_map())

    assert first == second


def test_write_xmind_creates_valid_zip_package(tmp_path):
    destination = tmp_path / "nested" / "mapa.xmind"

    result = write_xmind(make_map(), destination)

    assert result == destination
    with zipfile.ZipFile(destination) as archive:
        names = archive.namelist()
        assert names == [
            "mimetype",
            "content.json",
            "metadata.json",
            "manifest.json",
            "Thumbnails/thumbnail.png",
        ]
        assert archive.getinfo("mimetype").compress_type == zipfile.ZIP_STORED
        assert archive.read("mimetype").decode("ascii") == MIMETYPE
        content = json.loads(archive.read("content.json"))
        metadata = json.loads(archive.read("metadata.json"))
        manifest = json.loads(archive.read("manifest.json"))
        assert content[0]["rootTopic"]["title"] == "Raíz"
        assert metadata["activeSheetId"] == content[0]["id"]
        assert "content.json" in manifest["file-entries"]
        assert archive.testzip() is None


@pytest.mark.parametrize(
    "change, message",
    [
        (lambda m: setattr(m.topics[0], "kind", "detached"), "kind"),
        (lambda m: m.assets.append({"src": "image.png"}), "recursos"),
        (lambda m: m.boundaries.append({"id": "b1"}), "boundaries"),
        (lambda m: m.summaries.append({"id": "s1"}), "summaries"),
        (lambda m: m.topics[0].extensions.update({"custom": True}), "extensiones"),
    ],
)
def test_unsupported_features_fail_explicitly(change, message):
    mind_map = make_map()
    change(mind_map)

    with pytest.raises(XMindAdapterError, match=message):
        build_xmind_content(mind_map)


def test_unknown_style_property_fails_instead_of_being_dropped():
    mind_map = make_map()
    mind_map.topics[0].resolved_style = {"effects": {"shadow": True}}

    with pytest.raises(XMindAdapterError, match="no soportada"):
        build_xmind_content(mind_map)


def test_relationship_with_unknown_topic_id_is_rejected():
    mind_map = make_map()
    mind_map.relationships[0]["target"] = "missing"

    with pytest.raises(XMindAdapterError, match="no existe"):
        build_xmind_content(mind_map)


def test_named_style_must_be_resolved_before_export():
    mind_map = make_map()
    mind_map.topics[0].style_ref = "named-style"
    mind_map.topics[0].style_overrides = {"text": {"bold": True}}

    with pytest.raises(XMindAdapterError, match="no están resueltos"):
        build_xmind_content(mind_map)
