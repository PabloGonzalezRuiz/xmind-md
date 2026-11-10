"""Parser Markdown enriquecido de XMind MD."""
from __future__ import annotations

import re
from datetime import date, datetime
from pathlib import Path
from typing import Any
from uuid import NAMESPACE_URL, uuid5

import yaml

from .model import MindMap, Topic


class MarkdownParseError(ValueError):
    """Error sintáctico o estructural del documento fuente."""


_HEADING_RE = re.compile(r"^(#{1,6})[ \t]+(.+?)\s*#*\s*$")
_OLD_DIRECTIVE_RE = re.compile(r"^@(conjunto|estilo)\(([^()]*)\)\s*$")
_DIRECTIVES = {"xmind", "xmind-note", "xmind-relationship", "xmind-boundary", "xmind-summary"}


def _normalize_yaml(value: Any) -> Any:
    """Convierte escalares YAML no JSON, como fechas, a valores serializables."""
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(key): _normalize_yaml(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_normalize_yaml(item) for item in value]
    return value


class _UniqueKeyLoader(yaml.SafeLoader):
    """Loader seguro que rechaza claves YAML duplicadas."""


def _construct_unique_mapping(loader: _UniqueKeyLoader, node: yaml.MappingNode, deep: bool = False):
    mapping = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            duplicate = key in mapping
        except TypeError as exc:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping", node.start_mark,
                "unhashable mapping key", key_node.start_mark,
            ) from exc
        if duplicate:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping", node.start_mark,
                f"duplicate key {key!r}", key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


_UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_unique_mapping
)


def _yaml_mapping(source: str, line: int, label: str) -> dict[str, Any]:
    try:
        value = yaml.load(source, Loader=_UniqueKeyLoader) or {}
    except yaml.YAMLError as exc:
        raise MarkdownParseError(f"YAML inválido en {label}, línea {line}: {exc}") from exc
    if not isinstance(value, dict):
        raise MarkdownParseError(f"{label} debe contener un objeto YAML (línea {line})")
    return _normalize_yaml(value)


def _validate_id(value: Any, label: str, line: int) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]*", value):
        raise MarkdownParseError(
            f"{label} debe ser un ID no vacío y usar letras, números, punto, guion, dos puntos o guion bajo (línea {line})"
        )
    return value


def _stable_id(prefix: str, seed: str) -> str:
    return f"{prefix}_{uuid5(NAMESPACE_URL, seed).hex[:16]}"


def _inline_runs(text: str) -> list[dict[str, Any]]:
    """Reconoce énfasis, código inline y enlaces; conserva el resto del texto."""
    tick = chr(96)
    token = re.compile(r"(!?\[[^\]]*\]\([^)]*\)|\*\*[^*]+\*\*|(?<!\*)\*[^*]+\*(?!\*)|" + re.escape(tick) + r"[^" + re.escape(tick) + r"]+" + re.escape(tick) + r")")
    runs: list[dict[str, Any]] = []
    cursor = 0
    for match in token.finditer(text):
        if match.start() > cursor:
            runs.append({"text": text[cursor:match.start()]})
        value = match.group(0)
        if value.startswith("!["):
            inner = re.match(r"!\[([^\]]*)\]\(([^)]*)\)", value)
            runs.append({"type": "image", "alt": inner.group(1), "src": inner.group(2)})
        elif value.startswith("["):
            inner = re.match(r"\[([^\]]*)\]\(([^)]*)\)", value)
            runs.append({"type": "link", "text": inner.group(1), "url": inner.group(2)})
        elif value.startswith("**"):
            runs.append({"text": value[2:-2], "style": {"bold": True}})
        elif value.startswith("*"):
            runs.append({"text": value[1:-1], "style": {"italic": True}})
        else:
            runs.append({"text": value[1:-1], "style": {"code": True}})
        cursor = match.end()
    if cursor < len(text):
        runs.append({"text": text[cursor:]})
    return runs or [{"text": text}]


def _parse_list(lines: list[str], start: int) -> tuple[dict[str, Any], int]:
    """Analiza listas con niveles de anidamiento y conserva su estructura."""
    marker_re = re.compile(r"^( *)([-+*]|\d+[.)])\s+(.+)$")

    def parse_level(index: int, indent: int) -> tuple[dict[str, Any], int]:
        first = marker_re.match(lines[index])
        assert first is not None
        ordered = first.group(2)[0].isdigit()
        items: list[dict[str, Any]] = []
        i = index
        while i < len(lines):
            match = marker_re.match(lines[i])
            if not match:
                break
            current_indent = len(match.group(1).expandtabs(4))
            if current_indent < indent:
                break
            if current_indent > indent:
                if not items:
                    break
                nested, i = parse_level(i, current_indent)
                items[-1]["children"].extend(nested["items"])
                continue

            item = {
                "content": [{"type": "paragraph", "runs": _inline_runs(match.group(3))}],
                "children": [],
            }
            items.append(item)
            i += 1

            # Las líneas de lista con mayor sangría pertenecen al último elemento.
            while i < len(lines):
                child_match = marker_re.match(lines[i])
                if not child_match:
                    break
                child_indent = len(child_match.group(1).expandtabs(4))
                if child_indent <= indent:
                    break
                nested, i = parse_level(i, child_indent)
                item["children"].extend(nested["items"])
        return {"type": "list", "ordered": ordered, "items": items}, i

    first = marker_re.match(lines[start])
    assert first is not None
    base_indent = len(first.group(1).expandtabs(4))
    return parse_level(start, base_indent)


def _list_plain_text(block: dict[str, Any]) -> str:
    values = []
    for item in block.get("items", []):
        for content in item.get("content", []):
            if content.get("type") == "paragraph":
                values.append("".join(run.get("text", "") for run in content.get("runs", [])))
        if item.get("children"):
            values.append(_list_plain_text({"items": item["children"]}))
    return "\\n".join(values)


def _parse_table(lines: list[str], start: int) -> tuple[dict[str, Any], int]:
    def cells(line: str) -> list[str]:
        return [cell.strip() for cell in line.strip().strip("|").split("|")]
    header = cells(lines[start])
    i = start + 2
    rows = []
    while i < len(lines) and "|" in lines[i] and lines[i].strip():
        rows.append(cells(lines[i]))
        i += 1
    return {"type": "table", "header": [_inline_runs(c) for c in header],
            "rows": [[_inline_runs(c) for c in row] for row in rows]}, i


def parse_markdown(text: str, source_path: str = "<string>") -> MindMap:
    """Analiza front matter, temas, bloques Markdown y directivas XMind."""
    lines = text.splitlines()
    metadata: dict[str, Any] = {}
    i = 0
    if lines and lines[0].strip() == "---":
        end = next((n for n in range(1, len(lines)) if lines[n].strip() in {"---", "..."}), None)
        if end is None:
            raise MarkdownParseError("Front matter sin delimitador de cierre (línea 1)")
        metadata = _yaml_mapping("\n".join(lines[1:end]), 2, "front matter")
        i = end + 1

    roots: list[Topic] = []
    stack: list[Topic] = []
    pending: dict[str, Any] | None = None
    globals_: dict[str, list[dict[str, Any]]] = {
        "relationships": [], "boundaries": [], "summaries": []
    }
    assets: list[dict[str, Any]] = []
    fence_char = chr(96)

    while i < len(lines):
        raw = lines[i]
        stripped = raw.strip()
        line_no = i + 1
        if not stripped:
            i += 1
            continue

        # Código cercado: su contenido es literal y no se analiza como Markdown.
        fence = re.match(r"^\s*(" + re.escape(fence_char) + r"{3,}|~{3,})(.*)$", raw)
        if fence:
            if not stack:
                raise MarkdownParseError(f"Código antes del tema raíz (línea {line_no})")
            marker, language = fence.groups()
            code_lines = []
            i += 1
            closing = re.compile(r"^\s*" + re.escape(marker[0]) + "{" + str(len(marker)) + r",}\s*$")
            while i < len(lines) and not closing.match(lines[i]):
                code_lines.append(lines[i])
                i += 1
            if i >= len(lines):
                raise MarkdownParseError(f"Bloque de código sin cierre (línea {line_no})")
            code = "\n".join(code_lines)
            stack[-1].content_blocks.append({"type": "code", "language": language.strip() or None, "text": code})
            stack[-1].content.append(code)
            i += 1
            continue

        directive = re.match(r"^:::([a-z][a-z0-9-]*)\s*$", stripped)
        if directive:
            name = directive.group(1)
            if name not in _DIRECTIVES:
                raise MarkdownParseError(f"Directiva desconocida '{name}' (línea {line_no})")
            end = next((n for n in range(i + 1, len(lines)) if lines[n].strip() == ":::"), None)
            if end is None:
                raise MarkdownParseError(f"Directiva {name} sin cierre (línea {line_no})")
            payload_text = "\n".join(lines[i + 1:end])
            payload = (_yaml_mapping(payload_text, line_no + 1, name)
                       if payload_text.strip() and name != "xmind-note" else {})
            if name == "xmind":
                if pending is not None:
                    raise MarkdownParseError(f"Directivas de tema consecutivas (línea {line_no})")
                pending = payload
            elif name == "xmind-note":
                if not stack:
                    raise MarkdownParseError(f"Nota antes del tema raíz (línea {line_no})")
                stack[-1].annotations.setdefault("notes", []).append(payload_text)
            else:
                key = {"xmind-relationship": "relationships", "xmind-boundary": "boundaries",
                       "xmind-summary": "summaries"}[name]
                globals_[key].append(payload)
            i = end + 1
            continue

        legacy = _OLD_DIRECTIVE_RE.fullmatch(stripped)
        if legacy:
            if pending is None:
                pending = {}
            key, value = legacy.groups()
            pending["style_set" if key == "conjunto" else "style"] = value.strip()
            i += 1
            continue
        if stripped.startswith("@"):
            raise MarkdownParseError(f"Directiva no reconocida (línea {line_no}): {stripped}")

        heading = _HEADING_RE.match(raw)
        if heading:
            level = len(heading.group(1))
            title = heading.group(2).strip()
            if not title:
                raise MarkdownParseError(f"Encabezado vacío (línea {line_no})")
            props = pending or {}
            allowed = {"id", "kind", "style_set", "style", "style_overrides", "labels",
                       "markers", "task", "layout", "links", "extensions"}
            unknown = set(props) - allowed
            if unknown:
                raise MarkdownParseError(f"Propiedades desconocidas en :::xmind: {sorted(unknown)} (línea {line_no})")
            if props.get("kind", "attached") not in {"attached", "callout", "summary"}:
                raise MarkdownParseError(f"kind no válido en :::xmind (línea {line_no})")
            for field_name in ("style_overrides", "layout", "extensions"):
                if field_name in props and not isinstance(props[field_name], dict):
                    raise MarkdownParseError(f"{field_name} debe ser un objeto YAML (línea {line_no})")
            if "links" in props and not isinstance(props["links"], list):
                raise MarkdownParseError(f"links debe ser una lista (línea {line_no})")
            if "labels" in props and (
                not isinstance(props["labels"], list)
                or any(not isinstance(label, str) for label in props["labels"])
            ):
                raise MarkdownParseError(f"labels debe ser una lista de textos (línea {line_no})")
            if "markers" in props and (
                not isinstance(props["markers"], list)
                or any(not isinstance(marker, dict) for marker in props["markers"])
            ):
                raise MarkdownParseError(f"markers debe ser una lista de objetos (línea {line_no})")
            if "task" in props:
                task = props["task"]
                if not isinstance(task, dict):
                    raise MarkdownParseError(f"task debe ser un objeto YAML (línea {line_no})")
                progress = task.get("progress")
                if progress is not None and (
                    not isinstance(progress, int) or isinstance(progress, bool) or not 0 <= progress <= 100
                ):
                    raise MarkdownParseError(f"task.progress debe ser un entero entre 0 y 100 (línea {line_no})")
            if not stack and (roots or level != 1):
                raise MarkdownParseError("El primer encabezado debe ser H1 y solo puede existir una raíz")
            siblings = stack[-1].children if stack else roots
            occurrence = sum(1 for sibling in siblings if sibling.title == title)
            hierarchy = "/".join([ancestor.title for ancestor in stack] + [title])
            seed = f"{source_path}|{hierarchy}|{occurrence}"
            explicit_id = _validate_id(props["id"], "id del tema", line_no) if "id" in props else None
            topic = Topic(
                id=explicit_id or _stable_id("topic", seed), title=title, level=level,
                style_set=props.get("style_set") or (metadata.get("style_set") if not stack else None),
                kind=props.get("kind", "attached"),
                style_ref=props.get("style"), style_overrides=props.get("style_overrides", {}),
                annotations={k: props[k] for k in ("labels", "markers", "task") if k in props},
                links=props.get("links", []), layout=props.get("layout", {}),
                extensions=props.get("extensions", {}),
                source={"file": source_path, "line_start": line_no, "line_end": line_no},
            )
            pending = None
            while stack and stack[-1].level >= level:
                stack.pop()
            if stack:
                stack[-1].children.append(topic)
            else:
                roots.append(topic)
            stack.append(topic)
            i += 1
            continue

        if pending is not None:
            raise MarkdownParseError(f":::xmind debe preceder inmediatamente a un encabezado (línea {line_no})")
        if not stack:
            raise MarkdownParseError(f"Contenido antes del tema raíz (línea {line_no})")

        topic = stack[-1]
        if stripped.startswith(">"):
            quote = []
            while i < len(lines) and lines[i].lstrip().startswith(">"):
                quote.append(lines[i].lstrip()[1:].lstrip())
                i += 1
            topic.content_blocks.append({"type": "quote", "content": [
                {"type": "paragraph", "runs": _inline_runs(value)} for value in quote]})
            topic.content.extend(quote)
            continue
        if re.match(r"^\s*([-+*]|\d+[.)])\s+", raw):
            block, i = _parse_list(lines, i)
            topic.content_blocks.append(block)
            topic.content.append("\n".join("".join(r.get("text", "") for r in item["content"]) for item in block["items"]))
            continue
        if "|" in raw and i + 1 < len(lines) and re.match(r"^\s*\|?\s*:?-{3,}", lines[i + 1]):
            block, i = _parse_table(lines, i)
            topic.content_blocks.append(block)
            continue
        if re.match(r"^\s*([-*_])(?:\s*\1){2,}\s*$", raw):
            topic.content_blocks.append({"type": "divider"})
            i += 1
            continue
        if stripped.startswith("!["):
            match = re.match(r"!\[([^\]]*)\]\(([^)]*)\)", stripped)
            if match:
                asset = {"alt": match.group(1), "src": match.group(2)}
                assets.append(asset)
                topic.content_blocks.append({"type": "image", **asset})
                topic.resources.append(asset)
                i += 1
                continue

        paragraph = [stripped]
        i += 1
        while i < len(lines) and lines[i].strip():
            candidate = lines[i]
            if (_HEADING_RE.match(candidate) or candidate.lstrip().startswith((":::", ">", fence_char * 3, "~~~", "!["))
                    or re.match(r"^\s*([-+*]|\d+[.)])\s+", candidate)):
                break
            paragraph.append(candidate.strip())
            i += 1
        joined = " ".join(paragraph)
        topic.content.append(joined)
        topic.content_blocks.append({"type": "paragraph", "runs": _inline_runs(joined)})

    if pending is not None:
        raise MarkdownParseError("Directiva de tema al final del documento sin encabezado")
    if len(roots) != 1:
        raise MarkdownParseError("El documento debe contener un único tema raíz (un H1)")

    topic_index: dict[str, Topic] = {}
    def index_topic(topic: Topic) -> None:
        if not topic.id or topic.id in topic_index:
            raise MarkdownParseError(f"ID de tema vacío o duplicado: {topic.id!r}")
        topic_index[topic.id] = topic
        for child in topic.children:
            index_topic(child)
    index_topic(roots[0])

    entity_ids: set[str] = set()
    for kind, entries in globals_.items():
        for entry in entries:
            required = {"relationships": ("id", "source", "target"),
                        "boundaries": ("id", "topics"), "summaries": ("id", "topics")}[kind]
            missing = [key for key in required if key not in entry]
            if missing:
                raise MarkdownParseError(f"{kind}: faltan campos obligatorios {missing}")
            if entry["id"] in entity_ids:
                raise MarkdownParseError(f"ID de entidad global duplicado: {entry['id']}")
            entity_ids.add(entry["id"])
            refs = [entry["source"], entry["target"]] if kind == "relationships" else entry["topics"]
            if not isinstance(refs, list) and kind != "relationships":
                raise MarkdownParseError(f"{kind}: topics debe ser una lista")
            if any(ref not in topic_index for ref in refs):
                raise MarkdownParseError(f"{kind}: referencia a tema inexistente")
            if kind == "relationships" and entry["source"] == entry["target"]:
                raise MarkdownParseError("Una relación no puede conectar un tema consigo mismo")

    title = metadata.get("title") or roots[0].title
    if not isinstance(title, str) or not title.strip():
        raise MarkdownParseError("title del front matter debe ser texto no vacío")
    known = {"title", "id", "author", "description", "style_set", "layout", "styles", "style_sets", "extensions"}
    unknown = set(metadata) - known
    if unknown:
        raise MarkdownParseError(f"Campos desconocidos en front matter: {sorted(unknown)}")
    layout = metadata.get("layout", {})
    if not isinstance(layout, dict):
        raise MarkdownParseError("layout del front matter debe ser un objeto")

    map_id = _validate_id(metadata["id"], "id del mapa", 1) if "id" in metadata else _stable_id("map", f"{source_path}|{title}")
    for field_name in ("styles", "style_sets", "extensions"):
        if field_name in metadata and not isinstance(metadata[field_name], dict):
            raise MarkdownParseError(f"{field_name} del front matter debe ser un objeto")
    if "style_set" in metadata and not isinstance(metadata["style_set"], str):
        raise MarkdownParseError("style_set del front matter debe ser texto")
    return MindMap(
        id=map_id,
        title=title, topics=roots, metadata=metadata, styles=metadata.get("styles", {}),
        style_sets=metadata.get("style_sets", {}), assets=assets,
        relationships=globals_["relationships"], boundaries=globals_["boundaries"],
        summaries=globals_["summaries"], layout=layout, extensions=metadata.get("extensions", {}),
    )


def parse_file(path: str | Path) -> MindMap:
    """Lee UTF-8 y utiliza la ruta como origen para IDs deterministas."""
    source = Path(path)
    return parse_markdown(source.read_text(encoding="utf-8"), source_path=source.as_posix())
