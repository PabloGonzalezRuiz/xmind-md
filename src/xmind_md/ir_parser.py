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
from .parser import parse_markdown


def _id(prefix: str, value: str) -> str:
    return f"{prefix}_{uuid5(NAMESPACE_URL, value).hex[:16]}"


def _runs(value: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result = []
    for run in value:
        if run.get("type") == "link":
            result.append({
                "text": run.get("text", ""),
                "link": {"kind": "web", "target": run.get("url", "")},
            })
        elif run.get("type") == "image":
            result.append({
                "text": run.get("alt", ""),
                "image_source": run.get("src", ""),
            })
        else:
            result.append({
                "text": run.get("text", ""),
                **({"style": run["style"]} if run.get("style") else {}),
            })
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


def _block(block: dict[str, Any], source_key: str, assets: dict[str, Asset],
           resource_refs: ResourceReferences) -> ContentBlock:
    kind = block.get("type")
    if kind == "paragraph":
        runs = _runs(block.get("runs", []))
        return _paragraph("".join(run["text"] for run in runs), runs)
    if kind == "list":
        return ContentBlock("list", {
            "ordered": bool(block.get("ordered")),
            "items": [_list_item(item) for item in block.get("items", [])],
        })
    if kind == "table":
        header = [_table_cell(cell) for cell in block.get("header", [])]
        rows = [{"cells": header, "header": True}]
        rows.extend({
            "cells": [_table_cell(cell) for cell in row],
            "header": False,
        } for row in block.get("rows", []))
        return ContentBlock("table", {"rows": rows})
    if kind == "code":
        return ContentBlock("code", {
            "language": block.get("language"),
            "code": block.get("text", ""),
        })
    if kind == "quote":
        paragraphs = block.get("content", [])
        return ContentBlock("quote", {
            "text": "\n".join(
                "".join(run.get("text", "") for run in item.get("runs", []))
                for item in paragraphs
            )
        })
    if kind == "divider":
        return ContentBlock("divider")
    if kind == "image":
        src = str(block.get("src", ""))
        asset_id = _id("asset", src)
        assets.setdefault(asset_id, Asset(
            kind="image", path=src, name=Path(src).name or None,
            metadata={"alt": block.get("alt", "")},
        ))
        if asset_id not in resource_refs.images:
            resource_refs.images.append(asset_id)
        return ContentBlock("image", {
            "asset_id": asset_id,
            "alt": block.get("alt"),
        })
    # No se pierde silenciosamente una construcción futura del parser.
    return ContentBlock("raw", {
        "format": "xmind-md-legacy",
        "data": dict(block),
    })


def _topic(old: Any, assets: dict[str, Asset]) -> Topic:
    resources = ResourceReferences()
    content = [
        _block(block, old.id, assets, resources)
        for block in old.content_blocks
    ]

    labels = [
        Label(_id("label", f"{old.id}|{index}|{value}"), value)
        for index, value in enumerate(old.annotations.get("labels", []))
    ]
    markers = [
        Marker(
            _id("marker", f"{old.id}|{index}|{marker.get('group')}|{marker.get('value')}"),
            marker["group"], marker["value"],
        )
        for index, marker in enumerate(old.annotations.get("markers", []))
    ]
    notes = [
        Note(
            _id("note", f"{old.id}|{index}|{value}"),
            [_paragraph(value)],
        )
        for index, value in enumerate(old.annotations.get("notes", []))
    ]
    annotation = Annotation(
        notes=notes,
        labels=labels,
        markers=markers,
        task=old.annotations.get("task"),
    )

    links = []
    for index, link in enumerate(old.links):
        item = dict(link)
        item.setdefault("id", _id("link", f"{old.id}|{index}|{item.get('target', '')}"))
        if "kind" not in item or "target" not in item:
            raise ValueError(f"Enlace inválido en el tema {old.id!r}: se requieren kind y target")
        links.append(item)

    return Topic(
        id=old.id,
        title=old.title,
        kind=old.kind,
        content=content,
        annotations=annotation,
        resources=resources,
        links=links,
        style=StyleState(
            ref=old.style_ref,
            style_set=old.style_set,
            overrides=dict(old.style_overrides),
            resolved=dict(old.resolved_style),
        ),
        layout=dict(old.layout),
        extensions=dict(old.extensions),
        source=dict(old.source),
        children=[_topic(child, assets) for child in old.children],
    )


def _convert(old: Any, source_path: str) -> MindMap:
    assets: dict[str, Asset] = {}

    def collect_images(topic: Any) -> None:
        for resource in topic.resources:
            src = str(resource.get("src", ""))
            if src:
                asset_id = _id("asset", src)
                assets.setdefault(asset_id, Asset(
                    kind="image", path=src, name=Path(src).name or None,
                    metadata={"alt": resource.get("alt", "")},
                ))
        for child in topic.children:
            collect_images(child)

    for root in old.topics:
        collect_images(root)

    root_topic = _topic(old.topics[0], assets)
    relationships = [
        Relationship(
            id=item["id"],
            source_topic=item["source"],
            target_topic=item["target"],
            title=item.get("title"),
            style=StyleState(ref=item.get("style")),
        )
        for item in old.relationships
    ]
    boundaries = [
        Boundary(
            id=item["id"],
            topic_ids=list(item["topics"]),
            title=item.get("title"),
            style=StyleState(ref=item.get("style")),
        )
        for item in old.boundaries
    ]
    summaries = [
        Summary(
            id=item["id"],
            topic_ids=list(item["topics"]),
            title=item.get("title"),
            style=StyleState(ref=item.get("style")),
        )
        for item in old.summaries
    ]

    layout = dict(old.layout)
    sheet_layout = SheetLayout(
        structure=layout.pop("structure", "mind_map"),
        direction=layout.pop("direction", "balanced"),
        properties=layout,
    )
    metadata = {
        key: old.metadata[key]
        for key in ("author", "description", "style_set")
        if key in old.metadata
    }
    metadata["source_file"] = source_path
    sheet_id = _id("sheet", f"{old.id}|{source_path}")
    mind_map = MindMap(
        id=old.id,
        title=old.title,
        metadata=metadata,
        styles=dict(old.styles),
        style_sets=dict(old.style_sets),
        assets=assets,
        sheet=Sheet(
            id=sheet_id,
            title=old.title,
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
    return _convert(parse_markdown(text, source_path), source_path)


def parse_file_ir(path: str | Path) -> MindMap:
    """Lee un Markdown UTF-8 y devuelve el modelo canónico IR 1.0.0."""
    source = Path(path)
    return parse_markdown_ir(
        source.read_text(encoding="utf-8"),
        source_path=source.as_posix(),
    )
