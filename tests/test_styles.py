from xmind_md.parser import parse_markdown
from xmind_md.styles import resolve_styles


def test_resolve_style_from_named_set():
    mind_map = parse_markdown(
        "@conjunto(TAI)\n# Mapa\n@estilo(clave)\n## Tema"
    )
    style_sets = {"TAI": {"styles": {"clave": {"font_weight": "bold"}}}}
    resolve_styles(mind_map, style_sets)
    assert mind_map.topics[0].children[0].resolved_style == {
        "font_weight": "bold"
    }
