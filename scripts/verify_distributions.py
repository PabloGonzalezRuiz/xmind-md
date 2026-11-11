"""Verifica el contenido legal y técnico de wheel y sdist construidos."""

from __future__ import annotations

import ast
import sys
import tarfile
import zipfile
from email.parser import Parser
from pathlib import Path


def project_version() -> str:
    """Lee la versión literal del paquete, única fuente de verdad."""
    source = Path("src/xmind_md/__init__.py").read_text(encoding="utf-8")
    module = ast.parse(source)
    for node in module.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__version__":
                    value = ast.literal_eval(node.value)
                    if isinstance(value, str):
                        return value
    raise SystemExit("No se encontró una asignación literal de __version__")


def verify_metadata(metadata: str, path: Path, expected_version: str) -> None:
    """Comprueba nombre y versión de los metadatos PEP 621."""
    parsed = Parser().parsestr(metadata)
    if parsed.get("Name", "").lower().replace("_", "-") != "xmind-md":
        raise SystemExit(f"{path}: nombre de distribución incorrecto")
    if parsed.get("Version") != expected_version:
        raise SystemExit(
            f"{path}: versión {parsed.get('Version')} distinta de {expected_version}"
        )


def verify_wheel(path: Path, expected_version: str) -> None:
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        metadata_files = [name for name in names if name.endswith(".dist-info/METADATA")]
        if len(metadata_files) != 1:
            raise SystemExit(f"{path}: se esperaba un único METADATA")
        metadata = archive.read(metadata_files[0]).decode("utf-8")
        verify_metadata(metadata, path, expected_version)
        if "License-Expression: MIT" not in metadata:
            raise SystemExit(f"{path}: falta License-Expression: MIT")
        if not any(name.endswith(".dist-info/licenses/LICENSE") for name in names):
            raise SystemExit(f"{path}: falta LICENSE en el wheel")
        if "xmind_md/cli.py" not in names:
            raise SystemExit(f"{path}: falta el módulo CLI")
    print(f"Wheel verificado: {path}")


def verify_sdist(path: Path, expected_version: str) -> None:
    with tarfile.open(path, "r:gz") as archive:
        names = set(archive.getnames())
        metadata_files = [name for name in names if name.endswith("/PKG-INFO")]
        if len(metadata_files) != 1:
            raise SystemExit(f"{path}: se esperaba un único PKG-INFO")
        metadata = archive.extractfile(metadata_files[0])
        if metadata is None:
            raise SystemExit(f"{path}: no se pudo leer PKG-INFO")
        verify_metadata(metadata.read().decode("utf-8"), path, expected_version)
        if not any(name.endswith("/LICENSE") for name in names):
            raise SystemExit(f"{path}: falta LICENSE en el sdist")
        if not any(name.endswith("/pyproject.toml") for name in names):
            raise SystemExit(f"{path}: falta pyproject.toml en el sdist")
        if not any(name.endswith("/src/xmind_md/cli.py") for name in names):
            raise SystemExit(f"{path}: falta el módulo CLI en el sdist")
    print(f"Sdist verificado: {path}")


def main() -> int:
    directory = Path(sys.argv[1] if len(sys.argv) > 1 else "dist")
    wheels = list(directory.glob("*.whl"))
    sdists = list(directory.glob("*.tar.gz"))
    if len(wheels) != 1 or len(sdists) != 1:
        raise SystemExit(
            f"Se esperaba un wheel y un sdist; encontrados {len(wheels)} y {len(sdists)}"
        )
    expected_version = project_version()
    verify_wheel(wheels[0], expected_version)
    verify_sdist(sdists[0], expected_version)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
