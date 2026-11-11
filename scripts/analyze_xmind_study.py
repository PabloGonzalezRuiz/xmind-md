#!/usr/bin/env python3
"""Read-only XMind ZIP analyzer. Produces JSON and focused tree-table reports."""
import json, re, zipfile
from pathlib import Path

SRC = Path("examples/xmind-study")
OUT = Path("pmd-xmind-study-report")
WORDS = re.compile(r"\b(tabla|cuadro|art[ií]culo|apartado|p[aá]rrafo|letra|n[uú]mero)\b", re.I)
TREE_TABLE = "org.xmind.ui.treetable.toptitle"
SPREADSHEET = "org.xmind.ui.spreadsheet"

def text_of(t):
    for k in ("title", "text", "label", "name"):
        v = t.get(k)
        if isinstance(v, str) and v.strip(): return v.strip()
        if isinstance(v, dict):
            for sk in ("content", "text", "title"):
                if isinstance(v.get(sk), str) and v[sk].strip(): return v[sk].strip()
    return ""

def kids(t):
    c = t.get("children") or {}
    if isinstance(c, list): return [x for x in c if isinstance(x, dict)]
    if not isinstance(c, dict): return []
    return [x for key in ("attached", "detached") for x in (c.get(key) or []) if isinstance(x, dict)]

def walk(t, path, depth, out):
    title = text_of(t); p = path + ([title] if title else [])
    children = kids(t)
    out.append({"depth": depth, "path": p, "title": title, "id": t.get("id"),
      "structureClass": t.get("structureClass"), "style": t.get("style"),
      "labels": t.get("labels"), "markers": t.get("markers"),
      "hyperlink": t.get("href") or t.get("hyperlink"), "notes": t.get("notes"),
      "children_count": len(children), "raw_topic": t})
    for ch in children: walk(ch, p, depth + 1, out)

def analyze(path):
    result = {"file": path.name, "format": "unknown", "members": [], "sheets": [], "topics": [], "styles": None, "metadata": {}}
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        result["members"] = [{"name": n, "size": z.getinfo(n).file_size} for n in names]
        content = next((n for n in names if n.lower().endswith("content.json")), None)
        styles = next((n for n in names if n.lower().endswith("styles.json")), None)
        if content:
            result["format"] = "xmind-zip-json"
            payload = json.loads(z.read(content).decode("utf-8-sig"))
            sheets = payload if isinstance(payload, list) else payload.get("sheets", [])
            for i, s in enumerate(sheets):
                root = s.get("rootTopic") or s.get("root_topic") or {}
                result["sheets"].append({"index": i, "title": s.get("title") or s.get("name") or f"Hoja {i+1}", "id": s.get("id")})
                if isinstance(root, dict) and root: walk(root, [result["sheets"][-1]["title"]], 0, result["topics"])
            result["metadata"]["top_level_keys"] = list(payload.keys()) if isinstance(payload, dict) else []
            if styles: result["styles"] = json.loads(z.read(styles).decode("utf-8-sig"))
            for n in names:
                if n.lower().endswith(("manifest.json", "metadata.json", "meta.json")):
                    try: result["metadata"][n] = json.loads(z.read(n).decode("utf-8-sig"))
                    except Exception: pass
        else:
            xml = next((n for n in names if n.lower().endswith("content.xml")), None)
            if xml:
                result["format"] = "xmind-zip-xml"
                result["metadata"]["content_xml"] = z.read(xml).decode("utf-8", "replace")
                sx = next((n for n in names if n.lower().endswith("styles.xml")), None)
                if sx: result["styles"] = z.read(sx).decode("utf-8", "replace")
    return result

def candidates(rows):
    groups = {}
    for r in rows:
        p = tuple(r["path"][:-1]); groups.setdefault(p, []).append(r)
    found = []
    for parent, rs in groups.items():
        if len(rs) < 2: continue
        counts = [r["children_count"] for r in rs]
        titles = [r["title"] for r in rs]
        if len(set(counts)) <= max(2, len(counts)//2) or any(WORDS.search(x or "") for x in titles + list(parent)):
            found.append({"parent_path": list(parent), "siblings": len(rs), "child_counts": counts,
              "titles": titles, "confidence": "heuristic candidate; visual confirmation required"})
    return sorted(found, key=lambda x: -x["siblings"])

def style_props(t):
    return (t.get("style") or {}).get("properties", {})

def table_outline(t, depth=0):
    props = style_props(t)
    line = "  " * depth + "- " + (text_of(t).replace("\n", " / ") or "[sin título]")
    details = []
    for key in ("shape-class", "svg:fill", "fo:color", "fo:font-size", "fo:font-weight",
                "border-line-color", "border-line-width", "line-color", "line-pattern"):
        if key in props: details.append(f"{key}={props[key]}")
    if details: line += " {" + "; ".join(details) + "}"
    lines = [line]
    for ch in kids(t): lines.extend(table_outline(ch, depth + 1))
    return lines

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    files = sorted(SRC.glob("*.xmind"))
    if not files: raise SystemExit(f"No .xmind files found in {SRC}")
    report = ["# Informe de análisis de mapas XMind", "",
      "Análisis de solo lectura. Los originales no se modifican.", ""]
    tables_report = ["# Inventario de tablas de árbol XMind", "",
      "Identificación basada en structureClass=org.xmind.ui.treetable.toptitle.",
      "Cada nodo conserva su árbol de descendientes y las propiedades de estilo locales.", ""]
    for f in files:
        try:
            d = analyze(f); cs = candidates(d["topics"])
            table_rows = [r for r in d["topics"] if r["raw_topic"].get("structureClass") == TREE_TABLE]
            spreadsheet_rows = [r for r in d["topics"] if r["raw_topic"].get("structureClass") == SPREADSHEET]
            inline_styles = sum(bool(r["raw_topic"].get("style")) for r in d["topics"])
            d["tree_table_candidates"] = cs
            d["tree_tables"] = [{"path": r["path"], "topic": r["raw_topic"]} for r in table_rows]
            d["spreadsheet_topics"] = [{"path": r["path"], "topic": r["raw_topic"]} for r in spreadsheet_rows]
            safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", f.stem)
            (OUT / (safe + ".json")).write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
            report += [f"## {f.name}", "", f"- Formato: {d['format']}",
              f"- Hojas: {len(d['sheets'])}", f"- Temas: {len(d['topics'])}",
              f"- Tablas de árbol explícitas: {len(table_rows)}",
              f"- Estructuras spreadsheet: {len(spreadsheet_rows)}",
              f"- Temas con estilo local: {inline_styles}",
              f"- Candidatos heurísticos adicionales: {len(cs)}", ""]
            tables_report += [f"## {f.name}", "",
              f"Tablas de árbol: {len(table_rows)} · Spreadsheet: {len(spreadsheet_rows)}", ""]
            for i, r in enumerate(table_rows, 1):
                tables_report += [f"### {i}. {' / '.join(r['path'])}", ""]
                tables_report += table_outline(r["raw_topic"])
                tables_report.append("")
            if spreadsheet_rows:
                tables_report += ["### Estructuras spreadsheet", ""]
                for r in spreadsheet_rows:
                    tables_report.append("- " + " / ".join(r["path"]))
                tables_report.append("")
            if cs:
                report += ["### Candidatos heurísticos (no equivalen a tablas confirmadas)", ""]
                for c in cs[:10]:
                    report.append("- " + " / ".join(c["parent_path"]) + f": {c['siblings']} nodos hermanos")
                report.append("")
        except Exception as e:
            report += [f"## {f.name}", "", f"ERROR: {type(e).__name__}: {e}", ""]
            tables_report += [f"## {f.name}", "", f"ERROR: {type(e).__name__}: {e}", ""]
    (OUT / "INFORME.md").write_text("\n".join(report), encoding="utf-8")
    (OUT / "TABLAS_ARBOL.md").write_text("\n".join(tables_report), encoding="utf-8")
    print(f"Processed {len(files)} XMind files; reports include explicit tree-table structures.")

if __name__ == "__main__": main()
