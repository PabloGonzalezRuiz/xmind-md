# Guía de desarrollo

## Requisitos

- Python 3.10 o superior (Python 3.10 está fuera de soporte upstream desde 2026-10-01; la compatibilidad de proyecto se comprueba en la matriz CI).
- Git.
- Un editor Python; VS Code o PyCharm son opciones válidas.
- Conexión a Internet para instalar dependencias.

## Preparar el entorno en Windows

Desde la raíz del repositorio:

~~~powershell
py -3.12 -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
~~~

Si PowerShell bloquea la activación, puede ejecutarse el intérprete del entorno directamente:

~~~powershell
.\\.venv\\Scripts\\python.exe -m pip install -e ".[dev]"
.\\.venv\\Scripts\\python.exe -m pytest
~~~

## Preparar el entorno en Linux/macOS

~~~bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
~~~

## Ejecutar el proyecto

El formato de salida se deduce de la extensión:

~~~bash
# Modelo intermedio JSON
xmind-md examples/constitucion.md --styles config/styles.yaml --output output/constitucion.json

# Libro XMind moderno
xmind-md examples/xmind-smoke-test.md --styles config/styles.yaml --output output/prueba.xmind
~~~

También se puede seleccionar explícitamente:

~~~bash
xmind-md examples/xmind-smoke-test.md --styles config/styles.yaml --output output/prueba.xmind --format xmind
~~~

Como módulo:

~~~bash
python -m xmind_md examples/xmind-smoke-test.md --styles config/styles.yaml --output output/prueba.xmind
~~~

La CLI analiza el Markdown y construye el IR canónico. Para XMind, resuelve los estilos y pasa el resultado al adaptador; para JSON, serializa el IR. Las extensiones conocidas `.json` y `.xmind` deben concordar con `--format`. Si se usa una extensión distinta, hay que indicar `--format`.



`examples/constitucion.md` es el ejemplo avanzado para parsing, IR y JSON; no debe utilizarse como smoke de XMind porque contiene características que el perfil XMind rechaza. Para exportación XMind utiliza `examples/xmind-smoke-test.md`.

La exportación XMind sigue siendo parcial: las capacidades no representables se rechazan explícitamente. Consulta [xmind-adapter.md](xmind-adapter.md).

## Ejecutar pruebas

~~~bash
python -m pytest
~~~

## Comprobar estilo del código

~~~bash
ruff check src tests
ruff format --check src tests
~~~

## Ciclo recomendado para una modificación

1. Crear una rama para el cambio.
2. Leer arquitectura, gramática y catálogo de archivos.
3. Añadir o modificar pruebas antes o junto con el código.
4. Implementar el cambio en la capa adecuada.
5. Ejecutar pytest y Ruff.
6. Actualizar documentación y ejemplos.
7. Revisar el diff completo.
8. Crear un commit con un mensaje descriptivo.

## Comentarios y documentación del código

Todo módulo debe explicar su propósito. Las clases y funciones públicas deben tener docstrings. Añade comentarios en español a los bloques que expresen decisiones, invariantes, limitaciones o pasos no obvios.

Evita comentarios redundantes del tipo "# incrementar i" justo antes de "i += 1". El objetivo es que otra persona o IA pueda comprender por qué existe una sección y qué contrato debe preservar.

## GitHub Actions

El workflow `.github/workflows/ci.yml` se ejecuta en Ubuntu con Python 3.12 y contiene dos jobs:

1. `Tests (Ubuntu / Python 3.10, 3.11 y 3.12)`: instalación editable con `.[dev]`, Ruff lint/format, descarga del fixture XMind de referencia, pytest, generación del smoke XMind y publicación de un artefacto por versión.
2. `Build and install distributions (Ubuntu)`: depende de toda la matriz; construye wheel y sdist, ejecuta `scripts/verify_distributions.py`, instala cada distribución en un entorno virtual limpio separado usando Python 3.12, convierte un Markdown autónomo a JSON y XMind y publica `python-distributions`.

El run [43007222944](https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/43007222944), sobre el HEAD que incluye la documentación posterior a la auditoría funcional, validó la matriz Python 3.10/3.11/3.12 con 161 pruebas por versión, Ruff, generación de smoke XMind, build de wheel/sdist, verificación de metadatos/licencia e instalación y conversiones CLI JSON/XMind desde ambas distribuciones. Los libros generados pasaron las comprobaciones estructurales ZIP/MIME/JSON.

La CI ejecuta pruebas y Ruff en Ubuntu con Python 3.10, 3.11 y 3.12. La construcción e instalación de wheel/sdist se valida en Python 3.12. No se deduce compatibilidad con Windows de estos resultados. Python 3.10 está fuera de soporte upstream desde 2026-10-01, aunque el proyecto mantiene compatibilidad técnica declarada. Un cambio no debe considerarse validado hasta que el run correspondiente al commit termine con conclusión `success`. Toda evidencia debe quedar registrada en `docs/development-status.md`.
