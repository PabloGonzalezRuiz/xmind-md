"""Adaptador de depuración que serializa el modelo intermedio a JSON."""

from __future__ import annotations

import json
from pathlib import Path

from ..model import MindMap


def write_json(mind_map: MindMap, destination: str | Path) -> None:
    """Escribe el mapa como JSON UTF-8 con formato legible."""
    path = Path(destination)

    # Crear directorios intermedios para que la CLI admita rutas nuevas.
    path.parent.mkdir(parents=True, exist_ok=True)

    # ensure_ascii=False conserva caracteres españoles y indent facilita inspección.
    serialized = json.dumps(mind_map.to_dict(), ensure_ascii=False, indent=2) + "\n"
    path.write_text(serialized, encoding="utf-8")
