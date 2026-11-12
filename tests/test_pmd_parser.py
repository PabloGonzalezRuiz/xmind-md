"""Pruebas del parser PMD 1.0.0 y su conversión a IR 1.1.0."""

from pathlib import Path

import pytest

from xmind_md.ir import validate_mind_map
from xmind_md.ir_parser import PMDParseError, parse_pmd_file, parse_pmd_markdown

ROOT = Path(__file__).resolve().parents[1]
CATALOG = """catalog:
  id: xmind-md.study
  version: "1.0.0"
"""


def _document(body: str, *, catalog: bool = True) -> str:
    reference = CATALOG if catalog else ""
    return '---\npmd_version: "1.0.0"\ntitle: Mapa PMD\n' + reference + "---\n\n" + body


@pytest.mark.parametrize(
    "filename",
    ["constitucion-estructura.pmd.md", "tabla-arbol-tema1.pmd.md"],
)
def test_reference_examples_parse_to_ir_1_1(filename: str) -> None:
    result = parse_pmd_file(ROOT / "examples" / "pmd" / filename)
    assert result.ir_version == "1.1.0"
    assert result.sheet.root_topic.id
    assert validate_mind_map(result) is result


def test_tree_table_roles_styles_and_parent_override_are_preserved() -> None:
    result = parse_pmd_file(ROOT / "examples" / "pmd" / "tabla-arbol-tema1.pmd.md")
    root = result.sheet.root_topic
    topics = {}

    def visit(topic):
        topics[topic.id] = topic
        for child in topic.children:
            visit(child)

    visit(root)
    article = topics["articulo"]
    assert article.semantic_role == "legal.article"
    assert article.structure.type == "tree_table"
    assert [[cell.topic_id for cell in row.cells] for row in article.structure.rows] == [
        ["cabecera", "cuerpo"]
    ]
    assert article.style.ref is None
    assert topics["cabecera"].semantic_role == "table.header_cell"
    assert topics["cabecera"].style.ref == "visual.table.header-cell"
    assert topics["cuerpo"].style.ref == "visual.table.body-cell"
    assert topics["cuerpo"].style.overrides["topic"]["fill"]["color"] == "#F6A04D"
    assert [child.id for child in article.children] == ["cabecera", "cuerpo"]
    assert result.metadata["catalog"] == {"id": "xmind-md.study", "version": "1.0.0"}


def test_pmd_generated_topic_ids_are_deterministic_and_source_independent_of_line_numbers() -> None:
    first = _document("# Raíz\n## Rama\n")
    second = _document("# Raíz\n\nPárrafo añadido.\n\n## Rama\n")
    one = parse_pmd_markdown(first)
    two = parse_pmd_markdown(second)
    assert one.sheet.root_topic.id.startswith("auto-")
    assert one.sheet.root_topic.id == two.sheet.root_topic.id
    assert one.sheet.root_topic.children[0].id == two.sheet.root_topic.children[0].id


def test_parent_can_reference_a_topic_declared_later() -> None:
    source = _document(
        "# Raíz\n:::pmd\nid: hijo\nparent: padre\n:::\n## Hijo\n:::pmd\nid: padre\n:::\n## Padre\n"
    )
    result = parse_pmd_markdown(source)
    assert [topic.id for topic in result.sheet.root_topic.children] == ["padre"]
    assert [topic.id for topic in result.sheet.root_topic.children[0].children] == ["hijo"]


def test_pmd_note_is_converted_to_topic_annotation() -> None:
    result = parse_pmd_markdown(_document("# Raíz\n:::pmd-note\nNota **importante**.\n:::\n"))
    note = result.sheet.root_topic.annotations.notes[0]
    assert note.content[0].data["text"] == "Nota importante."


@pytest.mark.parametrize(
    ("source", "message"),
    [
        (
            _document("# Raíz\n", catalog=False).replace(
                'pmd_version: "1.0.0"', 'pmd_version: "2.0.0"'
            ),
            "pmd_version",
        ),
        (_document(":::pmd\nrole: unknown.role\n:::\n# Raíz\n"), "Rol semántico"),
        (_document(":::pmd\nstyle_ref: visual.no-existe\n:::\n# Raíz\n"), "Referencia visual"),
        (
            _document(":::pmd\nid: a\n:::\n# Raíz\n:::pmd\nparent: ausente\n:::\n## Hijo\n"),
            "parent",
        ),
        (
            _document(
                ":::pmd\nid: a\nstructure:\n  type: tree_table\n  rows:\n    - cells: [no_existe]\n:::\n# Raíz\n## Hijo\n"
            ),
            "tree_table",
        ),
        (_document("# Raíz\n:::xmind\nid: legacy\n:::\n## Hijo\n"), "legacy"),
    ],
)
def test_invalid_pmd_documents_are_rejected(source: str, message: str) -> None:
    with pytest.raises(PMDParseError, match=message):
        parse_pmd_markdown(source)


def test_catalog_is_required_when_roles_or_visual_refs_are_used() -> None:
    source = _document(":::pmd\nrole: study.note\n:::\n# Raíz\n", catalog=False)
    with pytest.raises(PMDParseError, match="catalog es obligatorio"):
        parse_pmd_markdown(source)


def test_style_overrides_preserve_null_and_reject_inherited_literal() -> None:
    accepted = _document(
        ":::pmd\nid: raiz\nstyle_overrides:\n  topic:\n    fill: null\n:::\n# Raíz\n"
    )
    result = parse_pmd_markdown(accepted)
    assert result.sheet.root_topic.style.overrides["topic"]["fill"] is None

    rejected = _document(
        ':::pmd\nid: raiz\nstyle_overrides:\n  topic:\n    fill: "inherited"\n:::\n# Raíz\n'
    )
    with pytest.raises(PMDParseError, match="inherited"):
        parse_pmd_markdown(rejected)


def test_markdown_parser_remains_ir_1_0_and_legacy_compatible() -> None:
    from xmind_md.ir_parser import parse_markdown_ir

    result = parse_markdown_ir("# Raíz\n## Hijo\n")
    assert result.ir_version == "1.0.0"


def test_yaml_aliases_and_implicit_dates_are_rejected() -> None:
    alias_source = _document(
        ":::pmd\nid: raiz\nlabels: &labels [A]\nextensions: {vendor: *labels}\n:::\n# Raíz\n"
    )
    with pytest.raises(PMDParseError, match="alias YAML"):
        parse_pmd_markdown(alias_source)

    date_source = _document(":::pmd\nid: raiz\ntask: {due_date: 2026-12-15}\n:::\n# Raíz\n")
    with pytest.raises(PMDParseError, match="cadenas ISO 8601"):
        parse_pmd_markdown(date_source)


def test_explicit_marker_ids_are_preserved() -> None:
    source = _document(
        ":::pmd\nid: raiz\nmarkers:\n  - id: marca_prioridad\n    group: priority\n    value: high\n:::\n# Raíz\n"
    )
    result = parse_pmd_markdown(source)
    assert result.sheet.root_topic.annotations.markers[0].id == "marca_prioridad"


def test_style_override_paths_and_types_are_checked_against_catalog() -> None:
    unknown = _document(
        ":::pmd\nid: raiz\nstyle_overrides:\n  topic:\n    fill:\n      unknown: true\n:::\n# Raíz\n"
    )
    with pytest.raises(PMDParseError, match="Propiedad visual no definida"):
        parse_pmd_markdown(unknown)

    wrong_type = _document(
        ":::pmd\nid: raiz\nstyle_overrides:\n  topic:\n    fill:\n      color: 42\n:::\n# Raíz\n"
    )
    with pytest.raises(PMDParseError, match="Tipo no válido"):
        parse_pmd_markdown(wrong_type)

    boolean_as_number = _document(
        ":::pmd\nid: raiz\nstyle_overrides:\n  topic:\n    fill:\n      opacity: true\n:::\n# Raíz\n"
    )
    with pytest.raises(PMDParseError, match="Tipo no válido"):
        parse_pmd_markdown(boolean_as_number)


def test_global_pmd_directives_use_strict_yaml_validation() -> None:
    source = _document(
        "# Raíz\n:::pmd-boundary\ntitle: &name Uno\ntopics: *name\n:::\n"
    )
    with pytest.raises(PMDParseError, match="alias YAML"):
        parse_pmd_markdown(source)
