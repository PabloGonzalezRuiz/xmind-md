"""Punto de entrada para la ejecución mediante python -m xmind_md."""

# Reutilizar la misma función principal que utiliza el comando instalado.
from .cli import main

# Propagar al sistema operativo el código de salida de la CLI.
raise SystemExit(main())
