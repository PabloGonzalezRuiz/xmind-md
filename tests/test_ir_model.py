"""Pruebas del modelo canónico IR 1.0.0 y sus invariantes."""

import pytest

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
    TopicStructure,
    TreeTableCell,
    TreeTableRow,
    validate_mind_map,
)
from xmind_md.styles import StyleError, resolve_styles


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

    with pytest.raises(IRValidationError, match="entero no negativo"):
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


def test_sheet_title_type_errors_are_reported_as_ir_validation_errors():
    mind_map = make_map()
    mind_map.sheet.title = 42

    with pytest.raises(IRValidationError, match="sheet.title"):
        validate_mind_map(mind_map)


def test_malformed_link_entries_are_reported_as_ir_validation_errors():
    mind_map = make_map()
    mind_map.sheet.root_topic.links.append([])

    with pytest.raises(IRValidationError, match="debe ser un objeto"):
        validate_mind_map(mind_map)


def test_content_block_payload_must_be_a_mapping():
    mind_map = make_map()
    mind_map.sheet.root_topic.children[0].content[0].data = []

    with pytest.raises(IRValidationError, match="data"):
        validate_mind_map(mind_map)


def test_asset_size_must_be_an_integer_not_boolean():
    mind_map = make_map()
    mind_map.assets["asset_image"].size = True

    with pytest.raises(IRValidationError, match="entero no negativo"):
        validate_mind_map(mind_map)


def test_ir_1_1_tree_table_serializes_roles_and_order_without_duplicate_content():
    header = Topic(id="topic_header", title="Cabecera", semantic_role="table.header_cell")
    body = Topic(
        id="topic_body",
        title="Cuerpo",
        semantic_role="table.body_cell",
        content=[ContentBlock("paragraph", {"text": "Texto de la celda"})],
    )
    root = Topic(
        id="topic_article",
        title="Artículo",
        semantic_role="legal.article",
        children=[header, body],
        structure=TopicStructure(
            "tree_table",
            [TreeTableRow([TreeTableCell("topic_header"), TreeTableCell("topic_body")])],
        ),
    )
    mind_map = MindMap(
        id="map_1_1",
        title="Mapa",
        sheet=Sheet(id="sheet_1_1", title="Hoja", root_topic=root),
        ir_version="1.1.0",
    )

    validate_mind_map(mind_map)
    result = mind_map.to_dict()["sheet"]["root_topic"]

    assert result["semantic_role"] == "legal.article"
    assert result["structure"] == {
        "type": "tree_table",
        "rows": [{"cells": [{"topic_id": "topic_header"}, {"topic_id": "topic_body"}]}],
    }
    assert result["children"][1]["semantic_role"] == "table.body_cell"
    assert result["children"][1]["content"][0]["text"] == "Texto de la celda"
    assert "content" not in result["structure"]["rows"][0]["cells"][1]


def test_ir_1_0_rejects_semantic_roles_and_structures():
    mind_map = make_map()
    mind_map.sheet.root_topic.semantic_role = "legal.article"

    with pytest.raises(IRValidationError, match="requiere ir_version 1.1.0"):
        validate_mind_map(mind_map)


def test_tree_table_requires_each_direct_child_exactly_once():
    mind_map = make_map()
    root = mind_map.sheet.root_topic
    root.children.append(Topic(id="topic_extra", title="Extra"))
    root.structure = TopicStructure(
        "tree_table",
        [TreeTableRow([TreeTableCell(root.children[0].id)])],
    )
    mind_map.ir_version = "1.1.0"

    with pytest.raises(IRValidationError, match="todos los hijos deben aparecer"):
        validate_mind_map(mind_map)


def test_tree_table_rejects_duplicate_cell_references():
    mind_map = make_map()
    root = mind_map.sheet.root_topic
    root.structure = TopicStructure(
        "tree_table",
        [TreeTableRow([TreeTableCell("topic_child"), TreeTableCell("topic_child")])],
    )
    mind_map.ir_version = "1.1.0"

    with pytest.raises(IRValidationError, match="no puede repetirse"):
        validate_mind_map(mind_map)


def test_tree_table_rejects_non_direct_child_references():
    mind_map = make_map()
    root = mind_map.sheet.root_topic
    nested = Topic(id="topic_nested", title="Nieto")
    root.children[0].children.append(nested)
    root.structure = TopicStructure(
        "tree_table",
        [TreeTableRow([TreeTableCell("topic_nested")])],
    )
    mind_map.ir_version = "1.1.0"

    with pytest.raises(IRValidationError, match="hijo directo"):
        validate_mind_map(mind_map)


def test_tree_table_supports_nested_structures_on_cell_topics():
    nested_cell = Topic(id="topic_nested_cell", title="Subcelda", semantic_role="table.body_cell")
    nested_container = Topic(
        id="topic_nested_container",
        title="Celda compuesta",
        semantic_role="table.body_cell",
        children=[nested_cell],
        structure=TopicStructure(
            "tree_table",
            [TreeTableRow([TreeTableCell("topic_nested_cell")])],
        ),
    )
    root = Topic(
        id="topic_root",
        title="Raíz",
        children=[nested_container],
        structure=TopicStructure(
            "tree_table",
            [TreeTableRow([TreeTableCell("topic_nested_container")])],
        ),
    )
    mind_map = MindMap(
        id="map_nested",
        title="Mapa",
        sheet=Sheet(id="sheet_nested", title="Hoja", root_topic=root),
        ir_version="1.1.0",
    )

    assert validate_mind_map(mind_map) is mind_map


def test_ir_1_1_rejects_xmind_structure_class_in_layout():
    mind_map = make_map()
    mind_map.ir_version = "1.1.0"
    mind_map.sheet.root_topic.layout["structure_class"] = "org.xmind.ui.treetable.toptitle"

    with pytest.raises(IRValidationError, match="layout.structure_class"):
        validate_mind_map(mind_map)


def test_literal_inherited_is_preserved_as_an_explicit_style_value():
    mind_map = make_map()
    mind_map.sheet.root_topic.style.overrides = {"border": {"color": "inherited", "width": None}}
    defaults = {"topic": {"border": {"color": "#000000", "width": 2, "pattern": "solid"}}}

    resolve_styles(mind_map, defaults=defaults)

    assert mind_map.sheet.root_topic.style.resolved["border"] == {
        "color": "inherited",
        "width": None,
        "pattern": "solid",
    }
