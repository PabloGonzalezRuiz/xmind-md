"""Migraciones explícitas entre versiones del contrato IR."""

from __future__ import annotations

import warnings
from copy import deepcopy

from .entities import MindMap, Topic
from .validation import IRValidationError, validate_mind_map


def migrate_ir_1_0_to_1_1(mind_map: MindMap) -> MindMap:
    """Devuelve una copia IR 1.1.0 sin inferir semántica no declarada.

    La antigua clave layout.structure_class se preserva bajo
    extensions.xmind.legacy_structure_class. No se convierte automáticamente
    en tree_table porque IR 1.0.0 no contiene roles explícitos de celda.
    """
    if not isinstance(mind_map, MindMap):
        raise TypeError("La migración requiere un MindMap IR.")
    if mind_map.ir_version != "1.0.0":
        raise IRValidationError(
            f"Solo se puede migrar IR 1.0.0; recibido {mind_map.ir_version!r}"
        )
    validate_mind_map(mind_map)
    migrated = deepcopy(mind_map)
    migrated.ir_version = "1.1.0"
    preserved: list[str] = []

    def visit(topic: Topic, path: str) -> None:
        legacy_class = topic.layout.pop("structure_class", None)
        if legacy_class is not None:
            xmind_extension = topic.extensions.setdefault("xmind", {})
            if not isinstance(xmind_extension, dict):
                raise IRValidationError(
                    f"{path}.extensions.xmind: debe ser un objeto para preservar "
                    "structure_class"
                )
            if "legacy_structure_class" in xmind_extension:
                raise IRValidationError(
                    f"{path}.extensions.xmind.legacy_structure_class: "
                    "ya existe y no se sobrescribirá"
                )
            xmind_extension["legacy_structure_class"] = legacy_class
            preserved.append(path)
        for index, child in enumerate(topic.children):
            visit(child, f"{path}.children[{index}]")

    visit(migrated.sheet.root_topic, "sheet.root_topic")
    if preserved:
        warning_message = (
            "Se han preservado clases estructurales XMind históricas como "
            "extensions.xmind.legacy_structure_class; requieren migración "
            "semántica manual antes de exportar como estructura neutral: "
        )
        warnings.warn(
            f"{warning_message}{', '.join(preserved)}",
            UserWarning,
            stacklevel=2,
        )
    return validate_mind_map(migrated)
