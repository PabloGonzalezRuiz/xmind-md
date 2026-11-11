"""Adaptador IR 1.0.0 para generar libros XMind modernos (ZIP + JSON).

El adaptador solo consume entidades canónicas. No interpreta Markdown, no
resuelve estilos y rechaza explícitamente las capacidades que aún no exporta.
"""

from __future__ import annotations

import json
import math
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import NAMESPACE_URL, uuid5

from ..ir import MindMap, Topic


MIMETYPE = "application/vnd.xmind.workbook"
DATA_STRUCTURE_VERSION = "3"
LAYOUT_ENGINE_VERSION = "5"
THUMBNAIL_PNG = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4"
    "890000000d49444154789c6300010000000500010d0a2db40000000049454e44"