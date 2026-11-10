"""Parser de la gramática inicial de XMind MD.

En esta fase se reconocen encabezados Markdown y dos directivas:
@conjunto(NOMBRE) y @estilo(NOMBRE). El texto restante se conserva
como contenido del tema activo. Este parser no pretende implementar todo
CommonMark ni convertir listas en nodos.
"""

from __future__ import annotations

import re
from pathlib import Path

from .model import MindMap, Topic

# Solo se aceptan estas dos directivas, con el argumento entre paréntesis.
_METADATA_RE = re.compile(r"^@(conjunto|estilo)\(([^()]*)\)\s*$")


class MarkdownParseError(ValueError):
    """Error de sintaxis o de estructura en un documento Markdown enriquecido."""


def parse_markdown(text: str) -> MindMap:
    """Convierte encabezados Markdown y metadatos en un árbol de temas.

    Las directivas se acumulan hasta el siguiente encabezado. El nivel del
    encabezado determina la jerarquía: al encontrar un nivel igual o superior
    se cierran los temas anteriores de la pila.
    """
    # Los temas raíz se mantienen separados de la pila de ancestros.
    roots: list[Topic] = []
    # La pila contiene el camino desde la raíz hasta el tema actual.
    stack: list[Topic] = []
    # Las directivas pendientes se aplican al siguiente encabezado encontrado.
    pending: dict[str, str] = {}
    document_title = "Mapa sin título"

    # Enumerar desde 1 permite ofrecer errores con números de línea útiles.
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.rstrip()
        stripped = line.strip()

        # Las líneas vacías no alteran la pila ni las directivas pendientes.
        if not stripped:
            continue

        # Primero se comprueba si la línea contiene una directiva reconocida.
        metadata_match = _METADATA_RE.fullmatch(stripped)
        if metadata_match:
            key, value = metadata_match.groups()
            if not value.strip():
                raise MarkdownParseError(
                    f"Metadato vacío en la línea {line_number}: {stripped}"
                )
            # Traducir los nombres de directiva a campos del modelo intermedio.
            pending["style_set" if key == "conjunto" else "style_ref"] = value.strip()
            continue

        # Los encabezados son los únicos elementos que crean nodos en esta versión.
        heading_match = re.match(r"^(#{1,6})\s+(.+?)\s*#*\s*$", line)
        if heading_match:
            level = len(heading_match.group(1))
            title = heading_match.group(2).strip()
            if not title:
                raise MarkdownParseError(f"Encabezado vacío en la línea {line_number}")

            # Consumir las directivas pendientes al crear el nuevo tema.
            topic = Topic(
                title=title,
                level=level,
                style_set=pending.pop("style_set", None),
                style_ref=pending.pop("style_ref", None),
            )
            # Si queda alguna clave, se trata de una directiva sin destino válido.
            if pending:
                raise MarkdownParseError(
                    f"Metadatos sin destino antes de la línea {line_number}: {pending}"
                )

            # Retirar de la pila los temas del mismo nivel o de niveles inferiores.
            while stack and stack[-1].level >= level:
                stack.pop()

            # El último tema restante es el padre; si no existe, el tema es raíz.
            if stack:
                stack[-1].children.append(topic)
            else:
                roots.append(topic)
                # El primer encabezado raíz se utiliza como título del documento.
                if len(roots) == 1:
                    document_title = title

            # El tema recién creado pasa a ser el posible padre de los siguientes.
            stack.append(topic)
            continue

        # Una línea que empieza por @ y no coincide con la gramática es un error.
        if stripped.startswith("@"):
            raise MarkdownParseError(
                f"Metadato no reconocido en la línea {line_number}: {stripped}"
            )

        # No se permite contenido sin un tema al que asociarlo.
        if not stack:
            raise MarkdownParseError(
                f"Contenido antes del primer encabezado (línea {line_number})"
            )

        # Conservar texto y listas literalmente, sin convertirlos aún en subtemas.
        stack[-1].content.append(stripped)

    # Detectar directivas que nunca llegaron a asociarse a un encabezado.
    if pending:
        raise MarkdownParseError(f"Metadatos al final del documento sin encabezado: {pending}")
    if not roots:
        raise MarkdownParseError("El documento no contiene ningún encabezado Markdown")

    # Devolver el árbol completo sin acoplarlo a ningún formato de exportación.
    return MindMap(title=document_title, topics=roots)


def parse_file(path: str | Path) -> MindMap:
    """Lee un archivo UTF-8 y delega su interpretación al parser de cadenas."""
    # Separar la lectura del análisis facilita probar el parser con cadenas directas.
    return parse_markdown(Path(path).read_text(encoding="utf-8"))
