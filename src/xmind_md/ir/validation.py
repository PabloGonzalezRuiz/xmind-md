"""Validación semántica del modelo intermedio IR 1.0.0."""

from __future__ import annotations

import re
from typing import Any

from .entities import MindMap, Topic


_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]*$")
_CONTENT_TYPES = {
    "paragraph", "list", "table", "code", "quote",
    "equation", "image", "divider", "raw",
}


class IRValidationError(ValueError):
    """El documento IR incumple una o más invariantes semánticas."""


def _require_id(value: str, path: str) -> None:
    if not isinstance(value, str) or not _ID_RE.fullmatch(value):
        raise IRValidationError(f"{path}: ID vacío o con formato no válido: {value!r}")
