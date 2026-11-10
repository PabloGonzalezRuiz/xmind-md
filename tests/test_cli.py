"""Pruebas de la interfaz de línea de comandos."""

import json
import sys
import zipfile

from xmind_md.cli import build_parser, main


def _run_cli(monkeypatch, *arguments):
    monkeypatch.setattr(sys, "argv", ["xmind-md", *map(str, arguments)])
    return main()


def test_cli_preserves_json_output_by_extension(tmp_path, monkeypatch, capsys):
    source = tmp_path / "mapa.md"
    output = tmp_path / "mapa.json"
    source.write_text("# Raíz\n## Rama\n", encoding="utf-8")

    assert _run_cli(monkeypatch, source, "--output", output) == 0

    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["ir_version"] == "1.0.0"
    assert "Modelo JSON generado" in capsys.readouterr().out


def test_cli_generates_xmind_from_canonical_ir(tmp_path, monkeypatch, capsys):
    source = tmp_path / "mapa.md"
    output = tmp_path / "mapa.xmind"
    source.write_text("# Raíz\n## Rama\n", encoding="utf-8")

    assert _run_cli(monkeypatch, source, "--output", output) == 0

    assert zipfile.is_zipfile(output)
    with zipfile.ZipFile(output) as archive:
        content = json.loads(archive.read("content.json"))
    assert content[0]["rootTopic"]["title"] == "Raíz"
    assert "Archivo XMind generado" in capsys.readouterr().out


def test_cli_accepts_explicit_format_without_known_extension(tmp_path, monkeypatch):
    source = tmp_path / "mapa.md"
    output = tmp_path / "resultado"
    source.write_text("# Raíz\n", encoding="utf-8")

    assert _run_cli(
        monkeypatch, source, "--output", output, "--format", "xmind"
    ) == 0
    assert zipfile.is_zipfile(output)


def test_cli_rejects_format_extension_mismatch(tmp_path, monkeypatch, capsys):
    source = tmp_path / "mapa.md"
    source.write_text("# Raíz\n", encoding="utf-8")

    result = _run_cli(
        monkeypatch, source, "--output", tmp_path / "mapa.json", "--format", "xmind"
    )

    assert result == 2
    assert "no coincide con la extensión .json" in capsys.readouterr().err


def test_cli_rejects_unknown_extension_without_explicit_format(
    tmp_path, monkeypatch, capsys
):
    source = tmp_path / "mapa.md"
    source.write_text("# Raíz\n", encoding="utf-8")

    result = _run_cli(monkeypatch, source, "--output", tmp_path / "mapa.bin")

    assert result == 2
    assert "No se puede deducir el formato" in capsys.readouterr().err


def test_cli_reports_missing_input_with_nonzero_exit_code(
    tmp_path, monkeypatch, capsys
):
    result = _run_cli(
        monkeypatch, tmp_path / "inexistente.md", "--output", tmp_path / "mapa.xmind"
    )

    assert result == 2
    assert "Error:" in capsys.readouterr().err


def test_cli_help_documents_both_formats(monkeypatch, capsys):
    parser = build_parser()
    try:
        parser.parse_args(["--help"])
    except SystemExit as exc:
        assert exc.code == 0
    output = capsys.readouterr().out
    assert ".json o .xmind" in output
    assert "--format" in output

def test_cli_reports_ir_feature_not_supported_by_xmind(tmp_path, monkeypatch, capsys):
    source = tmp_path / "mapa.md"
    source.write_text("# Raíz\\n![Imagen](imagen.png)\\n", encoding="utf-8")

    result = _run_cli(monkeypatch, source, "--output", tmp_path / "mapa.xmind")

    assert result == 2
    assert "no está soportado" in capsys.readouterr().err


def test_cli_reports_unresolved_style_for_xmind(tmp_path, monkeypatch, capsys):
    source = tmp_path / "mapa.md"
    source.write_text(
        "# Raíz\\n:::xmind\\nstyle: inexistente\\n:::\\n## Rama\\n",
        encoding="utf-8",
    )

    result = _run_cli(monkeypatch, source, "--output", tmp_path / "mapa.xmind")

    assert result == 2
    assert "no definido" in capsys.readouterr().err
