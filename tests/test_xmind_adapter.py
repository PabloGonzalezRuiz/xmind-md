"""Pruebas del adaptador XMind moderno con entidades IR 1.0.0."""

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
from xmind_md.ir import (
    Annotation,
    Asset,
    Boundary,
    ContentBlock,
    Label,
    Marker,
    MindMap,
    Note,
    Relationship,
    ResourceReferences,
    Sheet,
    StyleState,
    Summary,
    Topic,
)


def make_map() -> MindMap:
    child = Topic(
        id="topic_child",
        title="Hijo",
        content=[ContentBlock(
            "paragraph",
            {"text": "Texto del hijo", "runs": [{"text": "Texto "}, {"text": "del hijo"}]},
        )],
        annotations=Annotation(
            labels=[Label("label_1", "IMPORTANTE")],
            markers=[Marker("marker_1", "priority", 1)],
            notes=[Note("note_1", [ContentBlock("paragraph", {"text": "Nota adicional"})])],
        ),
        links=[{"id": "link_1", "kind": "web", "target": "https://example.com"}],
        style=StyleState(resolved={
            "shape": "org.xmind.topicShape.roundRect",
            "text": {"font_size": 14, "bold": True, "color": "#123456"},
            "background": {"color": "#ffffff"},
            "border": {"color": "#000000", "width": 2},
        }),
    )
    root = Topic(id="topic_root", title="Raíz", children=[child])
    return MindMap(
        id="map_test",
        title="Mapa de prueba",
        sheet=Sheet(
            id="sheet_test",
            title="Hoja de prueba",
            root_topic=root,
            relationships=[Relationship("rel_1", "topic_root", "topic_child", title="Conecta")],
        ),
    )


def test_build_content_creates_one_sheet_and_recursive_topic_tree():
    sheet = build_xmind_content(make_map())[0]
    root = sheet["rootTopic"]
    child = root["children"]["attached"][0]
    assert sheet["class"] == "sheet"
    assert sheet["title"] == "Hoja de prueba"
    assert root["title"] == "Raíz"
    assert child["title"] == "Hijo"
    assert uuid.UUID(root["id"])
    assert uuid.UUID(child["id"])
    assert root["id"] != child["id"]


def test_build_content_maps_annotations_links_and_resolved_styles():
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
    assert relationship["title"] == "Conecta"
    assert relationship["controlPoints"] == {
        "0": {"x": 0, "y": 0},
        "1": {"x": 0, "y": 0},
    }


def test_generated_ids_are_deterministic():
    assert build_xmind_content(make_map()) == build_xmind_content(make_map())


def test_write_xmind_creates_valid_zip_package(tmp_path):
    destination = tmp_path / "nested" / "mapa.xmind"
    result = write_xmind(make_map(), destination)
    assert result == destination
    with zipfile.ZipFile(destination) as archive:
        assert archive.namelist() == [
            "mimetype", "content.json", "metadata.json", "manifest.json",
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
        (lambda m: setattr(m.sheet.root_topic, "kind", "detached"), "kind"),
        (lambda m: setattr(m.sheet.root_topic, "resources", ResourceReferences(images=["a1"])), "recursos"),
        (lambda m: m.assets.update({"a1": Asset("image", "image.png")}), "recursos"),
        (lambda m: m.sheet.boundaries.append(Boundary("b1", ["topic_child"])), "boundaries"),
        (lambda m: m.sheet.summaries.append(Summary("s1", ["topic_child"])), "summaries"),
        (lambda m: m.sheet.root_topic.extensions.update({"custom": True}), "extensiones"),
    ],
)
def test_unsupported_features_fail_explicitly(change, message):
    mind_map = make_map()
    change(mind_map)
    with pytest.raises(XMindAdapterError, match=message):
        build_xmind_content(mind_map)


def test_unknown_style_property_fails_instead_of_being_dropped():
    mind_map = make_map()
    mind_map.sheet.root_topic.style.resolved = {"effects": {"shadow": True}}
    with pytest.raises(XMindAdapterError, match="no soportada"):
        build_xmind_content(mind_map)


def test_relationship_with_unknown_topic_id_is_rejected():
    mind_map = make_map()
    mind_map.sheet.relationships[0].target_topic = "missing"
    with pytest.raises(XMindAdapterError, match="no existe"):
        build_xmind_content(mind_map)


def test_named_style_must_be_resolved_before_export():
    mind_map = make_map()
    mind_map.sheet.root_topic.style.ref = "named-style"
    mind_map.sheet.root_topic.style.overrides = {"text": {"bold": True}}
    with pytest.raises(XMindAdapterError, match="no están resueltos"):
        build_xmind_content(mind_map)


def test_relationship_style_uses_resolved_state():
    mind_map = make_map()
    mind_map.sheet.relationships[0].style.resolved = {"text": {"bold": True}}
    relationship = build_xmind_content(mind_map)[0]["relationships"][0]
    assert relationship["style"]["properties"] == {"fo:font-weight": "bold"}
