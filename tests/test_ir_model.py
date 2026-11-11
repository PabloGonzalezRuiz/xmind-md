"""Pruebas del modelo canónico IR 1.0.0 y sus invariantes."""

import pytest

from xmind_md.styles import StyleError, resolve_styles

from xmind_md.ir import (
    Annotation,
    Asset,
    Boundary,
    ContentBlock,
    IRValidationError,
    Label,
    MindMap,
    Relationship,
    ResourceReferences,
    Sheet,
    StyleState,
    Summary,
    Topic,
    validate_mind_map,
)


def make_map() -> MindMap:
    child = Topic(
        id="topic_child",
        title="Hijo",
        content=[ContentBlock("paragraph", {"text": "Contenido"})],
        annotations=Annotation(labels=[Label("label_child", "IMPORTANTE")]),
        resources=ResourceReferences(images=["asset_image"]),
    )
    root = Topic(id="topic_root", title="Raíz", children=[child])
    sheet = Sheet(
        id="sheet_main",
        title="Hoja principal",
        root_topic=root,
        relationships=[Relationship("rel_1", "topic_root", "topic_child")],
        boundaries=[Boundary("boundary_1", ["topic_child"])],
        summaries=[Summary("summary_1", ["topic_child"])],
    )
    return MindMap(
        id="map_1",
        title="Mapa",
        sheet=sheet,
        assets={"asset_image": Asset("image", "images/example.png")},
    )


def test_serialization_matches_ir_document_shape():
    result = make_map().to_dict()

    assert set(result) == {
        "ir_version",
        "id",
        "title",
        "metadata",
        "styles",
        "style_sets",
        "assets",
        "sheet",
    }
    assert result["ir_version"] == "1.0.0"
    assert "root_topic" in result["sheet"]
    assert "topics" not in result
    topic = result["sheet"]["root_topic"]["children"][0]
    assert topic["content"][0] == {"type": "paragraph", "text": "Contenido"}
    assert topic["annotations"]["labels"] == [{"id": "label_child", "text": "IMPORTANTE"}]
    assert topic["resources"]["images"] == ["asset_image"]


def test_style_state_always_serializes_all_three_layers():
    style = StyleState(ref="important", overrides={"text": {"bold": True}})
    assert style.to_dict() == {
        "ref": "important",
        "style_set": None,
        "overrides": {"text": {"bold": True}},
        "resolved": {},
    }


def test_valid_document_passes_semantic_validation():
    assert validate_mind_map(make_map()) is not None


def test_duplicate_ids_are_rejected_across_entity_types():
    mind_map = make_map()
    mind_map.sheet.root_topic.children[0].annotations.labels[0].id = "topic_root"

    with pytest.raises(IRValidationError, match="ID duplicado"):
        validate_mind_map(mind_map)


def test_relationship_must_reference_existing_topics():
    mind_map = make_map()
    mind_map.sheet.relationships[0].target_topic = "missing"

    with pytest.raises(IRValidationError, match="tema inexistente"):
        validate_mind_map(mind_map)


def test_boundary_and_summary_references_must_exist():
    mind_map = make_map()
    mind_map.sheet.boundaries[0].topic_ids = ["missing"]

    with pytest.raises(IRValidationError, match="referencia a tema inexistente"):
        validate_mind_map(mind_map)


def test_topic_cannot_be_shared_by_two_parents():
    mind_map = make_map()
    child = mind_map.sheet.root_topic.children[0]
    mind_map.sheet.root_topic.children.append(child)

    with pytest.raises(IRValidationError, match="más de un padre"):
        validate_mind_map(mind_map)


def test_cycles_are_rejected():
    mind_map = make_map()
    child = mind_map.sheet.root_topic.children[0]
    child.children.append(mind_map.sheet.root_topic)

    with pytest.raises(IRValidationError, match="ciclo"):
        validate_mind_map(mind_map)


def test_resource_references_must_resolve():
    mind_map = make_map()
    mind_map.sheet.root_topic.children[0].resources.images = ["missing"]

    with pytest.raises(IRValidationError, match="recurso inexistente"):
        validate_mind_map(mind_map)


def test_asset_metadata_is_checked():
    mind_map = make_map()
    mind_map.assets["asset_image"].size = -1

    with pytest.raises(IRValidationError, match="no puede ser negativo"):
        validate_mind_map(mind_map)


def test_link_kind_and_target_are_validated():
    mind_map = make_map()
    mind_map.sheet.root_topic.links.append({"id": "link_1", "kind": "ftp", "target": "example"})

    with pytest.raises(IRValidationError, match="kind"):
        validate_mind_map(mind_map)


def test_topic_link_must_reference_existing_topic():
    mind_map = make_map()
    mind_map.sheet.root_topic.links.append({"id": "link_1", "kind": "topic", "target": "missing"})

    with pytest.raises(IRValidationError, match="tema enlazado inexistente"):
        validate_mind_map(mind_map)


def test_style_reference_is_resolved_after_external_catalogs_are_loaded():
    mind_map = make_map()
    mind_map.sheet.root_topic.style.ref = "missing"

    assert validate_mind_map(mind_map) is mind_map
    with pytest.raises(StyleError, match="Estilo"):
        resolve_styles(mind_map)


def test_topic_style_set_reference_is_resolved_after_external_catalogs_are_loaded():
    mind_map = make_map()
    mind_map.sheet.root_topic.style.style_set = "missing"

    assert validate_mind_map(mind_map) is mind_map
    with pytest.raises(StyleError, match="Conjunto"):
        resolve_styles(mind_map)
