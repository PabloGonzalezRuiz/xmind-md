"""Parser PMD 1.0.0 hacia el modelo canónico IR 1.1.0."""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections.abc import Mapping
from importlib.resources import files
from pathlib import Path
from typing import Any

import yaml
from yaml.events import AliasEvent
from yaml.nodes import MappingNode, ScalarNode, SequenceNode

from .ir import MindMap, TopicStructure, TreeTableCell, TreeTableRow, validate_mind_map
from .ir_builder import build_ir
from .parser import MarkdownParseError, _yaml_mapping, parse_markdown_syntax
from .syntax import TopicSyntax


class PMDParseError(ValueError):
    """Error sintáctico o semántico de un documento PMD."""


_FRONT_MATTER_FIELDS = {
    "pmd_version",
    "title",
    "id",
    "author",
    "description",
    "catalog",
    "inheritance",
    "metadata",
    "extensions",
}
_TOPIC_FIELDS = {
    "id",
    "parent",
    "kind",
    "role",
    "style_ref",
    "style_overrides",
    "structure",
    "labels",
    "markers",
    "task",
    "layout",
    "links",
    "extensions",
}
_GLOBAL_DIRECTIVES = {
    "pmd-relationship": "xmind-relationship",
    "pmd-boundary": "xmind-boundary",
    "pmd-summary": "xmind-summary",
}


def _strict_yaml_mapping(source: str, line: int, label: str) -> dict[str, Any]:
    """Rechaza alias y fechas YAML implícitas antes de normalizar a JSON."""
    try:
        if any(isinstance(event, AliasEvent) for event in yaml.parse(source)):
            raise PMDParseError(f"Los alias YAML no están permitidos en {label} (línea {line})")
        root = yaml.compose(source)

        def inspect(node: Any) -> None:
            if isinstance(node, ScalarNode):
                if node.tag == "tag:yaml.org,2002:timestamp":
                    raise PMDParseError(
                        f"Las fechas deben escribirse como cadenas ISO 8601 en {label} (línea {line})"
                    )
            elif isinstance(node, MappingNode):
                for key_node, value_node in node.value:
                    inspect(key_node)
                    inspect(value_node)
            elif isinstance(node, SequenceNode):
                for item in node.value:
                    inspect(item)

        if root is not None:
            inspect(root)
    except yaml.YAMLError as exc:
        raise PMDParseError(f"YAML inválido en {label}, línea {line}: {exc}") from exc
    try:
        return _yaml_mapping(source, line, label)
    except MarkdownParseError as exc:
        raise PMDParseError(str(exc)) from exc
    except RecursionError as exc:
        raise PMDParseError(f"Estructura YAML demasiado profunda en {label} (línea {line})") from exc


def _yaml_dump(value: Mapping[str, Any]) -> str:
    return yaml.safe_dump(
        dict(value), allow_unicode=True, sort_keys=False, default_flow_style=False
    ).rstrip()


def _front_matter(lines: list[str]) -> tuple[dict[str, Any], int]:
    if not lines or lines[0].strip() != "---":
        raise PMDParseError("PMD requiere front matter YAML en la primera línea")
    end = next((i for i in range(1, len(lines)) if lines[i].strip() in {"---", "..."}), None)
    if end is None:
        raise PMDParseError("Front matter sin delimitador de cierre (línea 1)")
    metadata = _strict_yaml_mapping("\n".join(lines[1:end]), 2, "front matter PMD")
    unknown = set(metadata) - _FRONT_MATTER_FIELDS
    if unknown:
        raise PMDParseError(f"Campos desconocidos en front matter PMD: {sorted(unknown)}")
    if metadata.get("pmd_version") != "1.0.0":
        raise PMDParseError(
            f"pmd_version no soportada: {metadata.get('pmd_version')!r}; se requiere '1.0.0'"
        )
    for key in ("metadata", "extensions"):
        if key in metadata and not isinstance(metadata[key], dict):
            raise PMDParseError(f"{key} del front matter PMD debe ser un objeto YAML")
    catalog = metadata.get("catalog")
    if catalog is not None and (
        not isinstance(catalog, dict)
        or set(catalog) != {"id", "version"}
        or not all(isinstance(catalog.get(k), str) and catalog[k] for k in ("id", "version"))
    ):
        raise PMDParseError("catalog debe contener exactamente id y version no vacíos")
    inheritance = metadata.get("inheritance", {})
    if not isinstance(inheritance, dict) or set(inheritance) - {"mode"}:
        raise PMDParseError("inheritance solo admite el campo mode")
    if inheritance.get("mode", "catalog") not in {"catalog", "none"}:
        raise PMDParseError("inheritance.mode debe ser 'catalog' o 'none'")
    return metadata, end


def _catalog_data(catalog: Mapping[str, Any] | None) -> dict[str, Any]:
    if catalog is not None:
        return dict(catalog)
    try:
        raw = files("xmind_md").joinpath("data/style-catalog.json").read_text(encoding="utf-8")
        value = json.loads(raw)
    except (OSError, json.JSONDecodeError) as exc:
        raise PMDParseError(f"No se pudo cargar el catálogo PMD incluido: {exc}") from exc
    if not isinstance(value, dict):
        raise PMDParseError("El catálogo PMD debe ser un objeto JSON")
    return value


def _catalog_indexes(
    metadata: dict[str, Any], catalog: Mapping[str, Any] | None
) -> tuple[set[str], set[str]]:
    reference = metadata.get("catalog")
    if reference is None:
        return set(), set()
    data = _catalog_data(catalog)
    if (
        data.get("catalog_id") != reference["id"]
        or data.get("catalog_version") != reference["version"]
    ):
        raise PMDParseError(
            "La identidad/versión del catálogo suministrado no coincide con front matter catalog"
        )
    roles, styles = data.get("roles"), data.get("styles")
    if not isinstance(roles, list) or not isinstance(styles, list):
        raise PMDParseError("Catálogo PMD inválido: roles y styles deben ser listas")
    role_ids: set[str] = set()
    style_ids: set[str] = set()
    role_styles: dict[str, str] = {}
    for role in roles:
        if not isinstance(role, dict) or not isinstance(role.get("id"), str):
            raise PMDParseError("Catálogo PMD inválido: definición de rol sin id textual")
        if role["id"] in role_ids:
            raise PMDParseError(f"Catálogo PMD inválido: rol duplicado {role['id']!r}")
        role_ids.add(role["id"])
        if role.get("style_ref") is not None:
            if not isinstance(role["style_ref"], str):
                raise PMDParseError(f"Catálogo PMD inválido: style_ref inválido para {role['id']}")
            role_styles[role["id"]] = role["style_ref"]
    for style in styles:
        if not isinstance(style, dict) or not isinstance(style.get("id"), str):
            raise PMDParseError("Catálogo PMD inválido: definición de estilo sin id textual")
        if style["id"] in style_ids:
            raise PMDParseError(f"Catálogo PMD inválido: estilo duplicado {style['id']!r}")
        style_ids.add(style["id"])
    for role_id, style_id in role_styles.items():
        if style_id not in style_ids:
            raise PMDParseError(
                f"Catálogo PMD inválido: el rol {role_id!r} referencia el estilo inexistente {style_id!r}"
            )
    return role_ids, style_ids


def _contains_inherited(value: Any) -> bool:
    if isinstance(value, str) and value == "inherited":
        return True
    if isinstance(value, dict):
        return any(_contains_inherited(item) for item in value.values())
    if isinstance(value, list):
        return any(_contains_inherited(item) for item in value)
    return False


def _transform_document(
    source: str, metadata: dict[str, Any]
) -> tuple[str, dict[int, dict[str, Any]], list[int]]:
    """Traduce directivas PMD a la sintaxis temporal ya reconocida."""
    lines = source.splitlines()
    _, front_end = _front_matter(lines)
    accepted = {
        key: metadata[key]
        for key in ("title", "id", "author", "description", "extensions")
        if key in metadata
    }
    extensions = dict(accepted.get("extensions", {}))
    if "pmd" in extensions:
        raise PMDParseError("El espacio de nombres extensions.pmd está reservado")
    extensions["pmd"] = {
        key: metadata[key]
        for key in ("pmd_version", "catalog", "inheritance", "metadata")
        if key in metadata
    }
    accepted["extensions"] = extensions
    front = ["---", *_yaml_dump(accepted).splitlines(), "---"]
    output = list(front)
    line_map = [1] + [2] * (len(front) - 2) + [front_end + 1]
    pending: dict[str, Any] | None = None
    sidecar: dict[int, dict[str, Any]] = {}
    fence_char: str | None = None
    fence_length = 0
    i = front_end + 1
    while i < len(lines):
        raw = lines[i]
        stripped = raw.strip()
        fence_match = re.match(r"^\s*(~{3,})", raw)
        if raw.lstrip().startswith(chr(96) * 3):
            left = raw.lstrip()
            marker_len = len(left) - len(left.lstrip(chr(96)))
            fence_match = None
            marker_char = chr(96)
        elif fence_match:
            marker_char, marker_len = "~", len(fence_match.group(1))
        else:
            marker_char, marker_len = "", 0
        if marker_char:
            if fence_char is None:
                fence_char, fence_length = marker_char, marker_len
            elif (
                marker_char == fence_char
                and marker_len >= fence_length
                and not stripped.strip(marker_char)
            ):
                fence_char, fence_length = None, 0
            output.append(raw)
            line_map.append(i + 1)
            i += 1
            continue
        directive = re.fullmatch(r":::([a-z][a-z0-9-]*)", stripped) if fence_char is None else None
        if directive:
            name = directive.group(1)
            if pending is not None and name != "pmd":
                raise PMDParseError(
                    f":::pmd debe preceder inmediatamente a un encabezado (línea {i + 1})"
                )
            if name == "pmd":
                if pending is not None:
                    raise PMDParseError(f"Directivas :::pmd consecutivas (línea {i + 1})")
                end = next((j for j in range(i + 1, len(lines)) if lines[j].strip() == ":::"), None)
                if end is None:
                    raise PMDParseError(f"Directiva :::pmd sin cierre (línea {i + 1})")
                props = _strict_yaml_mapping(
                    "\n".join(lines[i + 1 : end]), i + 2, ":::pmd"
                )
                unknown = set(props) - _TOPIC_FIELDS
                if unknown:
                    raise PMDParseError(
                        f"Propiedades desconocidas en :::pmd: {sorted(unknown)} (línea {i + 1})"
                    )
                if "style_ref" in props and "style" in props:
                    raise PMDParseError("PMD solo admite style_ref; no se admite style")
                if "style_ref" in props:
                    props["style_ref"] = props.pop("style_ref")
                if "style_overrides" in props:
                    if not isinstance(props["style_overrides"], dict):
                        raise PMDParseError(f"style_overrides debe ser un objeto (línea {i + 1})")
                    if _contains_inherited(props["style_overrides"]):
                        raise PMDParseError(
                            f"El literal 'inherited' no es un valor visual válido en PMD (línea {i + 1})"
                        )
                if "parent" in props and (
                    not isinstance(props["parent"], str)
                    or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]*", props["parent"])
                ):
                    raise PMDParseError(f"parent debe ser un ID textual no vacío (línea {i + 1})")
                if "role" in props and (not isinstance(props["role"], str) or not props["role"]):
                    raise PMDParseError(f"role debe ser un texto no vacío (línea {i + 1})")
                if "structure" in props and not isinstance(props["structure"], dict):
                    raise PMDParseError(f"structure debe ser un objeto YAML (línea {i + 1})")
                if "markers" in props:
                    markers = props["markers"]
                    if not isinstance(markers, list) or any(
                        not isinstance(marker, dict)
                        or set(marker) - {"id", "group", "value"}
                        or ("id" in marker and (
                            not isinstance(marker["id"], str)
                            or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]*", marker["id"])
                        ))
                        for marker in markers
                    ):
                        raise PMDParseError(
                            f"markers debe ser una lista de objetos con group, value e id opcional (línea {i + 1})"
                        )
                pending = props
                legacy = {
                    key: value
                    for key, value in props.items()
                    if key not in {"parent", "role", "structure", "style_ref"}
                }
                if "style_ref" in props:
                    legacy["style"] = props["style_ref"]
                output.append(":::xmind")
                line_map.append(i + 1)
                dumped = _yaml_dump(legacy) if legacy else ""
                for item in dumped.splitlines():
                    output.append(item)
                    line_map.append(i + 2)
                output.append(":::")
                line_map.append(end + 1)
                i = end + 1
                continue
            if name in _GLOBAL_DIRECTIVES:
                output.append(":::" + _GLOBAL_DIRECTIVES[name])
                line_map.append(i + 1)
                i += 1
                continue
            if name == "pmd-note":
                output.append(":::xmind-note")
                line_map.append(i + 1)
                i += 1
                continue
            if name.startswith("pmd-"):
                raise PMDParseError(f"Directiva PMD desconocida {name!r} (línea {i + 1})")
            if name.startswith("xmind"):
                raise PMDParseError(
                    f"Directiva legacy {name!r} no permitida en PMD 1.0.0 (línea {i + 1})"
                )
        heading = re.match(r"^(#{1,6})[ \t]+(.+?)\s*#*\s*$", raw) if fence_char is None else None
        if heading and pending is not None:
            sidecar[i + 1] = pending
            pending = None
        elif pending is not None and stripped:
            raise PMDParseError(
                f":::pmd debe preceder inmediatamente a un encabezado (línea {i + 1})"
            )
        output.append(raw)
        line_map.append(i + 1)
        i += 1
    if pending is not None:
        raise PMDParseError("Directiva :::pmd al final del documento sin encabezado")
    return "\n".join(output) + ("\n" if source.endswith("\n") else ""), sidecar, line_map


def _walk_syntax(root: TopicSyntax) -> list[TopicSyntax]:
    result: list[TopicSyntax] = []

    def visit(topic: TopicSyntax) -> None:
        result.append(topic)
        for child in topic.children:
            visit(child)

    visit(root)
    return result


def _remap_source(topic: TopicSyntax, line_map: list[int]) -> None:
    for key in ("line_start", "line_end"):
        value = topic.source.get(key)
        if isinstance(value, int) and 0 < value <= len(line_map):
            topic.source[key] = line_map[value - 1]
    for block in topic.blocks:
        source = block.get("source")
        if isinstance(source, dict):
            for key in ("line_start", "line_end"):
                value = source.get(key)
                if isinstance(value, int) and 0 < value <= len(line_map):
                    source[key] = line_map[value - 1]
    for child in topic.children:
        _remap_source(child, line_map)


def _stable_pmd_ids(root: TopicSyntax, source_path: str, explicit_ids: set[str]) -> None:
    normalized_path = unicodedata.normalize("NFC", source_path.replace("\\", "/"))
    if source_path in {"<string>", "<memory>"}:
        normalized_path = "<memory>"

    def visit(topic: TopicSyntax, titles: list[str], siblings: list[TopicSyntax]) -> None:
        title = unicodedata.normalize("NFC", topic.title)
        index = siblings.index(topic)
        occurrence = sum(
            1
            for sibling in siblings[: index + 1]
            if unicodedata.normalize("NFC", sibling.title) == title
        )
        route = [*titles, title]
        if topic.id not in explicit_ids:
            seed = "\0".join([normalized_path, *route, str(occurrence)])
            topic.id = "auto-" + hashlib.sha256(seed.encode("utf-8")).hexdigest()[:16]
        for child in topic.children:
            visit(child, route, topic.children)

    visit(root, [], [root])


def _rebuild_parent_tree(
    root: TopicSyntax, sidecar: dict[int, dict[str, Any]]
) -> tuple[set[str], dict[str, dict[str, Any]]]:
    topics = _walk_syntax(root)
    props_by_id: dict[str, dict[str, Any]] = {}
    explicit_ids: set[str] = set()
    for topic in topics:
        props = sidecar.get(topic.source.get("line_start"), {})
        props_by_id[topic.id] = props
        if "id" in props:
            explicit_ids.add(topic.id)
    inferred_parent: dict[str, str | None] = {}

    def index_parents(topic: TopicSyntax, parent: str | None = None) -> None:
        inferred_parent[topic.id] = parent
        for child in topic.children:
            index_parents(child, topic.id)

    index_parents(root)
    by_id = {topic.id: topic for topic in topics}
    desired_parent: dict[str, str | None] = {}
    for topic in topics:
        props = props_by_id[topic.id]
        if topic is root and "parent" in props:
            raise PMDParseError("El tema raíz no puede declarar parent")
        desired_parent[topic.id] = props.get("parent", inferred_parent[topic.id])
        if props.get("parent") is not None and props["parent"] not in explicit_ids:
            raise PMDParseError("parent debe referenciar un ID explícito de tema")
    for topic_id, parent_id in desired_parent.items():
        if parent_id is not None and parent_id not in by_id:
            raise PMDParseError(
                f"parent del tema {topic_id!r} referencia tema inexistente {parent_id!r}"
            )
        if parent_id == topic_id:
            raise PMDParseError(f"El tema {topic_id!r} no puede ser su propio padre")
    for topic in topics:
        topic.children = []
    for topic in topics[1:]:
        parent_id = desired_parent[topic.id]
        if parent_id is None:
            raise PMDParseError("Solo puede existir un tema raíz; parent desconectado")
        by_id[parent_id].children.append(topic)
    for topic in topics:
        topic.children.sort(key=lambda child: child.source.get("line_start", 0))
    visited: set[str] = set()
    active: set[str] = set()

    def check(topic: TopicSyntax) -> None:
        if topic.id in active:
            raise PMDParseError(f"Ciclo detectado en parent del tema {topic.id!r}")
        if topic.id in visited:
            raise PMDParseError(f"El tema {topic.id!r} tiene más de un padre")
        active.add(topic.id)
        visited.add(topic.id)
        for child in topic.children:
            check(child)
        active.remove(topic.id)

    check(root)
    if visited != set(by_id):
        raise PMDParseError(
            f"Jerarquía parent desconectada de la raíz: {sorted(set(by_id) - visited)}"
        )
    return explicit_ids, props_by_id


def parse_pmd_markdown(
    text: str,
    source_path: str = "<string>",
    *,
    catalog: Mapping[str, Any] | None = None,
) -> MindMap:
    """Analiza PMD 1.0.0 y devuelve IR 1.1.0 validado."""
    metadata, _ = _front_matter(text.splitlines())
    transformed, sidecar, line_map = _transform_document(text, metadata)
    try:
        syntax = parse_markdown_syntax(transformed, source_path=source_path)
    except MarkdownParseError as exc:
        raise PMDParseError(str(exc)) from exc
    _remap_source(syntax.root, line_map)
    inferred_topics = _walk_syntax(syntax.root)
    explicit_before_generation = {
        topic.id
        for topic in inferred_topics
        if "id" in sidecar.get(topic.source.get("line_start"), {})
    }
    # Generar IDs antes de aplicar overrides parent: la ruta de títulos procede
    # de la jerarquía ATX original, como exige la especificación PMD.
    _stable_pmd_ids(syntax.root, source_path, explicit_before_generation)
    explicit_ids, props_by_id = _rebuild_parent_tree(syntax.root, sidecar)
    props_by_id = {
        topic.id: sidecar.get(topic.source.get("line_start"), {})
        for topic in _walk_syntax(syntax.root)
    }
    has_catalog_feature = any(
        props.get("role") is not None or props.get("style_ref") is not None
        for props in props_by_id.values()
    )
    if has_catalog_feature and metadata.get("catalog") is None:
        raise PMDParseError("catalog es obligatorio cuando se utiliza role o style_ref")
    role_ids, style_ids = _catalog_indexes(metadata, catalog)
    for topic in _walk_syntax(syntax.root):
        props = props_by_id.get(topic.id, {})
        role, style_ref = props.get("role"), props.get("style_ref")
        if role is not None and role not in role_ids:
            raise PMDParseError(f"Rol semántico inexistente en el catálogo: {role!r}")
        if style_ref is not None and (not isinstance(style_ref, str) or style_ref not in style_ids):
            raise PMDParseError(f"Referencia visual inexistente en el catálogo: {style_ref!r}")
        if "structure" in props:
            descriptor = props["structure"]
            if set(descriptor) != {"type", "rows"} or descriptor.get("type") != "tree_table":
                raise PMDParseError("structure solo admite type: tree_table y rows")
            rows = descriptor.get("rows")
            if not isinstance(rows, list) or not rows:
                raise PMDParseError("structure.rows debe ser una lista no vacía")
            referenced: list[str] = []
            for row_index, row in enumerate(rows):
                if not isinstance(row, dict) or set(row) != {"cells"}:
                    raise PMDParseError(f"structure.rows[{row_index}] debe contener cells")
                cells = row["cells"]
                if (
                    not isinstance(cells, list)
                    or not cells
                    or any(
                        not isinstance(cell, str)
                        or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]*", cell)
                        for cell in cells
                    )
                ):
                    raise PMDParseError(f"structure.rows[{row_index}].cells debe contener IDs")
                referenced.extend(cells)
            if len(referenced) != len(set(referenced)):
                raise PMDParseError("Una celda tree_table no puede repetirse")
            if any(cell_id not in explicit_ids for cell_id in referenced):
                raise PMDParseError("Todas las celdas tree_table deben referenciar IDs explícitos")
            child_ids = {child.id for child in topic.children}
            if set(referenced) != child_ids:
                raise PMDParseError(
                    "tree_table debe referenciar exactamente una vez todos los hijos directos; "
                    f"faltan {sorted(child_ids - set(referenced))}, sobran {sorted(set(referenced) - child_ids)}"
                )
    mind_map = build_ir(syntax)
    mind_map.ir_version = "1.1.0"
    mind_map.metadata["pmd_version"] = metadata["pmd_version"]
    if metadata.get("catalog") is not None:
        mind_map.metadata["catalog"] = dict(metadata["catalog"])
    mind_map.metadata["inheritance"] = dict(metadata.get("inheritance", {"mode": "catalog"}))
    if metadata.get("metadata"):
        mind_map.metadata["pmd_metadata"] = dict(metadata["metadata"])
    for topic in _walk_ir_topics(mind_map):
        props = props_by_id.get(topic.id, {})
        if "role" in props:
            topic.semantic_role = props["role"]
        if "structure" in props:
            descriptor = props["structure"]
            topic.structure = TopicStructure(
                type="tree_table",
                rows=[
                    TreeTableRow(cells=[TreeTableCell(topic_id=value) for value in row["cells"]])
                    for row in descriptor["rows"]
                ],
            )
    return validate_mind_map(mind_map)


def _walk_ir_topics(mind_map: MindMap):
    def visit(topic):
        yield topic
        for child in topic.children:
            yield from visit(child)

    yield from visit(mind_map.sheet.root_topic)


def parse_pmd_file(path: str | Path, *, catalog: Mapping[str, Any] | None = None) -> MindMap:
    """Lee un archivo PMD UTF-8 y devuelve IR 1.1.0 validado."""
    source = Path(path)
    return parse_pmd_markdown(
        source.read_text(encoding="utf-8"), source_path=source.as_posix(), catalog=catalog
    )
