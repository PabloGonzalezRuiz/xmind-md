"""Validación semántica del modelo intermedio IR 1.0.0."""

from __future__ import annotations

import re
from typing import Any

from .entities import MindMap, Topic

_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]*$")
_CONTENT_TYPES = {
    "paragraph",
    "list",
    "table",
    "code",
    "quote",
    "equation",
    "image",
    "divider",
    "raw",
}


class IRValidationError(ValueError):
    """El documento IR incumple una o más invariantes semánticas."""


def _require_id(value: str, path: str) -> None:
    if not isinstance(value, str) or not _ID_RE.fullmatch(value):
        raise IRValidationError(f"{path}: ID vacío o con formato no válido: {value!r}")


def _register(value: str, path: str, seen: dict[str, str]) -> None:
    _require_id(value, path)
    if value in seen:
        raise IRValidationError(f"{path}: ID duplicado {value!r}; ya se utiliza en {seen[value]}")
    seen[value] = path


def _walk_topics(
    topic: Topic,
    path: str,
    seen: dict[str, str],
    topic_ids: set[str],
    asset_ids: set[str],
    active: set[int],
    visited: set[int],
) -> None:
    identity = id(topic)
    if identity in active:
        raise IRValidationError(f"{path}: ciclo detectado en el árbol de temas")
    if identity in visited:
        raise IRValidationError(f"{path}: un tema no puede tener más de un padre")
    active.add(identity)
    visited.add(identity)

    _register(topic.id, f"{path}.id", seen)
    topic_ids.add(topic.id)
    if not isinstance(topic.title, str) or not topic.title.strip():
        raise IRValidationError(f"{path}.title: debe ser texto no vacío")
    if not isinstance(topic.kind, str) or not topic.kind:
        raise IRValidationError(f"{path}.kind: debe ser texto no vacío")

    for index, block in enumerate(topic.content):
        block_path = f"{path}.content[{index}]"
        if not isinstance(block.type, str) or block.type not in _CONTENT_TYPES:
            raise IRValidationError(f"{block_path}.type: tipo no reconocido {block.type!r}")
        if not isinstance(block.data, dict):
            raise IRValidationError(f"{block_path}.data: debe ser un objeto")
        if block.id is not None:
            _register(block.id, f"{block_path}.id", seen)
        if block.type == "image":
            asset_id = block.data.get("asset_id")
            if asset_id is not None and asset_id not in asset_ids:
                raise IRValidationError(f"{block_path}.asset_id: recurso inexistente {asset_id!r}")

    for index, note in enumerate(topic.annotations.notes):
        note_path = f"{path}.annotations.notes[{index}]"
        _register(note.id, f"{note_path}.id", seen)
        for block_index, block in enumerate(note.content):
            if not isinstance(block.type, str) or block.type not in _CONTENT_TYPES:
                raise IRValidationError(
                    f"{note_path}.content[{block_index}].type: tipo no reconocido {block.type!r}"
                )
            if not isinstance(block.data, dict):
                raise IRValidationError(
                    f"{note_path}.content[{block_index}].data: debe ser un objeto"
                )
            if block.id is not None:
                _register(block.id, f"{note_path}.content[{block_index}].id", seen)
    for index, label in enumerate(topic.annotations.labels):
        _register(label.id, f"{path}.annotations.labels[{index}].id", seen)
    for index, marker in enumerate(topic.annotations.markers):
        _register(marker.id, f"{path}.annotations.markers[{index}].id", seen)

    for index, link in enumerate(topic.links):
        link_path = f"{path}.links[{index}]"
        if not isinstance(link, dict):
            raise IRValidationError(f"{link_path}: debe ser un objeto")
        _register(link.get("id"), f"{link_path}.id", seen)
        kind = link.get("kind")
        if not isinstance(kind, str) or kind not in {"web", "topic", "file", "internal"}:
            raise IRValidationError(f"{link_path}.kind: tipo de enlace no válido")
        if not isinstance(link.get("target"), str) or not link["target"]:
            raise IRValidationError(f"{link_path}.target: destino vacío o no textual")

    for group_name in ("images", "attachments", "audio"):
        for asset_id in getattr(topic.resources, group_name):
            if asset_id not in asset_ids:
                raise IRValidationError(
                    f"{path}.resources.{group_name}: recurso inexistente {asset_id!r}"
                )

    for index, child in enumerate(topic.children):
        _walk_topics(
            child,
            f"{path}.children[{index}]",
            seen,
            topic_ids,
            asset_ids,
            active,
            visited,
        )
    active.remove(identity)


def validate_mind_map(mind_map: MindMap) -> MindMap:
    """Comprueba IDs, árbol y referencias; devuelve el mismo documento validado."""
    if mind_map.ir_version != "1.0.0":
        raise IRValidationError(f"ir_version no soportada: {mind_map.ir_version!r}")
    if not isinstance(mind_map.title, str) or not mind_map.title.strip():
        raise IRValidationError("title: debe ser texto no vacío")

    seen: dict[str, str] = {}
    _register(mind_map.id, "id", seen)
    _register(mind_map.sheet.id, "sheet.id", seen)
    if not isinstance(mind_map.sheet.title, str) or not mind_map.sheet.title.strip():
        raise IRValidationError("sheet.title: debe ser texto no vacío")

    asset_ids = set(mind_map.assets)
    for asset_id, asset in mind_map.assets.items():
        _register(asset_id, f"assets[{asset_id!r}]", seen)
        if asset.kind not in {"image", "attachment", "audio"}:
            raise IRValidationError(f"assets[{asset_id!r}].kind: tipo no válido")
        if not asset.path:
            raise IRValidationError(f"assets[{asset_id!r}].path: ruta vacía")
        if asset.size is not None and asset.size < 0:
            raise IRValidationError(f"assets[{asset_id!r}].size: no puede ser negativo")

    topic_ids: set[str] = set()
    _walk_topics(
        mind_map.sheet.root_topic,
        "sheet.root_topic",
        seen,
        topic_ids,
        asset_ids,
        set(),
        set(),
    )

    def validate_inline_targets(value: Any, path: str) -> None:
        if isinstance(value, dict):
            link = value.get("link")
            if isinstance(link, dict) and link.get("kind") == "topic":
                target = link.get("target")
                if target not in topic_ids:
                    raise IRValidationError(
                        f"{path}.link.target: tema enlazado inexistente {target!r}"
                    )
            for key, item in value.items():
                validate_inline_targets(item, f"{path}.{key}")
        elif isinstance(value, list):
            for index, item in enumerate(value):
                validate_inline_targets(item, f"{path}[{index}]")

    def validate_topic_references(topic: Topic, path: str) -> None:
        # Las referencias de estilo se resuelven en resolve_styles(), que puede
        # combinar catálogos embebidos y YAML externo. El parser no conoce aún
        # la configuración externa y no debe rechazar referencias válidas a ella.
        for index, link in enumerate(topic.links):
            if link.get("kind") == "topic" and link.get("target") not in topic_ids:
                raise IRValidationError(f"{path}.links[{index}].target: tema enlazado inexistente")
        for index, block in enumerate(topic.content):
            validate_inline_targets(block.data, f"{path}.content[{index}]")
        for note_index, note in enumerate(topic.annotations.notes):
            for block_index, block in enumerate(note.content):
                validate_inline_targets(
                    block.data,
                    f"{path}.annotations.notes[{note_index}].content[{block_index}]",
                )
        for index, child in enumerate(topic.children):
            validate_topic_references(child, f"{path}.children[{index}]")

    validate_topic_references(mind_map.sheet.root_topic, "sheet.root_topic")

    for collection_name, collection in (
        ("relationships", mind_map.sheet.relationships),
        ("boundaries", mind_map.sheet.boundaries),
        ("summaries", mind_map.sheet.summaries),
    ):
        for index, entity in enumerate(collection):
            _register(entity.id, f"sheet.{collection_name}[{index}].id", seen)

    for index, relationship in enumerate(mind_map.sheet.relationships):
        path = f"sheet.relationships[{index}]"
        if relationship.source_topic not in topic_ids:
            raise IRValidationError(f"{path}.source_topic: tema inexistente")
        if relationship.target_topic not in topic_ids:
            raise IRValidationError(f"{path}.target_topic: tema inexistente")
        if relationship.source_topic == relationship.target_topic:
            raise IRValidationError(f"{path}: una relación no puede conectar un tema consigo mismo")

    for collection_name, collection in (
        ("boundaries", mind_map.sheet.boundaries),
        ("summaries", mind_map.sheet.summaries),
    ):
        for index, entity in enumerate(collection):
            if not entity.topic_ids:
                raise IRValidationError(f"sheet.{collection_name}[{index}].topic_ids: lista vacía")
            if len(entity.topic_ids) != len(set(entity.topic_ids)):
                raise IRValidationError(
                    f"sheet.{collection_name}[{index}].topic_ids: IDs duplicados"
                )
            if any(topic_id not in topic_ids for topic_id in entity.topic_ids):
                raise IRValidationError(
                    f"sheet.{collection_name}[{index}].topic_ids: referencia a tema inexistente"
                )

    return mind_map
