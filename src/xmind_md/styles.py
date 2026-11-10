"""Carga y resolución de conjuntos de estilos YAML."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .model import MindMap, Topic


class StyleError(ValueError):
    """Configuración de estilos inválida o referencia inexistente."""


def load_styles(path: str | Path) -> dict[str, Any]:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise StyleError("El archivo de estilos debe contener un objeto YAML")
    return data.get("style_sets", {})


def resolve_styles(mind_map: MindMap, style_sets: dict[str, Any]) -> MindMap:
    """Asocia a cada tema el estilo del rol definido en su conjunto.

    La primera versión no implementa todavía herencia ni combinaciones de
    estilos: cada tema referencia explícitamente un conjunto y un estilo.
    """
    def visit(topic: Topic, inherited_set: str | None = None) -> None:
        set_name = topic.style_set or inherited_set
        if topic.style_ref:
            if not set_name:
                raise StyleError(
                    f"El tema '{topic.title}' usa @estilo sin un @conjunto aplicable"
                )
            style_set = style_sets.get(set_name)
            if style_set is None:
                raise StyleError(f"Conjunto de estilos inexistente: {set_name}")
            styles = style_set.get("styles", {})
            if topic.style_ref not in styles:
                raise StyleError(
                    f"Estilo '{topic.style_ref}' no definido en el conjunto '{set_name}'"
                )
            topic.resolved_style = dict(styles[topic.style_ref])
        for child in topic.children:
            visit(child, set_name)

    for root in mind_map.topics:
        visit(root)
    return mind_map
