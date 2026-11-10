"""Genera un archivo XMind pequeño para validación manual en XMind Desktop."""
from __future__ import annotations

import argparse
from pathlib import Path

from xmind_md.adapters.xmind_adapter import write_xmind
from xmind_md.parser import parse_file


def main() -> None:
    """Parsea el ejemplo de humo y escribe el archivo XMind de salida."""
    project_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=project_root / "output" / "xmind-md-smoke-test.xmind",
        help="Ruta del archivo .xmind que se generará.",
    )
    args = parser.parse_args()

    source = project_root / "examples" / "xmind-smoke-test.md"
    mind_map = parse_file(source)
    result = write_xmind(mind_map, args.output)
    print(f"Archivo XMind generado: {result}")


if __name__ == "__main__":
    main()
