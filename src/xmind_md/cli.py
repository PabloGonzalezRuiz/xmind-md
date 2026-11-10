"""Interfaz de línea de comandos para XMind MD."""

from __future__ import annotations

import argparse
import sys

from .adapters.json_adapter import write_json
from .ir_parser import parse_file_ir
from .styles import StyleError, load_styles, resolve_styles


def build_parser() -> argparse.ArgumentParser:
    """Construye y devuelve la definición de argumentos de la CLI."""
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
        mind_map = parse_file_ir(args.input)
        if args.styles:
            resolve_styles(mind_map, load_styles(args.styles))
        write_json(mind_map, args.output)
    except (OSError, ValueError, StyleError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    print(f"Modelo JSON generado: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
