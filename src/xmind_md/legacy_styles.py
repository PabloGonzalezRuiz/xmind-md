"""Resolución de estilos del modelo legacy, aislada de la ruta IR."""
from __future__ import annotations

from copy import deepcopy
from typing import Any

from .model import Topic
from .styles import StyleError, _deep_merge, _mapping, _validate_definitions


def resolve_legacy_styles(
    mind_map: Any,
    style_config: dict[str, Any] | None = None,
) -> Any:
    """Mantiene la resolución histórica para objetos model.MindMap."""
    if not hasattr(mind_map, "topics") or not hasattr(mind_map, "style_sets"):
        raise TypeError("resolve_legacy_styles requiere un MindMap legacy")

    config = style_config or {}
    if "style_sets" in config or "styles" in config:
        external_sets = _mapping(config.get("style_sets", {}), "style_sets externos")
        external_styles = _mapping(config.get("styles", {}), "styles externos")
    else:
        external_sets, external_styles = config, {}

    document_sets = _mapping(mind_map.style_sets or {}, "style_sets del documento")
    document_styles = _mapping(mind_map.styles or {}, "styles del documento")
    sets = {**deepcopy(external_sets), **deepcopy(document_sets)}
    styles = {**deepcopy(external_styles), **deepcopy(document_styles)}
    _validate_definitions(sets, styles)

    def visit(topic: Topic, inherited_set: str | None = None) -> None:
        set_name = topic.style_set or inherited_set
        effective: dict[str, Any] = {}
        if set_name:
            definition = sets.get(set_name)
            if definition is None:
                raise StyleError(f"Conjunto de estilos inexistente: {set_name}")
            _mapping(definition, f"El conjunto '{set_name}'")
            effective = _deep_merge(effective, definition.get("topic", {}))

        if topic.style_ref:
            named = styles.get(topic.style_ref)
            if named is None and set_name:
                named = definition.get("styles", {}).get(topic.style_ref)
            if named is None:
                raise StyleError(f"Estilo '{topic.style_ref}' no definido")
            _mapping(named, f"Estilo '{topic.style_ref}'")
            # Las definiciones de estilo pueden agrupar propiedades por objeto
            # (topic, relationship...) o describir directamente el estilo topic.
            topic_style = named.get("topic", named)
            _mapping(topic_style, f"Propiedades topic del estilo '{topic.style_ref}'")
            effective = _deep_merge(effective, topic_style)

        overrides = _mapping(topic.style_overrides or {}, f"Overrides de '{topic.title}'")
        effective = _deep_merge(effective, overrides)
        topic.resolved_style = effective

        for child in topic.children:
            visit(child, set_name)

    for root in mind_map.topics:
        visit(root, mind_map.metadata.get("style_set"))
    return mind_map


