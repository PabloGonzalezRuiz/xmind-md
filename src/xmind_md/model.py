"""Modelo intermedio neutral para mapas mentales XMind MD.

Las clases describen contenido y estructura sin importar Markdown ni motores
de exportación. Los campos legacy se conservan durante la transición.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class Topic:
    """Tema jerárquico del mapa."""

    title: str
    level: int
    id: str = ""
    kind: str = "attached"
    children: list["Topic"] = field(default_factory=list)
    # Compatibilidad temporal con consumidores de la primera versión.
    content: list[str] = field(default_factory=list)
    content_blocks: list[dict[str, Any]] = field(default_factory=list)
    style_set: str | None = None
    style_ref: str | None = None
    style_overrides: dict[str, Any] = field(default_factory=dict)
    resolved_style: dict[str, Any] = field(default_factory=dict)
    annotations: dict[str, Any] = field(default_factory=dict)
    resources: list[dict[str, Any]] = field(default_factory=list)
    links: list[dict[str, Any]] = field(default_factory=list)
    layout: dict[str, Any] = field(default_factory=dict)
    extensions: dict[str, Any] = field(default_factory=dict)
    source: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Devuelve una representación recursiva serializable a JSON."""
        return asdict(self)


@dataclass
class MindMap:
    """Documento de mapa mental; una única raíz equivale a una hoja."""

    title: str
    topics: list[Topic] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    id: str = ""
    styles: dict[str, Any] = field(default_factory=dict)
    style_sets: dict[str, Any] = field(default_factory=dict)
    assets: list[dict[str, Any]] = field(default_factory=list)
    relationships: list[dict[str, Any]] = field(default_factory=list)
    boundaries: list[dict[str, Any]] = field(default_factory=list)
    summaries: list[dict[str, Any]] = field(default_factory=list)
    layout: dict[str, Any] = field(default_factory=dict)
    extensions: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convierte el mapa completo a tipos JSON estándar."""
        return asdict(self)
