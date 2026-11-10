"""Modelo intermedio neutral para representar mapas mentales."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class Topic:
    """Nodo del mapa mental, independiente del motor de exportación."""

    title: str
    level: int
    children: list["Topic"] = field(default_factory=list)
    content: list[str] = field(default_factory=list)
    style_set: str | None = None
    style_ref: str | None = None
    resolved_style: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class MindMap:
    """Documento completo de mapa mental."""

    title: str
    topics: list[Topic] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
