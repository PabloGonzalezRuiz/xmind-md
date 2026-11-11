"""Verifica el contenido legal y técnico de wheel y sdist construidos."""

from __future__ import annotations

import sys
import tarfile
import zipfile
from pathlib import Path


def verify_wheel(path: Path) -> None:
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        metadata_files = [name for name in names if name.endswith(".dist-info/METADATA")]
        if len(metadata_files) != 1:
            raise SystemExit(f"{path}: se esperaba un único METADATA")
        metadata = archive.read(metadata_files[0]).decode("utf-8")
        if "Name: xmind-md" not in metadata or "Version: 0.1.0" not in metadata:
            raise SystemExit(f"{path}: nombre o versión incorrectos en METADATA")
        if "License-Expression: MIT" not in metadata:
            raise SystemExit(f"{path}: falta License-Expression: MIT")
        if not any(name.endswith(".dist-info/licenses/LICENSE") for name in names):
            raise SystemExit(f"{path}: falta LICENSE en el wheel")
        if "xmind_md/cli.py" not in names:
            raise SystemExit(f"{path}: falta el módulo CLI")
    print(f"Wheel verificado: {path}")


def verify_sdist(path: Path) -> None:
    with tarfile.open(path, "r:gz") as archive:
        names = set(archive.getnames())
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
    verify_wheel(wheels[0])
    verify_sdist(sdists[0])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
