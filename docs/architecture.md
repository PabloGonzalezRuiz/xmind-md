# Arquitectura de XMind MD

## 1. Propósito y estado

XMind MD convierte Markdown enriquecido en un modelo intermedio neutral (IR 1.1.0) y exporta ese modelo a JSON o a un libro XMind moderno (`.xmind`). La implementación principal es Python (>=3.10).

La arquitectura separa parsing, representación semántica, resolución de estilos y serialización. El adaptador XMind implementa un perfil parcial y validado; las capacidades no soportadas se rechazan explícitamente.

## 2. Flujo de datos real

```text
Markdown + front matter/directivas YAML
                  |
                  v
       parser.py → DocumentSyntax
                  |
                  v
          ir_builder.py
                  |
                  v
             IR 1.1.0
              /      \
             v        v
     resolve_styles   json_adapter
             |        |
             v        v
       xmind_adapter  JSON IR
             |
             v
       libro .xmind
```

La CLI usa `parse_file_ir()`. La salida JSON serializa el IR. La salida XMind resuelve estilos y luego llama a `write_xmind()`. La selección del formato se realiza mediante `.json`, `.xmind` o `--format`.

## 3. Capas y responsabilidades

### 3.1 Entrada y parser

**Estado implementado:**

- `src/xmind_md/parser.py`: reconoce la gramática y produce un AST temporal (`DocumentSyntax` / `TopicSyntax`), sin construir entidades de dominio legacy.
- `src/xmind_md/syntax.py`: define los tipos AST sintácticos.
- `src/xmind_md/ir_builder.py`: construye directamente las entidades IR desde el AST y valida el documento.
- `src/xmind_md/ir_parser.py`: fachada pública `parse_markdown_ir()` / `parse_file_ir()`.
- `src/xmind_md/legacy_adapter.py`: proyecta el AST al modelo antiguo solo para las API legacy.
- La gramática implementada no equivale a CommonMark ni GFM completos. Su matriz y restricciones están en [grammar.md](grammar.md).

El diseño, la secuencia de migración y la evidencia están en [ir-parser-design.md](ir-parser-design.md) y [ir-consolidation-audit.md](ir-consolidation-audit.md).

El parser no genera archivos XMind ni conoce estructuras privadas del formato de salida.

### 3.2 Modelo intermedio (IR)

Directorio: `src/xmind_md/ir/`.

El contrato neutral vigente es IR 1.1.0 e incluye `MindMap`, `Sheet`, `Topic`, `ContentBlock`, anotaciones, recursos, relaciones, límites, resúmenes y estados de estilo. `Topic.semantic_role` separa el significado documental de `Topic.kind`; `Topic.structure` incorpora estructuras compuestas, inicialmente `tree_table`, con filas ordenadas y celdas que referencian temas hijos. IR 1.0.0 sigue siendo legible y dispone de migración explícita. El esquema JSON Draft 2020-12 y el ejemplo canónico están en `docs/ir-schema.json` y `examples/ir/constitucion.json`.

`src/xmind_md/model.py` se conserva para consumidores de la API antigua. La ruta canónica de parsing, resolución IR, CLI y adaptadores no lo utilizan. Las únicas dependencias runtime están aisladas en `legacy_adapter.py` y `legacy_styles.py`; no se elimina mientras no se conozcan consumidores externos.

### 3.3 Resolución de estilos

Archivo: `src/xmind_md/styles.py`.

`resolve_styles()` es la fachada pública: los documentos IR se delegan a `resolve_ir_styles()`; los objetos antiguos se delegan a `legacy_styles.py`, módulo de compatibilidad aislado. `styles.py` no importa `model.py`. Para IR, la precedencia por propiedad es:

1. Defaults del sistema.
2. `metadata.style_defaults` del documento.
3. Conjunto efectivo.
4. Estilo nombrado.
5. Overrides locales.

El conjunto se hereda por descendencia y puede sustituirse en un tema. Las definiciones del documento prevalecen sobre las externas con el mismo nombre. Las referencias de estilo se resuelven después de cargar ambos catálogos; las referencias externas no deben rechazarse antes de ejecutar `resolve_styles()`. La fusión es recursiva y no muta las definiciones originales; escribe el resultado en `style.resolved`. Se resuelven estilos de temas, notas, relaciones, límites y resúmenes.

La resolución neutral no implica que el adaptador XMind pueda traducir todas las propiedades. El adaptador mantiene su propio catálogo de propiedades admitidas y falla ante propiedades desconocidas.

### 3.4 Adaptadores

Directorio: `src/xmind_md/adapters/`.

- `json_adapter.py`: serializa el documento IR mediante su representación neutral.
- `xmind_adapter.py`: crea `content.json`, metadatos, manifiesto, miniatura y contenedor ZIP del formato XMind moderno.

El adaptador XMind recibe IR 1.0.0 y 1.1.0, pero todavía rechaza explícitamente `semantic_role` y `Topic.structure` hasta que exista su mapeo en la Fase 7. No analiza Markdown, no resuelve estilos y no modifica el IR. Valida el perfil soportado y lanza `XMindAdapterError` ante construcciones no exportables. La matriz detallada está en [xmind-adapter.md](xmind-adapter.md).

### 3.5 CLI

Archivo: `src/xmind_md/cli.py`.

La CLI:
- recibe un Markdown de entrada y una ruta de salida obligatoria;
- acepta `--styles` para configuración YAML externa;
- admite `--format json|xmind`, o infiere el formato por extensión;
- analiza a IR mediante `parse_file_ir()`;
- resuelve estilos antes de exportar XMind;
- serializa JSON y, si se proporciona configuración externa, puede resolver estilos antes de serializar;
- comunica errores de E/S, formato y estilos por stderr y devuelve código 2.

El comando instalado es `xmind-md`; también está disponible `python -m xmind_md`.

### 3.6 Automatización y pruebas

- `tests/`: pruebas unitarias y de integración de parser, IR, estilos, adaptadores y CLI.
- `.github/workflows/ci.yml`: matriz de pruebas Ubuntu/Python 3.10, 3.11 y 3.12 con Ruff, fixture, pytest y generación XMind; el job dependiente construye wheel/sdist, inspecciona metadatos/licencia, instala cada distribución en un entorno limpio con Python 3.12 y ejecuta conversiones CLI a JSON y XMind.
- `scripts/create_xmind_smoke.py`: genera un libro de comprobación para interoperabilidad manual.
- `scripts/verify_distributions.py`: comprueba que wheel/sdist contienen metadatos, LICENSE y módulos esenciales.
- `pyproject.toml`: metadatos de paquete, dependencias, entry point y configuración de herramientas.

La CI final de la consolidación [43227325673](https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/43227325673), commit `0361f290a490c61e108ee0aa8a9d212c7f7b73c3`, completó los cuatro jobs: 166 pruebas en Python 3.10/3.11/3.12, Ruff y build/install wheel/sdist. La CI histórica [43009510391](https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/43009510391), commit `69a583350a794ec0a567ff8e5e3770acd81f0110`, completó los cuatro jobs: Ruff y 161 pruebas en cada versión Python 3.10/3.11/3.12; smoke XMind en cada versión; build y verificación de wheel/sdist; instalación limpia de ambas distribuciones y conversiones CLI JSON/XMind con validación estructural ZIP/MIME/JSON. La evidencia detallada se mantiene en [development-status.md](development-status.md) y [release-audit.md](release-audit.md).

## 4. Contratos e invariantes

1. El parser produce una representación neutral, no un archivo XMind.
2. El IR no importa librerías de exportación.
3. Los adaptadores consumen entidades IR 1.x, no el modelo legacy; cada adaptador declara explícitamente las capacidades que exporta.
4. El orden de temas, bloques y colecciones significativas se conserva.
5. Las referencias de estilo son simbólicas; las propiedades resueltas se almacenan separadamente.
6. El adaptador no interpreta Markdown ni resuelve estilos.
7. Las capacidades no implementadas se rechazan explícitamente; no se descartan silenciosamente.
8. La generación de un ZIP válido y las pruebas JSON no equivalen a compatibilidad completa con XMind Desktop.
9. La compatibilidad se declara por característica y evidencia de versión, no como promesa genérica.

## 5. Decisiones técnicas vigentes

- Python >= 3.10; CI de pruebas en Python 3.10/3.11/3.12 sobre Ubuntu; build/install wheel/sdist en Python 3.12.
- Paquete con diseño `src/`.
- PyYAML como dependencia de ejecución.
- pytest, Ruff y jsonschema como dependencias de desarrollo.
- IR 1.1.0 como contrato vigente; IR 1.0.0 continúa siendo legible mediante compatibilidad y migración explícita.
- JSON como formato de inspección.
- XMind moderno ZIP + JSON como formato de salida.
- Serialización XMind mediante biblioteca estándar de Python; los SDK externos son referencias técnicas, no dependencias obligatorias.
- Sin generación de temas flotantes en el modelo neutral.
- CI Linux/Ubuntu; la interoperabilidad Windows se verifica con XMind Desktop, no mediante un runner Windows.

## 6. Verificación de interoperabilidad

El fixture `tests/fixtures/xmind/xmind-md-smoke-test.xmind` fue abierto, inspeccionado, guardado, cerrado y reabierto por el usuario en XMind Desktop 26.05.01107 para Windows. Se comprobaron tema central, ramas, subtema, nota, etiqueta, marcador y relación.

Esta comprobación acredita esos elementos del fixture en esa versión. No demuestra que todos los elementos del IR, todos los estilos o todas las capacidades del formato XMind estén soportados.

## 7. Extensiones y limitaciones

Las capacidades del parser, del IR y del adaptador son distintas. Que el IR pueda representar una entidad no significa que el parser pueda crearla desde Markdown ni que el adaptador XMind pueda exportarla. Consultar:

- [Gramática Markdown](grammar.md).
- [Especificación IR](ir-specification.md).
- [Sistema de estilos](style-system.md).
- [Matriz del adaptador XMind](xmind-adapter.md).
- [Intercambio Markdown ↔ XMind](xmind-markdown-behavior.md): observaciones verificadas y límites del Markdown exportado por XMind.
- [Formato JSON XMind](xmind-json-format.md): contenedor, estructura, estilos y traducciones del adaptador.
- [Análisis Tema1](reference-analysis-tema1.md): fixture de referencia que correlaciona JSON, SVG y Markdown.

## 8. Criterios para aceptar cambios

Cada cambio debe incluir:
- responsabilidad y capa afectada;
- cambios del IR si se introduce un concepto neutral nuevo;
- pruebas positivas y negativas;
- actualización de documentación y ejemplos;
- actualización de la matriz de capacidades;
- ejecución satisfactoria de CI antes de declarar el cambio validado.


## 9. Dirección arquitectónica objetivo: PMD e IA

Las secciones anteriores describen la implementación real de la versión Alpha. La siguiente evolución añade una capa de autoría PMD y conversión asistida por IA; no debe interpretarse como código ya implementado.

```text
Markdown de origen → IA → PMD → parser/validador PMD
       → IR neutral → resolución determinista → XMind
```

- La IA identifica semántica y estructuras y genera PMD usando catálogo, reglas y ejemplos.
- PMD expresa intención de autoría; IR sigue siendo el contrato neutral de ejecución. No son el mismo formato.
- La biblioteca de estilos describe estilos reutilizables, significado, destinatarios y reglas de aplicación.
- Las reglas semánticas son primarias y las estructurales complementarias.
- El motor resuelve defaults y herencia de forma determinista.
- Se contempla herencia por referencia al primer hijo, excepciones explícitas y recursividad; el algoritmo exacto está pendiente.
- El SVG debe ser lo más fiel posible a la apariencia original de XMind, sin exigir identidad de XML, atributos o IDs.

Ver [pmd-design.md](pmd-design.md) y [roadmap.md](roadmap.md). La ruta actual Markdown → IR → XMind debe seguir operativa durante la transición.


## 10. Referencias de implementación oficial XMind

Se han investigado tres repositorios oficiales TypeScript/MIT: [xmind-sdk-js](https://github.com/xmindltd/xmind-sdk-js), [xmind-model](https://github.com/xmindltd/xmind-model) y [xmind-generator](https://github.com/xmindltd/xmind-generator). El análisis técnico, sus esquemas, diferencias de empaquetado y límites se documentan en [xmind-official-sdk-research.md](xmind-official-sdk-research.md).

Conclusión arquitectónica: se utilizan como referencias y fuentes de fixtures, no como dependencias runtime ni como contrato neutral del proyecto. xmind-model evidencia entidades y familias de estilo adicionales; xmind-generator evidencia una segunda ruta oficial de serialización, con dataStructureVersion 2. Sus ZIP difieren del perfil actual del adaptador XMind MD (dataStructureVersion 3, layoutEngineVersion 5, mimetype y thumbnail). No se deben mezclar fragmentos de estos perfiles sin pruebas de apertura/guardado en la versión objetivo de XMind Desktop.


### Referencias oficiales de autoría y agentes

Además de los SDKs y serializadores, se ha estudiado [XMindMark](https://github.com/xmindltd/xmindmark), un lenguaje oficial de marcado para mapas mentales inspirado en Markdown (TypeScript/MIT), y el [XMind CLI Skill](https://github.com/xmindltd/xmind-cli), guía oficial para generación/edición asistida por agentes. XMindMark confirma un precedente de sintaxis textual ligera con relaciones, límites y resúmenes, pero no cubre tabla de árbol ni estilos semánticos por nodo. El repositorio público del CLI distribuye el Skill; el paquete CLI se publica por separado y no se ha inspeccionado su serializador. Ver [xmind-official-sdk-research.md](xmind-official-sdk-research.md).


## 11. Decisión arquitectónica vigente

La evolución PMD/IR se rige por [ADR-001](decisions/ADR-001-pmd-ir-architecture.md), [ADR-002](decisions/ADR-002-ir-semantic-structures.md) y [roadmap.md](roadmap.md). La dirección aprobada es consolidar el IR como único modelo de dominio de ejecución, añadir roles semánticos y estructuras neutrales (incluida `tree_table`), diseñar un catálogo de estilos semántico/visual y mantener los adaptadores desacoplados.

**Estado real:** la ruta canónica construye IR desde AST y no depende de `model.py`; las API antiguas se mantienen aisladas mediante adaptadores. El contrato 1.1.0 añade roles semánticos y `tree_table`. El adaptador XMind rechaza estas dos capacidades hasta la Fase 7. La especificación de 1.1.0 está en [ir-specification.md](ir-specification.md), el diseño en [ir-1.1-design.md](ir-1.1-design.md) y la decisión en [ADR-002](decisions/ADR-002-ir-semantic-structures.md).
