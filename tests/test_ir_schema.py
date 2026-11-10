"""Validación formal del contrato IR 1.0.0 y sus ejemplos JSON."""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "docs" / "ir-schema.json"
EXAMPLES_DIR = ROOT / "examples" / "ir"


@pytest.fixture(scope="module")
def schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def validator(schema: dict) -> Draft202012Validator:
    return Draft202012Validator(schema, format_checker=FormatChecker())


def test_ir_schema_is_valid_draft_2020_12(schema: dict) -> None:
    Draft202012Validator.check_schema(schema)


def test_all_ir_json_examples_conform_to_schema(validator: Draft202012Validator) -> None:
    examples = sorted(EXAMPLES_DIR.rglob("*.json"))
    assert examples, f"No se encontraron ejemplos JSON en {EXAMPLES_DIR}"

    failures: list[str] = []
    for path in examples:
        instance = json.loads(path.read_text(encoding="utf-8"))
        errors = sorted(
            validator.iter_errors(instance),
            key=lambda error: tuple(str(part) for part in error.absolute_path),
        )
        failures.extend(
            f"{path.relative_to(ROOT)}: "
            f"{'/'.join(str(part) for part in error.absolute_path) or '<root>'}: "
            f"{error.message}"
            for error in errors
        )

    assert not failures, "Ejemplos IR no conformes:\n" + "\n".join(failures)


@pytest.mark.parametrize(
    ("mutate", "description"),
    [
        (
            lambda document: document.update(ir_version="2.0.0"),
            "versión IR no admitida",
        ),
        (
            lambda document: document["sheet"]["root_topic"].pop("children"),
            "propiedad obligatoria ausente",
        ),
        (
            lambda document: document["sheet"]["root_topic"]["links"][0].update(
                kind="ftp"
            ),
            "tipo de enlace no admitido",
        ),
        (
            lambda document: document["metadata"].update(created="no-es-una-fecha"),
            "formato date-time no válido",
        ),
    ],
)
def test_schema_rejects_invalid_documents(
    schema: dict,
    mutate,
    description: str,
) -> None:
    example_path = EXAMPLES_DIR / "constitucion.json"
    document = json.loads(example_path.read_text(encoding="utf-8"))
    invalid_document = copy.deepcopy(document)
    mutate(invalid_document)

    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    assert not validator.is_valid(invalid_document), description
