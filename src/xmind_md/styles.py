"""Carga, valida y resuelve estilos neutrales de XMind MD.

Precedencia: valores base del conjunto -> estilo nombrado -> overrides locales.
Las definiciones del documento prevalecen sobre las externas con el mismo nombre.
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml

from .model import MindMap, Topic


class _UniqueKeyLoader(yaml.SafeLoader):
    """Loader YAML seguro que rechaza claves duplicadas."""


def _construct_unique_mapping(loader: _UniqueKeyLoader, node: yaml.MappingNode, deep: bool = False):
    mapping = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            duplicate = key in mapping
        except TypeError as exc:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping", node.start_mark,
                "unhashable mapping key", key_node.start_mark,
            ) from exc
        if duplicate:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping", node.start_mark,
                f"duplicate key {key!r}", key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


_UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_unique_mapping
)


class StyleError(ValueError):
    """Configuración de estilos inválida o referencia inexistente."""


def _mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise StyleError(f"{label} debe ser un objeto YAML")
    return value


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Fusiona recursivamente sin mutar las definiciones originales.

    Los valores null se conservan como instrucciones explícitas de reinicio;
    el adaptador de salida decidirá cómo materializarlas.
    """
    result = deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result


def load_styles(path: str | Path) -> dict[str, Any]:
    """Carga estilos externos conservando tanto styles como style_sets."""
    try:
        data = yaml.load(Path(path).read_text(encoding="utf-8"), Loader=_UniqueKeyLoader) or {}
    except yaml.YAMLError as exc:
        raise StyleError(f"YAML de estilos inválido: {exc}") from exc
    _mapping(data, "El archivo de estilos")
    style_sets = data.get("style_sets", {})
    styles = data.get("styles", {})
    _mapping(style_sets, "style_sets")
    _mapping(styles, "styles")
    _validate_definitions(style_sets, styles)
    return {"style_sets": deepcopy(style_sets), "styles": deepcopy(styles)}


def _validate_definitions(style_sets: dict[str, Any], styles: dict[str, Any]) -> None:
    for name, definition in styles.items():
        _mapping(definition, f"El estilo '{name}'")
    for set_name, definition in style_sets.items():
        _mapping(definition, f"El conjunto '{set_name}'")
        if "styles" in definition:
            _mapping(definition["styles"], f"styles del conjunto '{set_name}'")
            for style_name, style in definition["styles"].items():
                _mapping(style, f"Estilo '{style_name}' del conjunto '{set_name}'")
        for target in ("topic", "relationship", "boundary", "summary", "notes", "extensions"):
            if target in definition:
                _mapping(definition[target], f"{target} del conjunto '{set_name}'")


def resolve_styles(mind_map: MindMap, style_config: dict[str, Any] | None = None) -> MindMap:
    """Resuelve estilos del documento y configuración externa sobre cada tema.

    Acepta el formato nuevo devuelto por load_styles y, temporalmente, un
    mapping legacy que contenga directamente los conjuntos de estilos.
    """
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


def resolve_ir_styles(
    mind_map: Any,
    style_config: dict[str, Any] | None = None,
    defaults: dict[str, Any] | None = None,
) -> Any:
    """Resuelve la cascada de estilos sobre un MindMap IR 1.0.0.

    Precedencia por propiedad:
    defaults del sistema -> style_defaults globales del documento ->
    conjunto aplicable -> estilo nombrado -> overrides locales.

    Un tema hereda el conjunto efectivo de su padre; puede sustituirlo mediante
    style.style_set. Las definiciones externas se sobrescriben por las del mapa.
    La función modifica únicamente los campos style.resolved, no las definiciones.
    """
    from .ir.entities import MindMap as IRMindMap

    if not isinstance(mind_map, IRMindMap):
        raise TypeError("resolve_ir_styles requiere un MindMap IR 1.0.0")

    config = style_config or {}
    _mapping(config, "La configuración externa de estilos")
    if "style_sets" in config or "styles" in config:
        external_sets = _mapping(config.get("style_sets", {}), "style_sets externos")
        external_styles = _mapping(config.get("styles", {}), "styles externos")
    else:
        # Compatibilidad con el formato histórico: el mapping contiene conjuntos.
        external_sets, external_styles = config, {}

    document_sets = _mapping(mind_map.style_sets, "style_sets del documento")
    document_styles = _mapping(mind_map.styles, "styles del documento")
    sets = {**deepcopy(external_sets), **deepcopy(document_sets)}
    styles = {**deepcopy(external_styles), **deepcopy(document_styles)}
    _validate_definitions(sets, styles)

    system_defaults = _mapping(defaults or {}, "Los valores predeterminados")
    global_defaults = _mapping(
        mind_map.metadata.get("style_defaults", {}),
        "style_defaults del documento",
    )
    global_set = mind_map.metadata.get("style_set")
    if global_set is not None and not isinstance(global_set, str):
        raise StyleError("metadata.style_set debe ser texto")
    if global_set and global_set not in sets:
        raise StyleError(f"Conjunto de estilos inexistente: {global_set}")

    def target_properties(definition: Any, target: str, label: str) -> dict[str, Any]:
        mapping = _mapping(definition, label)
        properties = mapping.get(target, mapping)
        return _mapping(properties, f"{label}.{target}")

    def resolve_state(
        state: Any,
        target: str,
        inherited_set: str | None,
        label: str,
    ) -> str | None:
        set_name = state.style_set or inherited_set or global_set
        effective = _deep_merge(
            _mapping(system_defaults.get(target, {}), f"defaults.{target}"),
            _mapping(global_defaults.get(target, {}), f"style_defaults.{target}"),
        )

        set_definition = None
        if set_name:
            set_definition = sets.get(set_name)
            if set_definition is None:
                raise StyleError(f"Conjunto de estilos inexistente: {set_name}")
            _mapping(set_definition, f"El conjunto '{set_name}'")
            effective = _deep_merge(
                effective,
                target_properties(
                    set_definition.get(target, {}),
                    target,
                    f"Conjunto '{set_name}'",
                ),
            )

        if state.ref:
            named = styles.get(state.ref)
            if named is None and set_definition is not None:
                named = set_definition.get("styles", {}).get(state.ref)
            if named is None:
                raise StyleError(f"Estilo '{state.ref}' no definido para {label}")
            effective = _deep_merge(
                effective,
                target_properties(named, target, f"Estilo '{state.ref}'"),
            )

        overrides = _mapping(state.overrides, f"Overrides de {label}")
        state.resolved = _deep_merge(effective, overrides)
        return set_name

    def visit_topic(topic: Any, inherited_set: str | None = None) -> None:
        effective_set = resolve_state(
            topic.style, "topic", inherited_set, f"tema '{topic.title}'"
        )
        for index, note in enumerate(topic.annotations.notes):
            resolve_state(
                note.style, "notes", effective_set,
                f"nota {index} del tema '{topic.title}'",
            )
        for child in topic.children:
            visit_topic(child, effective_set)

    visit_topic(mind_map.sheet.root_topic)

    for index, relationship in enumerate(mind_map.sheet.relationships):
        resolve_state(
            relationship.style, "relationship", global_set,
            f"relación {relationship.id}",
        )
    for index, boundary in enumerate(mind_map.sheet.boundaries):
        resolve_state(
            boundary.style, "boundary", global_set,
            f"límite {boundary.id}",
        )
    for index, summary in enumerate(mind_map.sheet.summaries):
        resolve_state(
            summary.style, "summary", global_set,
            f"resumen {summary.id}",
        )

    return mind_map
