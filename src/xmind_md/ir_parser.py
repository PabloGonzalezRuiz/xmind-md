"""Puente de migración: convierte el resultado del parser legacy a IR 1.0.0.

La API legacy se mantiene temporalmente para que el resolutor de estilos y los
adaptadores aún no migrados sigan funcionando. Las nuevas integraciones deben
utilizar parse_markdown_ir() o parse_file_ir().
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from uuid import NAMESPACE_URL, uuid5

from .ir import (
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
    validate_mind_map,
)
from .parser import _inline_runs, parse_markdown_syntax


def _id(prefix: str, value: str) -> str:
    return f"{prefix}_{uuid5(NAMESPACE_URL, value).hex[:16]}"


def _runs(value: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result = []
    for run in value:
        if run.get("type") == "link":
            target = run.get("url", "")
            if target.startswith("topic:"):
                result.append(
                    {
                        "text": run.get("text", ""),
                        "link": {"kind": "topic", "target": target[len("topic:") :]},
                    }
                )
            else:
                result.append(
                    {
                        "text": run.get("text", ""),
                        "link": {"kind": "web", "target": target},
                    }
                )
        elif run.get("type") == "image":
            result.append(
                {
                    "text": run.get("alt", ""),
                    "image_source": run.get("src", ""),
                }
            )
        else:
            result.append(
                {
                    "text": run.get("text", ""),
                    **({"style": run["style"]} if run.get("style") else {}),
                }
            )
    return result


def _paragraph(text: str, runs: list[dict[str, Any]] | None = None) -> ContentBlock:
    return ContentBlock("paragraph", {"text": text, "runs": runs or [{"text": text}]})


def _list_item(item: dict[str, Any]) -> dict[str, Any]:
    content = []
    for block in item.get("content", []):
        if block.get("type") == "paragraph":
            runs = _runs(block.get("runs", []))
            content.append(_paragraph("".join(run["text"] for run in runs), runs).to_dict())
    return {
        "content": content,
        "children": [_list_item(child) for child in item.get("children", [])],
    }


def _table_cell(runs: list[dict[str, Any]]) -> dict[str, Any]:
    converted = _runs(runs)
    return {"content": [_paragraph("".join(run["text"] for run in converted), converted).to_dict()]}


def _block(
    block: dict[str, Any],
    source_key: str,
    assets: dict[str, Asset],
    resource_refs: ResourceReferences,
) -> ContentBlock:
    kind = block.get("type")

    def make(block_type: str, data: dict[str, Any] | None = None) -> ContentBlock:
        values = dict(data or {})
        if block.get("source"):
            values["source"] = dict(block["source"])
        return ContentBlock(block_type, values)

    if kind == "paragraph":
        runs = _runs(block.get("runs", []))
        return make(
            "paragraph",
            {
                "text": "".join(run["text"] for run in runs),
                "runs": runs,
            },
        )
    if kind == "list":
        return make(
            "list",
            {
                "ordered": bool(block.get("ordered")),
                "items": [_list_item(item) for item in block.get("items", [])],
            },
        )
    if kind == "table":
        header = [_table_cell(cell) for cell in block.get("header", [])]
        rows = [{"cells": header, "header": True}]
        rows.extend(
            {
                "cells": [_table_cell(cell) for cell in row],
                "header": False,
            }
            for row in block.get("rows", [])
        )
        return make("table", {"rows": rows})
    if kind == "code":
        return make(
            "code",
            {
                "language": block.get("language"),
                "code": block.get("text", ""),
            },
        )
    if kind == "quote":
        paragraphs = block.get("content", [])
        return make(
            "quote",
            {
                "text": "\n".join(
                    "".join(run.get("text", "") for run in item.get("runs", []))
                    for item in paragraphs
                )
            },
        )
    if kind == "divider":
        return make("divider")
    if kind == "image":
        src = str(block.get("src", ""))
        asset_id = _id("asset", src)
        assets.setdefault(
            asset_id,
            Asset(
                kind="image",
                path=src,
                name=Path(src).name or None,
                metadata={"alt": block.get("alt", "")},
            ),
        )
        if asset_id not in resource_refs.images:
            resource_refs.images.append(asset_id)
        return make(
            "image",
            {
                "asset_id": asset_id,
                "alt": block.get("alt"),
            },
        )
    # No se pierde silenciosamente una construcción futura del parser.
    return make(
        "raw",
        {
            "format": "xmind-md-legacy",
            "data": dict(block),
        },
    )


def _topic(syntax: Any, assets: dict[str, Asset]) -> Topic:
    properties = syntax.properties
    resources = ResourceReferences()
    content = [_block(block, syntax.id, assets, resources) for block in syntax.blocks]

    labels = [
        Label(_id("label", f"{syntax.id}|{index}|{value}"), value)
        for index, value in enumerate(properties.get("labels", []))
    ]
    markers = [
        Marker(
            _id("marker", f"{syntax.id}|{index}|{marker.get('group')}|{marker.get('value')}"),
            marker["group"],
            marker["value"],
        )
        for index, marker in enumerate(properties.get("markers", []))
    ]
    notes = []
    for index, value in enumerate(syntax.notes):
        note_runs = _runs(_inline_runs(value))
        note_text = "".join(run["text"] for run in note_runs)
        notes.append(
            Note(
                _id("note", f"{syntax.id}|{index}|{value}"),
                [_paragraph(note_text, note_runs)],
            )
        )
    annotation = Annotation(
        notes=notes,
        labels=labels,
        markers=markers,
        task=properties.get("task"),
    )

    links = []
    for index, link in enumerate(properties.get("links", [])):
        item = dict(link)
        item.setdefault("id", _id("link", f"{syntax.id}|{index}|{item.get('target', '')}"))
        if "kind" not in item or "target" not in item:
            raise ValueError(
                f"Enlace inválido en el tema {syntax.id!r}: se requieren kind y target"
            )
        links.append(item)

    return Topic(
        id=syntax.id,
        title=syntax.title,
        kind=properties.get("kind", "attached"),
        content=content,
        annotations=annotation,
        resources=resources,
        links=links,
        style=StyleState(
            ref=properties.get("style"),
            style_set=properties.get("style_set"),
            overrides=dict(properties.get("style_overrides", {})),
        ),
        layout=dict(properties.get("layout", {})),
        extensions=dict(properties.get("extensions", {})),
        source=dict(syntax.source),
        children=[_topic(child, assets) for child in syntax.children],
    )


def _build_ir(syntax: Any) -> MindMap:
    assets: dict[str, Asset] = {}
    root_topic = _topic(syntax.root, assets)

    relationships = [
        Relationship(
            id=item["id"],
            source_topic=item["source"],
            target_topic=item["target"],
            title=item.get("title"),
            style=StyleState(ref=item.get("style")),
            extensions=dict(item.get("extensions", {})),
        )
        for item in syntax.relationships
    ]
    boundaries = [
        Boundary(
            id=item["id"],
            topic_ids=list(item["topics"]),
            title=item.get("title"),
            style=StyleState(ref=item.get("style")),
            extensions=dict(item.get("extensions", {})),
        )
        for item in syntax.boundaries
    ]
    summaries = [
        Summary(
            id=item["id"],
            topic_ids=list(item["topics"]),
            title=item.get("title"),
            style=StyleState(ref=item.get("style")),
            extensions=dict(item.get("extensions", {})),
        )
        for item in syntax.summaries
    ]

    source_metadata = syntax.metadata
    title = source_metadata.get("title", syntax.root.title)
    map_id = source_metadata.get("id") or _id("map", f"{syntax.source_path}|{title}")
    layout = dict(source_metadata.get("layout", {}))
    sheet_layout = SheetLayout(
        structure=layout.pop("structure", "mind_map"),
        direction=layout.pop("direction", "balanced"),
        properties=layout,
    )
    metadata = {
        key: source_metadata[key]
        for key in ("author", "description", "style_set")
        if key in source_metadata
    }
    if source_metadata.get("extensions"):
        metadata["extensions"] = dict(source_metadata["extensions"])
    metadata["source_file"] = syntax.source_path
    sheet_id = _id("sheet", f"{map_id}|{syntax.source_path}")
    mind_map = MindMap(
        id=map_id,
        title=title,
        metadata=metadata,
        styles=dict(source_metadata.get("styles", {})),
        style_sets=dict(source_metadata.get("style_sets", {})),
        assets=assets,
        sheet=Sheet(
            id=sheet_id,
            title=title,
            root_topic=root_topic,
            metadata={},
            layout=sheet_layout,
            relationships=relationships,
            boundaries=boundaries,
            summaries=summaries,
        ),
    )
    return validate_mind_map(mind_map)


def parse_markdown_ir(text: str, source_path: str = "<string>") -> MindMap:
    """Analiza Markdown enriquecido y devuelve el modelo canónico IR 1.0.0."""
    return _build_ir(parse_markdown_syntax(text, source_path))


def parse_file_ir(path: str | Path) -> MindMap:
    """Lee un Markdown UTF-8 y devuelve el modelo canónico IR 1.0.0."""
    source = Path(path)
    return parse_markdown_ir(
        source.read_text(encoding="utf-8"),
        source_path=source.as_posix(),
    )
