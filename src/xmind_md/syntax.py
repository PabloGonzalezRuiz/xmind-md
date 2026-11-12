"""Árbol sintáctico temporal del parser Markdown.

Estas estructuras conservan la sintaxis reconocida y la procedencia. No son
entidades de dominio y no forman parte del contrato IR ni de la API pública.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TopicSyntax:
    """Encabezado analizado y sus construcciones sintácticas asociadas."""

    id: str
    title: str
    level: int
    properties: dict[str, Any] = field(default_factory=dict)
    source: dict[str, Any] = field(default_factory=dict)
    blocks: list[dict[str, Any]] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    children: list[TopicSyntax] = field(default_factory=list)


@dataclass
class DocumentSyntax:
    """Documento Markdown analizado, todavía no construido como modelo IR."""

    source_path: str
    metadata: dict[str, Any]
    root: TopicSyntax
    relationships: list[dict[str, Any]] = field(default_factory=list)
    boundaries: list[dict[str, Any]] = field(default_factory=list)
    summaries: list[dict[str, Any]] = field(default_factory=list)
