"""API pública del modelo intermedio canónico IR 1.x."""

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
    TopicStructure,
    TreeTableCell,
    TreeTableRow,
)
from .migrations import migrate_ir_1_0_to_1_1
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
    "TopicStructure",
    "TreeTableCell",
    "TreeTableRow",
    "migrate_ir_1_0_to_1_1",
    "validate_mind_map",
]
