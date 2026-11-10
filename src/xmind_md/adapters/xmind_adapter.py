"""Adaptador inicial para generar libros XMind modernos (ZIP + JSON).

El adaptador traduce exclusivamente el IR; no interpreta Markdown ni modifica
el documento de entrada. Las características no soportadas se rechazan para
evitar pérdidas silenciosas.
"""
from __future__ import annotations

import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import NAMESPACE_URL, uuid5

from ..model import MindMap, Topic


MIMETYPE = "application/vnd.xmind.workbook"
DATA_STRUCTURE_VERSION = "3"
LAYOUT_ENGINE_VERSION = "5"

# PNG transparente de 1 x 1 píxel, utilizado como miniatura inicial.
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
    """Convierte IDs del IR en UUID estables aceptables por el formato XMind."""
    return str(uuid5(NAMESPACE_URL, f"xmind-md:{kind}:{map_id}:{source_id}"))


def _validate_supported_features(mind_map: MindMap) -> None:
    if len(mind_map.topics) != 1:
        raise XMindAdapterError("XMind requiere exactamente un tema raíz en esta versión.")

    if mind_map.assets:
        raise XMindAdapterError(
            "La exportación de recursos/imágenes aún no está implementada."
        )
    if mind_map.boundaries:
        raise XMindAdapterError("La exportación de boundaries aún no está implementada.")
    if mind_map.summaries:
        raise XMindAdapterError("La exportación de summaries aún no está implementada.")
    if mind_map.layout or mind_map.extensions:
        raise XMindAdapterError(
            "El layout o las extensiones del mapa aún no están soportados."
        )

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

        if topic.resources:
            raise XMindAdapterError(
                f"El tema '{topic.title}' contiene recursos aún no soportados."
            )
        if topic.layout or topic.extensions:
            raise XMindAdapterError(
                f"El tema '{topic.title}' contiene layout o extensiones no soportados."
            )
        unsupported_annotations = set(topic.annotations) - {"notes", "labels", "markers"}
        if unsupported_annotations:
            names = ", ".join(sorted(unsupported_annotations))
            raise XMindAdapterError(
                f"Anotaciones no soportadas en '{topic.title}': {names}."
            )
        if (topic.style_ref or topic.style_set) and not topic.resolved_style:
            raise XMindAdapterError(
                f"Los estilos de '{topic.title}' no están resueltos. "
                "Ejecuta resolve_styles antes de exportar."
            )
        for child in topic.children:
            visit(child)

    visit(mind_map.topics[0])

    for relationship in mind_map.relationships:
        source = relationship.get("source")
        target = relationship.get("target")
        if source not in topic_ids or target not in topic_ids:
            raise XMindAdapterError(
                "Una relationship referencia un tema que no existe en el IR."
            )


def _inline_text(runs: list[dict[str, Any]]) -> str:
    values: list[str] = []
    for run in runs:
        if "text" in run:
            values.append(str(run["text"]))
        elif run.get("type") == "link":
            values.append(f"[{run.get('text', '')}]({run.get('url', '')})")
        elif run.get("type") == "image":
            values.append(f"![{run.get('alt', '')}]({run.get('src', '')})")
    return "".join(values)


def _list_text(block: dict[str, Any], depth: int = 0) -> list[str]:
    lines: list[str] = []
    ordered = bool(block.get("ordered"))
    for index, item in enumerate(block.get("items", []), start=1):
        prefix = f"{index}. " if ordered else "- "
        content = item.get("content", [])
        text = " ".join(
            _inline_text(part.get("runs", []))
            for part in content
            if part.get("type") == "paragraph"
        )
        lines.append(("  " * depth) + prefix + text)
        for child in item.get("children", []):
            lines.extend(_list_text({"items": [child]}, depth + 1))
    return lines


def _content_as_note(topic: Topic) -> str:
    """Aplana bloques IR a texto legible para el campo plain de las notas."""
    parts: list[str] = []
    for block in topic.content_blocks:
        kind = block.get("type")
        if kind == "paragraph":
            parts.append(_inline_text(block.get("runs", [])))
        elif kind == "list":
            parts.extend(_list_text(block))
        elif kind == "code":
            language = block.get("language") or ""
            parts.append(f"\u0060\u0060\u0060{language}\n{block.get('text', '')}\n\u0060\u0060\u0060")
        elif kind == "quote":
            quoted = block.get("content", [])
            for paragraph in quoted:
                if paragraph.get("type") == "paragraph":
                    parts.append("> " + _inline_text(paragraph.get("runs", [])))
        elif kind == "table":
            header = [_inline_text(cell) for cell in block.get("header", [])]
            rows = block.get("rows", [])
            if header:
                parts.append(" | ".join(header))
                parts.append(" | ".join("---" for _ in header))
            parts.extend(" | ".join(_inline_text(cell) for cell in row) for row in rows)
        elif kind == "divider":
            parts.append("---")
        elif kind == "image":
            parts.append(f"![{block.get('alt', '')}]({block.get('src', '')})")
        else:
            raise XMindAdapterError(
                f"Bloque de contenido no reconocido en '{topic.title}': {kind!r}."
            )

    # El campo legacy se conserva por compatibilidad con el parser inicial.
    if not topic.content_blocks and topic.content:
        parts.extend(topic.content)

    notes = topic.annotations.get("notes", [])
    if isinstance(notes, str):
        notes = [notes]
    if notes:
        parts.extend(str(note) for note in notes)

    return "\n\n".join(part for part in parts if part).strip()


def _style_properties(style: dict[str, Any], topic_title: str) -> dict[str, Any]:
    """Traduce el subconjunto de propiedades neutrales implementado."""
    properties: dict[str, Any] = {}

    def visit(value: Any, prefix: str = "") -> None:
        if not isinstance(value, dict):
            raise XMindAdapterError(
                f"El estilo de '{topic_title}' debe usar objetos agrupados por propiedad."
            )
        for key, item in value.items():
            path = f"{prefix}.{key}" if prefix else key
            if isinstance(item, dict):
                visit(item, path)
                continue
            target = _STYLE_KEYS.get(path)
            if target is None:
                raise XMindAdapterError(
                    f"Propiedad de estilo no soportada en '{topic_title}': {path}."
                )
            if item is None:
                raise XMindAdapterError(
                    f"El reinicio null de estilo no está soportado todavía: {path}."
                )
            if path == "text.bold":
                target = "fo:font-weight"
                item = "bold" if item else "normal"
            elif path == "text.italic":
                target = "fo:font-style"
                item = "italic" if item else "normal"
            elif path == "shape" and not isinstance(item, str):
                raise XMindAdapterError("shape debe ser texto.")
            if isinstance(item, bool):
                raise XMindAdapterError(
                    f"El valor de estilo '{path}' debe ser texto o número, no booleano."
                )
            # El esquema JSON oficial declara las propiedades de estilo como texto.
            properties[target] = str(item)

    visit(style)
    return properties


def _topic_to_json(
    topic: Topic,
    map_id: str,
    id_map: dict[str, str],
) -> dict[str, Any]:
    data: dict[str, Any] = {
        "id": id_map[topic.id],
        "class": "topic",
        "title": topic.title,
    }

    labels = topic.annotations.get("labels", [])
    if labels:
        data["labels"] = list(labels)

    markers = topic.annotations.get("markers", [])
    if markers:
        marker_data = []
        for marker in markers:
            group = str(marker["group"]).strip()
            value = str(marker["value"]).strip()
            if not group or not value:
                raise XMindAdapterError(
                    f"Marcador vacío en el tema '{topic.title}'."
                )
            marker_id = value if value.startswith(group + "-") else f"{group}-{value}"
            marker_data.append({"markerId": marker_id})
        data["markers"] = marker_data

    note = _content_as_note(topic)
    if note:
        data["notes"] = {"plain": {"content": note}}

    if topic.links:
        if len(topic.links) != 1:
            raise XMindAdapterError(
                f"El tema '{topic.title}' tiene varios enlaces; XMind admite un href "
                "en el perfil inicial."
            )
        link = topic.links[0]
        href = link.get("url") or link.get("href")
        if not isinstance(href, str) or not href:
            raise XMindAdapterError(
                f"El enlace del tema '{topic.title}' no contiene url/href."
            )
        data["href"] = href

    style = topic.resolved_style or topic.style_overrides
    if style:
        properties = _style_properties(style, topic.title)
        if properties:
            data["style"] = {
                "id": _xmind_id("style", map_id, topic.id),
                "properties": properties,
            }

    if topic.children:
        data["children"] = {
            "attached": [
                _topic_to_json(child, map_id, id_map)
                for child in topic.children
            ]
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

    root = mind_map.topics[0]
    index(root)

    relationships = []
    for relationship in mind_map.relationships:
        item: dict[str, Any] = {
            "id": _xmind_id("relationship", map_id, str(relationship["id"])),
            "class": "relationship",
            "title": relationship.get("title", ""),
            "end1Id": id_map[relationship["source"]],
            "end2Id": id_map[relationship["target"]],
        }
        if relationship.get("style"):
            style_props = _style_properties(
                relationship["style"], f"relationship {relationship['id']}"
            )
            if style_props:
                item["style"] = {
                    "id": _xmind_id("relationship-style", map_id, str(relationship["id"])),
                    "properties": style_props,
                }
        relationships.append(item)

    sheet_id = _xmind_id("sheet", map_id, mind_map.id or mind_map.title)
    return [{
        "id": sheet_id,
        "class": "sheet",
        "title": mind_map.metadata.get("sheet_title", mind_map.title),
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
        archive.writestr(
            "content.json",
            json.dumps(content, ensure_ascii=False, indent=2),
        )
        archive.writestr(
            "metadata.json",
            json.dumps(metadata, ensure_ascii=False, indent=2),
        )
        archive.writestr(
            "manifest.json",
            json.dumps(manifest, ensure_ascii=False, indent=2),
        )
        archive.writestr("Thumbnails/thumbnail.png", THUMBNAIL_PNG)

    return path
