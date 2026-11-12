"""Fachada pública de parsing hacia el modelo canónico IR 1.0.0."""
from __future__ import annotations

from pathlib import Path

from .ir import MindMap
from .ir_builder import build_ir
from .parser import parse_markdown_syntax


def parse_markdown_ir(text: str, source_path: str = "<string>") -> MindMap:
    """Analiza Markdown enriquecido y devuelve el modelo canónico IR 1.0.0."""
    return build_ir(parse_markdown_syntax(text, source_path))


def parse_file_ir(path: str | Path) -> MindMap:
    """Lee un Markdown UTF-8 y devuelve el modelo canónico IR 1.0.0."""
    source = Path(path)
    return parse_markdown_ir(
        source.read_text(encoding="utf-8"),
        source_path=source.as_posix(),
    )
