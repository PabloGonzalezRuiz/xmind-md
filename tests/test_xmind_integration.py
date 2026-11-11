"""Pruebas de integración con un paquete XMind de referencia externo.

El fixture se descarga en CI desde una revisión fijada de sc0tfree/xmind-mcp.
Su origen no acredita por sí solo que se haya guardado con XMind Desktop:
se usa para contrastar la estructura de un archivo real, no como certificación
de compatibilidad visual.
"""

from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pytest

from xmind_md.adapters.xmind_adapter import build_xmind_content, write_xmind
from xmind_md.ir import MindMap, Relationship, Sheet, Topic


REFERENCE_FILE = Path(__file__).parent / "fixtures" / "reference.xmind"


def _read_content(path: Path) -> list[dict]:
    with zipfile.ZipFile(path) as archive: