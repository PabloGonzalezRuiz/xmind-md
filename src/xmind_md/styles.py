"""Carga y resolución de conjuntos de estilos YAML.

El módulo traduce nombres de conjunto y estilo a diccionarios neutrales.
El adaptador de salida será responsable de convertir esas propiedades al
vocabulario específico de XMind u otro destino.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .model import MindMap, Topic


class StyleError(ValueError):
    """Configuración de estilos inválida o referencia inexistente."""


def load_styles(path: str | Path) -> dict[str, Any]:
    """Carga el apartado style_sets de un archivo YAML."""
    # safe_load evita construir objetos Python arbitrarios desde el YAML.
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise StyleError("El archivo de estilos debe contener un objeto YAML")

    # La clave raíz permite añadir en el futuro otras secciones de configuración.
    style_sets = data.get("style_sets", {})
    if not isinstance(style_sets, dict):
        raise StyleError("La propiedad 'style_sets' debe ser un objeto YAML")
    return style_sets


def resolve_styles(mind_map: MindMap, style_sets: dict[str, Any]) -> MindMap:
    """Asocia a cada tema el estilo definido en el conjunto que le corresponda.

    El conjunto se hereda recursivamente desde el tema padre. Una directiva
    @conjunto en un tema reemplaza el conjunto heredado para esa rama.
    La primera versión no combina estilos ni implementa herencia de propiedades.
    """
    def visit(topic: Topic, inherited_set: str | None = None) -> None:
        # Un conjunto explícito tiene prioridad sobre el heredado del padre.
        set_name = topic.style_set or inherited_set

        if topic.style_ref:
            # No es posible resolver un estilo si no hay conjunto aplicable.
            if not set_name:
                raise StyleError(
                    f"El tema '{topic.title}' usa @estilo sin un @conjunto aplicable"
                )

            # Validar primero el conjunto y después el nombre de estilo.
            style_set = style_sets.get(set_name)
            if style_set is None:
                raise StyleError(f"Conjunto de estilos inexistente: {set_name}")
            if not isinstance(style_set, dict):
                raise StyleError(f"El conjunto '{set_name}' debe ser un objeto")
            styles = style_set.get("styles", {})
            if not isinstance(styles, dict):
                raise StyleError(f"La propiedad 'styles' de '{set_name}' debe ser un objeto")
            if topic.style_ref not in styles:
                raise StyleError(
                    f"Estilo '{topic.style_ref}' no definido en el conjunto '{set_name}'"
                )

            # Copiar el diccionario evita compartir accidentalmente el objeto YAML.
            topic.resolved_style = dict(styles[topic.style_ref])

        # Propagar el conjunto efectivo a los descendientes de este tema.
        for child in topic.children:
            visit(child, set_name)

    # Resolver cada raíz sin conjunto heredado; puede tener uno explícito.
    for root in mind_map.topics:
        visit(root)
    return mind_map
