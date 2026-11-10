"""Interfaz de línea de comandos para XMind MD."""

from __future__ import annotations

import argparse
import sys

from .adapters.json_adapter import write_json
from .parser import MarkdownParseError, parse_file
from .styles import StyleError, load_styles, resolve_styles


def build_parser() -> argparse.ArgumentParser:
    """Construye y devuelve la definición de argumentos de la CLI."""
    # argparse genera automáticamente la ayuda y valida los argumentos requeridos.
    parser = argparse.ArgumentParser(
        prog="xmind-md",
        description="Analiza Markdown enriquecido y genera el modelo intermedio JSON.",
    )
    parser.add_argument("input", help="Archivo Markdown de entrada")
    parser.add_argument("--styles", help="Archivo YAML con conjuntos de estilos")
    parser.add_argument("--output", required=True, help="Archivo JSON de salida")
    return parser


def main() -> int:
    """Ejecuta el flujo completo y devuelve un código de salida convencional."""
    args = build_parser().parse_args()

    try:
        # 1. Leer el documento y construir el árbol neutral de temas.
        mind_map = parse_file(args.input)

        # 2. Resolver estilos solo si se ha indicado un archivo de configuración.
        if args.styles:
            resolve_styles(mind_map, load_styles(args.styles))

        # 3. Escribir el modelo intermedio; todavía no se genera un .xmind.
        write_json(mind_map, args.output)
    except (OSError, MarkdownParseError, StyleError) as exc:
        # Los errores controlados se muestran por stderr y producen código 2.
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    # Informar del destino únicamente después de que la escritura haya terminado.
    print(f"Modelo JSON generado: {args.output}")
    return 0


if __name__ == "__main__":
    # Permitir también la ejecución directa de este archivo durante el desarrollo.
    raise SystemExit(main())
