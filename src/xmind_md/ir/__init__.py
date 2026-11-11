"""API pública del modelo intermedio canónico IR 1.0.0."""

from .entities import (
    Annotation,
    Asset,
    Boundary,
    ContentBlock,
    Label,
    Marker,
    MindMap,
    Note,
    Relationship,
    ResourceReferences,
    Sheet,
    SheetLayout,
    StyleState,
    Summary,
    Topic,
)
from .validation import IRValidationError, validate_mind_map

__all__ = [
    "Annotation",
    "Asset",
    "Boundary",
    "ContentBlock",
    "IRValidationError",
    "Label",
    "Marker",
    "MindMap",
    "Note",
    "Relationship",
    "ResourceReferences",
    "Sheet",
    "SheetLayout",
    "StyleState",
    "Summary",
    "Topic",
    "validate_mind_map",
]
