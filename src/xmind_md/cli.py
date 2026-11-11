"""Interfaz de línea de comandos para XMind MD."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .adapters.json_adapter import write_json
from .adapters.xmind_adapter import write_xmind
from .ir_parser import parse_file_ir
from .styles import StyleError, load_styles, resolve_styles
from . import __version__


def build_parser() -> argparse.ArgumentParser:
    """Construye y devuelve la definición de argumentos de la CLI."""
    parser = argparse.ArgumentParser(
        prog="xmind-md",
        description="Convierte Markdown enriquecido a JSON IR o a un libro XMind.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument("input", help="Archivo Markdown de entrada")
    parser.add_argument("--styles", help="Archivo YAML con conjuntos de estilos")
    parser.add_argument(
        "--output",
        required=True,
        help="Archivo de salida (.json o .xmind)",
    )
    parser.add_argument(
        "--format",
        choices=("json", "xmind"),
        help="Formato de salida; si se omite, se deduce de la extensión",
    )
    return parser


def _output_format(output: str, requested: str | None) -> str:
    """Determina el formato y evita extensiones que contradigan la opción."""
    suffix = Path(output).suffix.lower()
    by_suffix = {".json": "json", ".xmind": "xmind"}
    inferred = by_suffix.get(suffix)
    if requested is None:
        if inferred is None:
            raise ValueError(
                "No se puede deducir el formato de salida: usa .json, .xmind o --format."
            )
        return inferred
    if inferred is not None and inferred != requested:
        raise ValueError(
            f"El formato indicado ({requested}) no coincide con la extensión {suffix}."
        )
    return requested


def main() -> int:
    """Ejecuta el flujo completo y devuelve un código de salida convencional."""
    args = build_parser().parse_args()
    try:
        output_format = _output_format(args.output, args.format)
        mind_map = parse_file_ir(args.input)
        style_config = load_styles(args.styles) if args.styles else None

        if output_format == "xmind":
            # XMind necesita estilos materializados; el adaptador no los resuelve.
            resolve_styles(mind_map, style_config)
            write_xmind(mind_map, args.output)
        else:
            # Conservar el comportamiento JSON anterior: resolver solo si se
            # proporciona expresamente una configuración externa de estilos.
            if style_config is not None:
                resolve_styles(mind_map, style_config)
            write_json(mind_map, args.output)
    except (OSError, ValueError, StyleError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    label = "Archivo XMind" if output_format == "xmind" else "Modelo JSON"
    print(f"{label} generado: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
