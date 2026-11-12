# XMind MD

**XMind MD** es un proyecto Python para transformar documentos estructurados en mapas XMind modernos (`.xmind`). La versión Alpha implementa una primera ruta Markdown → IR 1.0.0 → XMind. La dirección evoluciona hacia **PMD (Pableras Markdown)**: un lenguaje de autoría enriquecido, legible por personas y fácil de generar mediante IA, que reduzca el formateo manual posterior.

> Estado: `v0.1.0` Alpha publicada como prerelease el 2026-11-11. La CI del commit auditado `2c206dbc` está verde. La exportación XMind sigue siendo un perfil parcial; consulta la matriz de capacidades. La hoja de ruta actual se centra en PMD y la conversión asistida por IA.

## Dirección de producto: PMD

El objetivo futuro no es depender de la importación Markdown limitada de XMind. PMD permitirá describir roles semánticos, estructuras especiales (incluidas tablas de árbol), referencias de estilo y excepciones. Una IA podrá transformar Markdown ordinario en PMD consultando una biblioteca de estilos y reglas; el conversor resolverá el formato de forma determinista.

Consulta [Dirección de producto y diseño de PMD](docs/pmd-design.md) y la [hoja de ruta](docs/roadmap.md). Esta dirección es futura: no debe confundirse con las capacidades implementadas en la Alpha actual.

## Qué hace hoy la versión Alpha

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
.\\.venv\\Scripts\\Activate.ps1
python -m pip install .
```

Linux/macOS:

```bash
source .venv/bin/activate
python -m pip install .
```

Para ejecutar pruebas y herramientas de calidad, instala las dependencias de desarrollo:

```bash
python -m pip install ".[dev]"
```

## Uso de la CLI

El comando instalado es `xmind-md`. También puede ejecutarse como módulo con `python -m xmind_md`.

### Generar un archivo XMind

```bash
xmind-md examples/xmind-smoke-test.md --styles config/styles.yaml --output output/prueba.xmind
```

### Generar el IR en JSON

```bash
xmind-md examples/constitucion.md --styles config/styles.yaml --output output/constitucion.json
```

El formato se deduce de la extensión `.xmind` o `.json`. También puede indicarse con `--format xmind` o `--format json`. Si la extensión es conocida, debe coincidir con el formato indicado. Para otras extensiones es obligatorio especificar `--format`.

La exportación XMind resuelve los estilos antes de invocar el adaptador. Si el IR contiene una propiedad no soportada por el perfil de salida, la CLI muestra un error y termina con código 2. `examples/constitucion.md` está destinado a demostrar el parser/IR/JSON; no es un ejemplo exportable a XMind por contener recursos, tareas, boundaries y summaries.

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

- Temas `attached`, `detached` (con `layout.position.x/y`) y `callout`; el tema raíz debe ser `attached`.
- Notas de texto, etiquetas y marcadores.
- Enlaces web, enlaces internos entre temas y enlaces `file://`.
- Relaciones entre temas.
- Un subconjunto de propiedades de estilo y layout.

Existen pérdidas explícitas: el contenido principal y las notas se aplanan a texto de nota XMind; se pierde la estructura original de bloques y parte del formato inline. No se exportan actualmente recursos/imágenes, tareas, boundaries, summaries ni extensiones. La matriz completa está en [docs/xmind-adapter.md](docs/xmind-adapter.md).

### Interoperabilidad comprobada

El fixture `tests/fixtures/xmind/xmind-md-smoke-test.xmind` se descargó, abrió, inspeccionó, guardó, cerró y volvió a abrir en XMind Desktop para Windows 26.05.01107. Se comprobaron el tema central, dos ramas, un subtema, una nota, una etiqueta, un marcador de prioridad y una relación. Esta validación cubre ese fixture y esa versión; no certifica todas las capacidades del formato.

## Calidad y pruebas

En GitHub Actions se ejecutan en Ubuntu con Python 3.10, 3.11 y 3.12:

```bash
python -m ruff check src tests
python -m ruff format --check src tests
python -m pytest
python scripts/create_xmind_smoke.py
```

La CI ejecuta Ruff y **161 pruebas por versión** en Python 3.10, 3.11 y 3.12, y genera un XMind de comprobación en cada job. Un segundo job construye wheel y sdist, verifica sus metadatos/licencia, instala cada paquete en un entorno limpio y ejecuta conversiones CLI a JSON y XMind; los libros generados pasan verificaciones estructurales ZIP/MIME/JSON. La evidencia y los límites de las pruebas están en el [estado de desarrollo](docs/development-status.md) y la [auditoría de Release](docs/release-audit.md).

## Versiones publicadas y cambios

- [Changelog](CHANGELOG.md)
- [Notas de XMind MD 0.1.0 (Alpha)](docs/releases/v0.1.0.md)

La publicación se automatiza mediante `.github/workflows/release.yml`. El workflow exige confirmación de inspección manual del smoke en XMind Desktop y CI verde en el mismo commit candidato.

## Licencia

XMind MD se distribuye bajo la licencia [MIT](LICENSE), con el aviso de copyright de Pablo González Ruiz. Consulta [la decisión y el alcance de la licencia](docs/license-adoption.md) y el [inventario de avisos y procedencia de terceros](THIRD_PARTY_NOTICES.md). La licencia MIT del proyecto no cubre automáticamente los recursos y fixtures de terceros.

## Documentación

- [Estado de desarrollo](docs/development-status.md)
- [Hoja de ruta vigente](docs/roadmap.md)
- [Dirección de producto y diseño de PMD](docs/pmd-design.md)
- [Análisis detallado de la referencia Tema1](docs/reference-analysis-tema1.md)
- [Comportamiento de intercambio Markdown de XMind](docs/xmind-markdown-behavior.md)
- [Formato JSON de XMind y estrategia de conversión](docs/xmind-json-format.md)
- [Investigación de SDKs, esquemas, XMindMark y CLI oficiales XMind](docs/xmind-official-sdk-research.md)
- [Prompt maestro de reconstrucción](docs/ai-reconstruction-prompt.md)
- [Auditoría de empaquetado y publicación](docs/release-audit.md)
- [Auditoría de sincronización documental](docs/documentation-audit.md)
- [Decisión y adopción de licencia MIT](docs/license-adoption.md)
- [Avisos de terceros y procedencia](THIRD_PARTY_NOTICES.md)
- [Arquitectura](docs/architecture.md)
- [Especificación IR 1.0.0](docs/ir-specification.md)
- [Gramática Markdown y matriz de implementación](docs/grammar.md)
- [Sistema de estilos](docs/style-system.md)
- [Guía de usuario: estilos y temas personalizados](docs/user-guide/styles-and-themes.md)
- [Adaptador XMind y matriz de capacidades](docs/xmind-adapter.md)
- [Evaluación del motor XMind](docs/xmind-engine-evaluation.md)
- [Pruebas de interoperabilidad](docs/xmind-integration-tests.md)
- [Guía de desarrollo](docs/development.md)
- [Catálogo de archivos](docs/file-reference.md)

## Estructura del repositorio

- `src/xmind_md/`: parser, puente al IR, modelo, estilos, CLI y adaptadores.
- `config/`: estilos YAML de ejemplo.
- `examples/`: documentos Markdown de ejemplo y [mapas XMind de estudio y referencia](examples/xmind-study/README.md).
- `tests/`: pruebas unitarias, de integración y fixture XMind.
- `scripts/`: utilidades de generación de pruebas.
- `docs/`: especificaciones y documentación operativa.
- `.github/workflows/`: integración continua.

## Versión y estado

La versión del paquete tiene una única fuente de verdad: `src/xmind_md/__init__.py`. Setuptools la lee para construir los metadatos PEP 621 de `pyproject.toml`; el verificador extrae esa misma constante y la contrasta con `METADATA` del wheel y `PKG-INFO` del sdist. La CLI la muestra mediante `xmind-md --version`. Wheel y sdist se construyen, instalan y prueban en CI en entornos limpios separados. Desde ambos paquetes se ha comprobado la generación de JSON y XMind; el XMind resultante pasa verificaciones estructurales ZIP/MIME/JSON. La versión `0.1.0` está publicada como Alpha/pre-1.0 en la [GitHub Release](https://github.com/PabloGonzalezRuiz/xmind-md/releases/tag/v0.1.0), con wheel, sdist y `SHA256SUMS.txt`. No se presenta como estable porque el perfil XMind es parcial y quedan limitaciones documentadas.
