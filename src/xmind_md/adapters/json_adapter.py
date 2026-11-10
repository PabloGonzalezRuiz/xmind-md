"""Adaptador JSON del modelo intermedio canónico IR 1.0.0."""

from __future__ import annotations

import json
from pathlib import Path

from ..ir import MindMap


def write_json(mind_map: MindMap, destination: str | Path) -> None:
    """Escribe el documento IR canónico como JSON UTF-8 legible."""
    if not isinstance(mind_map, MindMap):
        raise TypeError("write_json requiere un MindMap IR 1.0.0.")
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(mind_map.to_dict(), ensure_ascii=False, indent=2) + "\n"
    path.write_text(serialized, encoding="utf-8")
