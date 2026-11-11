# XMind MD

**XMind MD** convierte documentos Markdown enriquecidos en mapas mentales XMind modernos (`.xmind`). El proyecto está implementado en Python y utiliza un modelo intermedio neutral (IR 1.0.0) para separar el lenguaje de entrada del formato de salida.

> Estado: versión de desarrollo 0.1.0. La CLI genera JSON IR y libros XMind; la CI de Ubuntu está operativa. Se ha comprobado manualmente en XMind Desktop 26.05.01107 un fixture con jerarquía, nota, etiqueta, marcador y relación. El exportador sigue siendo un perfil parcial: consulta la matriz de capacidades antes de usar construcciones avanzadas.

## Qué hace

- Convierte encabezados Markdown ATX (`#` a `######`) en una jerarquía de temas.
- Interpreta front matter YAML y directivas `:::xmind`, `:::xmind-note` y directivas globales de relación, límite y resumen.
- Conserva bloques de contenido estructurados en el IR: párrafos, listas, tablas, código, citas, separadores e imágenes como recursos.
- Resuelve estilos neutrales definidos en el documento y/o en YAML externo.
- Exporta el IR a JSON para inspección.
- Exporta un subconjunto validado del IR a un libro XMind moderno ZIP + JSON.
- Rechaza explícitamente las características que el perfil XMind actual no puede representar.

No es un conversor CommonMark/GFM completo. La gramática implementada y sus restricciones se describen en [docs/grammar.md](docs/grammar.md).

## Arquitectura

```text
Markdown + YAML
      |
      v
  parser.py
      |
      v
  ir_parser.py
      |
      v
    IR 1.0.0
      |
      +----> resolución de estilos
      |
      +----> adaptador JSON ----> .json
      |
      +----> adaptador XMind --> .xmind
```

El IR es el contrato neutral entre parser, estilos y adaptadores. El adaptador no interpreta Markdown ni resuelve estilos. Consulta [docs/architecture.md](docs/architecture.md) y [docs/ir-specification.md](docs/ir-specification.md).

## Requisitos

- Python 3.10 o superior.
- PyYAML 6 o superior (dependencia de ejecución).

## Instalación

Desde la raíz del repositorio:

```bash
python -m venv .venv
```

Windows (PowerShell):

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
```

Linux/macOS:

```bash
source .venv/bin/activate
python -m pip install -e .
```

Para ejecutar pruebas y herramientas de calidad, instala las dependencias de desarrollo:

```bash
python -m pip install -e ".[dev]"
```

## Uso de la CLI

El comando instalado es `xmind-md`. También puede ejecutarse como módulo con `python -m xmind_md`.

### Generar un archivo XMind

```bash
xmind-md examples/constitucion.md --styles config/styles.yaml --output output/constitucion.xmind
```

### Generar el IR en JSON

```bash
xmind-md examples/constitucion.md --styles config/styles.yaml --output output/constitucion.json
```

El formato se deduce de la extensión `.xmind` o `.json`. También puede indicarse con `--format xmind` o `--format json`. Si la extensión es conocida, debe coincidir con el formato indicado. Para otras extensiones es obligatorio especificar `--format`.

La exportación XMind resuelve los estilos antes de invocar el adaptador. Si el IR contiene una propiedad no soportada por el perfil de salida, la CLI muestra un error y termina con código 2.

## Ejemplo de entrada

```md
---
title: Constitución Española
style_set: TAI_LEGISLACION
---

# Constitución Española

## Título preliminar

:::xmind
id: articulo_1
labels:
  - IMPORTANTE
markers:
  - group: priority
    value: 1
:::
### Artículo 1

España se constituye en un Estado social y democrático de Derecho.
```

Los encabezados crean la jerarquía. Los párrafos, listas y demás bloques de contenido pertenecen al tema activo; no crean temas adicionales.

## Capacidades y limitaciones importantes

El exportador XMind actual incluye, entre otras capacidades:

- Temas `attached`, `detached` (con posición) y `callout`.
- Notas de texto, etiquetas y marcadores.
- Enlaces web, enlaces internos entre temas y enlaces `file://`.
- Relaciones entre temas.
- Un subconjunto de propiedades de estilo y layout.

Existen pérdidas explícitas: el contenido principal y las notas se aplanan a texto de nota XMind; se pierde la estructura original de bloques y parte del formato inline. No se exportan actualmente recursos/imágenes, tareas, boundaries, summaries ni extensiones. La matriz completa está en [docs/xmind-adapter.md](docs/xmind-adapter.md).

### Interoperabilidad comprobada

El fixture `tests/fixtures/xmind/xmind-md-smoke-test.xmind` se descargó, abrió, inspeccionó, guardó, cerró y volvió a abrir en XMind Desktop para Windows 26.05.01107. Se comprobaron el tema central, dos ramas, un subtema, una nota, una etiqueta, un marcador de prioridad y una relación. Esta validación cubre ese fixture y esa versión; no certifica todas las capacidades del formato.

## Calidad y pruebas

En GitHub Actions se ejecutan en Ubuntu con Python 3.12:

```bash
python -m ruff check src tests
python -m ruff format --check src tests
python -m pytest
python scripts/create_xmind_smoke.py
```

La ejecución de referencia más reciente de la tarea CI/Ruff completó lint, formato, descarga del fixture, 131 pruebas, generación XMind y publicación del artefacto. Consulta el [estado de desarrollo](docs/development-status.md) para la evidencia más reciente.

## Documentación

- [Estado de desarrollo y hoja de ruta](docs/development-status.md)
- [Prompt maestro de reconstrucción](docs/ai-reconstruction-prompt.md)
- [Arquitectura](docs/architecture.md)
- [Especificación IR 1.0.0](docs/ir-specification.md)
- [Gramática Markdown y matriz de implementación](docs/grammar.md)
- [Sistema de estilos](docs/style-system.md)
- [Adaptador XMind y matriz de capacidades](docs/xmind-adapter.md)
- [Evaluación del motor XMind](docs/xmind-engine-evaluation.md)
- [Pruebas de interoperabilidad](docs/xmind-integration-tests.md)
- [Guía de desarrollo](docs/development.md)
- [Catálogo de archivos](docs/file-reference.md)

## Estructura del repositorio

- `src/xmind_md/`: parser, puente al IR, modelo, estilos, CLI y adaptadores.
- `config/`: estilos YAML de ejemplo.
- `examples/`: documentos Markdown de ejemplo.
- `tests/`: pruebas unitarias, de integración y fixture XMind.
- `scripts/`: utilidades de generación de pruebas.
- `docs/`: especificaciones y documentación operativa.
- `.github/workflows/`: integración continua.

## Versión y estado

La versión del paquete es `0.1.0`, declarada en `pyproject.toml` y `src/xmind_md/__init__.py`. Todavía no se ha publicado una Release estable. La publicación se realizará después de la auditoría final de capacidades, packaging, licencia y documentación.
