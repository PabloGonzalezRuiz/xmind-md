"""Pruebas de cascada de estilos sobre el modelo IR 1.0.0."""
from copy import deepcopy

import pytest

from xmind_md.ir import (
    Annotation,
    Boundary,
    MindMap,
    Note,
    Relationship,
    Sheet,
    StyleState,
    Summary,
    Topic,
)
from xmind_md.styles import StyleError, resolve_ir_styles


def make_map(root=None, metadata=None, **sheet_kwargs):
    return MindMap(
        id="mapa",
        title="Mapa",
        metadata=metadata or {},
        sheet=Sheet(
            id="hoja",
            title="Mapa",
            root_topic=root or Topic(id="raiz", title="Raíz"),
            **sheet_kwargs,
        ),
    )


def test_ir_style_cascade_applies_all_levels_and_merges_recursively():
    child = Topic(
        id="hijo",
        title="Hijo",
        style=StyleState(
            ref="alerta",
            overrides={"text": {"italic": True, "color": "purple"}},
        ),
    )
    root = Topic(
        id="raiz",
        title="Raíz",
        style=StyleState(style_set="BASE"),
        children=[child],
    )
    mind_map = make_map(
        root,
        metadata={"style_defaults": {"topic": {"text": {"font_size": 10, "color": "black"}}}},
    )
    mind_map.style_sets = {
        "BASE": {
            "topic": {"text": {"font_size": 12, "bold": False}, "shape": {"type": "round"}},
            "styles": {"alerta": {"topic": {"text": {"color": "red", "bold": True}}}},
        }
    }
    resolve_ir_styles(mind_map, defaults={"topic": {"text": {"font_size": 8}}})

    assert root.style.resolved == {
        "text": {"font_size": 12, "color": "black", "bold": False},
        "shape": {"type": "round"},
    }
    assert child.style.resolved == {
        "text": {
            "font_size": 12,
            "color": "purple",
            "bold": True,
            "italic": True,
        },
        "shape": {"type": "round"},
    }


def test_topic_can_override_inherited_style_set_for_its_branch():
    root = Topic(id="raiz", title="Raíz", style=StyleState(style_set="BASE"))
    child = Topic(id="hijo", title="Hijo", style=StyleState(style_set="ALTERNATIVO"))
    grandchild = Topic(id="nieto", title="Nieto")
    child.children.append(grandchild)
    root.children.append(child)
    mind_map = make_map(root)
    mind_map.style_sets = {
        "BASE": {"topic": {"text": {"color": "black"}}},
        "ALTERNATIVO": {"topic": {"text": {"color": "orange"}}},
    }

    resolve_ir_styles(mind_map)

    assert root.style.resolved["text"]["color"] == "black"
    assert child.style.resolved["text"]["color"] == "orange"
    assert grandchild.style.resolved["text"]["color"] == "orange"


def test_document_definitions_override_external_definitions():
    root = Topic(id="raiz", title="Raíz", style=StyleState(style_set="BASE", ref="normal"))
    mind_map = make_map(root)
    mind_map.style_sets = {"BASE": {"topic": {"text": {"size": 14}}}}
    mind_map.styles = {"normal": {"topic": {"text": {"color": "red"}}}}
    external = {
        "style_sets": {"BASE": {"topic": {"text": {"size": 10}}}},
        "styles": {"normal": {"topic": {"text": {"color": "blue"}}}},
    }

    resolve_ir_styles(mind_map, external)

    assert root.style.resolved == {"text": {"size": 14, "color": "red"}}


def test_global_style_set_is_used_when_topic_does_not_select_one():
    root = Topic(id="raiz", title="Raíz")
    mind_map = make_map(root)
    mind_map.metadata["style_set"] = "GLOBAL"
    mind_map.style_sets = {"GLOBAL": {"topic": {"text": {"bold": True}}}}

    resolve_ir_styles(mind_map)

    assert root.style.resolved == {"text": {"bold": True}}


def test_missing_style_set_and_style_raise_clear_errors():
    root = Topic(id="raiz", title="Raíz", style=StyleState(style_set="NO_EXISTE"))
    with pytest.raises(StyleError, match="Conjunto"):
        resolve_ir_styles(make_map(root))

    root.style.style_set = None
    root.style.ref = "NO_EXISTE"
    with pytest.raises(StyleError, match="Estilo"):
        resolve_ir_styles(make_map(root))


def test_malformed_definitions_and_overrides_raise_style_error():
    root = Topic(id="raiz", title="Raíz")
    mind_map = make_map(root)
    mind_map.style_sets = {"BASE": {"topic": []}}
    root.style.style_set = "BASE"
    with pytest.raises(StyleError, match="topic"):
        resolve_ir_styles(mind_map)

    mind_map.style_sets = {}
    root.style.style_set = None
    root.style.overrides = []
    with pytest.raises(StyleError, match="Overrides"):
        resolve_ir_styles(mind_map)


def test_resolution_does_not_mutate_source_definitions():
    root = Topic(id="raiz", title="Raíz", style=StyleState(style_set="BASE", ref="normal"))
    mind_map = make_map(root)
    mind_map.style_sets = {"BASE": {"topic": {"text": {"color": "black"}}}}
    mind_map.styles = {"normal": {"topic": {"text": {"bold": True}}}}
    before = deepcopy((mind_map.style_sets, mind_map.styles))

    resolve_ir_styles(mind_map)

    assert (mind_map.style_sets, mind_map.styles) == before


def test_sheet_entities_and_notes_resolve_their_own_style_targets():
    root = Topic(
        id="raiz",
        title="Raíz",
        style=StyleState(style_set="BASE"),
        annotations=Annotation(notes=[Note("nota", style=StyleState(ref="nota-estilo"))]),
    )
    relationship = Relationship("rel", "raiz", "otro", style=StyleState(ref="rel-estilo"))
    boundary = Boundary("limite", ["raiz"], style=StyleState(ref="limite-estilo"))
    summary = Summary("resumen", ["raiz"], style=StyleState(ref="resumen-estilo"))
    mind_map = make_map(root, relationships=[relationship], boundaries=[boundary], summaries=[summary])
    mind_map.style_sets = {
        "BASE": {
            "topic": {"text": {"bold": True}},
            "styles": {"nota-estilo": {"notes": {"text": {"italic": True}}}},
        }
    }
    mind_map.styles = {
        "rel-estilo": {"relationship": {"line": {"width": 2}}},
        "limite-estilo": {"boundary": {"border": {"color": "red"}}},
        "resumen-estilo": {"summary": {"text": {"color": "blue"}}},
    }

    resolve_ir_styles(mind_map)

    assert root.annotations.notes[0].style.resolved == {"text": {"italic": True}}
    assert relationship.style.resolved == {"line": {"width": 2}}
    assert boundary.style.resolved == {"border": {"color": "red"}}
    assert summary.style.resolved == {"text": {"color": "blue"}}
