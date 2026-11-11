"""Entidades canónicas del modelo intermedio IR 1.0.0.

Este módulo no depende del parser, de PyYAML ni de motores de exportación.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class StyleState:
    """Referencia, modificaciones locales y resultado de la cascada."""

    ref: str | None = None
    style_set: str | None = None
    overrides: dict[str, Any] = field(default_factory=dict)
    resolved: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "ref": self.ref,
            "style_set": self.style_set,
            "overrides": self.overrides,
            "resolved": self.resolved,
        }


@dataclass
class ContentBlock:
    """Bloque de contenido tipado; data contiene sus propiedades específicas."""

    type: str
    data: dict[str, Any] = field(default_factory=dict)
    id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        result = dict(self.data)
        if self.id is not None:
            result["id"] = self.id
        result["type"] = self.type
        return result


@dataclass
class Note:
    id: str
    content: list[ContentBlock] = field(default_factory=list)
    style: StyleState = field(default_factory=StyleState)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "content": [item.to_dict() for item in self.content],
            "style": self.style.to_dict(),
        }


@dataclass
class Label:
    id: str
    text: str

    def to_dict(self) -> dict[str, str]:
        return {"id": self.id, "text": self.text}


@dataclass
class Marker:
    id: str
    group: str
    value: str | int | float | bool

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "group": self.group, "value": self.value}


@dataclass
class Annotation:
    notes: list[Note] = field(default_factory=list)
    labels: list[Label] = field(default_factory=list)
    markers: list[Marker] = field(default_factory=list)
    task: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "notes": [item.to_dict() for item in self.notes],
            "labels": [item.to_dict() for item in self.labels],
            "markers": [item.to_dict() for item in self.markers],
            "task": self.task,
        }


@dataclass
class ResourceReferences:
    images: list[str] = field(default_factory=list)
    attachments: list[str] = field(default_factory=list)
    audio: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, list[str]]:
        return {
            "images": list(self.images),
            "attachments": list(self.attachments),
            "audio": list(self.audio),
        }


@dataclass
class Topic:
    id: str
    title: str
    kind: str = "attached"
    content: list[ContentBlock] = field(default_factory=list)
    annotations: Annotation = field(default_factory=Annotation)
    resources: ResourceReferences = field(default_factory=ResourceReferences)
    links: list[dict[str, Any]] = field(default_factory=list)
    style: StyleState = field(default_factory=StyleState)
    layout: dict[str, Any] = field(default_factory=dict)
    extensions: dict[str, Any] = field(default_factory=dict)
    source: dict[str, Any] = field(default_factory=dict)
    children: list[Topic] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "kind": self.kind,
            "content": [item.to_dict() for item in self.content],
            "annotations": self.annotations.to_dict(),
            "resources": self.resources.to_dict(),
            "links": [dict(item) for item in self.links],
            "style": self.style.to_dict(),
            "layout": dict(self.layout),
            "extensions": dict(self.extensions),
            "source": dict(self.source),
            "children": [item.to_dict() for item in self.children],
        }


@dataclass
class Asset:
    kind: str
    path: str
    name: str | None = None
    mime_type: str | None = None
    size: int | None = None
    sha256: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "path": self.path,
            "name": self.name,
            "mime_type": self.mime_type,
            "size": self.size,
            "sha256": self.sha256,
            "metadata": dict(self.metadata),
        }


@dataclass
class Relationship:
    id: str
    source_topic: str
    target_topic: str
    title: str | None = None
    style: StyleState = field(default_factory=StyleState)
    extensions: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "source_topic": self.source_topic,
            "target_topic": self.target_topic,
            "title": self.title,
            "style": self.style.to_dict(),
            "extensions": dict(self.extensions),
        }


@dataclass
class Boundary:
    id: str
    topic_ids: list[str]
    title: str | None = None
    style: StyleState = field(default_factory=StyleState)
    extensions: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "topic_ids": list(self.topic_ids),
            "title": self.title,
            "style": self.style.to_dict(),
            "extensions": dict(self.extensions),
        }


@dataclass
class Summary:
    id: str
    topic_ids: list[str]
    title: str | None = None
    style: StyleState = field(default_factory=StyleState)
    extensions: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "topic_ids": list(self.topic_ids),
            "title": self.title,
            "style": self.style.to_dict(),
            "extensions": dict(self.extensions),
        }


@dataclass
class SheetLayout:
    structure: str = "mind_map"
    direction: str | None = "balanced"
    properties: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "structure": self.structure,
            "direction": self.direction,
            **self.properties,
        }


@dataclass
class Sheet:
    id: str
    title: str
    root_topic: Topic
    metadata: dict[str, Any] = field(default_factory=dict)
    layout: SheetLayout = field(default_factory=SheetLayout)
    relationships: list[Relationship] = field(default_factory=list)
    boundaries: list[Boundary] = field(default_factory=list)
    summaries: list[Summary] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "metadata": dict(self.metadata),
            "layout": self.layout.to_dict(),
            "root_topic": self.root_topic.to_dict(),
            "relationships": [item.to_dict() for item in self.relationships],
            "boundaries": [item.to_dict() for item in self.boundaries],
            "summaries": [item.to_dict() for item in self.summaries],
        }


@dataclass
class MindMap:
    id: str
    title: str
    sheet: Sheet
    metadata: dict[str, Any] = field(default_factory=dict)
    styles: dict[str, dict[str, Any]] = field(default_factory=dict)
    style_sets: dict[str, dict[str, Any]] = field(default_factory=dict)
    assets: dict[str, Asset] = field(default_factory=dict)
    ir_version: str = "1.0.0"

    def to_dict(self) -> dict[str, Any]:
        """Serializa exclusivamente la estructura canónica IR 1.0.0."""
        return {
            "ir_version": self.ir_version,
            "id": self.id,
            "title": self.title,
            "metadata": dict(self.metadata),
            "styles": dict(self.styles),
            "style_sets": dict(self.style_sets),
            "assets": {key: value.to_dict() for key, value in self.assets.items()},
            "sheet": self.sheet.to_dict(),
        }
