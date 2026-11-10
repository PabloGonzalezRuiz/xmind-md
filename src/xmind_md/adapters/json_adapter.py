"""Adaptador de depuración: serializa el modelo intermedio a JSON."""

from __future__ import annotations

import json
from pathlib import Path

from ..model import MindMap


def write_json(mind_map: MindMap, destination: str | Path) -> None:
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(mind_map.to_dict(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
