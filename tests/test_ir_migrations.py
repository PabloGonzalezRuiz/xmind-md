"""Pruebas de migración explícita del contrato IR."""

import warnings

import pytest

from xmind_md.ir import (
    MindMap,
    Sheet,
    Topic,
    IRValidationError,
    migrate_ir_1_0_to_1_1,
    validate_mind_map,
)


def make_map() -> MindMap:
    return MindMap(
        id="map_migration",
        title="Mapa",
        sheet=Sheet(
            id="sheet_migration",
            title="Hoja",
            root_topic=Topic(
                id="topic_root",
                title="Raíz",
                layout={"structure_class": "org.xmind.ui.treetable.toptitle"},
            ),
        ),
    )


def test_migration_returns_ir_1_1_copy_and_preserves_legacy_xmind_class():
    original = make_map()

    with pytest.warns(UserWarning, match="legacy_structure_class"):
        migrated = migrate_ir_1_0_to_1_1(original)

    assert migrated is not original
    assert migrated.ir_version == "1.1.0"
    assert migrated.sheet.root_topic.layout == {}
    assert migrated.sheet.root_topic.extensions == {
        "xmind": {"legacy_structure_class": "org.xmind.ui.treetable.toptitle"}
    }
    assert original.ir_version == "1.0.0"
    assert original.sheet.root_topic.layout["structure_class"] == (
        "org.xmind.ui.treetable.toptitle"
    )
    assert validate_mind_map(migrated) is migrated


def test_migration_without_legacy_fields_does_not_warn():
    original = make_map()
    original.sheet.root_topic.layout.clear()

    with warnings.catch_warnings(record=True) as recorded:
        warnings.simplefilter("always")
        migrated = migrate_ir_1_0_to_1_1(original)

    assert not recorded
    assert migrated.ir_version == "1.1.0"


def test_migration_rejects_non_1_0_documents():
    original = make_map()
    original.ir_version = "1.1.0"

    with pytest.raises(IRValidationError, match="Solo se puede migrar IR 1.0.0"):
        migrate_ir_1_0_to_1_1(original)
