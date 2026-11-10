"""Modelo intermedio neutral para representar mapas mentales.

Las clases de este módulo describen datos, no decisiones de exportación.
No deben importar XMind, xmindpy ni ninguna otra biblioteca de salida.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class Topic:
    """Representa un tema y sus relaciones jerárquicas.

    Attributes:
        title: Texto principal visible del tema.
        level: Nivel del encabezado Markdown que originó el tema (1 a 6).
        children: Temas subordinados, en el mismo orden que en el documento.
        content: Líneas de texto asociadas al tema en la gramática actual.
        style_set: Nombre del conjunto de estilos asociado explícitamente.
        style_ref: Nombre del estilo solicitado dentro del conjunto aplicable.
        resolved_style: Propiedades neutrales resueltas desde el YAML.
    """

    title: str
    level: int
    # La lista mantiene el orden de aparición de los temas hijos.
    children: list["Topic"] = field(default_factory=list)
    # El contenido se conserva como texto; todavía no se transforma en nodos.
    content: list[str] = field(default_factory=list)
    # Las referencias se guardan separadas de las propiedades ya resueltas.
    style_set: str | None = None
    style_ref: str | None = None
    resolved_style: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Devuelve una representación recursiva serializable a JSON."""
        # dataclasses.asdict convierte también los Topic contenidos en children.
        return asdict(self)


@dataclass
class MindMap:
    """Representa el documento completo que contiene el árbol de temas."""

    title: str
    # Puede haber varios temas raíz si el Markdown contiene varios H1.
    topics: list[Topic] = field(default_factory=list)
    # Reservado para metadatos generales del documento y futuras extensiones.
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convierte el mapa completo en diccionarios y listas estándar."""
        # La conversión mantiene la estructura del modelo sin conocer el destino.
        return asdict(self)
