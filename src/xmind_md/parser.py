"""Parser deliberadamente pequeño para la primera gramática de XMind MD."""

from __future__ import annotations

import re
from pathlib import Path

from .model import MindMap, Topic

_METADATA_RE = re.compile(r"^@(conjunto|estilo)\(([^()]*)\)\s*$")


class MarkdownParseError(ValueError):
    """Error de sintaxis en el documento Markdown enriquecido."""


def parse_markdown(text: str) -> MindMap:
    """Convierte encabezados Markdown y metadatos en un árbol de temas.

    Los metadatos se aplican al siguiente encabezado. El contenido que no sea
    encabezado se conserva en el tema activo como líneas de texto.
    """
    roots: list[Topic] = []
    stack: list[Topic] = []
    pending: dict[str, str] = {}
    document_title = "Mapa sin título"

    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.rstrip()
        stripped = line.strip()

        if not stripped:
            continue

        metadata_match = _METADATA_RE.fullmatch(stripped)
        if metadata_match:
            key, value = metadata_match.groups()
            if not value.strip():
                raise MarkdownParseError(
                    f"Metadato vacío en la línea {line_number}: {stripped}"
                )
            pending["style_set" if key == "conjunto" else "style_ref"] = value.strip()
            continue

        heading_match = re.match(r"^(#{1,6})\s+(.+?)\s*#*\s*$", line)
        if heading_match:
            level = len(heading_match.group(1))
            title = heading_match.group(2).strip()
            if not title:
                raise MarkdownParseError(f"Encabezado vacío en la línea {line_number}")

            topic = Topic(
                title=title,
                level=level,
                style_set=pending.pop("style_set", None),
                style_ref=pending.pop("style_ref", None),
            )
            if pending:
                raise MarkdownParseError(
                    f"Metadatos sin destino antes de la línea {line_number}: {pending}"
                )

            while stack and stack[-1].level >= level:
                stack.pop()

            if stack:
                stack[-1].children.append(topic)
            else:
                roots.append(topic)
                if len(roots) == 1:
                    document_title = title
            stack.append(topic)
            continue

        if stripped.startswith("@"):
            raise MarkdownParseError(
                f"Metadato no reconocido en la línea {line_number}: {stripped}"
            )

        if not stack:
            raise MarkdownParseError(
                f"Contenido antes del primer encabezado (línea {line_number})"
            )
        stack[-1].content.append(stripped)

    if pending:
        raise MarkdownParseError(f"Metadatos al final del documento sin encabezado: {pending}")
    if not roots:
        raise MarkdownParseError("El documento no contiene ningún encabezado Markdown")

    return MindMap(title=document_title, topics=roots)


def parse_file(path: str | Path) -> MindMap:
    """Lee y analiza un archivo Markdown UTF-8."""
    return parse_markdown(Path(path).read_text(encoding="utf-8"))
