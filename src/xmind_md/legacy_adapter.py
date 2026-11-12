"""Adaptador de compatibilidad del AST sintáctico al modelo legacy.

Solo lo utilizan las funciones públicas antiguas parse_markdown()/parse_file().
La ruta canónica AST → IR no instancia clases de este módulo.
"""
from __future__ import annotations

from typing import Any
from uuid import NAMESPACE_URL, uuid5

from .model import MindMap, Topic
from .syntax import DocumentSyntax, TopicSyntax


def _stable_id(prefix: str, seed: str) -> str:
    return f"{prefix}_{uuid5(NAMESPACE_URL, seed).hex[:16]}"


def _plain_runs(runs: list[dict[str, Any]]) -> str:
    return "".join(
        str(run.get("text", run.get("alt", "")))
        for run in runs
    )


def _list_plain_text(items: list[dict[str, Any]]) -> str:
    values: list[str] = []
    for item in items:
        for block in item.get("content", []):
            if block.get("type") == "paragraph":
                values.append(_plain_runs(block.get("runs", [])))
        if item.get("children"):
            values.append(_list_plain_text(item["children"]))
    return "\n".join(values)


def _topic(syntax: TopicSyntax) -> Topic:
    properties = syntax.properties
    content: list[str] = []
    resources: list[dict[str, Any]] = []

    for block in syntax.blocks:
        kind = block.get("type")
        if kind == "paragraph":
            content.append(_plain_runs(block.get("runs", [])))
        elif kind == "list":
            content.append(_list_plain_text(block.get("items", [])))
        elif kind == "code":
            content.append(block.get("text", ""))
        elif kind == "quote":
            content.extend(
                _plain_runs(item.get("runs", []))
                for item in block.get("content", [])
                if item.get("type") == "paragraph"
            )
        elif kind == "image":
            resources.append({"alt": block.get("alt", ""), "src": block.get("src", "")})

    annotations = {
        key: properties[key]
        for key in ("labels", "markers", "task")
        if key in properties
    }
    if syntax.notes:
        annotations["notes"] = list(syntax.notes)

    return Topic(
        id=syntax.id,
        title=syntax.title,
        level=syntax.level,
        kind=properties.get("kind", "attached"),
        children=[_topic(child) for child in syntax.children],
        content=content,
        content_blocks=[dict(block) for block in syntax.blocks],
        style_set=properties.get("style_set"),
        style_ref=properties.get("style"),
        style_overrides=dict(properties.get("style_overrides", {})),
        annotations=annotations,
        resources=resources,
        links=[dict(link) for link in properties.get("links", [])],
        layout=dict(properties.get("layout", {})),
        extensions=dict(properties.get("extensions", {})),
        source=dict(syntax.source),
    )


def to_legacy_mind_map(syntax: DocumentSyntax) -> MindMap:
    """Construye el modelo anterior exclusivamente para las API legacy."""
    metadata = dict(syntax.metadata)
    title = metadata.get("title", syntax.root.title)
    map_id = metadata.get("id") or _stable_id("map", f"{syntax.source_path}|{title}")
    assets = [
        {"alt": block.get("alt", ""), "src": block.get("src", "")}
        for topic in _walk(syntax.root)
        for block in topic.blocks
        if block.get("type") == "image"
    ]
    return MindMap(
        id=map_id,
        title=title,
        topics=[_topic(syntax.root)],
        metadata=metadata,
        styles=dict(metadata.get("styles", {})),
        style_sets=dict(metadata.get("style_sets", {})),
        assets=assets,
        relationships=[dict(item) for item in syntax.relationships],
        boundaries=[dict(item) for item in syntax.boundaries],
        summaries=[dict(item) for item in syntax.summaries],
        layout=dict(metadata.get("layout", {})),
        extensions=dict(metadata.get("extensions", {})),
    )


def _walk(root: TopicSyntax):
    yield root
    for child in root.children:
        yield from _walk(child)
