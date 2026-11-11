#!/usr/bin/env python3
"""Read-only XMind ZIP analyzer. Produces JSON and Markdown for PMD research."""
import json, re, zipfile
from pathlib import Path

SRC = Path("examples/xmind-study")
OUT = Path("pmd-xmind-study-report")
WORDS = re.compile(r"\b(tabla|cuadro|art[ií]culo|apartado|p[aá]rrafo|letra|n[uú]mero)\b", re.I)

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

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    files = sorted(SRC.glob("*.xmind"))
    if not files: raise SystemExit(f"No .xmind files found in {SRC}")
    report = ["# XMind study maps analysis", "", "Read-only analysis; original XMind files are never modified.", ""]
    for f in files:
        try:
            d = analyze(f); cs = candidates(d["topics"]); d["tree_table_candidates"] = cs
            safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", f.stem)
            (OUT / (safe + ".json")).write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
            report += [f"## {f.name}", "", f"- Format: {d['format']}", f"- Sheets: {len(d['sheets'])}",
              f"- Topics: {len(d['topics'])}", f"- Tree-table candidates: {len(cs)}",
              f"- Styles extracted: {d['styles'] is not None}", ""]
            for c in cs[:20]:
                report.append("- " + " / ".join(c["parent_path"]) + f": {c['siblings']} sibling rows; children={c['child_counts']}")
            report += ["", "### Topic outline", "", "| Depth | Path | Children |", "|---:|---|---:|"]
            for r in d["topics"][:120]:
                p = " → ".join(r["path"]).replace("|", "\\|")
                report.append(f"| {r['depth']} | {p} | {r['children_count']} |")
            report.append("")
        except Exception as e:
            report += [f"## {f.name}", "", f"ERROR: {type(e).__name__}: {e}", ""]
    (OUT / "INFORME.md").write_text("\n".join(report), encoding="utf-8")
    print(f"Processed {len(files)} XMind files.")

if __name__ == "__main__": main()
