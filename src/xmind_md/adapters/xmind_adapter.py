"""Adaptador IR 1.0.0 para generar libros XMind modernos (ZIP + JSON).

El adaptador solo consume entidades canónicas. No interpreta Markdown, no
resuelve estilos y rechaza explícitamente las capacidades que aún no exporta.
"""
from __future__ import annotations

import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import NAMESPACE_URL, uuid5

from ..ir import MindMap, Topic


MIMETYPE = "application/vnd.xmind.workbook"
DATA_STRUCTURE_VERSION = "3"
LAYOUT_ENGINE_VERSION = "5"
THUMBNAIL_PNG = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4"
    "890000000d49444154789c6300010000000500010d0a2db40000000049454e44"
    "ae426082"
)


class XMindAdapterError(ValueError):
    """El IR contiene datos que el adaptador inicial no puede representar."""


_STYLE_KEYS = {
    "shape": "shape-class",
    "text.font_family": "fo:font-family",
    "text.font_size": "fo:font-size",
    "text.font_weight": "fo:font-weight",
    "text.bold": "fo:font-weight",
    "text.italic": "fo:font-style",
    "text.color": "fo:color",
    "text.decoration": "fo:text-decoration",
    "background.color": "svg:fill",
    "background.fill": "svg:fill",
    "border.color": "line-color",
    "border.width": "line-width",
    "border.pattern": "line-pattern",
}


def _xmind_id(kind: str, map_id: str, source_id: str) -> str:
    return str(uuid5(NAMESPACE_URL, f"xmind-md:{kind}:{map_id}:{source_id}"))


def _validate_style_state(state: Any, label: str) -> None:
    if (state.ref or state.style_set or state.overrides) and not state.resolved:
        raise XMindAdapterError(
            f"Los estilos de {label} no están resueltos. "
            "Ejecuta resolve_styles antes de exportar."
        )


def _validate_supported_features(mind_map: MindMap) -> None:
    if not isinstance(mind_map, MindMap):
        raise TypeError("El adaptador XMind requiere un MindMap IR 1.0.0.")
    if mind_map.assets:
        raise XMindAdapterError("La exportación de recursos/imágenes aún no está implementada.")
    unsupported_metadata = set(mind_map.metadata) - {
        "author", "style_set", "style_defaults", "source_file"
    }
    if unsupported_metadata:
        names = ", ".join(sorted(unsupported_metadata))
        raise XMindAdapterError(f"Metadatos del mapa no soportados: {names}.")

    sheet = mind_map.sheet
    if sheet.boundaries:
        raise XMindAdapterError("La exportación de boundaries aún no está implementada.")
    if sheet.summaries:
        raise XMindAdapterError("La exportación de summaries aún no está implementada.")
    if (
        sheet.layout.structure != "mind_map"
        or sheet.layout.direction != "balanced"
        or sheet.layout.properties
    ):
        raise XMindAdapterError("El layout de hoja solicitado aún no está soportado.")
    if sheet.metadata:
        raise XMindAdapterError("Los metadatos específicos de hoja aún no están soportados.")

    topic_ids: set[str] = set()

    def visit(topic: Topic) -> None:
        if topic.kind != "attached":
            raise XMindAdapterError(
                f"El tema '{topic.title}' tiene kind='{topic.kind}'; "
                "solo se admiten temas jerárquicos attached."
            )
        if not topic.id:
            raise XMindAdapterError(f"El tema '{topic.title}' no tiene ID en el IR.")
        if topic.id in topic_ids:
            raise XMindAdapterError(f"ID de tema duplicado: {topic.id}")
        topic_ids.add(topic.id)

        if topic.resources.images or topic.resources.attachments or topic.resources.audio:
            raise XMindAdapterError(
                f"El tema '{topic.title}' contiene recursos aún no soportados."
            )
        if topic.layout or topic.extensions:
            raise XMindAdapterError(
                f"El tema '{topic.title}' contiene layout o extensiones no soportados."
            )
        if topic.annotations.task is not None:
            raise XMindAdapterError(
                f"La anotación task de '{topic.title}' aún no está soportada."
            )
        _validate_style_state(topic.style, f"'{topic.title}'")
        for index, note in enumerate(topic.annotations.notes):
            _validate_style_state(note.style, f"la nota {index} de '{topic.title}'")
        for block in topic.content:
            if block.type in {"image", "raw"}:
                raise XMindAdapterError(
                    f"El bloque '{block.type}' de '{topic.title}' aún no está soportado."
                )
        for child in topic.children:
            visit(child)

    visit(sheet.root_topic)

    for relationship in sheet.relationships:
        if (
            relationship.source_topic not in topic_ids
            or relationship.target_topic not in topic_ids
        ):
            raise XMindAdapterError("Una relationship referencia un tema que no existe en el IR.")
        if relationship.extensions:
            raise XMindAdapterError(
                f"La relationship '{relationship.id}' contiene extensiones no soportadas."
            )
        _validate_style_state(relationship.style, f"la relación '{relationship.id}'")


def _inline_text(runs: list[dict[str, Any]]) -> str:
    values: list[str] = []
    for run in runs:
        if "text" in run:
            values.append(str(run["text"]))
        elif "link" in run:
            values.append(str(run.get("text", "")))
        elif "image_source" in run:
            raise XMindAdapterError("Las imágenes en línea aún no están soportadas.")
    return "".join(values)


def _list_text(block: dict[str, Any], depth: int = 0) -> list[str]:
    lines: list[str] = []
    ordered = bool(block.get("ordered"))
    for index, item in enumerate(block.get("items", []), start=1):
        prefix = f"{index}. " if ordered else "- "
        text = " ".join(
            _block_text(part)
            for part in item.get("content", [])
            if part.get("type") == "paragraph"
        )
        lines.append(("  " * depth) + prefix + text)
        for child in item.get("children", []):
            lines.extend(_list_text({"items": [child]}, depth + 1))
    return lines


def _cell_text(cell: dict[str, Any]) -> str:
    return "\n".join(_block_text(block) for block in cell.get("content", []))


def _block_text(block: dict[str, Any]) -> str:
    kind = block.get("type")
    if kind == "paragraph":
        return (
            _inline_text(block.get("runs", []))
            if "runs" in block
            else str(block.get("text", ""))
        )
    if kind == "code":
        fence = chr(96) * 3
        return f"{fence}{block.get('language') or ''}\n{block.get('code', '')}\n{fence}"
    if kind == "quote":
        return "\n".join("> " + line for line in str(block.get("text", "")).splitlines())
    if kind == "divider":
        return "---"
    if kind == "list":
        return "\n".join(_list_text(block))
    if kind == "table":
        lines = []
        for row in block.get("rows", []):
            cells = [_cell_text(cell) for cell in row.get("cells", [])]
            lines.append(" | ".join(cells))
            if row.get("header"):
                lines.append(" | ".join("---" for _ in cells))
        return "\n".join(lines)
    if kind in {"image", "raw"}:
        raise XMindAdapterError(f"El bloque de contenido '{kind}' aún no está soportado.")
    raise XMindAdapterError(f"Bloque de contenido no reconocido: {kind!r}.")


def _content_as_note(topic: Topic) -> str:
    parts = [_block_text(block.to_dict()) for block in topic.content]
    for note in topic.annotations.notes:
        if note.style.resolved:
            raise XMindAdapterError(
                f"El estilo visual de las notas de '{topic.title}' aún no está soportado."
            )
        parts.extend(_block_text(block.to_dict()) for block in note.content)
    return "\n\n".join(part for part in parts if part).strip()


def _style_properties(style: dict[str, Any], label: str) -> dict[str, Any]:
    properties: dict[str, Any] = {}

    def visit(value: Any, prefix: str = "") -> None:
        if not isinstance(value, dict):
            raise XMindAdapterError(f"El estilo de {label} debe usar objetos agrupados por propiedad.")
        for key, item in value.items():
            path = f"{prefix}.{key}" if prefix else key
            if isinstance(item, dict):
                visit(item, path)
                continue
            target = _STYLE_KEYS.get(path)
            if target is None:
                raise XMindAdapterError(f"Propiedad de estilo no soportada en {label}: {path}.")
            if item is None:
                raise XMindAdapterError(f"El reinicio null de estilo no está soportado todavía: {path}.")
            if path == "text.bold":
                item = "bold" if item else "normal"
            elif path == "text.italic":
                item = "italic" if item else "normal"
            elif path == "shape" and not isinstance(item, str):
                raise XMindAdapterError("shape debe ser texto.")
            if isinstance(item, bool):
                raise XMindAdapterError(
                    f"El valor de estilo '{path}' debe ser texto o número, no booleano."
                )
            properties[target] = str(item)

    visit(style)
    return properties


def _topic_to_json(topic: Topic, map_id: str, id_map: dict[str, str]) -> dict[str, Any]:
    data: dict[str, Any] = {
        "id": id_map[topic.id],
        "class": "topic",
        "title": topic.title,
    }
    if topic.annotations.labels:
        data["labels"] = [label.text for label in topic.annotations.labels]
    if topic.annotations.markers:
        marker_data = []
        for marker in topic.annotations.markers:
            group = str(marker.group).strip()
            value = str(marker.value).strip()
            if not group or not value:
                raise XMindAdapterError(f"Marcador vacío en el tema '{topic.title}'.")
            marker_id = value if value.startswith(group + "-") else f"{group}-{value}"
            marker_data.append({"markerId": marker_id})
        data["markers"] = marker_data

    note = _content_as_note(topic)
    if note:
        data["notes"] = {"plain": {"content": note}}

    if topic.links:
        if len(topic.links) != 1:
            raise XMindAdapterError(
                f"El tema '{topic.title}' tiene varios enlaces; "
                "XMind admite un href en el perfil inicial."
            )
        link = topic.links[0]
        href = link.get("target")
        if link.get("kind") != "web" or not isinstance(href, str) or not href:
            raise XMindAdapterError(
                f"El enlace del tema '{topic.title}' debe ser de tipo web y tener target."
            )
        data["href"] = href

    if topic.style.resolved:
        properties = _style_properties(topic.style.resolved, f"'{topic.title}'")
        if properties:
            data["style"] = {
                "id": _xmind_id("style", map_id, topic.id),
                "properties": properties,
            }
    if topic.children:
        data["children"] = {
            "attached": [_topic_to_json(child, map_id, id_map) for child in topic.children]
        }
    return data


def build_xmind_content(mind_map: MindMap) -> list[dict[str, Any]]:
    """Construye el array content.json sin escribir ningún archivo."""
    _validate_supported_features(mind_map)
    map_id = mind_map.id or mind_map.title
    id_map: dict[str, str] = {}

    def index(topic: Topic) -> None:
        id_map[topic.id] = _xmind_id("topic", map_id, topic.id)
        for child in topic.children:
            index(child)

    root = mind_map.sheet.root_topic
    index(root)
    relationships = []
    for relationship in mind_map.sheet.relationships:
        item: dict[str, Any] = {
            "id": _xmind_id("relationship", map_id, relationship.id),
            "class": "relationship",
            "title": relationship.title or "",
            "end1Id": id_map[relationship.source_topic],
            "end2Id": id_map[relationship.target_topic],
            "controlPoints": {
                "0": {"x": 0, "y": 0},
                "1": {"x": 0, "y": 0},
            },
        }
        if relationship.style.resolved:
            properties = _style_properties(
                relationship.style.resolved, f"relationship {relationship.id}"
            )
            if properties:
                item["style"] = {
                    "id": _xmind_id("relationship-style", map_id, relationship.id),
                    "properties": properties,
                }
        relationships.append(item)

    sheet_id = _xmind_id("sheet", map_id, mind_map.sheet.id)
    return [{
        "id": sheet_id,
        "class": "sheet",
        "title": mind_map.sheet.title,
        "rootTopic": _topic_to_json(root, map_id, id_map),
        "relationships": relationships,
    }]


def write_xmind(mind_map: MindMap, destination: str | Path) -> Path:
    """Escribe un archivo XMind moderno ZIP + JSON en destination."""
    content = build_xmind_content(mind_map)
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    metadata = {
        "modifier": mind_map.metadata.get("author", ""),
        "creator": {"name": "XMind MD"},
        "dataStructureVersion": DATA_STRUCTURE_VERSION,
        "layoutEngineVersion": LAYOUT_ENGINE_VERSION,
        "activeSheetId": content[0]["id"],
        "created": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
    }
    manifest = {
        "file-entries": {
            "content.json": {"media-type": "application/json"},
            "metadata.json": {"media-type": "application/json"},
            "Thumbnails/thumbnail.png": {"media-type": "image/png"},
        }
    }
    with zipfile.ZipFile(path, "w") as archive:
        mimetype_info = zipfile.ZipInfo("mimetype")
        mimetype_info.compress_type = zipfile.ZIP_STORED
        archive.writestr(mimetype_info, MIMETYPE)
        archive.writestr("content.json", json.dumps(content, ensure_ascii=False, indent=2))
        archive.writestr("metadata.json", json.dumps(metadata, ensure_ascii=False, indent=2))
        archive.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
        archive.writestr("Thumbnails/thumbnail.png", THUMBNAIL_PNG)
    return path
